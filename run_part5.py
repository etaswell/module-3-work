"""
Part 5: Batch Extraction
Extract commitments from multiple companies and create a comparison table
"""
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import os
import json
import pandas as pd

print("=" * 70)
print("Part 5: Batch Extraction")
print("=" * 70)

# Define the ClimateCommitment schema
class ClimateCommitment(BaseModel):
    """Structured representation of a corporate climate commitment."""
    model_config = {"coerce_numbers_to_str": False, "strict": False}

    company_name: str = Field(description="Name of the company")
    target_year: Optional[int] = Field(None, description="Target year for the commitment (e.g., 2030, 2050)")
    target_description: str = Field(description="What the company committed to (e.g., 'net zero emissions')")
    baseline_year: Optional[int] = Field(None, description="Baseline year for measuring progress")
    scope_coverage: Optional[str] = Field(None, description="Which emission scopes are covered (e.g., 'Scope 1 and 2', 'Scope 1, 2, and 3')")
    interim_target: Optional[str] = Field(None, description="Any intermediate target before the main goal")

# Configure the client
client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "https://ellm.nrp-nautilus.io/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

MODEL = os.environ.get("OPENAI_MODEL", "qwen3")

print(f"\nConfiguration:")
print(f"  Model: {MODEL}")
print(f"  API Base: {os.environ.get('OPENAI_BASE_URL', 'default')}")

# Multiple companies' commitment texts
company_texts = {
    "Amazon": """
    Amazon's Climate Pledge commits the company to reaching net-zero carbon 
    emissions by 2040 — 10 years ahead of the Paris Agreement. The pledge 
    covers all three emission scopes. As of 2023, Amazon has reduced the 
    carbon intensity of its shipments by 11.5% compared to a 2019 baseline. 
    The company is the world's largest corporate purchaser of renewable energy, 
    with 500+ solar and wind projects globally.
    """,
    
    "BP": """
    BP aims to become a net zero company by 2050 or sooner, and to help the 
    world get to net zero. This ambition covers Scope 1, 2, and 3 emissions. 
    BP's interim target is to reduce Scope 1 and 2 operational emissions by 
    50% by 2030, compared to a 2019 baseline. The company also aims to reduce 
    the carbon intensity of the products it sells by 15-20% by 2030. BP has 
    faced criticism for potentially weakening its climate targets in 2023.
    """,
    
    "Apple": """
    Apple has committed to becoming carbon neutral across its entire supply chain 
    and product life cycle by 2030. This includes Scope 1, Scope 2, and Scope 3 
    emissions. Using a 2015 baseline, Apple has already reduced its comprehensive 
    carbon footprint by more than 55 percent since 2015. As an interim milestone, 
    Apple achieved carbon neutrality for its global corporate operations in 2020.
    """,
}

print(f"\n{'=' * 70}")
print(f"Processing {len(company_texts)} companies...")
print(f"{'=' * 70}\n")

results = []

for company, text in company_texts.items():
    print(f"Processing {company}...", end=" ")
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Extract climate commitment as JSON. Fields: company_name, target_year, target_description, baseline_year, scope_coverage, interim_target. Use null for missing fields."
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            extra_body={"chat_template_kwargs": {"thinking": False}},
        )
        
        content = response.choices[0].message.content
        if content is None:
            print(f"⚠️ Model returned no content, skipping")
            continue
        
        extracted = json.loads(content)
        
        # Validate with Pydantic
        commitment = ClimateCommitment(**extracted)
        results.append(commitment.model_dump())
        
        print(f"✓ {commitment.target_year}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

print()

# Create a comparison table
print("=" * 70)
print("Climate Commitments Comparison Table")
print("=" * 70)
print()

if results:
    df = pd.DataFrame(results)
    
    # Display table
    print(df.to_string(index=False))
    
    # Save to CSV
    csv_file = "part5_batch_extraction.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    # Save to JSON
    json_file = "part5_batch_extraction.json"
    output = {
        "source": "Part 5 - Batch Extraction",
        "model": MODEL,
        "total_companies": len(company_texts),
        "successful_extractions": len(results),
        "commitments": results
    }
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Statistics
    print("\n" + "=" * 70)
    print("Statistics")
    print("=" * 70)
    print(f"Companies processed: {len(results)}/{len(company_texts)}")
    print(f"With target years: {df['target_year'].notna().sum()}")
    print(f"With baseline years: {df['baseline_year'].notna().sum()}")
    print(f"With scope coverage: {df['scope_coverage'].notna().sum()}")
    print(f"With interim targets: {df['interim_target'].notna().sum()}")
    
    if df['target_year'].notna().any():
        print(f"\nTarget year range: {df['target_year'].min():.0f} - {df['target_year'].max():.0f}")
        print(f"Average target year: {df['target_year'].mean():.0f}")
    
    print("\n" + "=" * 70)
    print("✅ Part 5 Complete!")
    print("=" * 70)
    print("Batch extraction demonstrates scalability:")
    print("  • Same code works for 3 companies or 3,000")
    print("  • Structured output enables easy analysis")
    print("  • Results ready for further processing")
    print()
    print("Output files:")
    print(f"  • {json_file} (structured JSON)")
    print(f"  • {csv_file} (CSV table)")
    print("=" * 70)

else:
    print("⚠️ No results to display")
