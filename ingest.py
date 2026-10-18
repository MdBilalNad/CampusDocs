import json
import chromadb
from sentence_transformers import SentenceTransformer
from config import *

def embed_text(p):
    return (
        f"{p['title']}. {p['description']} "
        f"Skills: {', '.join(p['skills'])}. "
        f"Domain: {p['domain']}. "
        f"Tags: {', '.join(p['tags'])}."
    )

def ingest():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    coll = client.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    projects = json.load(open(PROJECTS_FILE, encoding="utf-8"))
    print(f"Loaded {len(projects)} projects")

    for p in projects:
        coll.upsert(
            ids=[p["id"]],
            embeddings=[model.encode(embed_text(p)).tolist()],
            documents=[p["description"]],
            metadatas=[{
                "title": p["title"],
                "domain": p["domain"],
                "difficulty": p["difficulty"],
                "skills": ",".join(p["skills"]),
                "tech_stack": ",".join(p["tech_stack"]),
                "estimated_weeks": p["estimated_weeks"],
                "team_size": p["team_size"],
                "source_url": p.get("source_url", ""),
                "year": p.get("year", 0),
            }],
        )
        print(f"  ✓ {p['id']}  {p['title']}")

    print(f"\nCollection size: {coll.count()}")

if __name__ == "__main__":
    ingest()