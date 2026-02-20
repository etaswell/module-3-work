"""
Climate Commitment Extraction Pipeline
Runs structured extraction and saves outputs to files
"""
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import os
import json
import logging
from datetime import datetime
import pandas as pd

# Setup logging
log_filename = f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 70)
logger.info("Climate Commitment Extraction Pipeline Started")
logger.info("=" * 70)

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

logger.info("Schema loaded: ClimateCommitment")

# Configure the OpenAI client
try:
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "https://ellm.nrp-nautilus.io/v1"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    MODEL = os.environ.get("OPENAI_MODEL", "qwen3")
    
    logger.info(f"API Configuration:")
    logger.info(f"  Base URL: {os.environ.get('OPENAI_BASE_URL', 'NOT SET')}")
    logger.info(f"  API Key: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    logger.info(f"  Model: {MODEL}")
except Exception as e:
    logger.error(f"Failed to configure API client: {e}")
    raise

# Company commitment texts
company_texts = {
    "Apple": """
    Apple has committed to becoming carbon neutral across its entire supply chain 
    and product life cycle by 2030. This includes Scope 1, Scope 2, and Scope 3 
    emissions. Using a 2015 baseline, Apple has already reduced its comprehensive 
    carbon footprint by more than 55 percent since 2015. As an interim milestone, 
    Apple achieved carbon neutrality for its global corporate operations in 2020. 
    The company's approach prioritizes direct emissions reductions of 75 percent 
    from 2015 levels, with the remaining 25 percent addressed through high-quality 
    carbon removal projects.
    """,
    
    "Amazon": """
    Amazon's Climate Pledge commits the company to reaching net-zero carbon 
    emissions by 2040 — 10 years ahead of the Paris Agreement. The pledge 
    covers all three emission scopes. As of 2023, Amazon has reduced the 
    carbon intensity of its shipments by 11.5% compared to a 2019 baseline. 
    The company is the world's largest corporate purchaser of renewable energy, 
    with 500+ solar and wind projects globally.
    """,
    
    "BP": """
    BP aims to become a net zero company by 2050 or sooner, and to help the 
    world get to net zero. This ambition covers Scope 1, 2, and 3 emissions. 
    BP's interim target is to reduce Scope 1 and 2 operational emissions by 
    50% by 2030, compared to a 2019 baseline. The company also aims to reduce 
    the carbon intensity of the products it sells by 15-20% by 2030. BP has 
    faced criticism for potentially weakening its climate targets in 2023.
    """,
    
    "Microsoft": """
    Microsoft has announced its commitment to become carbon negative by 2030, 
    and by 2050, to remove all the carbon the company has emitted since it was 
    founded in 1975. This includes all Scope 1, 2, and 3 emissions. Starting in 
    2021, Microsoft has an internal carbon tax to drive accountability across 
    its divisions.
    """,
    
    "Google": """
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
}

logger.info(f"\nProcessing {len(company_texts)} companies...")

# Extract commitments
results = []
errors = []

for company, text in company_texts.items():
    logger.info(f"\n{'─' * 70}")
    logger.info(f"Processing: {company}")
    logger.info(f"{'─' * 70}")
    logger.info(f"Text length: {len(text)} characters")
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Extract climate commitment as JSON. Fields: company_name, target_year, target_description, baseline_year, scope_coverage, interim_target. Use null for missing fields."
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            extra_body={"chat_template_kwargs": {"thinking": False}},
        )
        
        content = response.choices[0].message.content
        if content is None:
            logger.warning(f"  ⚠️  {company}: Model returned no content, skipping")
            errors.append({"company": company, "error": "No content returned"})
            continue
        
        extracted = json.loads(content)
        
        # Validate with Pydantic
        commitment = ClimateCommitment(**extracted)
        
        # Add to results
        result_dict = commitment.model_dump()
        results.append(result_dict)
        
        logger.info(f"✓ Successfully extracted: {company}")
        logger.info(f"  Target: {commitment.target_description}")
        logger.info(f"  Year: {commitment.target_year}")
        logger.info(f"  Scopes: {commitment.scope_coverage}")
        
    except Exception as e:
        logger.error(f"✗ Error processing {company}: {e}")
        errors.append({"company": company, "error": str(e)})

# Save results to JSON file
output_filename = f"climate_commitments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
output_data = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "total_companies": len(company_texts),
        "successful_extractions": len(results),
        "failed_extractions": len(errors)
    },
    "results": results,
    "errors": errors
}

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

logger.info(f"\n{'=' * 70}")
logger.info(f"Results saved to: {output_filename}")
logger.info(f"{'=' * 70}")

# Create summary table
if results:
    df = pd.DataFrame(results)
    
    # Save to CSV
    csv_filename = f"climate_commitments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    logger.info(f"CSV table saved to: {csv_filename}")
    
    # Print summary table
    logger.info("\n📊 Climate Commitments Summary:")
    logger.info("\n" + df.to_string(index=False))
    
    # Statistics
    logger.info(f"\n{'─' * 70}")
    logger.info("Statistics:")
    logger.info(f"  Companies with target years: {df['target_year'].notna().sum()}")
    logger.info(f"  Companies with baseline years: {df['baseline_year'].notna().sum()}")
    logger.info(f"  Companies with scope coverage: {df['scope_coverage'].notna().sum()}")
    logger.info(f"  Companies with interim targets: {df['interim_target'].notna().sum()}")
    
    if df['target_year'].notna().any():
        logger.info(f"  Average target year: {df['target_year'].mean():.0f}")
        logger.info(f"  Earliest target: {df['target_year'].min()}")
        logger.info(f"  Latest target: {df['target_year'].max()}")

logger.info(f"\n{'=' * 70}")
logger.info("Pipeline Completion Summary")
logger.info(f"{'=' * 70}")
logger.info(f"✓ Successful extractions: {len(results)}/{len(company_texts)}")
logger.info(f"✗ Failed extractions: {len(errors)}/{len(company_texts)}")
logger.info(f"\nOutput files created:")
logger.info(f"  • {output_filename} (JSON with full details)")
logger.info(f"  • {csv_filename if results else 'N/A'} (CSV table)")
logger.info(f"  • {log_filename} (Execution log)")
logger.info(f"{'=' * 70}")

print(f"\n✅ Pipeline complete! Check {log_filename} for full details.")
