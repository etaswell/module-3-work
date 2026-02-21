"""
Retry extraction for Amazon and BP with increased chunks and retries
"""
import os
import pandas as pd
from extract_report import extract_sustainability_data

# Set up environment variables
os.environ["OPENAI_BASE_URL"] = "https://ellm.nrp-nautilus.io/v1"
os.environ["OPENAI_API_KEY"] = "KK6sZ0tDaA0CS2uOUbSbBYD1L5uf0Arv"
os.environ["OPENAI_MODEL"] = "qwen3"

print("=" * 70)
print("RETRY EXTRACTION: Amazon")
print("=" * 70)
print()
print("Note: BP PDF not found in data directory, skipping")
print()

# Define the report to retry (Amazon only - BP file doesn't exist)
reports = [
    {
        "path": "data/corporate-sustainability/amazon-sustainability-2022.pdf",
        "company": "Amazon"
    }
]

# Extract data from each report with more chunks
results = []

for i, report in enumerate(reports, 1):
    print(f"\n{'=' * 70}")
    print(f"PROCESSING: {report['company']}")
    print(f"{'=' * 70}\n")
    
    try:
        # Try with 8 chunks instead of 5 for better coverage
        result = extract_sustainability_data(
            pdf_path=report["path"],
            company_name=report["company"],
            top_chunks=8  # Process more chunks
        )
        
        if result:
            results.append(result.model_dump())
            print(f"\n✓ {report['company']} extraction complete")
            
            # Show what was extracted
            print(f"\nExtracted fields:")
            for key, value in result.model_dump().items():
                if value is not None:
                    print(f"  • {key}: {value}")
        else:
            print(f"\n✗ {report['company']} extraction failed - no data returned")
            results.append({"company_name": report["company"]})
    
    except Exception as e:
        print(f"\n✗ {report['company']} extraction failed: {e}")
        results.append({"company_name": report["company"]})

print("\n" + "=" * 70)
print("RETRY COMPLETE")
print("=" * 70)
print()

# Create DataFrame with new results
new_df = pd.DataFrame(results)

# Load existing results
existing_df = pd.read_csv("sustainability_comparison.csv")

# Update Amazon row (BP file doesn't exist)
for company in ["Amazon"]:
    if company in new_df['company_name'].values:
        # Get the new data for this company
        new_data = new_df[new_df['company_name'] == company].iloc[0].to_dict()
        # Update the existing dataframe
        mask = existing_df['company_name'] == company
        for col in new_data.keys():
            if col in existing_df.columns:
                existing_df.loc[mask, col] = new_data[col]

# Save updated results
existing_df.to_csv("sustainability_comparison.csv", index=False)
existing_df.to_json("sustainability_comparison.json", orient='records', indent=2)

print("=" * 70)
print("UPDATED COMPARISON TABLE")
print("=" * 70)
print()

# Display key metrics
key_columns = ['company_name', 'scope_1_emissions', 'scope_2_emissions_market_based', 
               'scope_3_emissions', 'total_emissions']
display_df = existing_df[key_columns]

print("EMISSIONS DATA:")
print("-" * 70)
print(display_df.to_string(index=False))
print()

print("✓ Files updated: sustainability_comparison.csv and sustainability_comparison.json")
