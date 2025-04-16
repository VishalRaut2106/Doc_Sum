# PDF and Image Text Analyzer

This application allows users to upload PDF files or images, extract text, generate summaries, break text into paragraphs, and create questions/answers for selected paragraphs.

## Features

- PDF and image text extraction
- Text summarization using T5 model
- Paragraph segmentation
- Question and answer generation

## Requirements

- Python 3.7+
- Tesseract OCR must be installed for image text extraction

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## Usage

1. Run the Streamlit app:
```
streamlit run app.py
```
2. Upload a PDF or image file
3. View the extracted text and summary
4. Explore the paragraphs
5. Select a paragraph number and click "Generate Q&A" to create questions and answers based on that paragraph

## Important Notes

- For large files, processing may take some time
- The quality of text extraction from images depends on the clarity of the image
- For optimal performance, ensure your PDF contains selectable text (not scanned images) 