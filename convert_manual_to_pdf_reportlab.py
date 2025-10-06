"""
Convert Markdown User Manual to PDF using ReportLab
"""

import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from html.parser import HTMLParser
import os
import re

class HTMLToParagraphConverter(HTMLParser):
    """Convert HTML to ReportLab flowables"""

    def __init__(self, styles):
        super().__init__()
        self.styles = styles
        self.flowables = []
        self.current_text = []
        self.current_style = styles['Normal']
        self.in_pre = False
        self.in_list = False
        self.list_items = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_style = self.styles['Heading1']
        elif tag == 'h2':
            self.current_style = self.styles['Heading2']
        elif tag == 'h3':
            self.current_style = self.styles['Heading3']
        elif tag == 'h4':
            self.current_style = self.styles['Heading4']
        elif tag == 'p':
            self.current_style = self.styles['Normal']
        elif tag == 'code':
            self.current_text.append('<font name="Courier" size="9" color="#c7254e">')
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')
        elif tag == 'pre':
            self.in_pre = True
        elif tag == 'ul' or tag == 'ol':
            self.in_list = True
            self.list_items = []
        elif tag == 'li':
            pass
        elif tag == 'hr':
            self.flush_text()
            self.flowables.append(Spacer(1, 0.2*inch))

    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'p']:
            self.flush_text()
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'code':
            self.current_text.append('</font>')
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('</b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('</i>')
        elif tag == 'pre':
            self.in_pre = False
            self.flush_text()
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'ul' or tag == 'ol':
            self.in_list = False
            for item in self.list_items:
                self.flowables.append(item)
            self.list_items = []
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'li':
            self.flush_list_item()

    def handle_data(self, data):
        if data.strip():
            # Escape special characters for ReportLab
            data = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if self.in_pre:
                # Preserve whitespace in code blocks
                self.current_text.append(data)
            else:
                self.current_text.append(data)

    def flush_text(self):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                if self.in_pre:
                    # Code block style
                    code_style = ParagraphStyle(
                        'Code',
                        parent=self.styles['Code'],
                        fontSize=9,
                        fontName='Courier',
                        leftIndent=20,
                        rightIndent=20,
                        spaceBefore=6,
                        spaceAfter=6,
                        backColor=colors.HexColor('#f8f8f8'),
                        borderColor=colors.HexColor('#dddddd'),
                        borderWidth=1,
                        borderPadding=10
                    )
                    para = Paragraph(text, code_style)
                else:
                    para = Paragraph(text, self.current_style)
                self.flowables.append(para)
            self.current_text = []
            self.current_style = self.styles['Normal']

    def flush_list_item(self):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                bullet_style = ParagraphStyle(
                    'Bullet',
                    parent=self.styles['Normal'],
                    leftIndent=20,
                    bulletIndent=10,
                    fontSize=11,
                    spaceBefore=3,
                    spaceAfter=3
                )
                para = Paragraph(f"• {text}", bullet_style)
                self.list_items.append(para)
            self.current_text = []

    def get_flowables(self):
        self.flush_text()
        return self.flowables

def add_page_number(canvas, doc):
    """Add page numbers to each page"""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, text)
    canvas.restoreState()

def convert_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF using ReportLab"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'code-friendly'
    ])

    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Customize styles
    styles['Heading1'].fontSize = 24
    styles['Heading1'].textColor = colors.HexColor('#2c3e50')
    styles['Heading1'].spaceAfter = 12
    styles['Heading1'].spaceBefore = 24

    styles['Heading2'].fontSize = 18
    styles['Heading2'].textColor = colors.HexColor('#34495e')
    styles['Heading2'].spaceAfter = 10
    styles['Heading2'].spaceBefore = 20

    styles['Heading3'].fontSize = 14
    styles['Heading3'].textColor = colors.HexColor('#2c3e50')
    styles['Heading3'].spaceAfter = 8
    styles['Heading3'].spaceBefore = 16

    styles['Heading4'].fontSize = 12
    styles['Heading4'].textColor = colors.HexColor('#555555')
    styles['Heading4'].spaceAfter = 6
    styles['Heading4'].spaceBefore = 12

    styles['Normal'].fontSize = 11
    styles['Normal'].leading = 14
    styles['Normal'].alignment = TA_JUSTIFY

    # Add custom code style if not exists
    if 'Code' not in styles:
        styles.add(ParagraphStyle(
            name='Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#f8f8f8')
        ))

    # Build flowables
    story = []

    # Add title page
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30
    )

    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("UPG Mentoring System", title_style))
    story.append(Paragraph("User Manual", title_style))
    story.append(Spacer(1, 0.5*inch))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    story.append(Paragraph("Version 1.0", subtitle_style))
    story.append(Paragraph("October 2025", subtitle_style))
    story.append(PageBreak())

    # Parse HTML and add to story
    parser = HTMLToParagraphConverter(styles)
    parser.feed(html_content)
    story.extend(parser.get_flowables())

    # Build PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    print(f"PDF created successfully: {pdf_file}")
    print(f"File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == "__main__":
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "mentoring_system_user_manual.md")
    pdf_file = os.path.join(base_dir, "mentoring_system_user_manual.pdf")

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        exit(1)

    print("Converting Markdown to PDF using ReportLab...")
    print(f"Source: {md_file}")
    print(f"Target: {pdf_file}")
    print()

    try:
        convert_markdown_to_pdf(md_file, pdf_file)
        print()
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
