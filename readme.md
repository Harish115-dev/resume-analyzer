# Resume Analyzer

A Flask-based resume analysis tool that combines classic NLP, TF-IDF matching, rule-based scoring, and an LLM feedback layer to give resumes an ATS-style scan: section/contact checks, skill extraction, quantified-achievement detection, job description matching, and natural-language feedback.

Built as a hybrid NLP + LLM pipeline — deterministic checks where correctness matters (skill matching, scoring), an LLM only where natural-language generation is genuinely needed (feedback narrative).

## Features

- **Resume parsing** — extracts text from PDF and DOCX (including Word list-formatted bullets and hyperlink URLs behind display text, e.g. a "LinkedIn" link that shows no visible URL)
- **Section detection** — regex-based classification into Summary, Experience, Education, Skills, Projects, Certifications, and more
- **Skill extraction** — spaCy `PhraseMatcher` against a ~12,000-entry taxonomy built from O*NET's Technology Skills database, merged with a second acronym-rich dataset and a small hand-curated alias list (SQL, JIRA, AWS, etc. — common short forms O*NET only stores as long vendor strings)
- **ATS-style scoring** — rule-based checks across sections present, contact info, quantified achievements (bullets containing numbers/%/$), strong action verbs vs. weak filler phrases, and word count, each independently weighted
- **Job description matching** — TF-IDF cosine similarity for overall text relevance, plus a taxonomy-grounded matched/missing skill breakdown (more precise than raw keyword ranking)
- **AI-generated feedback** — Groq (Llama 3.3 70B) turns the structured scoring data into a natural-language summary and prioritized suggestions, with a rule-based fallback if the API is unavailable
- **Authentication** — session-based register/login/logout (MongoDB + bcrypt), gating the analyze route behind login

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Flask, Flask-WTF (CSRF), Flask-CORS |
| Auth / DB | MongoEngine, MongoDB Atlas, bcrypt |
| Parsing | pdfplumber, python-docx |
| NLP | spaCy (`en_core_web_sm`), scikit-learn (TF-IDF) |
| LLM | Groq API (Llama 3.3 70B) |
| Frontend | Server-rendered Jinja templates, vanilla CSS/JS (dark theme) |

## Project structure

```
resume-analyzer/
├── app.py                      # App factory, config, blueprint registration
├── auth/
│   ├── models.py                # User document (MongoEngine)
│   └── routes.py                # register/login/logout, login_required decorator
├── routes/
│   └── analysis_routes.py       # /  and /analyze routes, pipeline orchestration
├── parsers/
│   ├── extractor.py             # PDF/DOCX -> raw text
│   └── section_splitter.py      # raw text -> {summary, experience, skills, ...}
├── analysis/
│   ├── skill_extractor.py       # PhraseMatcher-based skill extraction
│   ├── matcher.py                # TF-IDF similarity + skill overlap vs. a JD
│   ├── ats_scorer.py             # rule-based scoring
│   ├── llm_feedback.py           # Groq call + rule-based fallback
│   └── data/
│       ├── skills_taxonomy.json  # merged skill list + category map
│       └── action_verbs.py       # categorized strong-verb reference
├── templates/                   # index, result, login, register, nav partial
├── static/
│   ├── css/style.css
│   └── js/main.js
└── requirements.txt
```

## Setup

```bash
git clone <this-repo>
cd resume-analyzer
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create a `.env` file in the project root:

```
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/resume_analyzer_db?appName=Cluster0
SECRET_KEY=<a long random string>
GROQ_API_KEY=<your groq api key>
FLASK_DEBUG=True
```

**Mongo Atlas setup notes:** the connection string's database name goes directly between the last `/` and any `?` query params (e.g. `.../resume_analyzer_db?appName=...`) — an empty or missing database segment silently connects to `test` instead. Credentials come from **Database Access** (a database user), not your Atlas account login. URL-encode any special characters in the password.

Run it:

```bash
flask run
```

First startup takes ~10-15s while the skill-matcher builds ~12,000 `PhraseMatcher` patterns — this happens once per process start, not per request.

## How scoring works

Each resume gets a 0-100 overall score, built from independently-weighted components:

| Component | Weight | What it checks |
|---|---|---|
| Sections | 20 | Summary/Experience/Education/Skills present |
| Contact | 10 | Email, phone, LinkedIn detected |
| Quantified achievements | 20 | Ratio of bullet points containing numbers/%/$ |
| Action verbs | 15 | Strong verbs used vs. weak filler phrases |
| Word count | 10 | Falls in a healthy range (~350-800 words) |
| JD match | 25 | Taxonomy-based skill coverage, only if a job description is provided |

If no job description is given, the JD-match weight is redistributed proportionally across the other components rather than left as a flat loss.

Note: `Experience` and `Projects` sections are combined for the quantified-achievements and action-verb checks, since entry-level/student resumes often lead with Projects instead of a formal Experience section.

## Known limitations

- The skill taxonomy is exact-match (`PhraseMatcher`), not fuzzy — novel or unlisted skills won't be recognized. A trained NER model is a natural v2 upgrade, benchmarked against this rule-based baseline.
- LLM feedback occasionally makes small framing errors even on the larger model (e.g. describing a strong metric with hedging language). Numeric judgments (which categories are "weak") are computed in Python and handed to the LLM pre-filtered specifically to avoid this class of mistake — see `llm_feedback.py`.
- Scanned/image-only PDFs won't extract text (no OCR).
- The `/api/analyze` JSON endpoint exists in the codebase but is currently unauthenticated and not used anywhere — noted as a deliberate future extension point, not a finished feature.

## Possible extensions

- Analysis history stored per user in Mongo
- Free-tier usage limits before requiring login
- API-key-based programmatic access via `/api/analyze`
- Trained NER model for skill extraction, compared against the current taxonomy baseline