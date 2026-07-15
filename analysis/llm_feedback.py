
from groq import Groq
from dotenv import load_dotenv
import os
import json
from groq import Groq, APIError, RateLimitError


load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None
MODEL = "llama-3.1-8b-instant"

def _build_prompt(ats_result: dict, jd_match_result: dict | None) -> str:
    details = ats_result["details"]
    context={
        "overall_score":ats_result["overall_score"],
        "breakdown": ats_result["breakdown"],
        "section_missing":[ name for name,present in details["sections"]["present"].items()
                           if not present
                           ],
        "contact_missing":[k for k in ("phone","email","linkedin") if not details["contact"][k]],
        "quantified_ratio": details["quantified"]["ratio"],
        "strong_verbs_used": details["action_verbs"]["strong_verbs_used"],
        "weak_phrases_found": details["action_verbs"]["weak_phrases_found"],
        "word_count": details["word_count"]["word_count"],

    }
    if jd_match_result:
        context["jd_match"]={
            "coverage_pct": jd_match_result.get("coverage_pct"),
            "missing_skills": jd_match_result.get("missing_skills", []),
            "matched_skills": jd_match_result.get("matched_skills", []),
        }
    prompt = f"""You are a resume reviewer. Below is structured analysis data for a resume,
already computed by rule-based checks. Do NOT invent scores, numbers, or facts not present
in this data — only reference what's given.

IMPORTANT: Each category in "breakdown" is scored out of a DIFFERENT maximum, not out of 100:
- sections: out of 20
- contact: out of 10
- quantified: out of 20
- action_verbs: out of 15
- word_count: out of 10
- jd_match: out of 25 (if present)
Only "overall_score" is out of 100. Do not describe category scores as "out of 100."

Do NOT recommend action verbs that already appear in "strong_verbs_used" — only suggest
verbs or categories that are absent.

Do NOT suggest adding contact info that is not listed in "contact_missing" — if
"contact_missing" is empty, do not mention contact info at all.

DATA:
{json.dumps(context, indent=2)}

Write feedback in this exact structure:
1. A 2-3 sentence summary of the resume's overall strength, referencing the actual overall_score out of 100.
2. A bulleted list of 3-5 concrete, prioritized suggestions, each grounded in a specific
   data point above.

Be specific and concrete. Keep the total response under 200 words."""

    return prompt


def fallback_feedback(ats_result: dict, jd_match_result: dict | None) -> str:
    details = ats_result["details"]
    lines = []

    score = ats_result["overall_score"]
    if score >= 80:
        lines.append(f"Strong resume overall (score: {score}/100) — a few refinements will polish it further.")
    elif score >= 60:
        lines.append(f"Solid foundation (score: {score}/100), but a few gaps are holding it back.")
    else:
        lines.append(f"Several structural and content issues to address (score: {score}/100).")

    missing_sections = [n for n, p in details["sections"]["present"].items() if not p]
    if missing_sections:
        lines.append(f"- Add missing section(s): {', '.join(missing_sections)}.")

    missing_contact = [k for k in ("email", "phone", "linkedin") if not details["contact"][k]]
    if missing_contact:
        lines.append(f"- Add missing contact info: {', '.join(missing_contact)}.")

    if details["quantified"]["ratio"] < 0.5:
        lines.append(
            f"- Only {details['quantified']['quantified_bullets']} of "
            f"{details['quantified']['total_bullets']} bullets include numbers — "
            f"add more quantifiable results (%, $, time saved)."
        )

    if details["action_verbs"]["weak_phrases_found"]:
        lines.append(
            f"- Replace weak phrasing (e.g. \"{details['action_verbs']['weak_phrases_found'][0]}\") "
            f"with stronger action verbs."
        )

    if jd_match_result and jd_match_result.get("missing_skills"):
        top_missing = ", ".join(jd_match_result["missing_skills"][:5])
        lines.append(f"- Missing key skills from the job description: {top_missing}.")

    if len(lines) == 1:
        lines.append("- No major issues found — fine-tune wording and keep it tailored to each role.")

    return "\n".join(lines)

def generate_feedback(ats_result:dict,jd_match_result:dict | None=None)->dict:
    if not client :
        return{
            "feedback":fallback_feedback(ats_result,jd_match_result),
            "source": "fallback",
            "error": "GROQ_API_KEY not set",
        }
    prompt = _build_prompt(ats_result, jd_match_result)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.4,
        )
        text = response.choices[0].message.content.strip()
        return {"feedback": text, "source": "llm", "error": None}
    except RateLimitError as e:
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Groq rate limit hit: {e}",
        }
    except APIError as e:
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Groq API error: {e}",
        }
    except Exception as e:
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Unexpected error: {e}",
        }
    except RateLimitError as e:
        print(f"[llm_feedback] Rate limit: {e}")
        return {...}
    except APIError as e:
        print(f"[llm_feedback] API error: {e}")
        return {...}
