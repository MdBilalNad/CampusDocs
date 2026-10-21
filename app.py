import json
import os
import re
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)

# --- LOAD DATA ---
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cse_projects_enhanced.json')
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    RAW_DATA = json.load(f)

ALL_PROJECTS = []
DOMAINS_MAP = {}
ALL_LANGUAGES = set()
ALL_TIMES = set()

for domain_obj in RAW_DATA.get("domains", []):
    domain_name = domain_obj["domain"]
    domain_slug = re.sub(r'[^a-z0-9]+', '-', domain_name.lower()).strip('-')
    DOMAINS_MAP[domain_slug] = {
        "name": domain_name,
        "broad_tech_stack": domain_obj.get("broad_tech_stack", {})
    }
    
    for p in domain_obj.get("projects", []):
        p["domain"] = domain_name
        p["domain_slug"] = domain_slug
        ALL_PROJECTS.append(p)
        
        for lang in p.get("languages", []):
            ALL_LANGUAGES.add(lang)
        if p.get("estimated_time"):
            ALL_TIMES.add(p["estimated_time"])

ALL_LANGUAGES = sorted(list(ALL_LANGUAGES))
ALL_TIMES = sorted(list(ALL_TIMES), key=lambda x: int(x.split('-')[0]))
DOMAIN_LIST = sorted([v["name"] for k, v in DOMAINS_MAP.items()])

# --- FILTERING LOGIC ---
def filter_projects(filters):
    results = ALL_PROJECTS
    
    if filters.get("domain") and filters["domain"] != "Any":
        results = [p for p in results if p["domain"] == filters["domain"]]
        
    if filters.get("difficulty") and filters["difficulty"] != "Any":
        results = [p for p in results if p["difficulty"] == filters["difficulty"]]
        
    if filters.get("language") and filters["language"] != "Any":
        results = [p for p in results if filters["language"] in p.get("languages", [])]
        
    if filters.get("time") and filters["time"] != "Any":
        results = [p for p in results if p.get("estimated_time") == filters["time"]]
        
    if filters.get("python_friendly") == "true":
        results = [p for p in results if p.get("python_friendly") == True]
        
    if filters.get("tech"):
        q = filters["tech"].lower()
        results = [p for p in results if any(q in t.lower() for t in p.get("tech_stack", []))]
        
    return sorted(results, key=lambda x: x["title"])

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html', total=len(ALL_PROJECTS), domains=len(DOMAIN_LIST))

@app.route('/find')
def find():
    return render_template(
        'find.html', 
        domains=DOMAIN_LIST, 
        times=ALL_TIMES
    )

@app.route('/projects')
def projects():
    filters = {
        "domain": request.args.get("domain", "Any"),
        "difficulty": request.args.get("difficulty", "Any"),
        "language": request.args.get("language", "Any"),
        "time": request.args.get("time", "Any"),
        "python_friendly": request.args.get("python_friendly", "false"),
        "tech": request.args.get("tech", ""),
    }
    results = filter_projects(filters)
    return render_template('project.html', projects=results, filters=filters)

@app.route('/api/count')
def api_count():
    filters = {
        "domain": request.args.get("domain", "Any"),
        "difficulty": request.args.get("difficulty", "Any"),
        "language": request.args.get("language", "Any"),
        "time": request.args.get("time", "Any"),
        "python_friendly": request.args.get("python_friendly", "false"),
        "tech": request.args.get("tech", ""),
    }
    return jsonify({"count": len(filter_projects(filters))})

@app.route('/api/project/<domain_slug>/<id>')
def api_project(domain_slug, id):
    project = next((p for p in ALL_PROJECTS if p["domain_slug"] == domain_slug and str(p["id"]) == id), None)
    if not project: abort(404)
    return jsonify({
        "project": project,
        "broad_tech_stack": DOMAINS_MAP.get(domain_slug, {}).get("broad_tech_stack", {})
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()