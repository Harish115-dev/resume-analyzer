from groq import Groq, APIError, RateLimitError
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None
MODEL = "llama-3.3-70b-versatile"


def _build_prompt(ats_result: dict, jd_match_result: dict | None) -> str:
    details = ats_result["details"]
    breakdown = ats_result["breakdown"]

    category_maxes = {"sections": 20, "contact": 10, "quantified": 20, "action_verbs": 15, "word_count": 10}
    if jd_match_result:
        category_maxes["jd_match"] = 25

    weak_categories = []
    strong_categories = []
    for cat, max_val in category_maxes.items():
        score = breakdown.get(cat)
        if score is None:
            continue
        pct = (score / max_val) * 100 if max_val else 0
        if pct < 60:
            weak_categories.append({"category": cat, "score": score, "max": max_val, "pct": round(pct, 1)})
        else:
            strong_categories.append({"category": cat, "score": score, "max": max_val, "pct": round(pct, 1)})

    context = {
        "overall_score": ats_result["overall_score"],
        "weak_categories": weak_categories,      # only these should drive suggestions
        "strong_categories": strong_categories,  # mention as strengths, don't suggest "improving" these
        "section_missing": [
            name for name, present in details["sections"]["present"].items()
            if not present
        ],
        "contact_missing": [k for k in ("phone", "email", "linkedin") if not details["contact"][k]],
        "quantified_ratio": details["quantified"]["ratio"],
        "strong_verbs_used": details["action_verbs"]["strong_verbs_used"],
        "weak_phrases_found": details["action_verbs"]["weak_phrases_found"],
        "word_count": details["word_count"]["word_count"],
    }
    if jd_match_result:
        context["jd_match"] = {
            "coverage_pct": jd_match_result.get("coverage_pct"),
            "missing_skills": jd_match_result.get("missing_skills", []),
            "matched_skills": jd_match_result.get("matched_skills", []),
        }
    context_readable = {
    "overall_score": context["overall_score"],
    "categories_needing_improvement": context["weak_categories"],
    "categories_that_are_strengths": context["strong_categories"],
    "percentage_of_bullets_with_measurable_results": round(context["quantified_ratio"] * 100),
    "action_verbs_already_used": context["strong_verbs_used"],
    "missing_contact_fields": context["contact_missing"],
}

prompt = f"""You are a resume reviewer. Below is structured analysis data for a resume,
already computed by rule-based checks. Do NOT invent scores, numbers, or facts not present
in this data — only reference what's given.

"categories_needing_improvement" lists categories that scored below 60% of their maximum —
these are the ONLY categories you should suggest improving. "categories_that_are_strengths"
scored 60%+ — you may mention these briefly as strengths in the summary, but do NOT suggest
"improving" or "adding more" to anything in categories_that_are_strengths, even if it's not
a perfect 100%.

"percentage_of_bullets_with_measurable_results" is already given as a percentage — only
bring it up as an improvement area if "quantified" appears in categories_needing_improvement,
not categories_that_are_strengths.

Do NOT recommend action verbs that already appear in "action_verbs_already_used" — only
suggest verbs or categories that are absent.

Do NOT suggest adding contact info that is not listed in "missing_contact_fields" — if
"missing_contact_fields" is empty, do not mention contact info at all.

Never write internal field or key names verbatim in your output. Always translate data
into plain, natural language a human resume-writer would use — describe metrics and
categories in your own words, not as code-style labels.

DATA:
{json.dumps(context_readable, indent=2)}

Write feedback in this exact structure:
1. A 2-3 sentence summary of the resume's overall strength, referencing the actual overall_score out of 100.
2. A bulleted list of 3-5 concrete, prioritized suggestions, each grounded ONLY in
   categories_needing_improvement or other explicitly-listed gaps above (missing sections,
   missing contact, weak phrases, missing JD skills). Do not suggest improving anything in
   categories_that_are_strengths.

Be specific and concrete. Keep the total response under 200 words."""

if not jd_match_result:
    prompt += (
        "\n\nNo job description was provided for this analysis — do NOT mention "
        "JD match, job description alignment, coverage, or similar, since that "
        "data doesn't exist for this resume."
    )


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


def generate_feedback(ats_result: dict, jd_match_result: dict | None = None) -> dict:
    if not client:
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
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
        print(f"[llm_feedback] Rate limit: {e}")
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Groq rate limit hit: {e}",
        }
    except APIError as e:
        print(f"[llm_feedback] API error: {e}")
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Groq API error: {e}",
        }
    except Exception as e:
        print(f"[llm_feedback] Unexpected error: {e}")
        return {
            "feedback": fallback_feedback(ats_result, jd_match_result),
            "source": "fallback",
            "error": f"Unexpected error: {e}",
        }