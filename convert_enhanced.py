import json
import random

INPUT_FILE = "data/cse_projects_enhanced.json"
OUTPUT_FILE = "data/projects.json"

DIFFICULTY_MAP = {
    "Beginner": "easy",
    "Intermediate": "medium",
    "Advanced": "hard"
}

WEEKS_MAP = {
    "1-2 weeks": 2,
    "3-5 weeks": 4,
    "6-10 weeks": 8
}

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_projects = []
    
    for domain_data in data.get("domains", []):
        domain_name = domain_data["domain"]
        
        for p in domain_data.get("projects", []):
            difficulty = DIFFICULTY_MAP.get(p.get("difficulty"), "medium")
            weeks = WEEKS_MAP.get(p.get("estimated_time"), 6)
            
            tech_stack = p.get("tech_stack", [])
            skills = tech_stack.copy()
            if not skills:
                skills = ["Python"]
                
            project = {
                "id": f"p{len(flat_projects) + 1:04d}",
                "title": p["title"],
                "description": p["description"],
                "domain": domain_name,
                "skills": skills,
                "tech_stack": tech_stack,
                "difficulty": difficulty,
                "estimated_weeks": weeks,
                "team_size": random.randint(1, 3),
                "tags": [domain_name.lower().replace(" ", "-"), difficulty],
                "source_url": "",
                "year": 2026
            }
            flat_projects.append(project)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(flat_projects, f, indent=2, ensure_ascii=False)

    print(f"Successfully converted {len(flat_projects)} projects!")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()