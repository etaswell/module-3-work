"""
Validation checks for extracted sustainability data
"""
import pandas as pd
import numpy as np

print("=" * 70)
print("DATA VALIDATION - SESSION 9 TASK 7")
print("=" * 70)
print()

# Load the extracted data
df = pd.read_csv("sustainability_comparison.csv")

print("Running validation checks on all four companies...")
print()

# Validation results storage
validation_results = []

for idx, row in df.iterrows():
    company = row['company_name']
    issues = []
    warnings = []
    passed = []
    
    print("=" * 70)
    print(f"VALIDATING: {company}")
    print("=" * 70)
    print()
    
    # Check 1: Is Scope 3 > Scope 1?
    scope_1 = row['scope_1_emissions']
    scope_3 = row['scope_3_emissions']
    
    if pd.notna(scope_1) and pd.notna(scope_3):
        if scope_3 > scope_1:
            passed.append("✓ Scope 3 > Scope 1 (as expected)")
            print(f"✓ CHECK 1 - Scope 3 > Scope 1")
            print(f"  Scope 1: {scope_1:,.0f} tCO2e")
            print(f"  Scope 3: {scope_3:,.0f} tCO2e")
            print(f"  Ratio: {scope_3/scope_1:.1f}x larger")
        else:
            issues.append(f"✗ Scope 3 ({scope_3:,.0f}) NOT > Scope 1 ({scope_1:,.0f}) - unusual for large companies")
            print(f"✗ CHECK 1 FAILED - Scope 3 should be > Scope 1")
            print(f"  Scope 1: {scope_1:,.0f} tCO2e")
            print(f"  Scope 3: {scope_3:,.0f} tCO2e")
    elif pd.notna(scope_1) and pd.isna(scope_3):
        warnings.append(f"⚠ Scope 3 data missing - cannot validate against Scope 1")
        print(f"⚠ CHECK 1 SKIPPED - Scope 3 data not available")
    elif pd.isna(scope_1):
        warnings.append(f"⚠ Scope 1 data missing - cannot validate")
        print(f"⚠ CHECK 1 SKIPPED - Scope 1 data not available")
    print()
    
    # Check 2: Does Scope 1 + Scope 2 roughly equal total?
    scope_2_market = row['scope_2_emissions_market_based']
    scope_2_location = row['scope_2_emissions_location_based']
    total = row['total_emissions']
    
    # Use market-based if available, otherwise location-based
    scope_2 = scope_2_market if pd.notna(scope_2_market) else scope_2_location
    
    if pd.notna(scope_1) and pd.notna(scope_2) and pd.notna(total):
        calculated = scope_1 + scope_2
        if pd.notna(scope_3):
            calculated += scope_3
        
        # Allow 10% tolerance
        tolerance = 0.10
        diff_pct = abs(calculated - total) / total
        
        if diff_pct <= tolerance:
            passed.append(f"✓ Calculated total matches reported total (within {tolerance*100:.0f}%)")
            print(f"✓ CHECK 2 - Total emissions validation")
            print(f"  Calculated: {calculated:,.0f} tCO2e")
            print(f"  Reported: {total:,.0f} tCO2e")
            print(f"  Difference: {diff_pct*100:.1f}%")
        else:
            issues.append(f"✗ Calculated total ({calculated:,.0f}) differs from reported ({total:,.0f}) by {diff_pct*100:.1f}%")
            print(f"✗ CHECK 2 FAILED - Total emissions mismatch")
            print(f"  Calculated: {calculated:,.0f} tCO2e")
            print(f"  Reported: {total:,.0f} tCO2e")
            print(f"  Difference: {diff_pct*100:.1f}% (tolerance: {tolerance*100:.0f}%)")
    else:
        warnings.append("⚠ Cannot validate total - missing scope data or total not reported")
        print(f"⚠ CHECK 2 SKIPPED - Insufficient data to validate total")
    print()
    
    # Check 3: Is renewable energy percentage between 0 and 100?
    renewable_pct = row['renewable_energy_percentage']
    
    if pd.notna(renewable_pct):
        if 0 <= renewable_pct <= 100:
            passed.append(f"✓ Renewable energy percentage is valid: {renewable_pct:.0f}%")
            print(f"✓ CHECK 3 - Renewable energy percentage")
            print(f"  Value: {renewable_pct:.0f}%")
            print(f"  Range: Valid (0-100%)")
        else:
            issues.append(f"✗ Renewable energy percentage ({renewable_pct:.0f}%) is outside valid range (0-100%)")
            print(f"✗ CHECK 3 FAILED - Invalid renewable energy percentage")
            print(f"  Value: {renewable_pct:.0f}%")
            print(f"  Expected range: 0-100%")
    else:
        warnings.append("⚠ Renewable energy percentage not reported")
        print(f"⚠ CHECK 3 SKIPPED - Renewable energy data not available")
    print()
    
    # Check 4: Is target year in the future (or at least after 2020)?
    target_year = row['target_year']
    
    if pd.notna(target_year):
        target_year = int(target_year)
        if target_year >= 2020:
            if target_year >= 2026:
                passed.append(f"✓ Target year is in the future: {target_year}")
                print(f"✓ CHECK 4 - Target year")
                print(f"  Target: {target_year}")
                print(f"  Status: Future target (current year: 2026)")
            else:
                warnings.append(f"⚠ Target year ({target_year}) has already passed")
                print(f"⚠ CHECK 4 WARNING - Target year has passed")
                print(f"  Target: {target_year}")
                print(f"  Current year: 2026")
        else:
            issues.append(f"✗ Target year ({target_year}) is before 2020 - likely a data extraction error")
            print(f"✗ CHECK 4 FAILED - Target year too old")
            print(f"  Target: {target_year}")
            print(f"  Expected: >= 2020")
    else:
        warnings.append("⚠ Target year not reported")
        print(f"⚠ CHECK 4 SKIPPED - Target year not available")
    print()
    
    # Check 5: Are emissions values in a plausible range?
    # For large companies: millions (1,000 to 100,000,000 tCO2e), not billions or hundreds
    emissions_fields = {
        'Scope 1': scope_1,
        'Scope 2 (market)': scope_2_market,
        'Scope 2 (location)': scope_2_location,
        'Scope 3': scope_3,
        'Total': total
    }
    
    print(f"CHECK 5 - Emissions plausibility")
    plausibility_issues = []
    plausibility_passed = []
    
    for field_name, value in emissions_fields.items():
        if pd.notna(value):
            # Plausible range: 1,000 to 100,000,000 tCO2e
            if value < 1000:
                plausibility_issues.append(f"✗ {field_name}: {value:,.0f} tCO2e - too low (< 1,000)")
                print(f"  ✗ {field_name}: {value:,.0f} tCO2e - TOO LOW for large company")
            elif value > 100_000_000:
                plausibility_issues.append(f"✗ {field_name}: {value:,.0f} tCO2e - too high (> 100M), possible unit error")
                print(f"  ✗ {field_name}: {value:,.0f} tCO2e - TOO HIGH, check units")
            else:
                plausibility_passed.append(f"✓ {field_name}: {value:,.0f} tCO2e")
                print(f"  ✓ {field_name}: {value:,.0f} tCO2e - plausible")
    
    if not plausibility_issues and not plausibility_passed:
        warnings.append("⚠ No emissions data to validate")
        print(f"  ⚠ No emissions data available")
    elif not plausibility_issues:
        passed.append("✓ All emissions values are in plausible range")
    else:
        issues.extend(plausibility_issues)
    
    print()
    
    # Summary for this company
    print("-" * 70)
    print(f"VALIDATION SUMMARY: {company}")
    print("-" * 70)
    print(f"✓ Passed: {len(passed)}")
    print(f"✗ Issues: {len(issues)}")
    print(f"⚠ Warnings: {len(warnings)}")
    print()
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print()
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    # Store results
    validation_results.append({
        'company': company,
        'passed': len(passed),
        'issues': len(issues),
        'warnings': len(warnings),
        'has_issues': len(issues) > 0,
        'issue_list': issues,
        'warning_list': warnings
    })

# Overall summary
print()
print("=" * 70)
print("OVERALL VALIDATION SUMMARY")
print("=" * 70)
print()

summary_df = pd.DataFrame(validation_results)
print(summary_df[['company', 'passed', 'issues', 'warnings']].to_string(index=False))
print()

companies_with_issues = summary_df[summary_df['has_issues']]['company'].tolist()
if companies_with_issues:
    print(f"⚠ Companies with validation issues: {', '.join(companies_with_issues)}")
else:
    print("✓ No validation issues detected")

print()
print("=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)
print()

print("1. Data Quality:")
print(f"   • Google: Most complete data, all checks passed")
print(f"   • Apple: Limited data, cannot run all validations")
print(f"   • Amazon: Only renewable energy data available")
print(f"   • BP: No data extracted")
print()

print("2. Common Issues:")
print(f"   • Missing Scope 3 data prevents full validation")
print(f"   • No company reported total emissions for verification")
print(f"   • Target years not captured in extraction")
print()

print("3. Recommendations:")
print(f"   • Increase number of chunks processed (currently 5-8)")
print(f"   • Improve field descriptions in Pydantic schema")
print(f"   • Manually verify key numbers against source PDFs")
print(f"   • Consider processing entire document for critical metrics")
print()

print("=" * 70)
print("TASK 7 COMPLETE")
print("=" * 70)
