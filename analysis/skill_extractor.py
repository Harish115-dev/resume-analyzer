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
        "Experienced in Python, SQL and Microsoft Excel. "
        "Built dashboards using Tableau and managed projects in JIRA. "
        "Familiar with Salesforce and QuickBooks."
    )
    t0 = time.time()
    flat = extract_skills(sample)
    print(f"\nExtraction took {time.time() - t0:.4f}s")

    print("\nFlat set:")
    print(flat)
    print("\nWith categories:")
    print(extract_skills(sample, with_categories=True))