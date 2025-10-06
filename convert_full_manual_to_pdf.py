"""
Convert Complete UPG System Manual (with source code) to PDF using ReportLab
"""

import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
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
        self.in_code_block = False
        self.code_content = []

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
            # Check if this is inline code or code block
            if not self.in_pre:
                self.current_text.append('<font name="Courier" size="9" color="#c7254e">')
            else:
                self.in_code_block = True
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')
        elif tag == 'pre':
            self.in_pre = True
            self.code_content = []
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
            if not self.in_pre:
                self.current_text.append('</font>')
            else:
                self.in_code_block = False
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('</b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('</i>')
        elif tag == 'pre':
            self.in_pre = False
            self.flush_code_block()
        elif tag == 'ul' or tag == 'ol':
            self.in_list = False
            for item in self.list_items:
                self.flowables.append(item)
            self.list_items = []
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'li':
            self.flush_list_item()

    def handle_data(self, data):
        if self.in_pre and self.in_code_block:
            self.code_content.append(data)
        elif data.strip():
            # Escape special characters for ReportLab
            data = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.current_text.append(data)

    def flush_code_block(self):
        """Flush code block as Preformatted text"""
        if self.code_content:
            code_text = ''.join(self.code_content)
            # Split long lines if needed
            lines = code_text.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 90:
                    # Truncate very long lines
                    lines[i] = line[:87] + '...'

            code_text = '\n'.join(lines[:500])  # Limit to 500 lines per code block

            try:
                preformatted = Preformatted(
                    code_text,
                    self.styles['Code'],
                    maxLineLength=90
                )
                self.flowables.append(preformatted)
                self.flowables.append(Spacer(1, 0.1*inch))
            except Exception as e:
                # If preformatted fails, add as paragraph
                para = Paragraph(f"[Code block - see source file]", self.styles['Normal'])
                self.flowables.append(para)

            self.code_content = []

    def flush_text(self):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                try:
                    para = Paragraph(text, self.current_style)
                    self.flowables.append(para)
                except Exception as e:
                    # Fallback for problematic text
                    simplified_text = text[:500]  # Truncate if too long
                    para = Paragraph(simplified_text, self.current_style)
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

    print("Reading markdown file...")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print(f"Markdown file size: {len(md_content) / 1024:.2f} KB")

    # Split into Part 1 and Part 2 for better handling
    if "PART 2: COMPLETE SOURCE CODE APPENDIX" in md_content:
        print("Splitting into Part 1 (User Manual) and Part 2 (Source Code)...")
        parts = md_content.split("PART 2: COMPLETE SOURCE CODE APPENDIX")
        part1 = parts[0]
        part2_header = "# PART 2: COMPLETE SOURCE CODE APPENDIX\n\n" + parts[1][:5000]  # Limit source code

        print("Note: Due to size, PDF will include Part 1 fully and Part 2 summary.")
        print("Full source code is available in the .md file.")

        md_content = part1 + "\n\n---\n\n" + part2_header + "\n\n**Note:** Full source code (106 files) is available in the markdown file. This PDF includes the first portion for reference."

    print("Converting markdown to HTML...")
    html_content = markdown2.markdown(md_content, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'code-friendly'
    ])

    # Create PDF document
    print("Creating PDF document...")
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
    styles['Heading1'].fontSize = 20
    styles['Heading1'].textColor = colors.HexColor('#2c3e50')
    styles['Heading1'].spaceAfter = 12
    styles['Heading1'].spaceBefore = 20

    styles['Heading2'].fontSize = 16
    styles['Heading2'].textColor = colors.HexColor('#34495e')
    styles['Heading2'].spaceAfter = 10
    styles['Heading2'].spaceBefore = 16

    styles['Heading3'].fontSize = 13
    styles['Heading3'].textColor = colors.HexColor('#2c3e50')
    styles['Heading3'].spaceAfter = 8
    styles['Heading3'].spaceBefore = 12

    styles['Heading4'].fontSize = 11
    styles['Heading4'].textColor = colors.HexColor('#555555')
    styles['Heading4'].spaceAfter = 6
    styles['Heading4'].spaceBefore = 10

    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 13
    styles['Normal'].alignment = TA_JUSTIFY

    # Add custom code style if not exists
    if 'Code' not in styles:
        styles.add(ParagraphStyle(
            name='Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=7,
            leftIndent=10,
            rightIndent=10,
            leading=9
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
    story.append(Paragraph("UPG System", title_style))
    story.append(Paragraph("Complete System Manual", title_style))
    story.append(Spacer(1, 0.5*inch))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    story.append(Paragraph("With Complete Source Code Documentation", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Version 1.0", subtitle_style))
    story.append(Paragraph("October 2025", subtitle_style))
    story.append(PageBreak())

    # Parse HTML and add to story
    print("Parsing HTML content...")
    parser = HTMLToParagraphConverter(styles)
    parser.feed(html_content)
    story.extend(parser.get_flowables())

    # Build PDF
    print("Building PDF (this may take a few minutes)...")
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    print(f"PDF created successfully: {pdf_file}")
    print(f"File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == "__main__":
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "UPG_System_Complete_Manual.md")
    pdf_file = os.path.join(base_dir, "UPG_System_Complete_Manual.pdf")

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        exit(1)

    print("="*60)
    print("Converting UPG System Complete Manual to PDF")
    print("="*60)
    print(f"Source: {md_file}")
    print(f"Target: {pdf_file}")
    print()

    try:
        convert_markdown_to_pdf(md_file, pdf_file)
        print()
        print("="*60)
        print("Conversion completed successfully!")
        print("="*60)
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
