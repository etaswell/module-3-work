"""Test JSON mode and disable-thinking with live API call"""
from openai import OpenAI
import os
import json

print("=" * 70)
print("Testing JSON Mode and Disable-Thinking Configuration")
print("=" * 70)

# Configure the client
client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "https://ellm.nrp-nautilus.io/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

MODEL = os.environ.get("OPENAI_MODEL", "qwen3")

print(f"\nEnvironment Configuration:")
print(f"  Base URL: {os.environ.get('OPENAI_BASE_URL', 'NOT SET')}")
print(f"  API Key: {os.environ.get('OPENAI_API_KEY', 'NOT SET')[:8]}..." if os.environ.get('OPENAI_API_KEY') else "  API Key: NOT SET")
print(f"  Model: {MODEL}")

# Test sample text
test_text = """
Microsoft has announced its commitment to become carbon negative by 2030, 
and by 2050, to remove all the carbon the company has emitted since it was 
founded in 1975. This includes all Scope 1, 2, and 3 emissions. Starting in 
2021, Microsoft has an internal carbon tax to drive accountability across 
its divisions.
"""

print("\n" + "─" * 70)
print("Test: Structured Extraction with JSON Mode + Disable-Thinking")
print("─" * 70)

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Extract climate commitment details as JSON. Fields: company_name, target_year, target_description, baseline_year, scope_coverage, interim_target. Use null for missing fields."
            },
            {"role": "user", "content": test_text}
        ],
        response_format={"type": "json_object"},  # ✓ JSON mode
        extra_body={"chat_template_kwargs": {"thinking": False}},  # ✓ Disable thinking
    )
    
    print("✓ API call successful")
    print(f"✓ Response received (length: {len(response.choices[0].message.content)} chars)")
    
    # Parse and validate JSON
    content = response.choices[0].message.content
    if content is None:
        print("✗ ERROR: Response content is None")
        print("  This can happen if thinking mode is not properly disabled")
    else:
        parsed_json = json.loads(content)
        print("✓ Valid JSON response")
        print("\nExtracted Data:")
        print(json.dumps(parsed_json, indent=2))
        
        # Verify expected fields
        print("\n" + "─" * 70)
        print("Field Verification:")
        print("─" * 70)
        expected_fields = ['company_name', 'target_year', 'target_description', 
                          'baseline_year', 'scope_coverage', 'interim_target']
        
        for field in expected_fields:
            if field in parsed_json:
                value = parsed_json[field]
                status = "✓" if value is not None else "○"
                print(f"  {status} {field}: {value}")
            else:
                print(f"  ✗ {field}: MISSING")
        
        print("\n" + "=" * 70)
        print("✅ Configuration Test PASSED")
        print("=" * 70)
        print("Both settings are working correctly:")
        print("  • JSON mode: Returned valid JSON structure")
        print("  • Disable-thinking: Response content is not None")
        
except Exception as e:
    print(f"✗ ERROR: {e}")
    print("\nThis may indicate:")
    print("  • Environment variables not set correctly")
    print("  • API endpoint not reachable")
    print("  • Model not available")
