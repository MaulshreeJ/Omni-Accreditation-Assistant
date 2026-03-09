"""
Generate test PDFs with different quality levels for NAAC Criterion 3.2.1
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from pathlib import Path

def create_excellence_university_pdf():
    """Grade A+ - Excellent evidence with high funding"""
    output_path = Path("D:/NAAC_Test_PDFs") / "Excellence_University_A+_SSR.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Excellence University Self Study Report - NAAC Accreditation</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    subtitle = Paragraph("<b>Criterion 3.2.1: Extramural Funding for Research</b>", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    # Add explicit dimension keywords
    intro = Paragraph("""
    <b>Grants received from Government and non-governmental agencies for research projects during the last five years.</b><br/>
    Total number of projects funded: 127 projects<br/>
    Total funds received: INR 4580 Lakhs<br/>
    Funding agencies: DST, SERB, DBT, ICSSR, Industry, Corporate partners
    """, styles['Normal'])
    story.append(intro)
    story.append(Spacer(1, 12))
    
    # Table 1: Year-wise Summary
    table1_data = [
        ['Year', 'Number of Projects', 'Total Funding (INR Lakhs)', 'Funding Agencies', 'Average per Project (INR Lakhs)'],
        ['2019-20', '22', '785', 'DST, SERB, DBT, Industry', '35.68'],
        ['2020-21', '28', '920', 'SERB, DBT, ICSSR, DST', '32.86'],
        ['2021-22', '31', '1150', 'DST, SERB, Industry, Corporate', '37.10'],
        ['2022-23', '24', '890', 'DBT, DST, SERB, ICSSR', '37.08'],
        ['2023-24', '22', '835', 'ICSSR, DST, Industry, SERB', '37.95'],
        ['Total (5 Years)', '127', '4580', 'Multiple Agencies', '36.06']
    ]
    
    table1 = Table(table1_data)
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("<b>Table 1: Year-wise Extramural Research Funding Summary</b>", styles['Heading3']))
    story.append(Spacer(1, 6))
    story.append(table1)
    story.append(Spacer(1, 20))
    
    # Table 2: Agency-wise Distribution
    table2_data = [
        ['Funding Agency', 'Projects', 'Total Funding (INR Lakhs)', 'Percentage', 'Key Research Areas'],
        ['DST (Dept of Science & Technology)', '38', '1580', '34.5%', 'AI, Renewable Energy, Materials'],
        ['SERB (Science & Engg Research Board)', '32', '1240', '27.1%', 'Nanotech, Biotech, Computing'],
        ['DBT (Dept of Biotechnology)', '24', '890', '19.4%', 'Genomics, Drug Discovery, Agri-biotech'],
        ['ICSSR (Indian Council Social Science)', '18', '520', '11.4%', 'Economics, Sociology, Policy'],
        ['Industry & Corporate Partners', '15', '350', '7.6%', 'Applied Research, Product Dev'],
        ['Total', '127', '4580', '100%', 'Multi-disciplinary Research']
    ]
    
    table2 = Table(table2_data)
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("<b>Table 2: Funding Agency-wise Distribution</b>", styles['Heading3']))
    story.append(Spacer(1, 6))
    story.append(table2)
    
    doc.build(story)
    print(f"Created: {output_path.name} (Grade A+ - Excellent)")

def create_struggling_college_pdf():
    """Grade C - Poor evidence with minimal funding"""
    output_path = Path("D:/NAAC_Test_PDFs") / "Struggling_College_C_SSR.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title = Paragraph("<b>Struggling College Self Study Report - NAAC Accreditation</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    subtitle = Paragraph("<b>Criterion 3.2.1: Extramural Funding for Research</b>", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    # Minimal data
    table_data = [
        ['Year', 'Number of Projects', 'Total Funding (INR Lakhs)', 'Funding Agencies'],
        ['2019-20', '2', '15', 'UGC'],
        ['2020-21', '1', '8', 'State Govt'],
        ['2021-22', '3', '22', 'UGC, Local Industry'],
        ['2022-23', '1', '10', 'UGC'],
        ['2023-24', '2', '18', 'State Govt, UGC'],
        ['Total (5 Years)', '9', '73', 'Limited Sources']
    ]
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("<b>Table: Research Funding Summary</b>", styles['Heading3']))
    story.append(Spacer(1, 6))
    story.append(table)
    story.append(Spacer(1, 12))
    
    note = Paragraph("<i>Note: The college has limited research infrastructure and is working to improve external funding.</i>", styles['Normal'])
    story.append(note)
    
    doc.build(story)
    print(f"Created: {output_path.name} (Grade C - Struggling)")

def create_good_college_pdf():
    """Grade B+ - Good evidence with moderate funding"""
    output_path = Path("D:/NAAC_Test_PDFs") / "Good_College_B+_SSR.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title = Paragraph("<b>Good College Self Study Report - NAAC Accreditation</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    subtitle = Paragraph("<b>Criterion 3.2.1: Extramural Funding for Research</b>", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    # REDUCED DATA for B+ grade - fewer projects, less funding
    table_data = [
        ['Year', 'Number of Projects', 'Total Funding (INR Lakhs)', 'Funding Agencies', 'Average per Project'],
        ['2019-20', '8', '180', 'UGC, State Govt', '22.50'],
        ['2020-21', '10', '220', 'UGC, DST', '22.00'],
        ['2021-22', '9', '195', 'UGC, SERB', '21.67'],
        ['2022-23', '7', '160', 'UGC, State Govt', '22.86'],
        ['2023-24', '11', '245', 'DST, UGC, Industry', '22.27'],
        ['Total (5 Years)', '45', '1000', 'Multiple Agencies', '22.22']
    ]
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("<b>Table: Year-wise Research Funding Summary</b>", styles['Heading3']))
    story.append(Spacer(1, 6))
    story.append(table)
    
    doc.build(story)
    print(f"Created: {output_path.name} (Grade B+ - Good)")

def create_missing_evidence_pdf():
    """Grade D - Missing critical evidence"""
    output_path = Path("D:/NAAC_Test_PDFs") / "MissingEvidence_College_D_SSR.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title = Paragraph("<b>College with Missing Evidence - NAAC Self Study Report</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    subtitle = Paragraph("<b>Criterion 3.2.1: Extramural Funding for Research</b>", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    # Vague, incomplete data
    text = Paragraph("""
    The college has received some external funding for research activities over the past few years.
    Faculty members have submitted proposals to various funding agencies. Some projects were approved.
    The college is committed to improving research culture and seeking more external funding opportunities.
    """, styles['Normal'])
    story.append(text)
    story.append(Spacer(1, 12))
    
    note = Paragraph("<i>Note: Detailed funding data is being compiled and will be submitted separately.</i>", styles['Italic'])
    story.append(note)
    
    doc.build(story)
    print(f"Created: {output_path.name} (Grade D - Missing Evidence)")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("GENERATING TEST PDFs FOR NAAC CRITERION 3.2.1")
    print("="*60 + "\n")
    
    create_excellence_university_pdf()
    create_good_college_pdf()
    create_struggling_college_pdf()
    create_missing_evidence_pdf()
    
    print("\n" + "="*60)
    print("ALL TEST PDFs CREATED SUCCESSFULLY!")
    print("="*60)
    print("\nSaved to: D:/NAAC_Test_PDFs/")
    print("\nExpected Results:")
    print("  - Excellence_University_A+_SSR.pdf -> Grade A (70-85% confidence)")
    print("  - Good_College_B+_SSR.pdf -> Grade B+ (50-70% confidence)")
    print("  - Struggling_College_C_SSR.pdf -> Grade C (0-30% confidence)")
    print("  - MissingEvidence_College_D_SSR.pdf -> Grade D (0-25% confidence)")
    print("\nUpload any PDF through the UI to test!")
    print("These PDFs are saved separately and won't be deleted during ingestion.")
