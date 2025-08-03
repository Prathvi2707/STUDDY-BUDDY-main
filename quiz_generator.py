import os
import fitz  # PyMuPDF
from docx import Document
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")  # updated model name

def extract_text_from_pdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text")
        if not text.strip():
            raise ValueError("PDF may be scanned. Using OCR.")
    except Exception:
        # OCR fallback
        images = convert_from_path(file_path)
        for image in images:
            text += pytesseract.image_to_string(image)
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_notes(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return "Unsupported file format."

def generate_quiz(text, num_questions=5):
    prompt = f"""
    Generate {num_questions} quiz questions based on the following notes:
    - Each question must have 4 options.
    - Only one option should be correct.
    - Add an explanation for the correct answer.

    Notes:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during API call: {e}"

# For splitting large quizzes into batches
def generate_quiz_in_batches(text, total_questions):
    batch_size = 10
    final_result = ""
    for i in range(0, total_questions, batch_size):
        current_batch = min(batch_size, total_questions - i)
        result = generate_quiz(text, current_batch)
        final_result += f"\n\n📚 Questions {i+1} to {i+current_batch}:\n{result}"
    return final_result
