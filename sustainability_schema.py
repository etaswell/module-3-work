"""
Pydantic schema for sustainability report data extraction
"""
from pydantic import BaseModel, Field
from typing import Optional

class SustainabilityReport(BaseModel):
    """
    Comprehensive schema for extracting structured data from corporate
    sustainability and environmental reports.
    """
    
    # Company identification
    company_name: str = Field(
        description="Name of the company or organization reporting"
    )
    
    reporting_year: Optional[int] = Field(
        default=None,
        description="Fiscal year or calendar year covered by this report (e.g., 2022, 2023)"
    )
    
    # Emissions data - Scope 1
    scope_1_emissions: Optional[float] = Field(
        default=None,
        description="Scope 1 direct GHG emissions from sources owned or controlled by the company (e.g., on-site combustion, company vehicles). Look for 'Scope 1' in tables or emissions inventory sections."
    )
    
    # Emissions data - Scope 2
    scope_2_emissions_market_based: Optional[float] = Field(
        default=None,
        description="Scope 2 indirect GHG emissions from purchased electricity using market-based method (reflects renewable energy purchases and RECs). Often labeled 'Scope 2 (market-based)' or 'Scope 2 market approach'."
    )
    
    scope_2_emissions_location_based: Optional[float] = Field(
        default=None,
        description="Scope 2 indirect GHG emissions from purchased electricity using location-based method (uses grid average emissions factors). Often labeled 'Scope 2 (location-based)' or 'Scope 2 location approach'."
    )
    
    # Emissions data - Scope 3
    scope_3_emissions: Optional[float] = Field(
        default=None,
        description="Scope 3 indirect GHG emissions from the company's value chain (e.g., supply chain, product use, business travel, waste). Look for 'Scope 3' in emissions tables. This is typically the largest category."
    )
    
    # Total emissions
    total_emissions: Optional[float] = Field(
        default=None,
        description="Total greenhouse gas emissions across all scopes. May be reported as 'Total GHG emissions', 'Total emissions', or 'Carbon footprint'. Should equal or approximate Scope 1 + Scope 2 + Scope 3."
    )
    
    emissions_units: Optional[str] = Field(
        default=None,
        description="Units for emissions values (e.g., 'tCO2e', 'metric tons CO2e', 'MtCO2e', 'kilotons CO2e'). Look near emissions tables or in methodology sections."
    )
    
    # Energy data
    total_energy_consumption: Optional[float] = Field(
        default=None,
        description="Total energy consumed by the organization's operations. Look for 'Total energy consumption', 'Energy use', or 'Electricity consumption'. Often in data center/facility sections."
    )
    
    energy_consumption_units: Optional[str] = Field(
        default=None,
        description="Units for energy consumption (e.g., 'MWh', 'GWh', 'TWh', 'kWh'). Look near energy data tables."
    )
    
    renewable_energy_percentage: Optional[float] = Field(
        default=None,
        description="Percentage of total energy consumption from renewable sources. Look for statements like '100% renewable electricity', 'X% matched with renewable energy', or renewable energy procurement data. Should be between 0 and 100."
    )
    
    renewable_energy_absolute: Optional[float] = Field(
        default=None,
        description="Absolute amount of renewable energy procured or generated (e.g., in MWh or GWh). Look for 'renewable energy purchases', 'clean energy procurement', or solar/wind generation data."
    )
    
    # Climate targets
    target_description: Optional[str] = Field(
        default=None,
        description="Description of the company's primary climate or emissions reduction target. Look for statements about 'net zero', 'carbon neutral', 'Science Based Target', or specific reduction percentages (e.g., '50% reduction by 2030')."
    )
    
    target_year: Optional[int] = Field(
        default=None,
        description="Target year for achieving the company's primary climate goal (e.g., 2030, 2040, 2050). Look for phrases like 'by 2030', 'achieve by 2050', or 'carbon neutral by [year]'."
    )
    
    baseline_year: Optional[int] = Field(
        default=None,
        description="Base year used for measuring emissions reduction progress. Look for 'baseline year', 'base year', or 'compared to 2019 baseline'. Usually ranges from 2015-2020 for most companies."
    )
    
    scope_coverage: Optional[str] = Field(
        default=None,
        description="Which emission scopes are covered by the target (e.g., 'Scope 1 and 2', 'All scopes', 'Scope 1, 2, and 3'). Important for understanding the ambition level of the target."
    )
    
    interim_target: Optional[str] = Field(
        default=None,
        description="Any interim or near-term targets before the final target year (e.g., '35% reduction by 2025'). Look for multiple target years or phrases like 'interim target', 'near-term goal'."
    )
    
    # Water data
    total_water_withdrawal: Optional[float] = Field(
        default=None,
        description="Total volume of water withdrawn from all sources (municipal supply, groundwater, surface water). Look for 'water withdrawal', 'water use', or 'freshwater consumption' in environmental data sections."
    )
    
    water_consumption: Optional[float] = Field(
        default=None,
        description="Total volume of water consumed (withdrawn minus discharged). Look for 'water consumption', 'net water use', or 'water consumed'. This is typically less than withdrawal."
    )
    
    water_units: Optional[str] = Field(
        default=None,
        description="Units for water data (e.g., 'million cubic meters', 'megalitres', 'billion gallons'). Look near water data tables."
    )
    
    # Additional context
    report_title: Optional[str] = Field(
        default=None,
        description="Official title of the sustainability report (e.g., '2023 Environmental Progress Report', 'Sustainability Report 2022')"
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="Any important caveats, methodology notes, or context about the data reported (e.g., 'excludes acquisitions', 'includes offsets', 'verified by third party')"
    )


# Test the schema
if __name__ == "__main__":
    print("=" * 70)
    print("Sustainability Report Data Schema")
    print("=" * 70)
    print()
    
    # Show schema structure
    print("Schema fields:")
    print()
    for field_name, field_info in SustainabilityReport.model_fields.items():
        field_type = field_info.annotation
        description = field_info.description or "No description"
        required = field_info.is_required()
        
        print(f"• {field_name}")
        print(f"  Type: {field_type}")
        print(f"  Required: {required}")
        print(f"  Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print()
    
    print("=" * 70)
    print(f"Total fields: {len(SustainabilityReport.model_fields)}")
    required_count = sum(1 for f in SustainabilityReport.model_fields.values() if f.is_required())
    optional_count = len(SustainabilityReport.model_fields) - required_count
    print(f"Required fields: {required_count}")
    print(f"Optional fields: {optional_count}")
    print("=" * 70)
    print()
    
    # Test with sample data
    print("Testing schema with sample data...")
    print()
    
    sample_report = SustainabilityReport(
        company_name="Google",
        reporting_year=2022,
        scope_1_emissions=178000,
        scope_2_emissions_market_based=0,
        scope_2_emissions_location_based=2800000,
        scope_3_emissions=10100000,
        total_emissions=10276000,
        emissions_units="tCO2e",
        renewable_energy_percentage=100,
        target_description="Achieve net-zero emissions across all operations and value chain",
        target_year=2030,
        baseline_year=2019,
        scope_coverage="Scope 1, 2, and 3"
    )
    
    print("✓ Sample report created successfully")
    print()
    print(sample_report.model_dump_json(indent=2))
    print()
    
    # Validate
    print("=" * 70)
    print("Schema validation: PASSED")
    print("=" * 70)
