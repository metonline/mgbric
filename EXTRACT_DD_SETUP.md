# Screenshot DD Extraction Setup

## What It Does
Automatically extracts DD (Double Dummy) values from BBO screenshots using OCR (Optical Character Recognition).

## Installation

### Step 1: Install Python Packages
```bash
pip install pytesseract pillow opencv-python numpy
```

### Step 2: Install Tesseract OCR Engine

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default location is fine)
3. The script will auto-detect it

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

## Usage

### Method 1: From Command Line
```bash
python extract_dd_from_screenshot.py <image_file> <board_number>
```

**Examples:**
```bash
# Extract DD from board1.png and update Board 1
python extract_dd_from_screenshot.py board1.png 1

# Extract DD from board3_screenshot.jpg and update Board 3
python extract_dd_from_screenshot.py board3_screenshot.jpg 3
```

### Method 2: Batch Processing (Multiple Boards)
Create a `process_screenshots.bat` file:
```batch
@echo off
REM Process all PNG screenshots in current directory
for %%f in (*.png) do (
    echo Processing %%f
    python extract_dd_from_screenshot.py "%%f" (board number)
    pause
)
```

## Workflow

1. **Open BBO link** for each board (from the links list)
2. **Take screenshot** showing the DD table (bottom right)
3. **Save screenshot** to your desktop (e.g., `board1.png`, `board2.png`)
4. **Run extraction**:
   ```bash
   python extract_dd_from_screenshot.py board1.png 1
   ```
5. **Script will**:
   - Read the screenshot
   - Extract DD values using OCR
   - Validate values (6-13 range)
   - Update the database automatically
   - Show confirmation

## Tips for Best Results

- **Screenshot Quality**: Make sure the DD table is clear and readable
- **Zoom Level**: Use 100% or higher zoom on BBO for better OCR accuracy
- **Lighting**: Good contrast makes OCR more reliable
- **Table Area**: Include the full DD table with headers (NT, S, H, D, C)

## Troubleshooting

**"ModuleNotFoundError: No module named 'pytesseract'"**
- Install packages: `pip install pytesseract pillow opencv-python numpy`

**"tesseract is not installed or it's not in your PATH"**
- Windows: Reinstall Tesseract, make sure to add to PATH during installation
- macOS/Linux: Run the installation commands above

**"Could not extract DD values from screenshot"**
- Take a clearer screenshot
- Zoom in more on BBO
- Make sure the DD table is fully visible
- Try adjusting the image quality/contrast

**Values outside range (6-13)**
- Screenshot quality may be poor, causing OCR errors
- Try taking a new screenshot with better lighting/zoom

## Next Steps

After extracting DD for all 30 boards:

1. Verify in the web interface: `http://localhost:8000/hands_viewer.html`
2. Check completion: `python check_dd_status.py`
3. Export data if needed

## Support

If OCR extraction isn't working well for you, you can:
- Use the manual web form: `http://localhost:8000/dd_input.html`
- Enter values directly (takes 5 min per board)
- Or provide screenshots and I can extract values for you
