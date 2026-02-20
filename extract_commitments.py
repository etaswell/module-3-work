"""
Simple Climate Commitment Extraction - Saves to JSON and CSV
"""
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import os
import json
from datetime import datetime

# Define schema
class ClimateCommitment(BaseModel):
    """Structured representation of a corporate climate commitment."""
    model_config = {"coerce_numbers_to_str": False, "strict": False}
    
    company_name: str = Field(description="Name of the company")
    target_year: Optional[int] = Field(None, description="Target year for the commitment")
    target_description: str = Field(description="What the company committed to")
    baseline_year: Optional[int] = Field(None, description="Baseline year for measuring progress")
    scope_coverage: Optional[str] = Field(None, description="Which emission scopes are covered")
    interim_target: Optional[str] = Field(None, description="Any intermediate target")

# Configure client
client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "https://ellm.nrp-nautilus.io/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
MODEL = os.environ.get("OPENAI_MODEL", "qwen3")

print("=" * 70)
print("Climate Commitment Extraction Pipeline")
print("=" * 70)
print(f"Model: {MODEL}")
print(f"Timestamp: {datetime.now().isoformat()}")
print()

# Company texts
company_texts = {
    "Apple": "Apple has committed to becoming carbon neutral across its entire supply chain and product life cycle by 2030. This includes Scope 1, Scope 2, and Scope 3 emissions. Using a 2015 baseline, Apple has already reduced its comprehensive carbon footprint by more than 55 percent. As an interim milestone, Apple achieved carbon neutrality for its global corporate operations in 2020.",
    
    "Amazon": "Amazon's Climate Pledge commits the company to reaching net-zero carbon emissions by 2040 — 10 years ahead of the Paris Agreement. The pledge covers all three emission scopes. As of 2023, Amazon has reduced the carbon intensity of its shipments by 11.5% compared to a 2019 baseline.",
    
    "Microsoft": "Microsoft has announced its commitment to become carbon negative by 2030, and by 2050, to remove all the carbon the company has emitted since it was founded in 1975. This includes all Scope 1, 2, and 3 emissions.",
}

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
        
        if response.choices[0].message.content:
            extracted = json.loads(response.choices[0].message.content)
            commitment = ClimateCommitment(**extracted)
            results.append(commitment.model_dump())
            print(f"✓ ({commitment.target_year})")
        else:
            print("✗ (no content)")
    except Exception as e:
        print(f"✗ ({e})")

# Save JSON
json_file = f"climate_commitments_output.json"
output = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "total_processed": len(company_texts),
        "successful": len(results)
    },
    "commitments": results
}

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print()
print("=" * 70)
print(f"✅ Extraction complete!")
print(f"   • Processed: {len(results)}/{len(company_texts)} companies")
print(f"   • Output saved to: {json_file}")
print("=" * 70)
print()
print("Extracted Commitments:")
for r in results:
    print(f"  • {r['company_name']}: {r['target_description']} by {r['target_year']}")

# Also save as simple CSV format
csv_file = "climate_commitments_output.csv"
with open(csv_file, 'w', encoding='utf-8') as f:
    f.write("Company,Target Year,Target Description,Baseline Year,Scope Coverage,Interim Target\n")
    for r in results:
        f.write(f'"{r["company_name"]}",')
        f.write(f'{r["target_year"] if r["target_year"] else ""},')
        f.write(f'"{r["target_description"]}",')
        f.write(f'{r["baseline_year"] if r["baseline_year"] else ""},')
        f.write(f'"{r["scope_coverage"] if r["scope_coverage"] else ""}",')
        f.write(f'"{r["interim_target"] if r["interim_target"] else ""}"\n')

print(f"   • CSV saved to: {csv_file}")
print()
