"""
Part 3: Extract from a Text Passage
Extract structured climate commitment data from Apple's text
"""
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import os
import json

print("=" * 70)
print("Part 3: Extract from a Text Passage")
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

# A real passage about corporate climate commitments
sample_text = """
Apple has committed to becoming carbon neutral across its entire supply chain 
and product life cycle by 2030. This includes Scope 1, Scope 2, and Scope 3 
emissions. Using a 2015 baseline, Apple has already reduced its comprehensive 
carbon footprint by more than 55 percent since 2015. As an interim milestone, 
Apple achieved carbon neutrality for its global corporate operations in 2020. 
The company's approach prioritizes direct emissions reductions of 75 percent 
from 2015 levels, with the remaining 25 percent addressed through high-quality 
carbon removal projects.
"""

print("\n" + "-" * 70)
print("Sample Text (Apple Climate Commitment):")
print("-" * 70)
print(sample_text.strip())
print()

print("-" * 70)
print("Extracting structured data...")
print("-" * 70)

# Use the LLM to extract structured data
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a data extraction assistant. Extract the requested fields from the provided text. Return valid JSON matching the schema exactly."
        },
        {
            "role": "user", 
            "content": f"Extract the climate commitment details from this text:\n\n{sample_text}\n\nReturn JSON with these fields: company_name, target_year, target_description, baseline_year, scope_coverage, interim_target"
        }
    ],
    response_format={"type": "json_object"},
    # Disable thinking for structured extraction — avoids content=None issue
    # qwen3 uses {"thinking": False}, glm-4.7 uses {"enable_thinking": False}
    extra_body={"chat_template_kwargs": {"thinking": False}},
)

print("\n✓ API Response Received")

extracted = json.loads(response.choices[0].message.content)
print("\nExtracted data (raw JSON):")
print(json.dumps(extracted, indent=2))

# Validate against our schema
print("\n" + "-" * 70)
print("Validating with Pydantic schema...")
print("-" * 70)

commitment = ClimateCommitment(**extracted)

print(f"\n✓ Valid! Schema validation passed")
print(f"\nSummary:")
print(f"  Company: {commitment.company_name}")
print(f"  Commitment: {commitment.target_description}")
print(f"  Target Year: {commitment.target_year}")
print(f"  Baseline Year: {commitment.baseline_year}")
print(f"  Scope Coverage: {commitment.scope_coverage}")
print(f"  Interim Target: {commitment.interim_target}")

# Save result
output = {
    "source": "Part 3 - Apple Climate Commitment",
    "model": MODEL,
    "extraction": commitment.model_dump()
}

with open("part3_extraction_result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print("✅ Part 3 Complete!")
print("=" * 70)
print("Key Findings:")
print(f"  • {commitment.company_name} → {commitment.target_description} by {commitment.target_year}")
print(f"  • Baseline: {commitment.baseline_year}")
print(f"  • Covers: {commitment.scope_coverage}")
print("\nResult saved to: part3_extraction_result.json")
print("=" * 70)
