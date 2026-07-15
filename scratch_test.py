from parsers.extractor import extract_text

text = extract_text(r"C:\Users\hp\Downloads\Harishchandra_Rathwa_Resume.docx")
print("linkedin.com" in text.lower())
print(text)