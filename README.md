 Project Finder
<p align="center"> <b>A meticulously designed, full-stack web application for Computer Science students to discover and filter final-year project ideas.</b> </p><p align="center"> <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"> <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"> <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"> </p><p align="center"> <i>Built with a focus on speed, aesthetics, and user experience. No React, no Tailwind, no npm. Just pure, performant web technologies.</i> </p>
✦ The Vibe
We intentionally kept the stack lightweight and framework-free to ensure maximum performance and maintainability. The visual direction is heavily inspired by premium developer tools like Linear, Vercel, and Raycast.

It features a "vibe-coded" dark UI, a high-performance Python backend, and live, zero-latency filtering.

🚀 Key Features
⚡ Live Server-Side Filtering: Instantly filters 1,200 projects based on Domain, Difficulty, Estimated Time, Tech Stack, and Python-compatibility.

🔢 Live Match Counter: Dynamically queries the backend via fetch() to update the UI count without reloading the page.

🪟 Frictionless Detail View: Clicking a project opens a sleek, sliding side panel containing the full project description and the domain's broad technical context, powered by a lightweight JSON API.

🎨 Custom UI Components: Zero reliance on native browser dropdowns or checkboxes. All filters use custom-styled, animated chip components for a cohesive aesthetic.

✨ Micro-interactions: Staggered page-load animations, hover-lift physics on project cards, and smooth opacity transitions create a premium, tactile feel.

🛠️ Tech Stack
Layer	Technology
Backend	Python 3, Flask, Jinja2
Frontend	Vanilla HTML5, Vanilla CSS3, Vanilla ES6+
Data Layer	Local JSON (Loaded into memory at startup)
Typography	Instrument Serif, Inter, JetBrains Mono
📂 Project Structure
text
CampusDocs/
├── app.py                          # Flask server, routing, and filtering logic
├── data/
│   └── cse_projects_enhanced.json  # The source dataset (12 domains, 1200 projects)
├── static/
│   ├── style.css                   # Global design system and tokens
│   └── app.js                      # Client-side logic (Live count, Side panel API)
└── templates/
    ├── base.html                   # Shared layout, fonts, and script imports
    ├── index.html                  # Landing page
    ├── find.html                   # Filter configuration page
    ├── project.html                # Results page
    └── 404.html                    # Custom error page
⚙️ Getting Started
Prerequisites
You only need Python 3 installed on your system. No Node.js or npm is required.

Installation
Clone the repository and navigate into the project directory:

bash
git clone https://github.com/yourusername/project-finder.git
cd project-finder
Install Flask:

bash
pip install flask
Run the application:

bash
python app.py
(Alternatively, you can use flask run --debug)

Open in your browser:
Navigate to http://127.0.0.1:5000

🎨 Design System
Color Palette:

Base: #050505 (Deep Ink)

Surface: rgba(255, 255, 255, 0.03) (Glassmorphism)

Accent: #6366f1 (Signal Indigo)

Glow & Depth: The interface uses CSS radial gradients in the background to simulate ambient depth, while active states (like selected filters) emit a soft box-shadow glow.

Typography Rules:

Instrument Serif is used exclusively for large headlines and project titles to give it an editorial feel.

Inter handles all paragraph text for maximum readability.

JetBrains Mono is reserved for metadata, tags, and structural labels (e.g., // STEP 01).

🧠 Engineering Decisions
Why filter server-side? Filtering 1,200 items client-side is possible, but maintaining the logic in Python ensures that the URL query parameters (?domain=Web+Development&difficulty=Advanced) act as the absolute source of truth. This makes every search state shareable and bookmarkable.

Why no React? The application state is simple enough that DOM manipulation via vanilla JS is faster to load and easier to maintain than setting up a Webpack/Vite pipeline.

Data Loading: The 1,200-item JSON file is loaded into Python memory once at startup. Filtering happens instantly in-memory via list comprehensions, completely bypassing the need for a complex SQL database for a dataset of this size.

<p align="center"> <i>Built for CSE students, by CSE students.</i> </p>
