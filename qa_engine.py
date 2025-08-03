import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  # You can try "gemini-1.5-pro" too

# Question-Answer Function
def ask_question(context, question):
    prompt = f"""
You are a helpful AI assistant. Use the following context to answer the question.
Context: {context}
Question: {question}
"""
    try:
        response = model.generate_content(prompt)

        # Extract answer safely
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"Error during API call: {e}"
