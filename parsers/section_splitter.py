import re
SECTION_HEADERS = {
    "summary": [
        "summary", "professional summary", "career summary", "executive summary", 
        "career objective", "objective", "profile", "professional profile", "about me"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "professional skills", 
        "areas of expertise", "key skills", "expertise", "strengths"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment history", 
        "work history", "career history", "professional background", "relevant experience"
    ],
    "education": [
        "education", "academic background", "academic profile", "education history", 
        "qualifications", "formal education", "degrees"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects", 
        "featured projects", "capstone projects", "technical projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "credentials", 
        "professional certifications", "accreditations"
    ],
    "awards": [
        "awards", "honors", "achievements", "distinctions", "accolades", 
        "awards and honors", "recognitions"
    ],
    "publications": [
        "publications", "research", "published works", "papers", "articles"
    ],
    "languages": [
        "languages", "languages spoken", "linguistic skills", "language proficiency"
    ],
    "interests": [
        "interests", "hobbies", "hobbies and interests", "activities", "personal interests"
    ],
    "volunteer": [
        "volunteer experience", "volunteering", "community service", "social work", 
        "pro bono work", "community involvement"
    ],
    "references": [
        "references", "recommendations", "references available upon request"
    ],
    "affiliations": [
        "affiliations", "professional affiliations", "memberships", 
        "professional memberships", "associations"
    ]
}


def _match_header(line):
    normalize_line=line.strip().lower()
    if len(normalize_line.split()) > 4:
        return None
    for section_name,variants in SECTION_HEADERS.items():
        for variant in variants:
            if normalize_line== variant or normalize_line.startswith(variant + " "):
                return section_name
    return None


def split_section(raw_text):
    sections = {}
    current_section = "header"
    sections[current_section] = []

    lines = raw_text.split("\n")

    for line in lines:
        matched_section = _match_header(line)

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)
    final_sections = {}
    for section_name, line_list in sections.items():
        final_sections[section_name] = "\n".join(line_list)
        
    return final_sections
