from flask import Flask, request, jsonify
from flask_cors import CORS
from pymilvus import connections, Collection, FieldSchema, DataType, CollectionSchema, utility
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import json
import re
from datetime import datetime
import httpx
import concurrent.futures
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import bns_mapping

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

LOCAL_MODELS = {
    "Llama": "llama3",
    "Phi": "phi",
    "Mistral": "mistral"
}

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

# Load embedding model once globally
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def ensure_milvus_connection():
    """Lazily establish a connection to Milvus, preventing startup boot failures."""
    try:
        if not connections.has_connection("default"):
            connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    except Exception as e:
        print(f"[Milvus Connection Warning] Failed lazy connection: {e}")


# === Text Extraction & Chunking Helpers for Upload API ===

def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()


def extract_text_from_pdf_direct(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            page_text = page.get_text("text")
            if page_text and page_text.strip():
                text_parts.append(page_text)
        doc.close()
        return clean_text("\n".join(text_parts))
    except Exception as e:
        print(f"Error reading PDF directly {pdf_path}: {e}")
        return ""


def extract_text_from_pdf_ocr(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        ocr_text_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            mode = "RGB" if pix.alpha == 0 else "RGBA"
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(image)
            page_text = clean_text(page_text)
            if page_text:
                ocr_text_parts.append(page_text)
        doc.close()
        return clean_text("\n".join(ocr_text_parts))
    except Exception as e:
        print(f"Error OCR-reading PDF {pdf_path}: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    text = extract_text_from_pdf_direct(pdf_path)
    if text:
        print(f"Direct text extraction succeeded for {pdf_path}")
        return text
    print(f"Direct text extraction failed/empty for {pdf_path}, invoking OCR...")
    return extract_text_from_pdf_ocr(pdf_path)


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return clean_text(text)
    except Exception as e:
        print(f"Error OCR reading image {image_path}: {e}")
        return ""


def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break
        start = end - overlap
    return chunks


# === Core LLM & Translation Helpers ===

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
            timeout=180
        )
        r.raise_for_status()
        return r.json().get("response", "")
    except Exception as e:
        return f"[{model}] ERROR: {str(e)}"


def generate_multi_model(system: str, user: str) -> dict[str, str]:
    """Runs all configured local models in parallel."""
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


def ask_gemini(prompt: str) -> str:
    if not gemini_model:
        return "Gemini fallback unavailable: GEMINI_API_KEY not set."
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini ERROR: {str(e)}"


def generate_text(system: str, user: str, selected_model: str) -> dict[str, str]:
    """Generates LLM output for the selected model, with local and Gemini fallback."""
    full_prompt = f"{system}\n\n{user}"
    
    if selected_model == "All Models":
        answers = generate_multi_model(system, user)
        all_failed = True
        for ans in answers.values():
            if ans and "ERROR" not in ans and len(ans.strip()) > 40:
                all_failed = False
        if all_failed:
            if gemini_model:
                answers = {"Gemini": ask_gemini(full_prompt)}
            else:
                answers = {"Error": "All local models failed to respond and Gemini API key is not configured."}
        return answers
    
    elif selected_model == "Gemini":
        if gemini_model:
            return {"Gemini": ask_gemini(full_prompt)}
        else:
            return {"Error": "Gemini fallback requested, but GEMINI_API_KEY is not configured in your environment."}
        
    else:
        model_id = LOCAL_MODELS.get(selected_model, "llama3")
        local_ans = ask_ollama(model_id, full_prompt)
        
        # Check if local generation failed
        if not local_ans or "ERROR" in local_ans or len(local_ans.strip()) <= 40:
            print(f"[Fallback] Local model {selected_model} ({model_id}) failed. Trying alternative local models...")
            # Try other local models
            for alt_name, alt_id in LOCAL_MODELS.items():
                if alt_name != selected_model:
                    alt_ans = ask_ollama(alt_id, full_prompt)
                    if alt_ans and "ERROR" not in alt_ans and len(alt_ans.strip()) > 40:
                        print(f"[Fallback] Succeeded with alternative local model: {alt_name}")
                        return {alt_name: alt_ans}
            
            # If all local models failed, try Gemini
            if gemini_model:
                print(f"[Fallback] All local models failed. Falling back to Gemini.")
                return {"Gemini": ask_gemini(full_prompt)}
            else:
                return {"Error": f"The model {selected_model} failed, and no alternative local models or Gemini API keys were available to handle the fallback."}
            
        return {selected_model: local_ans}


import urllib.parse
from bs4 import BeautifulSoup

def translate_text(text: str, target_lang: str) -> str:
    """Translates text using Gemini. Returns input unchanged if English or if Gemini unavailable."""
    if not target_lang or target_lang.lower() == "english" or not gemini_model:
        return text
    
    prompt = f"Translate the following text to {target_lang}. Return ONLY the translation, with no extra conversational replies, comments, or intro/outro formatting:\n\n{text}"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation Exception: {e}")
        return text


def search_web_legal_context(query: str, max_results: int = 3) -> list[dict]:
    """Queries DuckDuckGo HTML search for real-time legal summaries and judgments."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    encoded_query = urllib.parse.quote(query + " Indian Law case judgment section")
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    try:
        r = httpx.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return []
            
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        
        for result in soup.find_all("div", class_="result")[:max_results]:
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            
            if title_tag and snippet_tag:
                title = title_tag.text.strip()
                snippet = snippet_tag.text.strip()
                link = title_tag.get("href")
                
                # Unquote DuckDuckGo redirect link
                if "uddg=" in link:
                    try:
                        link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                    except Exception:
                        pass
                
                results.append({
                    "text": f"Title: {title}\nSnippet: {snippet}\nSource: {link}",
                    "filename": f"Web: {title[:40]}",
                    "score": 0.85
                })
        return results
    except Exception as e:
        print(f"[Web Search Warning] DuckDuckGo search failed: {e}")
        return []


def index_web_docs_async(docs, collection_name):
    """Background task to index real-time web search results in Milvus for caching."""
    ensure_milvus_connection()
    try:
        collection = Collection(collection_name)
        collection.load()
        filename_list = []
        text_list = []
        vector_list = []
        for doc in docs:
            vector = embedding_model.encode([doc["text"]])[0].tolist()
            filename_list.append(doc["filename"])
            text_list.append(doc["text"])
            vector_list.append(vector)
        collection.insert([filename_list, text_list, vector_list])
        collection.flush()
        print(f"[Self-Update] Successfully cached {len(docs)} web search results into {collection_name}")
    except Exception as ex:
        print(f"[Self-Update Error] Background indexing failed: {ex}")


# === RAG & Context Utilities ===

def search_milvus(collection_name, query_text, top_k=3):
    ensure_milvus_connection()
    try:
        if not utility.has_collection(collection_name):
            return []
            
        collection = Collection(collection_name)
        collection.load()

        preferred_fields = ["text", "filename"]
        available_fields = {field.name for field in collection.schema.fields}
        output_fields = [field for field in preferred_fields if field in available_fields]

        query_embedding = embedding_model.encode([query_text])[0].tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields
        )

        distances = [hit.distance for hits in results for hit in hits]
        max_dist = max(distances) if distances else 1.0
        min_dist = min(distances) if distances else 0.0
        range_dist = max_dist - min_dist or 1.0

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
    except Exception as e:
        print(f"[Milvus Search Warning] Search failed for {collection_name}: {e}")
        return []


def compare_llm_output_to_retrieved(llm_output, retrieved_docs):
    """Heuristic word token matching to determine which retrieved documents were actually cited/used."""
    output_lower = llm_output.lower()
    used_docs = []
    unused_docs = []

    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'section', 'court', 'case', 'ipc', 'bns', 'under'}

    for doc in retrieved_docs:
        filename = doc.get("filename")
        filename_clean = os.path.splitext(filename)[0].lower() if filename else ""
        
        # Check snippet match
        text_snippet = doc["text"].lower()[:40]
        
        is_used = False
        if filename_clean and len(filename_clean) > 3 and filename_clean in output_lower:
            is_used = True
        elif text_snippet in output_lower:
            is_used = True
        else:
            # Fuzzy match: calculate intersection of keywords
            doc_words = set(re.findall(r'\w+', doc["text"].lower())) - stop_words
            output_words = set(re.findall(r'\w+', output_lower))
            overlap = doc_words.intersection(output_words)
            
            if len(doc_words) > 0 and (len(overlap) / len(doc_words)) > 0.35:
                is_used = True
                
        if is_used:
            used_docs.append(doc)
        else:
            unused_docs.append(doc)

    return used_docs, unused_docs


def log_interaction(query_text, retrieved_docs, llm_output, used_docs, unused_docs, log_file="llm_audit_log.json"):
    """Appends interactions as a clean, single-line JSON structure (JSONL)."""
    entry = {
        "query": query_text,
        "llm_output": llm_output,
        "retrieved_docs": retrieved_docs[:1],
        "used_docs": used_docs,
        "unused_docs": unused_docs,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error appending audit log: {e}")


# === Route Handlers ===

@app.route("/query/ipc", methods=["POST"])
def query_ipc():
    data = request.get_json()
    query_text = data.get("query")
    selected_model = data.get("model", "Llama")
    selected_lang = data.get("language", "English")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # 1. Translate query to English if necessary
    query_en = translate_text(query_text, "English") if selected_lang.lower() != "english" else query_text

    # 2. Extract IPC <-> BNS conversions
    bns_transitions = bns_mapping.extract_sections_from_text(query_en)

    # 3. Retrieve database context (always matches in English)
    retrieved_docs = search_milvus("IPC_collection", query_en)
    
    # If no local results or relevance is low, trigger web fallback
    if not retrieved_docs or (len(retrieved_docs) > 0 and max(doc["score"] for doc in retrieved_docs) < 0.45):
        print(f"[RAG Fallback] Weak local context in IPC_collection. Running web search for: {query_en}")
        web_docs = search_web_legal_context(query_en)
        if web_docs:
            retrieved_docs = web_docs
            # Run background thread to cache web search results in Milvus
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(index_web_docs_async, web_docs, "IPC_collection")

    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
You are a specialized AI assistant with expertise in Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS). Your primary responsibility is to analyze user queries, explain legal provisions, and provide accurate legal responses.

🧠 When explaining criminal laws, you must highlight the transition between IPC and BNS.
Show how key legal concepts trace between sections, e.g.:
"Intent" → Section 299 (Culpable Homicide) / Section 100 BNS → Section 300 (Murder) / Section 101 BNS

📌 Guidelines:
- Use only Indian laws (IPC, BNS, CrPC, BNSS, Indian Evidence Act).
- Detail sections cleanly with their numbers.
- If the provided context is empty or does not mention the relevant sections, use your general knowledge of Indian criminal law to provide a complete and correct answer. Do not say that no context is available.
- Format all section references as markdown links to Indian Kanoon searches, e.g., [IPC Section 302](https://indiankanoon.org/search/?formInput=IPC+Section+302) or [BNS Section 103](https://indiankanoon.org/search/?formInput=BNS+Section+103).
- Avoid giving legal advice—provide only academic, statutory responses.
"""

    user_prompt = f"Context:\n{context}\n\nQuestion: {query_en}"

    # 4. Generate Answer
    answers = generate_text(system_prompt, user_prompt, selected_model)
    first_model = next(iter(answers.keys()))
    answer_text = answers[first_model]

    # 5. Translate response back if necessary
    if selected_lang.lower() != "english":
        translated_answers = {}
        for m, txt in answers.items():
            translated_answers[m] = translate_text(txt, selected_lang)
        answers = translated_answers
        answer_text = answers[first_model]

    # 6. Audit & Log
    used_docs, unused_docs = compare_llm_output_to_retrieved(answer_text, retrieved_docs)
    log_interaction(query_text, retrieved_docs, answer_text, used_docs, unused_docs)

    return jsonify({
        "answers": answers,
        "retrieved_docs": retrieved_docs,
        "used_docs": used_docs,
        "unused_docs": unused_docs,
        "bns_transitions": bns_transitions
    })


@app.route("/query/legal", methods=["POST"])
def query_legal_documents():
    data = request.get_json()
    query_text = data.get("query")
    selected_model = data.get("model", "Llama")
    selected_lang = data.get("language", "English")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Translate input
    query_en = translate_text(query_text, "English") if selected_lang.lower() != "english" else query_text

    # Search vector database
    retrieved_docs = search_milvus("Precedence_collection", query_en)
    
    # If no local results or relevance is low, trigger web fallback
    if not retrieved_docs or (len(retrieved_docs) > 0 and max(doc["score"] for doc in retrieved_docs) < 0.45):
        print(f"[RAG Fallback] Weak local context in Precedence_collection. Running web search for: {query_en}")
        web_docs = search_web_legal_context(query_en)
        if web_docs:
            retrieved_docs = web_docs
            # Run background thread to cache web search results in Milvus
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(index_web_docs_async, web_docs, "Precedence_collection")

    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
You are a specialized AI assistant with expertise in Indian Law. Your task is to cite relevant Indian case laws and provide their key details.

Guidelines:
- Focus only on Indian case laws.
- Begin with a short reasoning paragraph explaining the legal topic.
- Provide bullet points with case name, year, court, and short legal significance.
- If the provided context is empty or doesn't match the query, do NOT fail or say no context is available. Instead, use your general legal knowledge to recall and describe the most famous and relevant Indian Supreme Court or High Court judgments related to the topic of the query.
- You must format every case name or citation as a clickable markdown link pointing to its search on Indian Kanoon, e.g., [Kesavananda Bharati v. State of Kerala (1973)](https://indiankanoon.org/search/?formInput=Kesavananda+Bharati+v.+State+of+Kerala+1973) or [Justice K.S. Puttaswamy v. Union of India (2017)](https://indiankanoon.org/search/?formInput=Justice+K.S.+Puttaswamy+v.+Union+of+India+2017).
"""

    user_prompt = f"Context:\n{context}\n\nQuestion: {query_en}"

    try:
        answers = generate_text(system_prompt, user_prompt, selected_model)
        first_model = next(iter(answers.keys()))
        answer_text = answers[first_model]

        # Translate output
        if selected_lang.lower() != "english":
            translated_answers = {}
            for m, txt in answers.items():
                translated_answers[m] = translate_text(txt, selected_lang)
            answers = translated_answers
            answer_text = answers[first_model]

        used_docs, unused_docs = compare_llm_output_to_retrieved(answer_text, retrieved_docs)
        log_interaction(query_text, retrieved_docs, answer_text, used_docs, unused_docs)

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
    selected_model = data.get("model", "Llama")
    selected_lang = data.get("language", "English")

    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    # Translate input
    query_en = translate_text(user_question, "English") if selected_lang.lower() != "english" else user_question

    try:
        retrieved_docs = search_milvus("Document_Creation_collection", query_en, top_k=3)
        
        # If no local results or relevance is low, trigger web fallback
        if not retrieved_docs or (len(retrieved_docs) > 0 and max(doc["score"] for doc in retrieved_docs) < 0.45):
            print(f"[RAG Fallback] Weak local context in Document_Creation_collection. Running web search for: {query_en}")
            web_docs = search_web_legal_context(query_en + " legal document contract template text")
            if web_docs:
                retrieved_docs = web_docs
                # Run background thread to cache web search results in Milvus
                executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                executor.submit(index_web_docs_async, web_docs, "Document_Creation_collection")

        context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

        system_prompt = """
You are a legal drafting assistant.
Draft a complete, formal, readable legal document based on the user's request.

Rules:
- Write the full document, not an explanation.
- Use clear section headings.
- Use formal legal language.
- If some details are missing, use reasonable placeholders like:
  [LANDLORD NAME], [TENANT NAME], [RENT AMOUNT], [PROPERTY ADDRESS], [START DATE]
- If the provided context is empty or doesn't contain the requested agreement template, use your general knowledge of Indian legal documents to draft a standard, legally valid, and complete version of the agreement.
Output only the document text.
"""

        user_prompt = f"Context:\n{context}\n\nQuestion: {query_en}"

        answers = generate_text(system_prompt, user_prompt, selected_model)
        first_model = next(iter(answers.keys()))
        llm_output = answers[first_model]

        # Translate output
        if selected_lang.lower() != "english":
            translated_answers = {}
            for m, txt in answers.items():
                translated_answers[m] = translate_text(txt, selected_lang)
            answers = translated_answers
            llm_output = answers[first_model]

        used_docs, unused_docs = compare_llm_output_to_retrieved(llm_output, retrieved_docs)
        log_interaction(user_question, retrieved_docs, llm_output, used_docs, unused_docs)

        return jsonify({
            "contract": llm_output,
            "answers": answers,
            "retrieved_docs": retrieved_docs,
            "used_docs": used_docs,
            "unused_docs": unused_docs
        })

    except Exception as e:
        print("ERROR in /generate_contract:", str(e))
        return jsonify({"error": f"Error generating contract: {str(e)}"}), 500


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Endpoint allowing real-time PDF/image document uploads to update the RAG collections."""
    ensure_milvus_connection()
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["file"]
    collection_type = request.form.get("type", "precedence")  # "ipc", "precedence", or "document"
    
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
        
    # Temporary workspace folder
    upload_dir = "./uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)
    
    try:
        extracted_text = ""
        ext = os.path.splitext(file.filename)[1].lower()
        
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        elif ext == ".pdf":
            extracted_text = extract_text_from_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            extracted_text = extract_text_from_image(file_path)
        else:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400
            
        extracted_text = clean_text(extracted_text)
        if not extracted_text or len(extracted_text) < 15:
            return jsonify({"error": "Failed to extract clean text from file. Check format or image quality."}), 400
            
        chunks = chunk_text(extracted_text, chunk_size=1000, overlap=200)
        if not chunks:
            return jsonify({"error": "No text chunks generated from file."}), 400
            
        # Select Milvus collection
        collection_name = "Precedence_collection"
        if collection_type == "document":
            collection_name = "Document_Creation_collection"
        elif collection_type == "ipc":
            collection_name = "IPC_collection"
            
        if not utility.has_collection(collection_name):
            # Create a simple collection if it's completely missing
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8000),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)
            ]
            schema = CollectionSchema(fields=fields, description="Dynamic collection upload")
            collection = Collection(name=collection_name, schema=schema)
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index(field_name="vector", index_params=index_params)
        else:
            collection = Collection(collection_name)
            
        collection.load()
        
        filename_list = []
        text_list = []
        vector_list = []
        
        for chunk in chunks:
            vector = embedding_model.encode([chunk])[0].tolist()
            filename_list.append(file.filename)
            text_list.append(chunk)
            vector_list.append(vector)
            
        collection.insert([filename_list, text_list, vector_list])
        collection.flush()
        
        print(f"Indexed {len(chunks)} chunks from {file.filename} successfully.")
        return jsonify({
            "success": True,
            "message": f"Successfully parsed & indexed {len(chunks)} text chunks from {file.filename}."
        })
        
    except Exception as e:
        print(f"Index Upload Error: {e}")
        return jsonify({"error": f"Indexing error occurred: {str(e)}"}), 500
    finally:
        # Clean up local temporary file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)