from fpdf import FPDF
import base64

def generate_pdf(text: str, title: str = "NexQA Report") -> bytes:
    """Generate PDF from text content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", "B", size=14)
    pdf.multi_cell(0, 10, title)
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=11)
    for line in text.split('\n'):
        pdf.multi_cell(0, 6, line)
    
    pdf_bytes = pdf.output()
    return pdf_bytes


def get_base64_image(image_path):
    """Convert image to base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
