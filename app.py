import streamlit as st
from file_loader import extract_text_from_pdf, extract_text_from_docx
from qa_engine import ask_question
from quiz_generator import generate_quiz
from pdf_generator import generate_pdf
import PyPDF2
import docx2txt
import fitz
import docx
import os
from dotenv import load_dotenv
from google.generativeai import GenerativeModel, configure

# ----------------- GEMINI SETUP ---------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
configure(api_key=GEMINI_API_KEY)

def get_gemini_response(prompt):
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# ----------------- STREAMLIT CONFIG ---------------------
st.set_page_config(page_title="STUDY BUDDY - Your AI Study Assistant")

# ----------------- SIDEBAR NAVIGATION ---------------------
page = st.sidebar.selectbox(
    "Select Page",
    ["🏠Home", 
     "📝Quiz Generator",
     "📚Flashcards",
     "🤖Doubt Solver Bot", 
     "🧾Notes Summarizer"]
)

# -------------------- PAGE 1: HOME --------------------
if page == "🏠Home":
    st.title("📚 STUDY BUDDY")
    st.subheader("Your AI Study Assistant")
    st.write("Upload your study material (PDF/DOCX) and start learning with AI!")

    uploading_file = st.file_uploader("Upload your study material", type=["pdf", "docx"])
    text = ""

    if uploading_file:
        if uploading_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploading_file)
        elif uploading_file.name.endswith(".docx"):
            text = extract_text_from_docx(uploading_file)

        if text:
            st.success("✅ File uploaded and text extracted successfully!")
            st.write(f"🧾 Total characters extracted: {len(text)}")
            st.text_area("📄 Extracted Text", text[:3000000], height=300)

            st.subheader("❓ Ask a question about your study material")
            user_question = st.text_input("Enter your question here:")

            if user_question:
                with st.spinner("🤖 Getting answer..."):
                    answer = ask_question(text, user_question)
                st.markdown(f"**Answer:** {answer}")
        else:
            st.warning("⚠️ Couldn't extract text. Please check the file content.")
    else:
        st.info("📤 Please upload a PDF or DOCX file to begin.")

# -------------------- PAGE 2: QUIZ GENERATOR --------------------
elif page == "📝Quiz Generator":
    st.title("📝 Quiz Generator")
    st.write("Upload a PDF or DOCX file to generate quiz questions from your notes.")

    uploaded_file = st.file_uploader("Upload your notes file", type=["pdf", "docx"])
    notes = ""

    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            notes = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            notes = extract_text_from_docx(uploaded_file)

        if notes:
            st.success("✅ Notes extracted successfully!")
            st.write(f"🧾 Total characters extracted: {len(notes)}")
            st.text_area("📄 Extracted Notes", notes[:3000000], height=300)

            num_questions = st.slider("Number of questions", 1, 20, 5)
            if st.button("Generate Quiz"):
                with st.spinner("🤖 Generating quiz..."):
                    quiz = generate_quiz(notes, num_questions)

                st.markdown("### 🧠 Quiz Questions")
                st.markdown(quiz)

                pdf_file_path = generate_pdf(quiz)

                with open(pdf_file_path, "rb") as f:
                    st.download_button(
                        label="Download Quiz PDF",
                        data=f,
                        file_name="quiz_output.pdf",
                        mime="application/pdf"
                    )
        else:
            st.warning("⚠️ Couldn't extract text. Please check the file content.")

# -------------------- PAGE 3: FLASHCARDS --------------------
elif page == "📚Flashcards":
    st.title("📚 Flashcards")
    st.write("This is a placeholder for the flashcards feature.")
    st.info("⚙️ Feature under construction... coming soon!")

# -------------------- PAGE 4: DOUBT SOLVER BOT --------------------
elif page == "🤖Doubt Solver Bot":
    def doubt_solver():
        st.title("🤖 Doubt Solver Bot")
        st.write("Ask me anything related to your studies, and I'll do my best to help you!")

        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Optional: Clear chat history button
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


        # Chat input
        user_input = st.chat_input("💬 Type your doubt here...")

        if user_input:
            # Save user's message
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Show user's message
            with st.chat_message("user"):
                st.markdown(user_input)

            # Gemini response
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    prompt = f"You are a helpful tutor. Answer this question clearly and simply:\n\n{user_input}"
                    response = get_gemini_response(prompt)
                    st.markdown(response)

            # Save bot's reply
            st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Show entire chat history (useful after rerun)
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    doubt_solver()


# -------------------- PAGE 5: NOTES SUMMARIZER --------------------
elif page == "🧾Notes Summarizer":

    def extract_text_from_file(uploaded_file):
        if uploaded_file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif uploaded_file.name.endswith(".docx"):
            return docx2txt.process(uploaded_file)
        else:
            return "Unsupported file type."

    def note_summarizer():
        st.title("📝 AI Notes Summarizer")

        tab1, tab2 = st.tabs(["💭 Upload & Summarize", "📝 View Summary"])

        # initialize session state for summary
        if "summary" not in st.session_state:
            st.session_state.summary = ""

        with tab1:
            uploaded_file = st.file_uploader("Upload your notes (PDF/DOCX)", type=["pdf", "docx"])

            if uploaded_file:
                with st.spinner("⏳ Extracting text..."):
                    full_text = extract_text_from_file(uploaded_file)

                st.text_area("📄 Extracted Notes", full_text[:3000000], height=300)

                if st.button("Summarize Notes"):
                    with st.spinner("🤖 Summarizing..."):
                        prompt = f"Summarize the following notes clearly and concisely:\n\n{full_text}"
                        summary = get_gemini_response(prompt)
                        st.success("✅ Summary saved!")
                        st.session_state.summary = summary  # store in session

        with tab2:
            if st.session_state.summary:
                st.subheader("📝 Your summarized notes:")
                st.write(st.session_state.summary)
                st.download_button(
                    "Download summary",
                    st.session_state.summary,
                    file_name="summary.txt"
                )
            else:
                st.info("No summary generated yet. Please upload and summarize in Tab 1.")

    note_summarizer()





st.markdown("___")
st.markdown("<p style='text-align: center; color: light black; font: bold; '> Made by PRATHVI PARTAP </p>", unsafe_allow_html=True)
