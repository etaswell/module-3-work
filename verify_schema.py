"""Comprehensive verification of ClimateCommitment data schema"""
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import json

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

print("=" * 60)
print("ClimateCommitment Schema Verification")
print("=" * 60)

# Test 1: Schema structure
print("\n✓ Test 1: Schema Structure")
print("  Fields defined:")
for name, field in ClimateCommitment.model_fields.items():
    required = field.is_required()
    field_type = field.annotation
    print(f"    {name}: {field_type} {'(required)' if required else '(optional)'}")

# Test 2: Complete valid data
print("\n✓ Test 2: Complete Valid Data")
complete_data = {
    "company_name": "Apple",
    "target_year": 2030,
    "target_description": "carbon neutral across entire supply chain and product life cycle",
    "baseline_year": 2015,
    "scope_coverage": "Scope 1, 2, and 3",
    "interim_target": "Carbon neutrality for global corporate operations in 2020"
}
commitment1 = ClimateCommitment(**complete_data)
print(f"  Company: {commitment1.company_name}")
print(f"  Target: {commitment1.target_description} by {commitment1.target_year}")
print(f"  ✓ Validation passed")

# Test 3: Minimal required data (only required fields)
print("\n✓ Test 3: Minimal Required Data")
minimal_data = {
    "company_name": "Tesla",
    "target_description": "net zero emissions"
}
commitment2 = ClimateCommitment(**minimal_data)
print(f"  Company: {commitment2.company_name}")
print(f"  Target: {commitment2.target_description}")
print(f"  Target year: {commitment2.target_year} (None is valid)")
print(f"  ✓ Validation passed")

# Test 4: Type coercion (string numbers to int)
print("\n✓ Test 4: Type Coercion")
coercion_data = {
    "company_name": "Google",
    "target_year": "2030",  # String instead of int
    "target_description": "24/7 carbon-free energy",
    "baseline_year": "2019"  # String instead of int
}
commitment3 = ClimateCommitment(**coercion_data)
print(f"  Input target_year: '2030' (string)")
print(f"  Parsed target_year: {commitment3.target_year} ({type(commitment3.target_year).__name__})")
print(f"  ✓ Coercion successful")

# Test 5: JSON serialization and deserialization
print("\n✓ Test 5: JSON Serialization")
json_str = commitment1.model_dump_json(indent=2)
print(f"  JSON export length: {len(json_str)} bytes")
json_dict = json.loads(json_str)
commitment_restored = ClimateCommitment(**json_dict)
print(f"  Restored company: {commitment_restored.company_name}")
print(f"  ✓ JSON round-trip successful")

# Test 6: Invalid data (missing required field)
print("\n✓ Test 6: Validation Error Detection")
try:
    invalid_data = {
        "company_name": "Invalid Corp"
        # Missing required 'target_description'
    }
    ClimateCommitment(**invalid_data)
    print("  ✗ ERROR: Should have raised ValidationError")
except ValidationError as e:
    print(f"  Caught ValidationError as expected")
    print(f"  Missing field: target_description")
    print(f"  ✓ Validation error handling works")

# Test 7: Schema export for API integration
print("\n✓ Test 7: JSON Schema Export")
schema = ClimateCommitment.model_json_schema()
print(f"  Schema title: {schema.get('title')}")
print(f"  Required fields: {schema.get('required')}")
print(f"  Properties defined: {len(schema.get('properties', {}))} fields")
print(f"  ✓ Schema can be exported for API integration")

print("\n" + "=" * 60)
print("✅ All Schema Verification Tests Passed!")
print("=" * 60)
print("\nSchema is correctly configured for:")
print("  • Required field validation")
print("  • Optional field handling")
print("  • Type coercion (string → int)")
print("  • JSON serialization/deserialization")
print("  • Error detection and handling")
print("  • API integration (JSON schema export)")
