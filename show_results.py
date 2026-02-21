"""
Display final comparison results
"""
import pandas as pd

df = pd.read_csv('sustainability_comparison.csv')

print('=' * 70)
print('FINAL COMPARISON TABLE - ALL FOUR COMPANIES')
print('=' * 70)
print()

print('EMISSIONS DATA:')
print('-' * 70)
emissions_cols = ['company_name', 'scope_1_emissions', 'scope_2_emissions_market_based', 'scope_3_emissions']
print(df[emissions_cols].to_string(index=False))
print()

print('ENERGY & TARGETS:')
print('-' * 70)
energy_cols = ['company_name', 'renewable_energy_percentage', 'baseline_year']
print(df[energy_cols].to_string(index=False))
print()

print('=' * 70)
print('DATA AVAILABILITY SUMMARY')
print('=' * 70)
metrics = {
    'Scope 1 emissions': 'scope_1_emissions',
    'Scope 2 emissions (market-based)': 'scope_2_emissions_market_based',
    'Scope 3 emissions': 'scope_3_emissions',
    'Renewable energy %': 'renewable_energy_percentage',
    'Baseline year': 'baseline_year'
}

for label, col in metrics.items():
    count = df[col].notna().sum()
    print(f'  {label}: {count}/4 companies')

print()
print('=' * 70)
print('KEY INSIGHTS')
print('=' * 70)

# Google has most complete data
print('\n✓ Google: Most complete dataset')
print('  - All three emission scopes captured')
print(f'  - Scope 3 ({df.loc[0, "scope_3_emissions"]:,.0f}) >> Scope 1+2 combined')

# Apple partial
print('\n✓ Apple: Partial dataset')
print('  - Scope 1 emissions and baseline year captured')

# Amazon 
print('\n✓ Amazon: Energy data only')
print(f'  - Renewable energy: {df.loc[2, "renewable_energy_percentage"]:.0f}%')
print('  - No emissions data extracted')

# BP
print('\n✗ BP: No data extracted')
print('  - PDF file not available in data directory')

print()
print('=' * 70)
print('TASK 6 COMPLETE')
print('=' * 70)
print('\nFiles saved:')
print('  • sustainability_comparison.csv')
print('  • sustainability_comparison.json')
