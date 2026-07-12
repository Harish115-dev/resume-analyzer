import json
import os
import time

import spacy
from spacy.matcher import PhraseMatcher


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TAXONOMY_PATH = os.path.join(_THIS_DIR, "data", "skills_taxonomy.json")

with open(_TAXONOMY_PATH, "r", encoding="utf-8") as f:
    _taxonomy = json.load(f)

SKILLS = _taxonomy["skills"]                
SKILL_CATEGORIES = _taxonomy["categories"]  

nlp = spacy.load("en_core_web_sm")


def _build_matcher():
    start = time.time()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = list(nlp.pipe(SKILLS))
    matcher.add("SKILLS", patterns)
    print(f"[skill_extractor] matcher built in {time.time() - start:.2f}s "
          f"({len(SKILLS)} patterns)")
    return matcher


matcher = _build_matcher()


def extract_skills(text, with_categories=False):
    if not text or not text.strip():
        return {} if with_categories else set()

    doc = nlp(text)
    matches = matcher(doc)

    found_skills = set()
    for match_id, start, end in matches:
        span_text = doc[start:end].text.lower().strip()
        found_skills.add(span_text)

    if not with_categories:
        return found_skills

    return {
        skill: SKILL_CATEGORIES.get(skill, "Uncategorized")
        for skill in found_skills
    }


if __name__ == "__main__":
    sample = (
        """
JOHN MEHTA
john.mehta@email.com | (555) 234-8890 | linkedin.com/in/johnmehta

SUMMARY
Full-stack software engineer with 6 years of experience building scalable web applications
and leading cross-functional teams. Strong background in cloud infrastructure, CI/CD, and
data-driven decision making.

SKILLS
Python, JavaScript, TypeScript, SQL, NoSQL, Java, C++
React, Angular, Node.js, Django, Flask, Express.js
AWS, GCP, Azure, Docker, Kubernetes, Terraform
MySQL, PostgreSQL, MongoDB, Redis
Git, Jenkins, CircleCI, Ansible
Agile, Scrum, Kanban
Tableau, Power BI, Excel, Pandas, NumPy
Machine Learning, TensorFlow, PyTorch, NLP
JIRA, Confluence, ServiceNow
Salesforce, QuickBooks, SAP
HTML, CSS, Sass, GraphQL, REST API, OAuth, JWT
Leadership, Communication, Stakeholder Management, Project Management

EXPERIENCE

Senior Software Engineer, Cloudwave Technologies (2021 - Present)
- Led a team of 5 engineers building a microservices platform on AWS using Docker and Kubernetes
- Migrated legacy SQL Server database to PostgreSQL, reducing query latency by 35%
- Built CI/CD pipelines with Jenkins and Terraform, cutting deployment time by 50%
- Implemented OAuth 2.0 and JWT-based authentication across all internal APIs
- Used JIRA for sprint planning and managed stakeholder communication across 3 departments

Software Engineer, DataForge Inc. (2018 - 2021)
- Developed REST APIs using Flask and Django, integrated with MongoDB and Redis
- Built machine learning models with TensorFlow and scikit-learn for customer churn prediction
- Created dashboards in Tableau and Power BI for executive reporting
- Automated infrastructure provisioning with Ansible, reducing manual setup by 80%
- Collaborated with Salesforce admin team to integrate CRM data into internal analytics tools

Junior Developer, WebSprint Solutions (2016 - 2018)
- Built responsive front-end interfaces using React and Angular
- Wrote unit tests using pytest and JUnit, improving code coverage from 40% to 85%
- Worked with GraphQL and Node.js for backend API development
- Used Git and Confluence for version control and documentation

EDUCATION
B.S. Computer Science, State University (2016)

CERTIFICATIONS
AWS Certified Solutions Architect
Certified ScrumMaster (CSM)

PROJECTS
Built a real-time analytics dashboard using Kafka, Elasticsearch, and GraphQL, deployed on GCP
with Kubernetes for orchestration and Prometheus for monitoring.
"""
    )
    t0 = time.time()
    flat = extract_skills(sample)
    print(f"\nExtraction took {time.time() - t0:.4f}s")

    print("\nFlat set:")
    print(flat)
    print("\nWith categories:")
    print(extract_skills(sample, with_categories=True))
    