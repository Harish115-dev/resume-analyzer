import os
import uuid

from flask import Blueprint, request, render_template, jsonify, current_app
from werkzeug.utils import secure_filename
from auth.routes import login_required

from parsers.extractor import extract_text
from parsers.section_splitter import split_section
from analysis.matcher import match_resume_to_jd
from analysis.ats_scorer import score_resume
from analysis.llm_feedback import generate_feedback

analysis_bp = Blueprint("analysis", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}


import re

def _parse_feedback_text(text):
    """
    Splits the LLM's numbered/bulleted feedback text into a summary
    paragraph plus a clean list of suggestion strings, so the template
    can render them as separate styled items instead of one text blob.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    summary_lines = []
    suggestions = []

    for line in lines:
        if re.match(r"^([\*\-•]|\d+\.)\s+", line):
            cleaned = re.sub(r"^([\*\-•]|\d+\.)\s+", "", line)
            suggestions.append(cleaned)
        else:
            summary_lines.append(line)

    return {
        "summary": " ".join(summary_lines).strip(),
        "suggestions": suggestions,
    }

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def run_pipeline(filepath,jd_text):
    raw_text=extract_text(filepath)
    if not raw_text or not raw_text.strip():
        return None, "Couldn't extract any text from that file. If it's a scanned/image PDF, try a text-based version."
    sections = split_section(raw_text)
    jd_match_result = None
    if jd_text and jd_text.strip():
        jd_match_result = match_resume_to_jd(raw_text, jd_text)
    ats_result = score_resume(raw_text, sections, jd_match_result)
    feedback_result = generate_feedback(ats_result, jd_match_result)
    feedback_result["parsed"] = _parse_feedback_text(feedback_result["feedback"])
    return {
        "sections": sections,
        "jd_match": jd_match_result,
        "ats_result": ats_result,
        "feedback": feedback_result,
    }, None
def save_upload_file(file):
    filename=secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder,exist_ok=True)
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)
    return filepath

@analysis_bp.route("/",methods=["GET"])
def index():
    return render_template("index.html")

@analysis_bp.route("/analyze",methods=["POST"])
@login_required
def analyze_web():
    file=request.files.get("resume")
    jd_text = request.form.get("job_description", "").strip()
    if not file or file.filename == "":
        return render_template("index.html", error="Please upload a resume file.")
    if not allowed_file(file.filename):
        return render_template("index.html", error="Unsupported file type. Please upload a PDF or DOCX file.")
    
    filepath = save_upload_file(file)
    try:
        result, error = run_pipeline(filepath, jd_text)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
    if error:
        return render_template("index.html", error=error)
    return render_template("result.html", result=result, filename=file.filename)

@analysis_bp.route("/api/analyze",methods=["POST"])
def analyze_api():
    file=request.files.get("resume")
    jd_text = request.form.get("job_description", "").strip()
    if not file or file.filename == "":
        return jsonify({"error": "No resume file provided."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF or DOCX."}), 400
    filepath =save_upload_file(file)
    try:
        result, error = run_pipeline(filepath, jd_text)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    if error:
        return jsonify({"error": error}), 422

    return jsonify(result), 200
