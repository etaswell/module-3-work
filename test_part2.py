from pydantic import BaseModel, Field
from typing import Optional
import json

# Define what we want to extract
class ClimateCommitment(BaseModel):
    """Structured representation of a corporate climate commitment."""
    model_config = {"coerce_numbers_to_str": False, "strict": False}

    company_name: str = Field(description="Name of the company")
    target_year: Optional[int] = Field(None, description="Target year for the commitment (e.g., 2030, 2050)")
    target_description: str = Field(description="What the company committed to (e.g., 'net zero emissions')")
    baseline_year: Optional[int] = Field(None, description="Baseline year for measuring progress")
    scope_coverage: Optional[str] = Field(None, description="Which emission scopes are covered (e.g., 'Scope 1 and 2', 'Scope 1, 2, and 3')")
    interim_target: Optional[str] = Field(None, description="Any intermediate target before the main goal")

print("Schema defined! Fields:")
for name, field in ClimateCommitment.model_fields.items():
    print(f"  {name}: {field.annotation} — {field.description}")

# Validate with sample data
print("\nValidating sample JSON...")
sample_data = {
    "company_name": "Apple",
    "target_year": 2030,
    "target_description": "carbon neutral across entire supply chain and product life cycle",
    "baseline_year": 2015,
    "scope_coverage": "Scope 1, 2, and 3",
    "interim_target": "Carbon neutrality for global corporate operations in 2020"
}

commitment = ClimateCommitment(**sample_data)
print(f"\n✓ Valid! {commitment.company_name} → {commitment.target_description} by {commitment.target_year}")
print(f"\nJSON representation:")
print(json.dumps(commitment.model_dump(), indent=2))
print("\n✅ Part 2: Schema validation complete!")
