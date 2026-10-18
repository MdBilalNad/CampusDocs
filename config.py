import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "openai/gpt-oss-20b"    # fast + free
EMBED_MODEL = "all-MiniLM-L6-v2"          # small, CPU-friendly
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "campus_docs"
PDF_DIR = "data/pdfs"
CHUNK_SIZE = 1200      # characters (~300 tokens)
CHUNK_OVERLAP = 200
TOP_K = 5