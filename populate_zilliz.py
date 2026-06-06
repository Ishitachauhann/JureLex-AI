# populate_zilliz.py
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connection parameters from environment
MILVUS_URI = os.getenv("MILVUS_URI", "https://in03-98d74f0540fd4ed.serverless.aws-eu-central-1.cloud.zilliz.com")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "db_98d74f0540fd4ed:Jb1.}c0}]N9ct^Md")

# Load embedding model once globally
logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()

def chunk_text(text, chunk_size=3000, overlap=200):
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

def extract_text_from_pdf(pdf_path):
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
        logger.error(f"Error reading PDF directly {pdf_path}: {e}")
        return ""

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {e}")
        return ""

def create_and_populate_collection(collection_name, files_list, is_precedence_folder=False):
    logger.info(f"\n=== Initializing Collection: {collection_name} ===")
    
    # Drop existing if it exists
    if utility.has_collection(collection_name):
        logger.info(f"Dropping existing collection '{collection_name}'...")
        Collection(collection_name).drop()
        
    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8000),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)
    ]
    schema = CollectionSchema(fields, description=f"JureLex_AI collection for {collection_name}")
    collection = Collection(name=collection_name, schema=schema)
    logger.info(f"Created collection '{collection_name}'.")
    
    # Collect files
    target_files = []
    if is_precedence_folder:
        folder = files_list[0]
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.lower().endswith(".pdf"):
                    target_files.append(os.path.join(folder, f))
    else:
        for f in files_list:
            if os.path.exists(f):
                target_files.append(f)
            else:
                logger.warning(f"File not found: {f}")
                
    # Process files
    all_filenames = []
    all_texts = []
    all_vectors = []
    
    for file_path in target_files:
        logger.info(f"Processing file: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""
        
        if ext == ".pdf":
            extracted_text = extract_text_from_pdf(file_path)
            # Fallback to OCR if empty
            if not extracted_text:
                logger.info(f"Direct PDF text empty. Trying OCR on {file_path}...")
                try:
                    doc = fitz.open(file_path)
                    ocr_parts = []
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        mode = "RGB" if pix.alpha == 0 else "RGBA"
                        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                        page_text = clean_text(pytesseract.image_to_string(image))
                        if page_text:
                            ocr_parts.append(page_text)
                    doc.close()
                    extracted_text = clean_text("\n".join(ocr_parts))
                except Exception as e:
                    logger.error(f"OCR failed for {file_path}: {e}")
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            extracted_text = extract_text_from_image(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
                
        extracted_text = clean_text(extracted_text)
        if not extracted_text:
            logger.warning(f"No text could be extracted from: {file_path}")
            continue
            
        chunks = chunk_text(extracted_text)
        logger.info(f"Generated {len(chunks)} chunks from {file_path}")
        
        # Batch encode
        if chunks:
            try:
                embeddings = embedding_model.encode(chunks, show_progress_bar=False).tolist()
                for chunk, vector in zip(chunks, embeddings):
                    all_filenames.append(os.path.basename(file_path))
                    all_texts.append(chunk)
                    all_vectors.append(vector)
            except Exception as e:
                logger.error(f"Embedding failed for chunks in {file_path}: {e}")
                
    # Insert in batches of 100 to prevent buffer overflows
    if all_texts:
        batch_size = 100
        total_inserted = 0
        for i in range(0, len(all_texts), batch_size):
            batch_filenames = all_filenames[i:i+batch_size]
            batch_texts = all_texts[i:i+batch_size]
            batch_vectors = all_vectors[i:i+batch_size]
            
            collection.insert([batch_filenames, batch_texts, batch_vectors])
            total_inserted += len(batch_texts)
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch_texts)} chunks...")
            
        collection.flush()
        logger.info(f"Finished inserting {total_inserted} chunks.")
        
        # Create Index
        logger.info("Creating vector search index...")
        index_params = {
            "metric_type": "L2",
            "index_type": "AUTOINDEX",  # Zilliz Serverless handles indexing automatically
            "params": {}
        }
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()
        logger.info(f"Collection {collection_name} is successfully loaded and ready for search!")
    else:
        logger.warning(f"No data inserted for {collection_name}")

def main():
    try:
        logger.info(f"Connecting to Zilliz Cloud at {MILVUS_URI}...")
        connections.connect(alias="default", uri=MILVUS_URI, token=MILVUS_TOKEN)
        logger.info("Successfully connected to Zilliz Cloud database!")
        
        # 1. Populate IPC Collection
        create_and_populate_collection("IPC_collection", ["./IPC.pdf"])
        
        # 2. Populate Drafting/Document Creation Collection
        create_and_populate_collection("Document_Creation_collection", ["./documentforms.pdf", "./legalform1.pdf", "./legalform1.webp"])
        
        # 3. Populate Precedence Collection
        create_and_populate_collection("Precedence_collection", ["./case_files"], is_precedence_folder=True)
        
        logger.info("\n🎉 All database collections have been successfully initialized and populated on Zilliz Cloud!")
        
    except Exception as e:
        logger.error(f"Execution failed: {e}")
    finally:
        connections.disconnect("default")

if __name__ == "__main__":
    main()
