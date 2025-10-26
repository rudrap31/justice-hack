import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

i = 1

def create_title_page(title, path="temp_title.pdf"):
    """Create a PDF page with the title centered."""
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height / 2, title)
    c.showPage()
    c.save()
    return path

def combine_pdfs(file_list):
    global i
    pdf_writer = PdfWriter()

    for file in file_list:
        ext = file.lower().split('.')[-1]
        # Remove the file extension for the title
        title = 'Exhibit {}'.format(i) + ": " + os.path.splitext(os.path.basename(file))[0]
        i += 1

        # 1. Add title page
        title_pdf_path = create_title_page(title)
        title_reader = PdfReader(title_pdf_path)
        pdf_writer.add_page(title_reader.pages[0])
        os.remove(title_pdf_path)

        # 2. Add the actual file
        if ext == "pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        elif ext in ["jpg", "jpeg", "png"]:
            image = Image.open(file).convert("RGB")
            temp_path = "temp_image.pdf"
            image.save(temp_path)
            pdf_reader = PdfReader(temp_path)
            pdf_writer.add_page(pdf_reader.pages[0])
            os.remove(temp_path)

        else:
            print(f"Skipping unsupported file: {file}")

    with open("files.pdf", "wb") as out_file:
        pdf_writer.write(out_file)

    print(f"Combined PDF with title pages saved to {"files.pdf"}")