import os
import fitz
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from pymilvus import (
    connections, Collection, CollectionSchema,
    FieldSchema, DataType, utility
)

INPUT_FILES = ["documentforms.pdf", "legalform1.pdf", "legalform1.webp"]
COLLECTION_NAME = "Document_Creation_collection"
EMBEDDING_DIM = 384

# Configure Milvus parameters from environment
MILVUS_URI = os.getenv("MILVUS_URI", "")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

if MILVUS_URI:
    print(f"Connecting to Zilliz Cloud at {MILVUS_URI}...")
    connections.connect(alias="default", uri=MILVUS_URI, token=MILVUS_TOKEN)
else:
    print(f"Connecting to local Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

if utility.has_collection(COLLECTION_NAME):
    print(f"Dropping existing collection: {COLLECTION_NAME}")
    Collection(COLLECTION_NAME).drop()

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8000),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
]

schema = CollectionSchema(fields=fields, description="Legal document generation embeddings")
collection = Collection(name=COLLECTION_NAME, schema=schema)

model = SentenceTransformer("all-MiniLM-L6-v2")


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
        print(f"Direct PDF extraction worked for {pdf_path}")
        return text

    print(f"Direct PDF extraction failed for {pdf_path}, trying OCR...")
    return extract_text_from_pdf_ocr(pdf_path)


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return clean_text(text)
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
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


all_filenames = []
all_texts = []
all_vectors = []

for file_path in INPUT_FILES:
    if not os.path.exists(file_path):
        print(f"Skipping missing file: {file_path}")
        continue

    print(f"\nProcessing file: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    if ext == ".pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        extracted_text = extract_text_from_image(file_path)
    else:
        print(f"Unsupported file type: {file_path}")
        continue

    if not extracted_text:
        print(f"No text extracted from {file_path}")
        continue

    print(f"Extracted text length from {file_path}: {len(extracted_text)}")
    chunks = chunk_text(extracted_text)
    print(f"Generated {len(chunks)} chunks from {file_path}")

    for chunk in chunks:
        try:
            vector = model.encode([chunk])[0].tolist()
            all_filenames.append(os.path.basename(file_path))
            all_texts.append(chunk)
            all_vectors.append(vector)
        except Exception as e:
            print(f"Embedding failed for chunk in {file_path}: {e}")

if all_texts:
    collection.insert([all_filenames, all_texts, all_vectors])
    collection.flush()

    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }

    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    print(f"\nInserted {len(all_texts)} chunks into {COLLECTION_NAME}")
else:
    print("No document chunks inserted.")