import os, glob
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer
from config import *

def extract_pages(pdf_path):
    reader = PdfReader(pdf_path)
    return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + size]
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap
    return chunks

def ingest():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"Found {len(pdfs)} PDFs")

    added = 0
    for pdf in pdfs:
        name = os.path.basename(pdf)
        print(f"→ {name}")
        for page_num, text in extract_pages(pdf):
            if not text.strip():
                continue
            for i, chunk in enumerate(chunk_text(text)):
                cid = f"{name}_p{page_num}_c{i}"
                collection.upsert(
                    ids=[cid],
                    embeddings=[model.encode(chunk).tolist()],
                    documents=[chunk],
                    metadatas=[{"source": name, "page": page_num, "chunk_index": i}],
                )
                added += 1

    print(f"\nDone. Upserted {added} chunks.")
    print(f"Collection size: {collection.count()}")

if __name__ == "__main__":
    ingest()