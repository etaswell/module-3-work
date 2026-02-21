"""
Complete PDF extraction pipeline for sustainability report data
"""
import os
import time
import fitz  # PyMuPDF
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sustainability_schema import SustainabilityReport

# Initialize OpenAI client
client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
MODEL = os.environ.get("OPENAI_MODEL", "qwen3")

# Keywords for scoring chunks
DATA_KEYWORDS = [
    "emissions", "Scope 1", "Scope 2", "Scope 3", "renewable",
    "target", "GHG", "tCO2", "MWh", "percent", "carbon neutral", "net zero"
]

def extract_pdf_text(pdf_path):
    """Extract text from all pages of a PDF."""
    print(f"Loading PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    num_pages = len(doc)
    full_text = ""
    for page_num in range(num_pages):
        page = doc[page_num]
        text = page.get_text()
        full_text += text
    
    doc.close()
    print(f"  Extracted {len(full_text):,} characters from {num_pages} pages")
    return full_text

def chunk_text(text, chunk_size=4000, chunk_overlap=200):
    """Split text into overlapping chunks."""
    print(f"Chunking text (size={chunk_size}, overlap={chunk_overlap})...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_text(text)
    print(f"  Created {len(chunks)} chunks")
    return chunks

def score_chunk(chunk, keywords):
    """Score a chunk by counting keyword occurrences."""
    chunk_lower = chunk.lower()
    score = 0
    for keyword in keywords:
        count = chunk_lower.count(keyword.lower())
        score += count
    return score

def select_top_chunks(chunks, keywords, top_n=10):
    """Score all chunks and return the top N highest-scoring ones."""
    print(f"Scoring chunks and selecting top {top_n}...")
    
    # Score each chunk
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        score = score_chunk(chunk, keywords)
        chunk_scores.append({
            'index': i,
            'score': score,
            'chunk': chunk
        })
    
    # Sort by score (descending) and take top N
    chunk_scores.sort(key=lambda x: x['score'], reverse=True)
    top_chunks = chunk_scores[:top_n]
    
    print(f"  Top chunk scores: {[c['score'] for c in top_chunks[:5]]}...")
    
    return [c['chunk'] for c in top_chunks]

def extract_from_chunk(chunk, company_name):
    """Send a chunk to the AI and extract structured data."""
    try:
        # Create the extraction prompt
        prompt = f"""Extract sustainability and environmental data from the following text excerpt from {company_name}'s report.

Extract all available information according to the schema. If a field is not mentioned or cannot be determined from this text, leave it as null.

Text excerpt:
{chunk}
"""
        
        # Call API with JSON mode and thinking disabled
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. Extract sustainability metrics from corporate reports accurately. Return only the requested structured data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            extra_body={"chat_template_kwargs": {"thinking": False}},
            temperature=0.0,
            timeout=120.0,  # 120 second timeout
        )
        
        # Parse response
        result_json = response.choices[0].message.content
        
        # Validate with Pydantic schema
        # Add company_name if not present
        import json
        result_dict = json.loads(result_json)
        if "company_name" not in result_dict or not result_dict["company_name"]:
            result_dict["company_name"] = company_name
        
        result = SustainabilityReport(**result_dict)
        return result
        
    except KeyboardInterrupt:
        print(f"\n    User interrupted extraction")
        raise  # Re-raise KeyboardInterrupt so it can be caught at higher level
    except Exception as e:
        print(f"✗ (error: {str(e)[:50]})")
        return None

def merge_results(results):
    """Merge multiple extraction results. First non-null value wins for each field."""
    if not results:
        return None
    
    # Start with the first result
    merged = results[0].model_dump()
    
    # For each subsequent result, fill in missing values
    for result in results[1:]:
        result_dict = result.model_dump()
        for field, value in result_dict.items():
            # If current field is null/None and new value is not, use the new value
            if merged[field] is None and value is not None:
                merged[field] = value
    
    return SustainabilityReport(**merged)

def extract_sustainability_data(pdf_path, company_name=None, top_chunks=5):
    """
    Complete extraction pipeline for sustainability report data.
    
    Args:
        pdf_path: Path to the PDF file
        company_name: Name of the company (inferred from filename if not provided)
        top_chunks: Number of top-scoring chunks to process (default: 5)
    
    Returns:
        SustainabilityReport object with extracted data
    """
    print("=" * 70)
    print(f"EXTRACTING SUSTAINABILITY DATA")
    print("=" * 70)
    print()
    
    # Infer company name from filename if not provided
    if company_name is None:
        filename = os.path.basename(pdf_path)
        if "google" in filename.lower():
            company_name = "Google"
        elif "apple" in filename.lower():
            company_name = "Apple"
        elif "amazon" in filename.lower():
            company_name = "Amazon"
        elif "bp" in filename.lower():
            company_name = "BP"
        else:
            company_name = "Unknown Company"
    
    print(f"Company: {company_name}")
    print()
    
    # Step 1: Extract text from PDF
    full_text = extract_pdf_text(pdf_path)
    print()
    
    # Step 2: Chunk the text
    chunks = chunk_text(full_text)
    print()
    
    # Step 3: Score and select top chunks
    selected_chunks = select_top_chunks(chunks, DATA_KEYWORDS, top_n=top_chunks)
    print()
    
    # Step 4: Extract data from each chunk
    print(f"Extracting data from {len(selected_chunks)} chunks...")
    results = []
    
    try:
        for i, chunk in enumerate(selected_chunks, 1):
            print(f"  Processing chunk {i}/{len(selected_chunks)}...", end=" ")
            
            result = extract_from_chunk(chunk, company_name)
            
            if result:
                print("✓")
                results.append(result)
            elif result is None:
                # Error message already printed in extract_from_chunk
                pass
            
            # Rate limiting
            if i < len(selected_chunks):
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user.")
        print(f"Processed {len(results)}/{len(selected_chunks)} chunks before interruption.")
    
    print()
    print(f"Successfully extracted data from {len(results)}/{len(selected_chunks)} chunks")
    print()
    
    # Step 5: Merge results
    if not results:
        print("✗ No data extracted")
        return None
    
    print("Merging results (first non-null value wins)...")
    final_result = merge_results(results)
    print("✓ Merge complete")
    print()
    
    return final_result


if __name__ == "__main__":
    # Test with Google report
    pdf_path = "data/corporate-sustainability/google-env-2024.pdf"
    
    result = extract_sustainability_data(pdf_path)
    
    if result:
        print("=" * 70)
        print("EXTRACTION RESULTS")
        print("=" * 70)
        print()
        
        # Display results in a readable format
        result_dict = result.model_dump()
        
        # Group fields by category
        categories = {
            "Company Information": ["company_name", "reporting_year", "report_title"],
            "Emissions Data": [
                "scope_1_emissions", "scope_2_emissions_market_based", 
                "scope_2_emissions_location_based", "scope_3_emissions",
                "total_emissions", "emissions_units"
            ],
            "Energy Data": [
                "total_energy_consumption", "energy_consumption_units",
                "renewable_energy_percentage", "renewable_energy_absolute"
            ],
            "Climate Targets": [
                "target_description", "target_year", "baseline_year",
                "scope_coverage", "interim_target"
            ],
            "Water Data": [
                "total_water_withdrawal", "water_consumption", "water_units"
            ],
            "Additional Context": ["notes"]
        }
        
        for category, fields in categories.items():
            print(f"{category}:")
            print("-" * 70)
            has_data = False
            for field in fields:
                value = result_dict.get(field)
                if value is not None:
                    has_data = True
                    # Format large numbers with commas
                    if isinstance(value, (int, float)) and value > 1000:
                        print(f"  {field}: {value:,.2f}")
                    else:
                        print(f"  {field}: {value}")
            if not has_data:
                print("  (no data extracted)")
            print()
        
        # Also save as JSON
        print("=" * 70)
        print("JSON OUTPUT")
        print("=" * 70)
        print()
        print(result.model_dump_json(indent=2))
