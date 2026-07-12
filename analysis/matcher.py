from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analysis.skill_extractor import extract_skills


def compute_match_score(resume_text,jd_text):
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    vectorize=TfidfVectorizer()
    vector=vectorize.fit_transform([resume_text,jd_text])
    similarity = cosine_similarity(vector[0:1], vector[1:2])[0][0]

    return round(float(similarity)*100,1)

def check_skills_overlap(resume_text,jd_text):
    resume_skills=extract_skills(resume_text)
    jd_skills=extract_skills(jd_text)
    print("RESUME SKILLS:", resume_skills)
    print("JD SKILLS:", jd_skills)


    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "jd_skill_count": len(jd_skills),
        "coverage_pct": round(len(matched) / len(jd_skills) * 100, 1) if jd_skills else 0.0,
    }


def match_resume_to_jd(resume_text, jd_text):
    return {
        "similarity_score": compute_match_score(resume_text, jd_text),
        **check_skills_overlap(resume_text, jd_text),
    }



if __name__ == "__main__":
    resume_sample = (
        "Experienced software engineer skilled in Python, SQL, AWS, Docker, "
        "and React. Built CI/CD pipelines with Jenkins."
    )
    jd_sample = (
        "Looking for a software engineer with experience in Python, AWS, "
        "Kubernetes, Terraform, and React. Kafka experience is a plus."
    )

    result = match_resume_to_jd(resume_sample, jd_sample)
    import json
    print(json.dumps(result, indent=2))