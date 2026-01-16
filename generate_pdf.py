#!/usr/bin/env python3
"""
Generate a PDF with all 30 tournament boards in a 3-column grid layout.
Includes DD tables, dealer info, and vulnerability.
"""

import json
from pathlib import Path
import subprocess
import sys

def install_package(package_name):
    """Install a pip package."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def ensure_weasyprint():
    """Ensure weasyprint is installed."""
    try:
        import weasyprint
        return True
    except ImportError:
        print("Installing weasyprint for PDF generation...")
        try:
            install_package("weasyprint")
            return True
        except Exception as e:
            print(f"Error installing weasyprint: {e}")
            print("Trying alternative: fpdf2...")
            try:
                install_package("fpdf2")
                return "fpdf2"
            except:
                return False

def generate_pdf_with_weasyprint():
    """Generate PDF using weasyprint (HTML to PDF)."""
    from weasyprint import HTML, CSS
    
    # Load database and DD tables
    db_path = Path('c:/Users/metin/Desktop/BRIC/app/www/hands_database.json')
    dd_path = Path('c:/Users/metin/Desktop/BRIC/app/www/dd_tables.json')
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    with open(dd_path, 'r') as f:
        dd_tables = json.load(f)
    
    # Create HTML content
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Tournament Boards - PDF</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: Arial, sans-serif;
                padding: 15mm;
                line-height: 1.4;
            }
            
            .header {
                text-align: center;
                margin-bottom: 20mm;
                border-bottom: 2px solid #333;
                padding-bottom: 10mm;
            }
            
            .header h1 {
                font-size: 24pt;
                color: #1a3a0f;
                margin-bottom: 5mm;
            }
            
            .header p {
                font-size: 11pt;
                color: #666;
            }
            
            .boards-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10mm;
                page-break-inside: avoid;
            }
            
            .board {
                border: 1px solid #333;
                padding: 8mm;
                page-break-inside: avoid;
                background: white;
                break-inside: avoid;
            }
            
            .board-header {
                background: #1a5490;
                color: white;
                padding: 5mm;
                margin: -8mm -8mm 5mm -8mm;
                text-align: center;
                font-weight: bold;
                font-size: 12pt;
            }
            
            .board-info {
                font-size: 9pt;
                margin-bottom: 5mm;
                line-height: 1.6;
            }
            
            .board-info strong {
                font-weight: bold;
            }
            
            .dd-table {
                margin: 5mm 0;
                border: 1px solid #ddd;
                font-size: 8pt;
            }
            
            .dd-table table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .dd-table th,
            .dd-table td {
                border: 0.5px solid #ccc;
                padding: 2mm;
                text-align: center;
            }
            
            .dd-table th {
                background: #1a5490;
                color: white;
                font-weight: bold;
            }
            
            .dd-table td {
                background: white;
            }
            
            @page {
                size: A4;
                margin: 10mm;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌉 PAZAR SIMULTANEE</h1>
            <p>Event #404377 • 04-01-2026 • All 30 Boards</p>
        </div>
        
        <div class="boards-grid">
    """
    
    # Add boards to HTML
    for board_num in range(1, 31):
        board_key = str(board_num)
        board_data = database.get(board_key)
        dd_data = dd_tables.get(board_key)
        
        if not board_data or not dd_data:
            continue
        
        # Get board info
        dealer = ((board_num - 1) % 4) + 1
        dealer_names = ['N', 'E', 'S', 'W']
        dealer_name = dealer_names[dealer - 1]
        
        vuln_pattern = [0, 1, 2, 3, 1, 2, 3, 0, 2, 3, 0, 1, 3, 0, 1, 2]
        vuln_num = vuln_pattern[(board_num - 1) % 16]
        vuln_names = ['None', 'N/S', 'E/W', 'Both']
        vuln_name = vuln_names[vuln_num]
        
        tricks = dd_data['NS_tricks']
        suits = ['♠', '♥', '♦', '♣', 'NT']
        
        # Build HTML for this board
        board_html = f"""
            <div class="board">
                <div class="board-header">Board {board_num}</div>
                <div class="board-info">
                    <strong>Dealer:</strong> {dealer_name}<br>
                    <strong>Vul:</strong> {vuln_name}
                </div>
                <div class="dd-table">
                    <table>
                        <tr>
                            <th>Suit</th>
                            <th>Tricks</th>
                        </tr>
        """
        
        for i in range(5):
            board_html += f"""
                        <tr>
                            <td>{suits[i]}</td>
                            <td><strong>{tricks[i]}</strong></td>
                        </tr>
            """
        
        board_html += """
                    </table>
                </div>
            </div>
        """
        
        html_content += board_html
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    output_path = Path('c:/Users/metin/Desktop/BRIC/Tournament_Boards.pdf')
    
    try:
        HTML(string=html_content).write_pdf(str(output_path))
        print(f"✅ PDF generated successfully: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

def generate_pdf_with_fpdf():
    """Generate PDF using fpdf2 (fallback method)."""
    from fpdf import FPDF
    
    # Load database and DD tables
    db_path = Path('c:/Users/metin/Desktop/BRIC/app/www/hands_database.json')
    dd_path = Path('c:/Users/metin/Desktop/BRIC/app/www/dd_tables.json')
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    with open(dd_path, 'r') as f:
        dd_tables = json.load(f)
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(26, 58, 15)
    pdf.cell(0, 10, 'PAZAR SIMULTANEE', ln=True, align='C')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Event #404377 - 04-01-2026', ln=True, align='C')
    pdf.ln(5)
    
    # Boards grid (3 columns)
    col_width = 60
    row_height = 55
    
    board_num = 1
    while board_num <= 30:
        # Check if we need a new page
        if pdf.will_page_break(row_height):
            pdf.add_page()
        
        # Draw 3 boards per row
        for col in range(3):
            if board_num > 30:
                break
            
            x = 10 + col * (col_width + 3)
            y = pdf.get_y()
            
            board_key = str(board_num)
            board_data = database.get(board_key)
            dd_data = dd_tables.get(board_key)
            
            if board_data and dd_data:
                # Get board info
                dealer = ((board_num - 1) % 4) + 1
                dealer_names = ['N', 'E', 'S', 'W']
                dealer_name = dealer_names[dealer - 1]
                
                vuln_pattern = [0, 1, 2, 3, 1, 2, 3, 0, 2, 3, 0, 1, 3, 0, 1, 2]
                vuln_num = vuln_pattern[(board_num - 1) % 16]
                vuln_names = ['None', 'N/S', 'E/W', 'Both']
                vuln_name = vuln_names[vuln_num]
                
                tricks = dd_data['NS_tricks']
                
                # Draw board box
                pdf.set_xy(x, y)
                pdf.set_draw_color(51, 51, 51)
                pdf.rect(x, y, col_width, row_height)
                
                # Header
                pdf.set_xy(x, y)
                pdf.set_fill_color(26, 84, 144)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(col_width, 6, f'Board {board_num}', border=1, align='C', fill=True)
                
                # Info
                pdf.set_xy(x, y + 6)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 7)
                info_text = f'D: {dealer_name} V: {vuln_name}'
                pdf.cell(col_width, 4, info_text, border=0, align='C')
                
                # DD Table header
                pdf.set_xy(x, y + 10)
                pdf.set_fill_color(200, 200, 200)
                pdf.set_font('Arial', 'B', 7)
                pdf.cell(col_width * 0.5, 4, 'Suit', border=1, align='C', fill=True)
                pdf.set_xy(x + col_width * 0.5, y + 10)
                pdf.cell(col_width * 0.5, 4, 'Tricks', border=1, align='C', fill=True)
                
                # DD Table data
                suits = ['S', 'H', 'D', 'C', 'N']
                for i in range(5):
                    pdf.set_xy(x, y + 14 + i * 3)
                    pdf.set_font('Arial', '', 7)
                    pdf.cell(col_width * 0.5, 3, suits[i], border=1, align='C')
                    pdf.set_xy(x + col_width * 0.5, y + 14 + i * 3)
                    pdf.cell(col_width * 0.5, 3, str(tricks[i]), border=1, align='C')
                
                board_num += 1
        
        pdf.ln(row_height)
    
    # Save PDF
    output_path = Path('c:/Users/metin/Desktop/BRIC/Tournament_Boards.pdf')
    pdf.output(str(output_path))
    
    print(f"✅ PDF generated successfully: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    return True

def main():
    print("🎯 Generating PDF with all 30 boards...")
    
    # Use fpdf2 (pure Python, no dependencies)
    print("Installing fpdf2 for PDF generation...")
    try:
        install_package("fpdf2")
        print("✅ fpdf2 installed")
    except Exception as e:
        print(f"Error installing fpdf2: {e}")
        return
    
    print("Using fpdf2 for PDF generation...")
    success = generate_pdf_with_fpdf()
    
    if success:
        pdf_path = Path('c:/Users/metin/Desktop/BRIC/Tournament_Boards.pdf')
        print(f"\n✅ PDF is ready!")
        print(f"📄 Location: {pdf_path}")
        print(f"📊 Contents: All 30 boards with DD tables (3 per row)")

if __name__ == '__main__':
    main()
