import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from config import *

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_or_create_collection(COLLECTION_NAME)
_model = SentenceTransformer(EMBED_MODEL)
_groq = Groq(api_key=GROQ_API_KEY)

PROMPT = """You are a study assistant. Answer using ONLY the context below.
If the answer isn't in the context, say: "I couldn't find this in the provided materials."
Cite sources inline like (filename, p. X).

Context:
{context}

Question: {question}

Answer:"""

def retrieve(query, top_k=TOP_K):
    res = _collection.query(
        query_embeddings=[_model.encode(query).tolist()],
        n_results=top_k,
    )
    return [
        {
            "text": res["documents"][0][i],
            "source": res["metadatas"][0][i]["source"],
            "page": res["metadatas"][0][i]["page"],
            "distance": res["distances"][0][i],
        }
        for i in range(len(res["ids"][0]))
    ]

def generate(question, chunks):
    context = "\n\n".join(
        f"[{c['source']}, p. {c['page']}]\n{c['text']}" for c in chunks
    )
    resp = _groq.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

def answer(question):
    chunks = retrieve(question)
    if not chunks:
        return "No documents indexed yet.", []
    return generate(question, chunks), chunks