"""
Convert Markdown User Manual to PDF using WeasyPrint
"""

import markdown2
from weasyprint import HTML, CSS
import os

def convert_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF with proper styling"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'toc',
        'code-friendly',
        'break-on-newline'
    ])

    # Create styled HTML document
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }}
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }}

            h1 {{
                color: #2c3e50;
                font-size: 24pt;
                margin-top: 24pt;
                margin-bottom: 12pt;
                border-bottom: 3px solid #3498db;
                padding-bottom: 8pt;
                page-break-after: avoid;
            }}

            h2 {{
                color: #34495e;
                font-size: 18pt;
                margin-top: 20pt;
                margin-bottom: 10pt;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 6pt;
                page-break-after: avoid;
            }}

            h3 {{
                color: #2c3e50;
                font-size: 14pt;
                margin-top: 16pt;
                margin-bottom: 8pt;
                page-break-after: avoid;
            }}

            h4 {{
                color: #555;
                font-size: 12pt;
                margin-top: 12pt;
                margin-bottom: 6pt;
                font-weight: 600;
                page-break-after: avoid;
            }}

            p {{
                margin: 8pt 0;
                text-align: justify;
            }}

            ul, ol {{
                margin: 8pt 0;
                padding-left: 24pt;
            }}

            li {{
                margin: 4pt 0;
            }}

            code {{
                background-color: #f4f4f4;
                padding: 2pt 6pt;
                border-radius: 3pt;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                color: #c7254e;
            }}

            pre {{
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4pt;
                padding: 12pt;
                overflow-x: auto;
                margin: 12pt 0;
                page-break-inside: avoid;
            }}

            pre code {{
                background-color: transparent;
                padding: 0;
                color: #333;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12pt 0;
                font-size: 10pt;
                page-break-inside: avoid;
            }}

            th {{
                background-color: #3498db;
                color: white;
                padding: 8pt;
                text-align: left;
                font-weight: 600;
            }}

            td {{
                border: 1px solid #ddd;
                padding: 8pt;
            }}

            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 16pt;
                margin: 12pt 0;
                color: #555;
                font-style: italic;
                background-color: #f9f9f9;
                padding: 12pt 16pt;
            }}

            strong {{
                color: #2c3e50;
                font-weight: 600;
            }}

            em {{
                color: #555;
            }}

            hr {{
                border: none;
                border-top: 2px solid #e0e0e0;
                margin: 24pt 0;
            }}

            .header {{
                background-color: #3498db;
                color: white;
                padding: 20pt;
                margin: -2.5cm -2cm 2cm -2cm;
                text-align: center;
            }}

            .header h1 {{
                color: white;
                border: none;
                margin: 0;
                padding: 0;
            }}

            .toc {{
                background-color: #f8f9fa;
                padding: 16pt;
                border: 1px solid #dee2e6;
                border-radius: 4pt;
                margin: 16pt 0;
                page-break-after: always;
            }}

            .toc h2 {{
                margin-top: 0;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            .page-break {{
                page-break-after: always;
            }}

            .no-break {{
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert HTML to PDF
    HTML(string=styled_html).write_pdf(pdf_file)

    print(f"✓ PDF created successfully: {pdf_file}")
    print(f"✓ File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == "__main__":
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "mentoring_system_user_manual.md")
    pdf_file = os.path.join(base_dir, "mentoring_system_user_manual.pdf")

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"✗ Error: Markdown file not found: {md_file}")
        exit(1)

    print("Converting Markdown to PDF...")
    print(f"Source: {md_file}")
    print(f"Target: {pdf_file}")
    print()

    try:
        convert_markdown_to_pdf(md_file, pdf_file)
        print()
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"✗ Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
