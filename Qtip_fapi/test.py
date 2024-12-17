from textExtract import extract_text

file_path = "./assets/test1.pdf"
extracted_text = extract_text(file_path)
print(f"Extracted text from {file_path}:\n{extracted_text}\n")