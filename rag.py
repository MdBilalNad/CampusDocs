import json
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from config import *

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_coll = _client.get_or_create_collection(COLLECTION_NAME)
_model = SentenceTransformer(EMBED_MODEL)
_groq = Groq(api_key=GROQ_API_KEY)

# Domains that should be treated as equivalent when filtering
DOMAIN_ALIASES = {
    "Machine Learning": ["Machine Learning", "ML", "Deep Learning", "AI"],
    "NLP": ["NLP", "Natural Language Processing"],
    "Computer Vision": ["Computer Vision", "CV", "Image Processing"],
    "Web Development": ["Web Development", "Web", "Full Stack"],
    "Blockchain": ["Blockchain", "Web3"],
    "IoT": ["IoT", "Internet of Things"],
    "Security": ["Security", "Cyber Security", "Cybersecurity"],
    "Systems": ["Systems", "Distributed", "Networking"],
}


def build_query(profile):
    parts = []
    if profile.get("interests"):
        parts.append(profile["interests"])
    if profile.get("domain") and profile["domain"] != "Any":
        parts.append(f"domain: {profile['domain']}")
    if profile.get("skills"):
        parts.append(f"skills: {', '.join(profile['skills'])}")
    if profile.get("difficulty") and profile["difficulty"] != "Any":
        parts.append(f"difficulty: {profile['difficulty']}")
    return ". ".join(parts) or "B.Tech CSE project"


def _build_where(profile, strict_skill=False):
    filters = []

    if profile.get("difficulty") and profile["difficulty"] != "Any":
        filters.append({"difficulty": {"$eq": profile["difficulty"]}})

    if profile.get("domain") and profile["domain"] != "Any":
        aliases = DOMAIN_ALIASES.get(profile["domain"], [profile["domain"]])
        filters.append({"domain": {"$in": aliases}})

    if profile.get("max_weeks"):
        filters.append({"estimated_weeks": {"$lte": profile["max_weeks"]}})

    # Skill filter: Chroma doesn't support tokenized match, so we use "$in"
    # against comma-joined strings won't work. Instead, filter skill on the
    # client side after retrieval (see retrieve_candidates). Strict mode
    # passes a flag so we drop non-matching hits.
    if len(filters) == 0:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def _skill_overlap(project_skills, user_skills):
    if not user_skills:
        return 0.0
    ps = {s.strip().lower() for s in project_skills if s}
    us = {s.strip().lower() for s in user_skills if s}
    if not ps or not us:
        return 0.0
    return len(ps & us) / len(us)


def retrieve_candidates(profile, k=CANDIDATES, strict_skill=False):
    where = _build_where(profile)
    q = build_query(profile)

    res = _coll.query(
        query_embeddings=[_model.encode(q).tolist()],
        n_results=k,
        where=where,
    )

    hits = []
    for i in range(len(res["ids"][0])):
        m = res["metadatas"][0][i]
        skills = m["skills"].split(",") if m["skills"] else []
        overlap = _skill_overlap(skills, profile.get("skills", []))
        if strict_skill and profile.get("skills") and overlap == 0.0:
            continue
        hits.append({
            "id": res["ids"][0][i],
            "description": res["documents"][0][i],
            "title": m["title"],
            "domain": m["domain"],
            "difficulty": m["difficulty"],
            "skills": skills,
            "tech_stack": m["tech_stack"].split(",") if m["tech_stack"] else [],
            "estimated_weeks": m["estimated_weeks"],
            "team_size": m["team_size"],
            "source_url": m["source_url"],
            "distance": res["distances"][0][i],
            "skill_overlap": overlap,
        })

    # Boost by skill overlap: lower effective distance = better
    for h in hits:
        h["effective_score"] = h["distance"] - 0.15 * h["skill_overlap"]

    hits.sort(key=lambda x: x["effective_score"])
    return hits


RERANK_PROMPT = """You are a project advisor for B.Tech CSE students.
Given a student profile and {n} candidate projects, rank the top {top_k} best matches.

Student profile:
- Interests: {interests}
- Skills: {skills}
- Difficulty: {difficulty}
- Domain: {domain}
- Team size: {team_size}
- Weeks available: {weeks}

Candidates:
{candidates}

Return ONLY valid JSON in this exact shape:
{{"results":[{{"id":"p001","rank":1,"score":85,"reason":"2 sentences explaining why this fits the student."}}]}}
Rules: {top_k} results, ranks 1-{top_k}, scores 0-100, no markdown, no extra text.
Make sure the top picks are diverse (avoid 5 projects from the same sub-area)."""


def rerank(profile, candidates, top_k=TOP_K):
    if not candidates:
        return []

    cand_text = "\n".join(
        f"{c['id']} | {c['title']} | {c['domain']} | {c['difficulty']} | "
        f"skills: {', '.join(c['skills'])} | {c['estimated_weeks']}w | "
        f"{c['description'][:200]}"
        for c in candidates
    )

    prompt = RERANK_PROMPT.format(
        n=len(candidates),
        top_k=top_k,
        interests=profile.get("interests", ""),
        skills=", ".join(profile.get("skills", [])),
        difficulty=profile.get("difficulty", "Any"),
        domain=profile.get("domain", "Any"),
        team_size=profile.get("team_size", "Any"),
        weeks=profile.get("weeks", "Any"),
        candidates=cand_text,
    )

    r = _groq.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    raw = r.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        data = {"results": []}
        if start != -1 and end != -1:
            try:
                data = json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass

    by_id = {c["id"]: c for c in candidates}
    ranked = []
    for item in data.get("results", []):
        pid = item.get("id")
        if pid in by_id:
            c = by_id[pid].copy()
            c["score"] = item.get("score", 0)
            c["reason"] = item.get("reason", "")
            c["rank"] = item.get("rank", 99)
            ranked.append(c)

    ranked.sort(key=lambda x: x["rank"])
    return ranked[:top_k]


def recommend(profile, strict_skill=False, top_k=TOP_K):
    # Retrieve a larger pool so diversity + skill boosting have room
    candidates = retrieve_candidates(profile, k=CANDIDATES, strict_skill=strict_skill)
    if not candidates:
        return []
    return rerank(profile, candidates, top_k=top_k)