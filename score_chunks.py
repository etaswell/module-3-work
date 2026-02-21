"""
Score PDF chunks by data-relevant keyword frequency
"""
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("=" * 70)
print("PDF Chunk Scoring by Data-Relevant Keywords")
print("=" * 70)
print()

# Keywords to search for
KEYWORDS = [
    "emissions",
    "Scope 1",
    "Scope 2", 
    "Scope 3",
    "renewable",
    "target",
    "GHG",
    "tCO2",
    "MWh",
    "percent",
    "carbon neutral",
    "net zero"
]

print("Keywords to search for:")
for kw in KEYWORDS:
    print(f"  • {kw}")
print()

# Load and extract text from PDF
pdf_path = "data/corporate-sustainability/google-env-2024.pdf"
doc = fitz.open(pdf_path)

print(f"PDF: {pdf_path}")
print(f"Total pages: {len(doc)}")
print()

# Extract text from each page and create page-to-text mapping
page_texts = []
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    page_texts.append(text)

# Get full text
full_text = "".join(page_texts)
doc.close()

print(f"Total characters extracted: {len(full_text):,}")
print()

# Split text into chunks
print("-" * 70)
print("Creating chunks...")
print("-" * 70)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_text(full_text)
print(f"✓ Created {len(chunks)} chunks")
print()

# Function to find which page(s) a chunk appears in
def find_chunk_pages(chunk_text, page_texts):
    """Find which pages contain this chunk text"""
    pages = []
    # Look for a substantial part of the chunk (first 500 chars)
    search_text = chunk_text[:500].strip()
    
    for page_num, page_text in enumerate(page_texts):
        if search_text in page_text:
            pages.append(page_num + 1)  # 1-indexed page numbers
    
    # If not found, try searching for unique phrases from the chunk
    if not pages:
        # Try with middle section
        search_text = chunk_text[len(chunk_text)//2:len(chunk_text)//2+500].strip()
        for page_num, page_text in enumerate(page_texts):
            if len(search_text) > 50 and search_text in page_text:
                pages.append(page_num + 1)
    
    return pages if pages else ["Unknown"]

# Score each chunk
print("-" * 70)
print("Scoring chunks...")
print("-" * 70)

chunk_scores = []

for i, chunk in enumerate(chunks):
    # Count keyword occurrences (case-insensitive)
    chunk_lower = chunk.lower()
    score = 0
    keyword_counts = {}
    
    for keyword in KEYWORDS:
        count = chunk_lower.count(keyword.lower())
        if count > 0:
            keyword_counts[keyword] = count
            score += count
    
    # Find pages for this chunk
    pages = find_chunk_pages(chunk, page_texts)
    
    chunk_scores.append({
        'chunk_id': i + 1,
        'score': score,
        'keyword_counts': keyword_counts,
        'pages': pages,
        'text': chunk,
        'length': len(chunk)
    })
    
    if (i + 1) % 10 == 0:
        print(f"  Processed {i + 1}/{len(chunks)} chunks...")

print(f"✓ Scoring complete")
print()

# Sort by score (descending)
chunk_scores.sort(key=lambda x: x['score'], reverse=True)

# Display top 5 chunks
print("=" * 70)
print("TOP 5 HIGHEST-SCORING CHUNKS")
print("=" * 70)
print()

for rank, chunk_data in enumerate(chunk_scores[:5], 1):
    print(f"RANK #{rank}")
    print(f"Chunk ID: {chunk_data['chunk_id']}/{len(chunks)}")
    print(f"Score: {chunk_data['score']} keyword matches")
    
    # Display pages
    pages = chunk_data['pages']
    if isinstance(pages, list) and len(pages) > 0:
        if len(pages) == 1:
            print(f"Page: {pages[0]}")
        else:
            print(f"Pages: {pages[0]}-{pages[-1]}")
    else:
        print(f"Pages: {pages}")
    
    print(f"Length: {chunk_data['length']} characters")
    print()
    
    # Show keyword breakdown
    print("Keyword matches:")
    for keyword, count in sorted(chunk_data['keyword_counts'].items(), 
                                  key=lambda x: x[1], reverse=True):
        print(f"  • {keyword}: {count}")
    print()
    
    # Show chunk preview (first 500 characters)
    preview = chunk_data['text'][:500].strip()
    print("Text preview:")
    print("-" * 70)
    print(preview)
    if len(chunk_data['text']) > 500:
        print("...")
    print("-" * 70)
    print()
    print()

# Summary statistics
print("=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print()
print(f"Total chunks analyzed: {len(chunks)}")
print(f"Chunks with keywords: {sum(1 for c in chunk_scores if c['score'] > 0)}")
print(f"Chunks without keywords: {sum(1 for c in chunk_scores if c['score'] == 0)}")
print()

# Overall keyword frequency
overall_keyword_counts = {}
for keyword in KEYWORDS:
    total = sum(c['keyword_counts'].get(keyword, 0) for c in chunk_scores)
    if total > 0:
        overall_keyword_counts[keyword] = total

print("Overall keyword frequency across all chunks:")
for keyword, count in sorted(overall_keyword_counts.items(), 
                              key=lambda x: x[1], reverse=True):
    print(f"  • {keyword}: {count} occurrences")
