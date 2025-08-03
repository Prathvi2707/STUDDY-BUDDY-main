from fpdf import FPDF

def generate_pdf(quiz_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in quiz_text.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)

    pdf_path = "quiz_output.pdf"
    pdf.output(pdf_path)
    return pdf_path
