"""
Save extraction results to output directory in JSON and CSV formats
"""
import os
import shutil

print("=" * 70)
print("SAVING RESULTS TO OUTPUT DIRECTORY - TASK 8")
print("=" * 70)
print()

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"✓ Created directory: {output_dir}/")
else:
    print(f"✓ Directory exists: {output_dir}/")

print()

# Define source and destination files
files_to_save = [
    {
        "source": "sustainability_comparison.csv",
        "dest": os.path.join(output_dir, "sustainability_comparison.csv"),
        "type": "CSV"
    },
    {
        "source": "sustainability_comparison.json",
        "dest": os.path.join(output_dir, "sustainability_comparison.json"),
        "type": "JSON"
    }
]

# Copy files to output directory
print("Copying files to output/...")
print("-" * 70)

for file_info in files_to_save:
    try:
        shutil.copy2(file_info["source"], file_info["dest"])
        file_size = os.path.getsize(file_info["dest"])
        print(f"✓ {file_info['type']}: {file_info['dest']}")
        print(f"  Size: {file_size:,} bytes")
    except Exception as e:
        print(f"✗ Error copying {file_info['source']}: {e}")

print()
print("=" * 70)
print("FILE FORMATS")
print("=" * 70)
print()

print("CSV Format:")
print("-" * 70)
print("• Spreadsheet-compatible table format")
print("• Easy to open in Excel, Google Sheets, or any CSV viewer")
print("• One row per company, columns for each metric")
print("• Missing values shown as empty cells")
print("• Best for: Quick analysis, pivot tables, sharing with non-technical users")
print()

print("JSON Format:")
print("-" * 70)
print("• Structured data format preserving all fields")
print("• Array of objects, one per company")
print("• Explicitly shows null values for missing data")
print("• Best for: Programmatic access, APIs, archiving, further processing")
print()

print("=" * 70)
print("CONTENTS SUMMARY")
print("=" * 70)
print()

import pandas as pd

df = pd.read_csv(os.path.join(output_dir, "sustainability_comparison.csv"))

print(f"Companies: {len(df)}")
print(f"Fields per company: {len(df.columns)}")
print()

print("Data availability:")
for col in ['scope_1_emissions', 'scope_2_emissions_market_based', 'scope_3_emissions', 
            'renewable_energy_percentage', 'baseline_year']:
    if col in df.columns:
        count = df[col].notna().sum()
        print(f"  • {col}: {count}/4 companies")

print()
print("=" * 70)
print("TASK 8 COMPLETE")
print("=" * 70)
print()
print("✓ Results saved to output/ directory")
print("✓ CSV format: Easy spreadsheet access")
print("✓ JSON format: Complete structured data")
