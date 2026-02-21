"""
Process all four sustainability reports and create comparison table
"""
import os
import pandas as pd
from extract_report import extract_sustainability_data

# Set up environment variables
os.environ["OPENAI_BASE_URL"] = "https://ellm.nrp-nautilus.io/v1"
os.environ["OPENAI_API_KEY"] = "KK6sZ0tDaA0CS2uOUbSbBYD1L5uf0Arv"
os.environ["OPENAI_MODEL"] = "qwen3"

print("=" * 70)
print("MULTI-COMPANY SUSTAINABILITY DATA EXTRACTION")
print("=" * 70)
print()

# Define the four reports
reports = [
    {
        "path": "data/corporate-sustainability/google-env-2024.pdf",
        "company": "Google"
    },
    {
        "path": "data/corporate-sustainability/apple-env-2024.pdf",
        "company": "Apple"
    },
    {
        "path": "data/corporate-sustainability/amazon-sustainability-2023.pdf",
        "company": "Amazon"
    },
    {
        "path": "data/corporate-sustainability/bp-sustainability-2023.pdf",
        "company": "BP"
    }
]

# Extract data from each report
results = []

for i, report in enumerate(reports, 1):
    print(f"\n{'=' * 70}")
    print(f"PROCESSING REPORT {i}/4: {report['company']}")
    print(f"{'=' * 70}\n")
    
    try:
        result = extract_sustainability_data(
            pdf_path=report["path"],
            company_name=report["company"],
            top_chunks=5  # Process top 5 chunks for each company
        )
        
        if result:
            results.append(result.model_dump())
            print(f"\n✓ {report['company']} extraction complete")
        else:
            print(f"\n✗ {report['company']} extraction failed - no data returned")
            # Add empty result to maintain table structure
            results.append({"company_name": report["company"]})
    
    except Exception as e:
        print(f"\n✗ {report['company']} extraction failed: {e}")
        # Add empty result to maintain table structure
        results.append({"company_name": report["company"]})

print("\n" + "=" * 70)
print("ALL EXTRACTIONS COMPLETE")
print("=" * 70)
print()

# Create DataFrame
df = pd.DataFrame(results)

# Reorder columns for better readability
column_order = [
    'company_name',
    'reporting_year',
    'scope_1_emissions',
    'scope_2_emissions_market_based',
    'scope_2_emissions_location_based',
    'scope_3_emissions',
    'total_emissions',
    'emissions_units',
    'total_energy_consumption',
    'energy_consumption_units',
    'renewable_energy_percentage',
    'renewable_energy_absolute',
    'target_description',
    'target_year',
    'baseline_year',
    'scope_coverage',
    'interim_target',
    'total_water_withdrawal',
    'water_consumption',
    'water_units',
    'report_title',
    'notes'
]

# Only include columns that exist in the dataframe
column_order = [col for col in column_order if col in df.columns]
df = df[column_order]

print("=" * 70)
print("COMPARISON TABLE - KEY METRICS")
print("=" * 70)
print()

# Display key emissions metrics
key_columns = ['company_name', 'scope_1_emissions', 'scope_2_emissions_market_based', 
               'scope_3_emissions', 'total_emissions', 'reporting_year']
key_df = df[[col for col in key_columns if col in df.columns]]

print("EMISSIONS DATA:")
print("-" * 70)
print(key_df.to_string(index=False))
print()

# Display energy and targets
if 'renewable_energy_percentage' in df.columns or 'target_year' in df.columns:
    print("ENERGY & TARGETS:")
    print("-" * 70)
    energy_columns = ['company_name', 'renewable_energy_percentage', 'target_year', 'baseline_year']
    energy_df = df[[col for col in energy_columns if col in df.columns]]
    print(energy_df.to_string(index=False))
    print()

print("=" * 70)
print("FULL DATA TABLE")
print("=" * 70)
print()

# Print full table (may be wide)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

print(df.to_string(index=False))
print()

# Summary statistics
print("=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print()

print(f"Total companies processed: {len(results)}")
print(f"Companies with emissions data: {df['scope_1_emissions'].notna().sum()}")
print(f"Companies with Scope 3 data: {df['scope_3_emissions'].notna().sum()}")

if 'renewable_energy_percentage' in df.columns:
    print(f"Companies with renewable energy data: {df['renewable_energy_percentage'].notna().sum()}")

if 'target_year' in df.columns:
    print(f"Companies with climate targets: {df['target_year'].notna().sum()}")

print()

# Interesting insights
print("=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print()

if 'scope_3_emissions' in df.columns and df['scope_3_emissions'].notna().any():
    max_scope3_company = df.loc[df['scope_3_emissions'].idxmax(), 'company_name']
    max_scope3_value = df['scope_3_emissions'].max()
    print(f"Highest Scope 3 emissions: {max_scope3_company} ({max_scope3_value:,.0f} tCO2e)")

if 'total_emissions' in df.columns and df['total_emissions'].notna().any():
    max_total_company = df.loc[df['total_emissions'].idxmax(), 'company_name']
    max_total_value = df['total_emissions'].max()
    print(f"Highest total emissions: {max_total_company} ({max_total_value:,.0f} tCO2e)")

if 'target_year' in df.columns and df['target_year'].notna().any():
    earliest_target = df['target_year'].min()
    earliest_company = df.loc[df['target_year'].idxmin(), 'company_name']
    print(f"Most ambitious target year: {earliest_company} ({int(earliest_target)})")

if 'renewable_energy_percentage' in df.columns and df['renewable_energy_percentage'].notna().any():
    max_renewable = df['renewable_energy_percentage'].max()
    max_renewable_company = df.loc[df['renewable_energy_percentage'].idxmax(), 'company_name']
    print(f"Highest renewable energy: {max_renewable_company} ({max_renewable:.0f}%)")

print()

# Save results
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

# Save as CSV
csv_path = "sustainability_comparison.csv"
df.to_csv(csv_path, index=False)
print(f"✓ Saved CSV: {csv_path}")

# Save as JSON
json_path = "sustainability_comparison.json"
df.to_json(json_path, orient='records', indent=2)
print(f"✓ Saved JSON: {json_path}")

print()
print("=" * 70)
print("TASK 6 COMPLETE")
print("=" * 70)
