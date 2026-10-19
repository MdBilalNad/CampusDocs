import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "openai/gpt-oss-20b"  # Groq's current free tier model
EMBED_MODEL = "all-MiniLM-L6-v2"

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "projects"
PROJECTS_FILE = "data/projects.json"

TOP_K = 5
CANDIDATES = 20