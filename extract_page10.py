"""
Extract text from Google Environmental Report using PyMuPDF
"""
import fitz  # PyMuPDF

# Open the PDF file
pdf_path = "data/corporate-sustainability/apple-env-2024.pdf"

print("=" * 70)
print("PDF Text Extraction with PyMuPDF")
print("=" * 70)
print(f"\nOpening: {pdf_path}")

try:
    # Check if file exists
    import os
    if not os.path.exists(pdf_path):
        print(f"Error: File does not exist at {pdf_path}")
        exit(1)
    
    file_size = os.path.getsize(pdf_path) / 1024 / 1024
    print(f"File size: {file_size:.2f} MB")
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    print(f"Total pages: {len(doc)}")
    print(f"PDF metadata: {doc.metadata}")
    print()
    
    # Extract text from page 10 (index 9, since PyMuPDF uses 0-based indexing)
    page_number = 10
    page_index = page_number - 1
    
    if page_index < len(doc):
        print("=" * 70)
        print(f"Text from Page {page_number}")
        print("=" * 70)
        print()
        
        page = doc[page_index]
        text = page.get_text()
        
        print(text)
        
        # Save to file
        output_file = "page10_text.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        print()
        print("=" * 70)
        print(f"Page {page_number} extraction complete")
        print(f"Characters extracted: {len(text)}")
        print(f"Text saved to: {output_file}")
        print("=" * 70)
    else:
        print(f"Error: Page {page_number} does not exist. PDF has {len(doc)} pages.")
    
    # Close the document
    doc.close()
    
except FileNotFoundError:
    print(f"Error: PDF file not found at {pdf_path}")
except Exception as e:
    print(f"Error: {e}")
