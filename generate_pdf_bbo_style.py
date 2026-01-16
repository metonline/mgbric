#!/usr/bin/env python3
"""
Generate a professional PDF with BBO-style design.
Includes all 30 boards with hands, DD tables, and bridge graphics.
"""

import json
from pathlib import Path
import subprocess
import sys

def install_package(package_name):
    """Install a pip package."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def generate_bbo_style_pdf():
    """Generate PDF with BBO-style design using fpdf2."""
    from fpdf import FPDF
    
    # Load database and DD tables
    db_path = Path('c:/Users/metin/Desktop/BRIC/app/www/hands_database.json')
    dd_path = Path('c:/Users/metin/Desktop/BRIC/app/www/dd_tables.json')
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    with open(dd_path, 'r') as f:
        dd_tables = json.load(f)
    
    class BBOPdf(FPDF):
        def __init__(self):
            super().__init__(orientation='L', unit='mm', format='A4')
            self.WIDTH = 297
            self.HEIGHT = 210
        
        def header(self):
            # Page header with title
            self.set_fill_color(26, 84, 144)  # BBO blue
            self.set_text_color(255, 255, 255)
            self.set_font('Helvetica', 'B', 16)
            self.cell(0, 12, 'PAZAR SIMULTANEE - Event #404377 (04-01-2026)', 
                     border=0, align='C', fill=True, new_y='NEXT')
            self.set_text_color(0, 0, 0)
            self.ln(2)
        
        def footer(self):
            self.set_y(-10)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    pdf = BBOPdf()
    pdf.add_page()
    
    # Board grid - 2 boards per row on landscape
    board_num = 1
    row = 0
    
    while board_num <= 30:
        if row >= 3:  # 3 rows per page on landscape
            pdf.add_page()
            row = 0
        
        # Draw 2 boards per row
        for col in range(2):
            if board_num > 30:
                break
            
            x_offset = 10 + col * 145
            y_offset = 35 + row * 55
            
            board_key = str(board_num)
            board_data = database.get(board_key)
            dd_data = dd_tables.get(board_key)
            
            if not board_data or not dd_data:
                board_num += 1
                continue
            
            # Get board info
            dealer = ((board_num - 1) % 4) + 1
            dealer_names = ['N', 'E', 'S', 'W']
            dealer_name = dealer_names[dealer - 1]
            
            vuln_pattern = [0, 1, 2, 3, 1, 2, 3, 0, 2, 3, 0, 1, 3, 0, 1, 2]
            vuln_num = vuln_pattern[(board_num - 1) % 16]
            vuln_names = ['-', 'N/S', 'E/W', 'All']
            vuln_name = vuln_names[vuln_num]
            
            tricks = dd_data['NS_tricks']
            
            # Board container background
            pdf.set_xy(x_offset, y_offset)
            pdf.set_draw_color(26, 84, 144)
            pdf.set_fill_color(240, 245, 250)
            pdf.rect(x_offset, y_offset, 133, 53, 'F')
            pdf.set_draw_color(26, 84, 144)
            pdf.set_line_width(0.5)
            pdf.rect(x_offset, y_offset, 133, 53)
            
            # Header with board number
            pdf.set_xy(x_offset, y_offset)
            pdf.set_fill_color(26, 84, 144)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 10)
            header_text = f"Board {board_num}  |  Dealer: {dealer_name}  |  Vul: {vuln_name}"
            pdf.cell(133, 5, header_text, border=0, align='C', fill=True)
            
            # Hands section
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 6.5)
            
            n_hand = board_data.get('N', {})
            e_hand = board_data.get('E', {})
            s_hand = board_data.get('S', {})
            w_hand = board_data.get('W', {})
            
            # North
            pdf.set_xy(x_offset + 40, y_offset + 6)
            pdf.set_text_color(26, 84, 144)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(20, 3, 'N', align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 6)
            pdf.set_xy(x_offset + 30, y_offset + 9)
            n_str = f"S{n_hand.get('S', '-')} H{n_hand.get('H', '-')} D{n_hand.get('D', '-')} C{n_hand.get('C', '-')}"
            pdf.cell(53, 3, n_str, align='C')
            
            # West
            pdf.set_xy(x_offset + 5, y_offset + 14)
            pdf.set_text_color(26, 84, 144)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(8, 3, 'W', align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 6)
            pdf.set_xy(x_offset + 2, y_offset + 17)
            w_str = f"S{w_hand.get('S', '-')}\nH{w_hand.get('H', '-')}\nD{w_hand.get('D', '-')}\nC{w_hand.get('C', '-')}"
            for i, line in enumerate(w_str.split('\n')):
                pdf.set_xy(x_offset + 2, y_offset + 17 + i * 2.5)
                pdf.cell(8, 2.5, line, align='C')
            
            # East
            pdf.set_xy(x_offset + 120, y_offset + 14)
            pdf.set_text_color(26, 84, 144)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(8, 3, 'E', align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 6)
            pdf.set_xy(x_offset + 120, y_offset + 17)
            e_str = f"S{e_hand.get('S', '-')}\nH{e_hand.get('H', '-')}\nD{e_hand.get('D', '-')}\nC{e_hand.get('C', '-')}"
            for i, line in enumerate(e_str.split('\n')):
                pdf.set_xy(x_offset + 120, y_offset + 17 + i * 2.5)
                pdf.cell(8, 2.5, line, align='C')
            
            # South
            pdf.set_xy(x_offset + 40, y_offset + 38)
            pdf.set_text_color(26, 84, 144)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(20, 3, 'S', align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 6)
            pdf.set_xy(x_offset + 30, y_offset + 41)
            s_str = f"S{s_hand.get('S', '-')} H{s_hand.get('H', '-')} D{s_hand.get('D', '-')} C{s_hand.get('C', '-')}"
            pdf.cell(53, 3, s_str, align='C')
            
            # DD Table on the right
            pdf.set_xy(x_offset + 85, y_offset + 6)
            pdf.set_fill_color(26, 84, 144)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 6)
            pdf.cell(20, 3, 'DD Table', border=1, align='C', fill=True)
            
            # DD data rows
            suits = ['S', 'H', 'D', 'C', 'NT']
            suit_names = ['Sp', 'H', 'D', 'C', 'NT']
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(200, 220, 240)
            pdf.set_font('Helvetica', '', 6)
            
            for i in range(5):
                pdf.set_xy(x_offset + 85, y_offset + 9 + i * 2.8)
                pdf.cell(10, 2.5, suit_names[i], border=1, align='C', fill=(i % 2 == 0))
                pdf.set_xy(x_offset + 95, y_offset + 9 + i * 2.8)
                pdf.cell(10, 2.5, str(tricks[i]), border=1, align='C', fill=(i % 2 == 0))
            
            board_num += 1
        
        row += 1
    
    # Save PDF
    output_path = Path('c:/Users/metin/Desktop/BRIC/Tournament_Boards.pdf')
    pdf.output(str(output_path))
    
    print(f"✅ PDF generated successfully: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"   Design: BBO-style with hands and DD tables")
    return True

def main():
    print("🎯 Generating BBO-style PDF with all 30 boards...")
    
    # Ensure fpdf2 is installed
    try:
        from fpdf import FPDF
    except ImportError:
        print("Installing fpdf2...")
        try:
            install_package("fpdf2")
        except Exception as e:
            print(f"Error installing fpdf2: {e}")
            return
    
    print("Generating PDF with professional BBO design...")
    success = generate_bbo_style_pdf()
    
    if success:
        pdf_path = Path('c:/Users/metin/Desktop/BRIC/Tournament_Boards.pdf')
        print(f"\n✅ PDF is ready!")
        print(f"📄 Location: {pdf_path}")
        print(f"🎨 Design: BBO-style layout with:")
        print(f"   • All 30 boards (2 per landscape page)")
        print(f"   • Complete hands for N, E, S, W")
        print(f"   • DD tables showing tricks per suit")
        print(f"   • Dealer and vulnerability info")

if __name__ == '__main__':
    main()
