import re
#Strong Action Verbs
ACTION_VERBS = {
    "leadership": [
        "led", "managed", "directed", "supervised", "oversaw", "headed",
        "guided", "mentored", "coached", "facilitated", "coordinated",
        "chaired", "administered", "delegated", "motivated", "influenced",
        "mobilized", "championed",
    ],
    "creation_development": [
        "developed", "created", "built", "designed", "engineered",
        "constructed", "produced", "crafted", "invented", "established",
        "formulated", "devised", "originated", "initiated", "launched",
        "founded", "assembled", "programmed", "coded", "implemented",
        "architected", "authored",
    ],
    "improvement": [
        "improved", "enhanced", "optimized", "streamlined", "refined",
        "upgraded", "modernized", "strengthened", "simplified",
        "accelerated", "boosted", "elevated", "maximized", "revamped",
        "transformed", "restructured", "expanded", "scaled", "standardized",
    ],
    "analysis": [
        "analyzed", "evaluated", "assessed", "examined", "investigated",
        "researched", "audited", "measured", "validated", "diagnosed",
        "identified", "interpreted", "modeled", "forecasted", "benchmarked",
    ],
    "technical_devops": [
        "automated", "deployed", "migrated", "integrated", "debugged",
        "maintained", "refactored", "containerized", "dockerized",
        "orchestrated", "provisioned", "scripted", "configured",
        "secured", "encrypted", "tuned", "virtualized",
    ],
    "data_ml": [
        "trained", "fine-tuned", "classified", "clustered", "predicted",
        "visualized", "preprocessed", "vectorized", "tokenized",
        "embedded", "engineered", "inferred", "retrieved",
    ],
    "project_management": [
        "planned", "executed", "scheduled", "delivered", "prioritized",
        "tracked", "allocated", "budgeted", "aligned",
    ],
    "communication": [
        "presented", "communicated", "negotiated", "collaborated",
        "consulted", "advised", "persuaded", "documented", "reported",
        "trained", "educated", "represented", "promoted", "advocated",
    ],
    "business_impact": [
        "generated", "increased", "reduced", "saved", "cut", "grew",
        "captured", "acquired", "retained", "converted", "closed",
        "marketed", "sold", "minimized",
    ],
    "problem_solving": [
        "resolved", "solved", "eliminated", "corrected", "addressed",
        "prevented", "fixed", "mitigated", "recovered", "restored",
        "troubleshot", "overcame", "remedied",
    ],
}

ALL_ACTION_VERBS = sorted(set(v for verbs in ACTION_VERBS.values() for v in verbs))

# Weak Resume Phrases 

WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "assisted in",
    "involved in",
    "duties included",
    "tasked with",
    "participated in",
    "was part of",
    "worked under",
    "worked alongside",
    "worked closely with",
    "supported",
    "provided support",
    "helped develop",
    "helped create",
    "helped build",
    "helped implement",
    "assisted with",
    "took part in",
    "contributed to",
    "exposed to",
    "gained experience in",
    "had knowledge of",
    "familiar with",
    "knowledge of",
    "basic understanding of",
    "basic knowledge of",
    "some experience with",
    "experience in",
    "experience with",
    "worked using",
    "used",
    "utilized",
    "was involved in",
    "participated",
    "handled",
    "performed",
    "did",
    "made",
    "worked as",
    "worked for",
    "worked under supervision",
    "assigned to",
    "asked to",
    "required to",
    "was responsible for",
    "was tasked with",
    "was assigned",
    "worked independently",
    "worked remotely",
    "worked with team",
    "worked in team",
    "team player",
    "hardworking",
    "fast learner",
    "quick learner",
    "go-getter",
    "self-motivated",
    "detail oriented",
    "results driven",
    "passionate about",
    "enthusiastic about",
    "interested in",
    "looking for opportunity",
    "seeking opportunity",
    "excellent communication skills",
    "good communication skills",
    "good leadership skills",
    "strong work ethic",
    "can work under pressure",
    "ability to work independently",
    "ability to multitask",
    "good interpersonal skills",
    "problem solver",
    "creative thinker",
    "dynamic individual",
    "highly motivated",
    "dedicated professional",
    "goal oriented",
    "responsible person",
    "hard worker",
    "effective communicator",
    "excellent team player",
    "works well under pressure",
    "willing to learn",
    "eager to learn",
    "proven track record",
    "go above and beyond",
    "think outside the box",
    "excellent organizational skills",
    "works well with others",
    "strong analytical skills",
    "excellent problem-solving skills",
    "excellent time management",
    "good at",
    "capable of",
    "can perform",
    "performed various tasks",
    "multiple responsibilities",
    "various duties",
    "other duties as assigned",
    "miscellaneous duties",
    "general responsibilities",
    "day-to-day responsibilities",
    "daily responsibilities",
    "routine tasks"
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[A-Za-z0-9\-_/]+", re.IGNORECASE)
NUMBER_RE = re.compile(r"(\$?\d[\d,]*\.?\d*\s?%?|\d+x\b)")
BULLET_RE = re.compile(r"^\s*[\-\u2022\*\u2023\u25E6\u2043]")

WEIGHTS = {
    "sections": 20,
    "contact": 10,
    "quantified": 20,
    "action_verbs": 15,
    "word_count": 10,
    "jd_match": 25,
}

def check_sections(sections:dict)->dict:
    present = {name: bool(text.strip()) for name, text in sections.items()}
    core = ["summary", "experience", "education", "skills"]
    core_present = sum(1 for c in core if present.get(c))
    score = (core_present / len(core)) * WEIGHTS["sections"]
    return {"score": round(score, 1), "present": present, "core_present": core_present}


def check_contact_info(resume_text:str)->str :
    email = bool(EMAIL_RE.search(resume_text))
    phone = bool(PHONE_RE.search(resume_text))
    linkedin = bool(LINKEDIN_RE.search(resume_text))
    found = sum([email, phone, linkedin])
    score = (found / 3) * WEIGHTS["contact"]
    return {"score": round(score, 1), "email": email, "phone": phone, "linkedin": linkedin}


def check_quantified_achievements(experience_text: str) -> dict:
    lines=[l.strip() for l in experience_text.split("\n") if l.strip()]
    bullets=[l for l in lines if BULLET_RE.match(l)]
    quantified = [l for l in bullets if NUMBER_RE.search(l)]
    total = len(bullets) or 1
    ratio = len(quantified) / total
    score = ratio * WEIGHTS["quantified"]
    return {
        "score": round(score, 1),
        "total_bullets": len(bullets),
        "quantified_bullets": len(quantified),
        "ratio": round(ratio, 2),
    }

def check_action_verbs(experience_text: str) -> dict:
    lower = experience_text.lower()
    strong_used = sorted(set(v for v in ALL_ACTION_VERBS if re.search(rf"\b{v}\b", lower)))
    weak_used = sorted(set(p for p in WEAK_PHRASES if p in lower))

    strong_score = min(len(strong_used), 10) / 10 
    weak_penalty = min(len(weak_used), 5) / 5 

    score = max(0.0, (strong_score - 0.3 * weak_penalty)) * WEIGHTS["action_verbs"]
    return {
        "score": round(score, 1),
        "strong_verbs_used": strong_used,
        "weak_phrases_found": weak_used,
    }

def check_word_count(resume_text:str)->dict:
    word_count = len(re.findall(r"\b\w+\b", resume_text))

    if 350 <= word_count <= 800:
        pct = 1.0
    elif 200 <= word_count < 350 or 800 < word_count <= 1000:
        pct = 0.6
    elif word_count < 200:
        pct = 0.2
    else:
        pct = 0.3

    score = pct * WEIGHTS["word_count"]
    return {"score": round(score, 1), "word_count": word_count}

def check_jd_match(jd_match_result: dict | None) -> dict:
    if not jd_match_result:
        return {"score": None, "coverage_pct": None}
    
    coverage = jd_match_result.get("coverage_pct", 0.0)
    score = (coverage / 100) * WEIGHTS["jd_match"]
    return {"score": round(score, 1), "coverage_pct": coverage}
    

def score_resume(resume_text: str, sections: dict, jd_match_result: dict | None = None) -> dict:
    experience_text = "\n".join(
        sections.get(key, "") for key in ("experience", "projects") if sections.get(key)
    )

    sections_result = check_sections(sections)
    contact_result = check_contact_info(resume_text)
    quantified_result = check_quantified_achievements(experience_text)
    verbs_result = check_action_verbs(experience_text)
    wordcount_result = check_word_count(resume_text)
    jd_result = check_jd_match(jd_match_result)

    component_scores = [
        sections_result["score"],
        contact_result["score"],
        quantified_result["score"],
        verbs_result["score"],
        wordcount_result["score"],
    ]
    if jd_match_result:
        component_scores.append(jd_result["score"])
        overall = sum(component_scores)
    else:

        non_jd_weight_sum = sum(w for k, w in WEIGHTS.items() if k != "jd_match")
        scale_factor = 100 / non_jd_weight_sum
        overall = sum(component_scores) * scale_factor

    return {
        "overall_score": round(min(100, max(0, overall)), 1),
        "breakdown": {
            "sections": sections_result["score"],
            "contact": contact_result["score"],
            "quantified": quantified_result["score"],
            "action_verbs": verbs_result["score"],
            "word_count": wordcount_result["score"],
            "jd_match": jd_result["score"],
        },
        "details": {
            "sections": sections_result,
            "contact": contact_result,
            "quantified": quantified_result,
            "action_verbs": verbs_result,
            "word_count": wordcount_result,
            "jd_match": jd_result,
        },
    }