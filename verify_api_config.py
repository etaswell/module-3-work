"""Verify JSON mode and disable-thinking are properly configured"""
import re

# Read the notebook file
with open('notebooks/session8-llm-apis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into code cells (marked by # %%)
cells = content.split('# %%')

print("=" * 70)
print("API Configuration Verification")
print("=" * 70)

# Find all API calls
api_calls = []
current_section = ""

for i, cell in enumerate(cells):
    # Track which section we're in
    if '# Part' in cell or '# ## Part' in cell:
        section_match = re.search(r'Part \d+[:\-]?\s*(.+)', cell)
        if section_match:
            current_section = f"Part {i}: {section_match.group(1).strip()[:50]}"
    
    # Find API calls
    if 'client.chat.completions.create' in cell:
        # Check for response_format
        has_json_mode = 'response_format' in cell and '"type": "json_object"' in cell
        
        # Check for thinking disabled
        has_thinking_disabled = (
            'extra_body' in cell and 
            ('{"thinking": False}' in cell or '{"enable_thinking": False}' in cell or 'thinking_kwargs' in cell)
        )
        
        # Determine if this call needs JSON mode (structured extraction)
        needs_json = any(keyword in cell.lower() for keyword in [
            'extract', 'json', 'schema', 'structured', 'pydantic'
        ])
        
        api_calls.append({
            'section': current_section or f"Cell {i}",
            'has_json_mode': has_json_mode,
            'has_thinking_disabled': has_thinking_disabled,
            'needs_json': needs_json,
            'cell': cell
        })

# Print results
for idx, call in enumerate(api_calls, 1):
    print(f"\n{'─' * 70}")
    print(f"API Call #{idx}: {call['section']}")
    print(f"{'─' * 70}")
    
    # Determine if JSON mode is needed
    if call['needs_json']:
        print(f"Type: Structured Extraction (requires JSON mode + thinking disabled)")
        json_status = "✓" if call['has_json_mode'] else "✗"
        thinking_status = "✓" if call['has_thinking_disabled'] else "✗"
        print(f"  {json_status} JSON mode: {'ENABLED' if call['has_json_mode'] else 'MISSING'}")
        print(f"  {thinking_status} Disable thinking: {'ENABLED' if call['has_thinking_disabled'] else 'MISSING'}")
        
        if not call['has_json_mode'] or not call['has_thinking_disabled']:
            print("  ⚠️  WARNING: Configuration incomplete for structured extraction!")
    else:
        print(f"Type: Simple Chat (JSON mode not required)")
        if call['has_json_mode']:
            print(f"  ℹ️  JSON mode: ENABLED (optional for this call)")
        if call['has_thinking_disabled']:
            print(f"  ℹ️  Disable thinking: ENABLED (optional for this call)")

# Summary
print(f"\n{'=' * 70}")
print("Summary")
print(f"{'=' * 70}")

structured_calls = [c for c in api_calls if c['needs_json']]
properly_configured = [c for c in structured_calls if c['has_json_mode'] and c['has_thinking_disabled']]

print(f"Total API calls found: {len(api_calls)}")
print(f"Structured extraction calls: {len(structured_calls)}")
print(f"Properly configured: {len(properly_configured)}/{len(structured_calls)}")

if len(properly_configured) == len(structured_calls) and len(structured_calls) > 0:
    print("\n✅ ALL structured extraction calls are properly configured!")
    print("   • JSON mode enabled: response_format={'type': 'json_object'}")
    print("   • Thinking disabled: extra_body={'chat_template_kwargs': {'thinking': False}}")
else:
    print("\n⚠️  Some calls may need configuration updates")

print(f"{'=' * 70}")
