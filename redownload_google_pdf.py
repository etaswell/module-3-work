"""
Re-download Google Environmental Report PDF and verify it works
"""
import urllib.request
import os
import fitz  # PyMuPDF

print("=" * 70)
print("Re-downloading Google Environmental Report")
print("=" * 70)
print()

# Google PDF URL
url = "https://www.gstatic.com/gumdrop/sustainability/google-2023-environmental-report.pdf"
output_dir = "data/corporate-sustainability"
output_path = os.path.join(output_dir, "google-env-2024.pdf")

# Create directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Remove old file if it exists
if os.path.exists(output_path):
    print(f"Removing existing file: {output_path}")
    os.remove(output_path)
    print()

print(f"Downloading from: {url}")
print(f"Saving to: {output_path}")
print()

try:
    # Download with progress indication
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded / total_size) * 100)
            if block_num % 50 == 0:  # Print every 50 blocks
                print(f"  Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)")
    
    urllib.request.urlretrieve(url, output_path, reporthook=report_progress)
    
    print()
    print("✓ Download complete")
    
    # Check file size
    file_size = os.path.getsize(output_path)
    print(f"  File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print()
    
    # Verify with PyMuPDF
    print("-" * 70)
    print("Verifying PDF with PyMuPDF...")
    print("-" * 70)
    
    doc = fitz.open(output_path)
    num_pages = len(doc)
    
    if num_pages > 0:
        print(f"✓ PDF is valid!")
        print(f"  Total pages: {num_pages}")
        
        # Get metadata
        metadata = doc.metadata
        if metadata:
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Author: {metadata.get('author', 'N/A')}")
        
        # Extract text from first page to confirm readability
        first_page = doc[0]
        first_page_text = first_page.get_text()
        
        if first_page_text.strip():
            print(f"  First page text length: {len(first_page_text)} characters")
            print()
            print("  First 200 characters of first page:")
            print("  " + "-" * 66)
            print("  " + first_page_text[:200].replace("\n", "\n  "))
            print("  " + "-" * 66)
        else:
            print("  Warning: First page appears to have no text")
        
        doc.close()
        print()
        print("=" * 70)
        print("SUCCESS: Google PDF is ready to use!")
        print("=" * 70)
        
    else:
        print("✗ Error: PDF has 0 pages")
        doc.close()
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
