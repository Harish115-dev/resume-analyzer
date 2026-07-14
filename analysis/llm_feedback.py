
from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def _build_prompt(ats_result: dict, jd_match_result: dict | None) -> str:
    details=ats_result
    context={
        "overall_score":ats_result["overall_score"],
        "breakdown": ats_result["breakdown"],
        "section_missing":[ name for name,present in details["sections"]["present"].items()
                           if not present
                           ],
        
        

    }