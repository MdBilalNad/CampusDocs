import json
import re
import pandas as pd
from pathlib import Path

CSV_PATH = "data/fyp_raw/FYP Data.csv"     # <-- adjust if needed
OUT_PATH = "data/projects.json"

# Map raw domain strings to the canonical domains your app.py expects
DOMAIN_MAP = {
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Machine Learning",
    "artificial intelligence": "Machine Learning",
    "ai": "Machine Learning",
    "data science": "Machine Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "image processing": "Computer Vision",
    "web": "Web Development",
    "web development": "Web Development",
    "web app": "Web Development",
    "full stack": "Web Development",
    "android": "Web Development",
    "mobile": "Web Development",
    "blockchain": "Blockchain",
    "web3": "Blockchain",
    "iot": "IoT",
    "internet of things": "IoT",
    "security": "Security",
    "cyber security": "Security",
    "cybersecurity": "Security",
    "cryptography": "Security",
    "systems": "Systems",
    "distributed": "Systems",
    "networking": "Systems",
    "cloud": "Systems",
}

# Skill detection from abstract text — add more as you see gaps
SKILL_KEYWORDS = {
    "Python": ["python"],
    "JavaScript": ["javascript", "js ", "node"],
    "React": ["react"],
    "Node.js": ["node.js", "nodejs", "node"],
    "PyTorch": ["pytorch"],
    "TensorFlow": ["tensorflow", "keras"],
    "OpenCV": ["opencv"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "SQL": ["mysql", "postgres", "sql", "database"],
    "MongoDB": ["mongodb", "mongo"],
    "AWS": ["aws", "amazon web services", "s3", "lambda"],
    "Solidity": ["solidity", "ethereum", "smart contract"],
    "Go": ["golang", " go "],
    "Java": ["java "],
    "C++": ["c++", "cpp"],
    "Android": ["android"],
    "Flutter": ["flutter"],
    "Arduino": ["arduino", "esp32", "esp8266"],
}

def detect_domain(raw: str) -> str:
    raw = (raw or "").lower()
    for k, v in DOMAIN_MAP.items():
        if k in raw:
            return v
    return "Machine Learning"  # safe default — most FYP entries are ML-ish

def detect_skills(text: str, tech: str) -> list[str]:
    blob = (text + " " + tech).lower()
    found = [s for s, kws in SKILL_KEYWORDS.items() if any(k in blob for k in kws)]
    return found or ["Python"]  # never empty

def detect_difficulty(text: str) -> str:
    t = (text or "").lower()
    if any(w in t for w in ["distributed", "blockchain", "real-time", "deep learning",
                            "reinforcement", "federated", "kubernetes", "compiler"]):
        return "hard"
    if any(w in t for w in ["simple", "basic", "crud", "calculator", "portfolio", "todo"]):
        return "easy"
    return "medium"

def guess_weeks(difficulty: str) -> int:
    return {"easy": 6, "medium": 8, "hard": 11}[difficulty]

def clean_title(t: str) -> str:
    t = re.sub(r"\s+", " ", str(t or "")).strip()
    return t[:120] if t else "Untitled Project"

def clean_desc(d: str) -> str:
    d = re.sub(r"\s+", " ", str(d or "")).strip()
    return d[:800] if d else "No description available."

def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded CSV: {df.shape[0]} rows, columns: {list(df.columns)}")

    # Normalize column names to lowercase snake_case for resilience
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    def pick(*names):
        for n in names:
            if n in df.columns:
                return n
        return None

    col_title = pick("title", "project_title", "name")
    col_desc  = pick("abstract", "description", "project_description", "summary")
    col_dom   = pick("domain", "category", "field")
    col_tech  = pick("technologies", "tech_stack", "technology", "tools")
    col_year  = pick("year", "batch", "session")
    col_url   = pick("source_url", "url", "link", "github")

    if not col_title or not col_desc:
        raise SystemExit(f"Could not find title/description columns. Available: {list(df.columns)}")

    projects, seen = [], set()
    for i, row in df.iterrows():
        title = clean_title(row[col_title])
        desc = clean_desc(row[col_desc])

        key = title.lower()
        if key in seen:
            continue
        seen.add(key)

        domain = detect_domain(str(row[col_dom]) if col_dom else "")
        skills = detect_skills(desc, str(row[col_tech]) if col_tech else "")
        difficulty = detect_difficulty(desc + " " + title)

        try:
            year = int(row[col_year]) if col_year and pd.notna(row[col_year]) else 0
        except (ValueError, TypeError):
            year = 0

        projects.append({
            "id": f"p{len(projects) + 1:04d}",
            "title": title,
            "description": desc,
            "domain": domain,
            "skills": skills,
            "tech_stack": skills[:4],     # reuse skills as a rough stack
            "difficulty": difficulty,
            "estimated_weeks": guess_weeks(difficulty),
            "team_size": 2,
            "tags": [domain.lower().replace(" ", "-")],
            "source_url": str(row[col_url]) if col_url and pd.notna(row[col_url]) else "",
            "year": year,
        })

    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(projects)} projects → {OUT_PATH}")
    print("\nDomain distribution:")
    from collections import Counter
    for d, c in Counter(p["domain"] for p in projects).most_common():
        print(f"  {d:20} {c}")

if __name__ == "__main__":
    main()