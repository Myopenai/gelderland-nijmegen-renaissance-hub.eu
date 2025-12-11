from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Logo or title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'University Capital / KEAN', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, 'Investment Case - December 2025', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 40, 'Investment Case', 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, 'University Capital / KEAN', 0, 1, 'C')
    pdf.ln(20)
    
    # Executive Summary
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Executive Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    summary = """
    University Capital/KEAN is a technology-driven platform with significant intellectual property and market potential. 
    Our analysis reveals:
    
    - Current Valuation: $7.27M (weighted average)
    - Documentation: 1.5M+ words across 99+ files
    - Technology Focus: 62,171+ technology mentions
    - Development Investment: 2,062 hours (valued at $594K)
    """
    # Replace any remaining special characters that might cause issues
    summary = summary.replace('•', '-')
    pdf.multi_cell(0, 10, summary)
    
    # Investment Highlights
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Investment Highlights', 0, 1)
    
    # Tech Footprint
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Tech Footprint', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, """
    - 99+ code and documentation files
    - 1.5M+ words of technical documentation
    - 2,062 development hours invested
    - 5x tech multiplier effect on valuation
    """)
    
    # Market & Valuation
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Market & Valuation', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, """
    - Current Valuation: $7.27M (weighted average)
    - Market Approach: $4.0M
    - Income Approach: $18.0M
    - Cost Approach: $891K
    - 5.2x revenue multiplier (market standard)
    """)
    
    # Growth Trajectory
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Growth Trajectory', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, """
    - User Growth: 1,000 → 5,000 (1Y) → 25,000 (3Y)
    - MRR Projection: $10K → $75K (1Y) → $500K (3Y)
    - Team Growth: 5 → 12 → 30 FTE
    - Valuation Uplift: 15-25% (1Y), 50-75% (3Y)
    """)
    
    # Market Positioning
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Market Positioning', 0, 1)
    
    # Table
    col_width = pdf.w / 4.0
    row_height = pdf.font_size * 2
    
    data = [
        ['Metric', 'Competitor A', 'Competitor B', 'University Capital'],
        ['Valuation', '$5.0M', '$12.0M', '$7.27M'],
        ['Employees', '25', '50', '5 (FTE equivalent)'],
        ['Revenue', '$2.0M', '$5.0M', 'Projected $0.9M']
    ]
    
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    
    # Financial Projections
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Financial Projections', 0, 1)
    
    data = [
        ['Metric', 'Current', '1Y Projection', '3Y Projection'],
        ['Users', '1,000', '5,000', '25,000'],
        ['MRR', '$10K', '$75K', '$500K'],
        ['Team Size', '5', '12', '30'],
        ['Valuation', '$7.27M', '$8.7-9.1M', '$10.9-12.7M']
    ]
    
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    
    # Save the PDF
    pdf.output('UNIVERSITY_CAPITAL_CASE.pdf')
    print("PDF generated successfully: UNIVERSITY_CAPITAL_CASE.pdf")

if __name__ == "__main__":
    create_pdf()
