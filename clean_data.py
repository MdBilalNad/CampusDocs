import json
import time
import os
from groq import Groq
from config import GROQ_API_KEY, PROJECTS_FILE, LLM_MODEL

client = Groq(api_key=GROQ_API_KEY)
TEMP_FILE = "data/projects_temp.json"

def clean_batch(batch):
    prompt = """You are fixing a dataset of B.Tech final year projects.
The titles and descriptions are messy, short, or unprofessional.
Rewrite them to be professional, descriptive, and clear.
For each project, provide:
1. A clean, capitalized "title" (e.g. "SimpleAIChat" -> "AI Chatbot using Large Language Models").
2. A 2-3 sentence "description" explaining what the project does, the tech stack used, and the outcome.

Input Data:
""" + json.dumps(batch, indent=2)

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON. Return a JSON object with a single key 'projects' containing an array of objects. Each object must have keys: 'id', 'title', 'description'."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4000, 
        response_format={"type": "json_object"}
    )
    
    raw = resp.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "projects" in data:
            return data["projects"]
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  JSON Parse Error: {e}")
        return []

def main():
    # 1. Load from temp file if it exists (RESUME)
    if os.path.exists(TEMP_FILE):
        print(f"Resuming from {TEMP_FILE}...")
        with open(TEMP_FILE, "r", encoding="utf-8") as f:
            projects = json.load(f)
    else:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            projects = json.load(f)
    
    print(f"Loaded {len(projects)} projects. Cleaning in batches of 10...")
    
    batch_size = 10
    updated = 0
    
    # 2. Find only the projects that don't have the "cleaned" flag
    # We process the list in chunks
    for i in range(0, len(projects), batch_size):
        batch = projects[i:i+batch_size]
        
        # Filter out projects that are already marked as cleaned
        needs_cleaning = [p for p in batch if not p.get("cleaned")]
        
        if not needs_cleaning:
            continue
            
        print(f"Processing {i} to {i+len(batch)} (Skipping {len(batch) - len(needs_cleaning)} already clean)...")
        
        try:
            results = clean_batch(needs_cleaning)
            for item in results:
                if "id" in item and "title" in item:
                    for p in projects:
                        if p["id"] == item["id"]:
                            p["title"] = item["title"]
                            p["description"] = item["description"]
                            p["cleaned"] = True  # Mark as done!
                            updated += 1
                            break
        except Exception as e:
            print(f"  Batch failed: {e}")
            # If rate limited, save progress and wait
            if "429" in str(e) or "404" in str(e):
                print("Rate limit or model error hit. Saving progress and waiting 60 seconds...")
                with open(TEMP_FILE, "w", encoding="utf-8") as f:
                    json.dump(projects, f, indent=2, ensure_ascii=False)
                time.sleep(60)
        
        # 3. Save progress to TEMP_FILE after every batch
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        
        time.sleep(1.5) 
        
    # Final save to the main file
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
        
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
        
    print(f"\nDone. Updated {updated} projects.")
    print("Next step: python ingest.py")

if __name__ == "__main__":
    main()