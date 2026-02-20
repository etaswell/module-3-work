"""
Part 4: Compare Across Models
Test extraction with multiple models to compare results
"""
from openai import OpenAI
import os
import json

print("=" * 70)
print("Part 4: Compare Across Models")
print("=" * 70)

# Configure the client
client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "https://ellm.nrp-nautilus.io/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# A more ambiguous passage to test model differences
ambiguous_text = """
Google has set ambitious sustainability goals. The company aims to run on 
24/7 carbon-free energy on every grid where it operates by 2030. Google 
achieved carbon neutrality in 2007 and has been purchasing enough renewable 
energy to match 100% of its annual electricity consumption since 2017. 
However, the company's total energy consumption has grown significantly — 
its data centers used approximately 25.3 TWh of electricity in 2023, 
a 17% increase over the previous year. Google has also committed to 
achieving net-zero emissions across all of its operations and value chain 
by 2030, covering Scopes 1, 2, and 3.
"""

print("\nSample Text (Google Sustainability Goals):")
print("-" * 70)
print(ambiguous_text.strip())
print()

# Try different models to compare extraction results
# Available models at our endpoint: qwen3, glm-4.7, gpt-oss, gemma3, kimi
models_to_test = ["qwen3", "glm-4.7"]

print("\n" + "=" * 70)
print(f"Testing {len(models_to_test)} models...")
print("=" * 70)

results = {}

for model_name in models_to_test:
    print(f"\n{'=' * 70}")
    print(f"Model: {model_name}")
    print(f"{'=' * 70}")
    
    try:
        # Disable "thinking" mode for structured extraction (avoids content=None)
        # Different models use different param names:
        if model_name == "glm-4.7":
            thinking_kwargs = {"enable_thinking": False}
        else:
            thinking_kwargs = {"thinking": False}
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Extract climate commitment details as JSON. Fields: company_name, target_year, target_description, baseline_year, scope_coverage, interim_target"
                },
                {"role": "user", "content": ambiguous_text}
            ],
            response_format={"type": "json_object"},
            extra_body={"chat_template_kwargs": thinking_kwargs},
        )
        
        content = response.choices[0].message.content
        if content is None:
            print("  ⚠️  Model returned no content")
            results[model_name] = {"error": "No content returned"}
            continue
        
        result = json.loads(content)
        results[model_name] = result
        
        print("\nExtracted:")
        print(json.dumps(result, indent=2))
        
        print(f"\n✓ Successfully extracted with {model_name}")
        
    except Exception as e:
        print(f"✗ Error with {model_name}: {e}")
        results[model_name] = {"error": str(e)}

# Save comparison results
output = {
    "source": "Part 4 - Google Model Comparison",
    "ambiguous_text": ambiguous_text.strip(),
    "models_tested": models_to_test,
    "results": results
}

with open("part4_model_comparison.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print("Comparison Summary")
print("=" * 70)

# Compare key fields
if len(results) > 1:
    print("\nField Comparison:")
    print("-" * 70)
    
    fields = ["company_name", "target_year", "target_description", "scope_coverage"]
    
    for field in fields:
        print(f"\n{field}:")
        for model, data in results.items():
            if "error" not in data:
                value = data.get(field, "N/A")
                print(f"  {model:12} -> {value}")
    
    print("\n" + "-" * 70)
    print("Note: Different models may interpret ambiguous text differently")
    print("This demonstrates the importance of model selection and validation")

print("\n" + "=" * 70)
print("✅ Part 4 Complete!")
print("=" * 70)
print(f"Tested {len(models_to_test)} models on ambiguous text")
print("Result saved to: part4_model_comparison.json")
print("=" * 70)
