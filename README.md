# Smart PDF Difference Compare

A Python tool for intelligent PDF comparison with character-level diff detection, formatting analysis, and highlighted output reports. Goes beyond simple text comparison by tracking font, size, color, and position changes.

## Features

- **Character-Level Comparison**: Detects differences at the character level, not just line-by-line
- **Formatting Awareness**: Tracks font, size, color, and position changes
- **Visual Highlighting**: Generates PDFs with highlighted differences
- **HTML Reports**: Creates interactive HTML comparison reports
- **Flask Web API**: RESTful API for integration with other applications
- **Batch Processing**: Compare multiple pages in PDF documents

## Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jagadeeshtroyer/smart-pdf-difference-compare.git
cd smart-pdf-difference-compare
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using the Flask Web API

1. Start the Flask server:
```bash
cd expirements
python app.py
```

2. The API will be available at `http://localhost:5000`

3. Make a POST request to `/comparePdf` with the following form data:
   - `soucePdfPath`: Path to source PDF
   - `destinationPdfPath`: Path to destination PDF
   - `testcaseName`: Name of the test case
   - `testCaseDescription`: Description
   - `appVersion`: Application version
   - `autVersion`: AUT version
   - `generatedAt`: Timestamp
   - `generatedBy`: User name

**Example using curl:**
```bash
curl -X POST http://localhost:5000/comparePdf \
  -F "soucePdfPath=/path/to/source.pdf" \
  -F "destinationPdfPath=/path/to/destination.pdf" \
  -F "testcaseName=Test1" \
  -F "testCaseDescription=Comparing PDFs" \
  -F "appVersion=1.0" \
  -F "autVersion=1.0" \
  -F "generatedAt=2025-10-20" \
  -F "generatedBy=User"
```

### Method 2: Using Python Script Directly

```python
from expirements.extract_compare_highlight import compare_and_highlight_pdf, create_final_highlighted_report

# Compare two PDFs
source_highlighted, dest_highlighted = compare_and_highlight_pdf(
    'path/to/source.pdf',
    'path/to/destination.pdf'
)

# Generate final report
final_report = create_final_highlighted_report(
    source_highlighted,
    dest_highlighted,
    testcase_name="My Test",
    testcase_description="PDF Comparison Test",
    app_version="1.0",
    aut_version="1.0",
    generated_at="2025-10-20",
    generated_by="Your Name"
)

print(f"Comparison complete! Report saved to: {final_report}")
```

## Project Structure

```
├── expirements/              # Main implementation
│   ├── app.py               # Flask web API
│   ├── extract_compare_highlight.py  # Core comparison logic
│   ├── pdf_comparison.py    # PDF comparison utilities
│   ├── py_pdf_highlight.py  # PDF highlighting functions
│   └── Comparision_Report_Template.html  # HTML report template
├── src/                     # Source code structure
│   ├── data/               # Data processing scripts
│   ├── features/           # Feature engineering
│   ├── models/             # Model scripts
│   └── visualization/      # Visualization scripts
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## How It Works

1. **Text Extraction**: Uses `pdfminer.six` to extract text with formatting metadata
2. **Character Analysis**: Breaks down text into individual characters with properties:
   - Font family
   - Font size
   - Color
   - Position (x, y coordinates)
3. **Diff Detection**: Uses Python's `difflib` to identify differences
4. **Highlighting**: Applies colored highlights to changed sections using `PyPDF2`
5. **Report Generation**: Creates HTML reports with side-by-side comparison

## API Endpoints

### GET `/comparePdf`
Returns API connection status and request format information.

### POST `/comparePdf`
Compares two PDF files and returns highlighted versions with a comparison report.

**Response:**
```json
{
  "message": "Comparison Successful!",
  "sourceHighlightedPdf": "/path/to/source_highlighted.pdf",
  "destinationHighlightedPdf": "/path/to/dest_highlighted.pdf",
  "finalReport": "/path/to/comparison_report.html"
}
```

### POST `/upload-pdf`
Uploads a PDF file to the server.

## Dependencies

- **Flask**: Web framework for API
- **PyPDF2**: PDF manipulation
- **pdfminer.six**: PDF text extraction with formatting
- **BeautifulSoup4**: HTML parsing
- **difflib**: Text comparison (Python standard library)

See `requirements.txt` for complete list.

## Examples

Sample PDFs are included in the `expirements/` directory:
- `Good question.pdf` - Source PDF
- `Good question2.pdf` - Modified PDF

Run a comparison on these samples to see the tool in action.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Jagadeesh D

## Acknowledgments

- Built with Python and open-source libraries
- Inspired by the need for intelligent PDF comparison in document workflows

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: This tool is designed for text-based PDFs. Image-based or scanned PDFs may require OCR preprocessing.
