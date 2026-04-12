from flask import Flask, request, jsonify
from flask_cors import CORS
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import json

import httpx, asyncio, concurrent.futures

OLLAMA_URL = "http://localhost:11434/api/generate"

LOCAL_MODELS = {
        "Llama": "llama3",
        "Phi": "phi",
        "Mistral": "mistral"

   # "Llama-3.2-1B": "llama3.2:1b",
    # "Mistral-7B"  : "mistral:7b",
    #"Phi-2.7B"    : "phi:2.7b",
    #"Gemma-3-1B"  : "gemma3:1b",
    #"Qwen3-1.7B"  : "qwen3:1.7b",
}

def ask_ollama(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        r = httpx.post(
            "http://127.0.0.1:11434/api/generate",
            json=payload,
            timeout=300
        )
        r.raise_for_status()

        data = r.json()

        # 🔥 IMPORTANT: correct field extraction
        return data.get("response", "")

    except Exception as e:
        return f"[{model}] ERROR: {str(e)}"

def generate_multi_model(system: str, user: str) -> dict[str,str]:
    """Return dict {model_name: answer, ...} in ~10-15 s (parallel)."""
    full_prompt = f"{system}\n\n{user}"
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exe:
        future_map = {
            exe.submit(ask_ollama, model_id, full_prompt): name
            for name, model_id in LOCAL_MODELS.items()
        }
        answers = {}
        for f in concurrent.futures.as_completed(future_map):
            name = future_map[f]
            answers[name] = f.result()
    return answers

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# Milvus connection parameters
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBGewtHd2LeVcKVRGhlP5rtL8eSTv5OepA")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

# === Helper Functions ===

def search_milvus(collection_name, query_text, top_k=3):
    collection = Collection(collection_name)
    collection.load()

    # Fields we want to include
    preferred_fields = ["text", "filename"]

    # Only include available fields
    available_fields = {field.name for field in collection.schema.fields}
    output_fields = [field for field in preferred_fields if field in available_fields]

    # Create query embedding
    query_embedding = embedding_model.encode([query_text])[0].tolist()
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=output_fields
    )

    # Normalize distances
    distances = [hit.distance for hits in results for hit in hits]
    max_dist = max(distances) if distances else 1.0
    min_dist = min(distances) if distances else 0.0
    range_dist = max_dist - min_dist or 1.0

    # Build response
    response = []
    for hits in results:
        for hit in hits:
            text_content = hit.entity.get("text")
            if text_content:
                normalized_score = 1 - ((hit.distance - min_dist) / range_dist)
                response.append({
                    "text": text_content,
                    "filename": hit.entity.get("filename") if "filename" in output_fields else None,
                    "score": round(normalized_score, 4)
                })
    return response



def compare_llm_output_to_retrieved(llm_output, retrieved_docs):
    output_lower = llm_output.lower()
    used_docs = []
    unused_docs = []

    for doc in retrieved_docs:
        if doc["text"].lower()[:50] in output_lower:
            used_docs.append(doc)
        else:
            unused_docs.append(doc)

    return used_docs, unused_docs

def log_interaction(query_text, retrieved_docs, llm_output, used_docs, unused_docs, log_file="llm_audit_log.json"):
    entry = {
        "query": query_text,
        "llm_output": llm_output,
        "retrieved_docs": retrieved_docs[:1],
        "used_docs": used_docs,
        "unused_docs": unused_docs,
    }
    with open(log_file, "a") as f:
        json.dump(entry, f, indent=2)
        f.write("\n")

# === Route Handlers ===




@app.route("/query/ipc", methods=["POST"])
def query_ipc():
    data = request.get_json()
    query_text = data.get("query")
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    retrieved_docs = search_milvus("IPC_collection", query_text)
    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
You are a specialized AI assistant with expertise in Indian Penal Code (IPC) and related laws. Your primary responsibility is to analyze user queries and provide accurate legal responses while clearly tracing the underlying legal logic between IPC sections.

🧠 Your answers must show a **Knowledge Graph Trace** of how key legal concepts like “intention”, “force”, or “consent” flow through IPC sections, e.g.:

"Intent" → Section 299 (Culpable Homicide) → Section 300 (Murder) → Section 302 (Punishment)

📌 Guidelines:
- Use only Indian laws (IPC, CrPC, Evidence Act).
- Use the provided context if relevant, otherwise use your general knowledge of IPC.
- Do not hallucinate or make assumptions.
- Include only **valid IPC section numbers** that are traceable from the query.
- Avoid giving legal advice—provide only academic, statutory responses.

📋 Response Format:

1. **Knowledge Graph Trace**: (Legal rule flow)
- Show how one legal section leads to another.
- Example:
  "Intent" → Section 299 → Section 300 → Section 302

2. **Answer**:
- Bullet point list:
  - Section Number (e.g., 299)
  - Short Description
  - [Filename or reference if available]

If context is not sufficient or query is unclear, ask for clarification.
"""  # Clean, single string without merge artifacts

    user_prompt = f"Context:\n{context}\n\nQuestion: {query_text}"

    # ←  NEW: five local answers instead of one Gemini answer
    answers = generate_multi_model(system_prompt, user_prompt)

    # keep the same audit log structure (log the first answer only)
    first_answer = answers.get("Llama") or  next(iter(answers.values()))
    used_docs, unused_docs = compare_llm_output_to_retrieved(first_answer, retrieved_docs)
    log_interaction(query_text, retrieved_docs, first_answer, used_docs, unused_docs)

    return jsonify({
        "answers": answers,
        "retrieved_docs": retrieved_docs,
        "used_docs": used_docs,
        "unused_docs": unused_docs
    })


@app.route("/query/legal", methods=["POST"])
def query_legal_documents():
    data = request.get_json()
    query_text = data.get("query")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    retrieved_docs = search_milvus("Precedence_collection", query_text)
    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
You are a specialized AI assistant with expertise in Indian Law. Your task is to cite relevant Indian case laws and provide their key details based on the specified legal context.

Guidelines:
- Focus only on Indian case laws.
- Begin with a short reasoning paragraph.
- Then provide bullet points with case name, year, court, and short legal significance.
- Use only retrieved context where possible.
- If the query is unclear, say so.

Response Format:
1. Reasoning
2. Answer:
- Case name
- Citation/year/court
- Short summary
"""

    user_prompt = f"Context:\n{context}\n\nQuestion: {query_text}"

    try:
        answers = generate_multi_model(system_prompt, user_prompt)
        first_answer = next(iter(answers.values()))
        used_docs, unused_docs = compare_llm_output_to_retrieved(first_answer, retrieved_docs)
        log_interaction(query_text, retrieved_docs, first_answer, used_docs, unused_docs)

        return jsonify({
            "answers": answers,
            "retrieved_docs": retrieved_docs,
            "used_docs": used_docs,
            "unused_docs": unused_docs
        })

    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500


@app.route("/generate_contract", methods=["POST"])
def generate_contract():
    data = request.get_json()
    user_question = data.get("question")

    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    try:
        
        retrieved_docs = search_milvus("Document_Creation_collection", user_question, top_k=3)
        context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

        system_prompt = """
You are a legal drafting assistant.

Draft a complete, formal, readable legal document based on the user's request.

Rules:
- Write the full document, not an explanation.
- Use clear section headings.
- Use formal legal language.
- If the user asks for a rental agreement, generate a proper rental agreement with standard clauses.
- Do not ask the user for more details unless absolutely necessary.
- If some details are missing, use reasonable placeholders like:
  [LANDLORD NAME], [TENANT NAME], [RENT AMOUNT], [PROPERTY ADDRESS], [START DATE]

Output only the document text.
"""

        user_prompt = f"Context:\n{context}\n\nQuestion: {user_question}"

        answers = generate_multi_model(system_prompt, user_prompt)

        llm_output = answers.get("Llama") or next(iter(answers.values()))

        used_docs, unused_docs = compare_llm_output_to_retrieved(llm_output, retrieved_docs)
        log_interaction(user_question, retrieved_docs, llm_output, used_docs, unused_docs)

        return jsonify({
            "contract": llm_output,
            "retrieved_docs": retrieved_docs,
            "used_docs": used_docs,
            "unused_docs": unused_docs
        })

    except Exception as e:
        print("ERROR in /generate_contract:", str(e))
        return jsonify({"error": f"Error generating contract: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050)