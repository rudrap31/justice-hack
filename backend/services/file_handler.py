import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from textwrap import wrap

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

def text_to_pdf(text, output_path="text_output.pdf", title=None):
    """Convert plain text into a nicely formatted PDF."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    margin = 50
    line_height = 14
    y = height - margin

    # Optional title at the top
    if title:
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, title)
        y -= 30

    c.setFont("Helvetica", 12)

    # Wrap text to fit within page width
    max_chars_per_line = 90
    wrapped_text = []
    for line in text.splitlines():
        wrapped_text.extend(wrap(line, max_chars_per_line))
        wrapped_text.append("")  # Blank line between paragraphs

    for line in wrapped_text:
        if y < margin:  # Start a new page if space runs out
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_height

    c.save()
    print(f"Text PDF saved to {output_path}")
    return output_path