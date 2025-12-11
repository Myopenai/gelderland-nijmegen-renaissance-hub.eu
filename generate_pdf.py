from weasyprint import HTML
import base64

def create_pdf():
    # Read the markdown content
    with open('UNIVERSITY_CAPITAL_CASE.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>University Capital - Investment Case</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @top-center {{
                    content: "University Capital / KEAN - Investment Case";
                    font-size: 12px;
                    color: #666;
                }}
                @bottom-center {{
                    content: counter(page) "/" counter(pages);
                    font-size: 10px;
                    color: #999;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }}
            h1, h2, h3, h4 {{
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            h1 {{
                color: #1a5276;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .highlight {{
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 15px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .footer {{
                font-size: 0.8em;
                color: #7f8c8d;
                margin-top: 50px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            }}
            pre {{
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            .emoji {{
                font-size: 1.2em;
                margin-right: 5px;
            }}
        </style>
    </head>
    <body>
        <h1><span class="emoji">🏛️</span> University Capital / KEAN</h1>
        <h2>Investment Case</h2>
        <p><em>December 2025</em></p>
        
        {markdown_to_html(md_content)}
        
        <div class="footer">
            <p>Confidential - For Investor Presentation Only</p>
            <p>© 2025 University Capital. All rights reserved.</p>
        </div>
    </body>
    </html>
    """.format(markdown_to_html=markdown_to_html(md_content))
    
    # Generate PDF
    HTML(string=html_content, base_url='.').write_pdf('UNIVERSITY_CAPITAL_CASE.pdf')

def markdown_to_html(text):
    # Simple markdown to HTML conversion
    import re
    
    # Headers
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Lists
    text = re.sub(r'^\* (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', text, flags=re.DOTALL)
    
    # Code blocks
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    
    # Tables
    text = re.sub(r'\|(.*)\|', r'<tr><td>' + r'</td><td>'.join(['\1']) + r'</td></tr>', text)
    text = re.sub(r'\|[-:]+\|', '', text)  # Remove separator lines
    
    # Bold and italics
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Line breaks
    text = text.replace('\n', '<br>')
    
    return text

if __name__ == "__main__":
    create_pdf()
    print("PDF generated successfully: UNIVERSITY_CAPITAL_CASE.pdf")
