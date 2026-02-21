"""
Extract text from PDF and split into chunks using LangChain
"""
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("=" * 70)
print("PDF Text Chunking with LangChain")
print("=" * 70)
print()

# Use Google PDF
pdf_paths = [
    "data/corporate-sustainability/google-env-2024.pdf",
]

doc = None
pdf_path = None

for path in pdf_paths:
    try:
        temp_doc = fitz.open(path)
        if len(temp_doc) > 0:
            doc = temp_doc
            pdf_path = path
            print(f"✓ Successfully opened: {path}")
            print(f"  Total pages: {len(doc)}")
            break
        else:
            print(f"✗ Skipping {path} (0 pages)")
            temp_doc.close()
    except Exception as e:
        print(f"✗ Error opening {path}: {e}")

if doc is None:
    print("\nError: Could not open any PDF file")
    exit(1)

print()
print("-" * 70)
print("Extracting text from all pages...")
print("-" * 70)

# Extract text from all pages
full_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    full_text += text
    if (page_num + 1) % 10 == 0:
        print(f"  Processed {page_num + 1}/{len(doc)} pages...")

doc.close()

print(f"✓ Extraction complete")
print(f"  Total characters: {len(full_text):,}")
print()

print("-" * 70)
print("Splitting text into chunks...")
print("-" * 70)

# Create text splitter with specified parameters
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

# Split the text into chunks
chunks = text_splitter.split_text(full_text)

print(f"✓ Text split complete")
print(f"  Number of chunks created: {len(chunks)}")
print(f"  Chunk size: 4,000 characters")
print(f"  Overlap: 200 characters")
print()

# Show statistics about chunk sizes
if chunks:
    chunk_lengths = [len(chunk) for chunk in chunks]
    print(f"  Chunk sizes:")
    print(f"    Min: {min(chunk_lengths):,} characters")
    print(f"    Max: {max(chunk_lengths):,} characters")
    print(f"    Average: {sum(chunk_lengths)//len(chunk_lengths):,} characters")

print()
print("=" * 70)
print("First Chunk")
print("=" * 70)
print()

if chunks:
    print(chunks[0])
    print()
    print("-" * 70)
    print(f"First chunk length: {len(chunks[0])} characters")
    print("-" * 70)
else:
    print("No chunks created")

# Save chunks to file for reference
output_file = "pdf_chunks.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"PDF: {pdf_path}\n")
    f.write(f"Total chunks: {len(chunks)}\n")
    f.write(f"=" * 70 + "\n\n")
    
    for i, chunk in enumerate(chunks, 1):
        f.write(f"CHUNK {i}/{len(chunks)}\n")
        f.write(f"Length: {len(chunk)} characters\n")
        f.write("-" * 70 + "\n")
        f.write(chunk)
        f.write("\n\n" + "=" * 70 + "\n\n")

print()
print(f"✓ All chunks saved to: {output_file}")
