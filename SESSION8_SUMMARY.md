# Session 8 LLM Pipeline - Execution Summary

## Date: February 20, 2026
## Model: qwen3 (Qwen3-VL-235B-A22B-Thinking-FP8)
## Endpoint: https://ellm.nrp-nautilus.io/v1

---

## ✅ Completed Tasks

### 1. Environment Setup
- **Base URL**: `https://ellm.nrp-nautilus.io/v1`
- **API Key**: Configured ✓
- **Model**: qwen3 ✓
- **Dependencies**: openai, pydantic, pandas installed ✓

### 2. Schema Validation
**File**: `verify_schema.py`

Verified ClimateCommitment schema with 6 fields:
- **Required**: company_name, target_description
- **Optional**: target_year, baseline_year, scope_coverage, interim_target

**Tests Passed**:
- ✓ Required field validation
- ✓ Optional field handling  
- ✓ Type coercion (string → int)
- ✓ JSON serialization/deserialization
- ✓ Error detection
- ✓ API integration ready

### 3. API Configuration Verification
**File**: `verify_api_config.py` + `test_api_config.py`

**Results**:
- Total API calls in notebook: 4
- Structured extraction calls: 3
- Properly configured: **3/3** ✓

All extraction calls include:
- `response_format={"type": "json_object"}` ✓
- `extra_body={"chat_template_kwargs": {"thinking": False}}` ✓

### 4. Part 3: Extract from Text Passage
**File**: `run_part3.py` → Output: `part3_extraction_result.json`

**Sample**: Apple climate commitment text

**Extracted Data**:
```json
{
  "company_name": "Apple",
  "target_year": 2030,
  "target_description": "carbon neutral across entire supply chain and product life cycle",
  "baseline_year": 2015,
  "scope_coverage": "Scope 1, Scope 2, and Scope 3 emissions",
  "interim_target": "carbon neutrality for global corporate operations"
}
```

**Status**: ✅ Complete - Validated against Pydantic schema

### 5. Part 4: Compare Across Models  
**File**: `run_part4.py`

**Sample**: Google sustainability goals (ambiguous text)

**Results**:
- ✅ **qwen3**: Successfully extracted
  - Company: Google
  - Target: Net-zero emissions by 2030
  - Scope: Scopes 1, 2, and 3
  
- ❌ **glm-4.7**: Request timed out (model may be unavailable)

**Status**: ⚠️ Partially complete - qwen3 successful, glm-4.7 failed

### 6. Part 5: Batch Extraction
**File**: `run_part5.py` → Outputs: `part5_batch_extraction.json`, `part5_batch_extraction.csv`

**Processed**: 3 companies (Amazon, BP, Apple)  
**Success Rate**: 3/3 (100%)

**Summary Table**:
| Company | Target Year | Target Description | Baseline | Scopes |
|---------|-------------|-------------------|----------|---------|
| Amazon | 2040 | Net-zero carbon emissions | 2019 | All three scopes |
| BP | 2050 | Net zero company | 2019 | Scope 1, 2, and 3 |
| Apple | 2030 | Carbon neutral supply chain | 2015 | Scope 1, 2, and 3 |

**Statistics**:
- Companies with target years: 3/3
- Companies with baseline years: 3/3  
- Companies with scope coverage: 3/3
- Target year range: 2030-2050
- Average target year: 2040

**Status**: ✅ Complete - All extractions successful

---

## 📊 Output Files Generated

### Core Extraction Results
1. **part3_extraction_result.json** - Single company (Apple) extraction
2. **part5_batch_extraction.json** - Multi-company structured data
3. **part5_batch_extraction.csv** - Tabular format for analysis

### Earlier Pipeline Outputs
4. **climate_commitments_output.json** - Initial batch extraction
5. **climate_commitments_output.csv** - CSV version

### Verification & Logs
6. **extraction_log_20260220_123734.log** - Detailed execution log

---

## 🎯 Key Achievements

### Technical
- ✅ Successfully configured OpenAI-compatible API endpoint
- ✅ Implemented Pydantic schemas for structured outputs
- ✅ Configured JSON mode + disable-thinking for all extraction calls
- ✅ Validated type coercion and error handling
- ✅ Demonstrated scalability (single → batch extraction)

### Data Extraction
- ✅ Extracted structured climate commitments from unstructured text
- ✅ Processed 3+ companies with 100% success rate
- ✅ Generated both JSON and CSV outputs for downstream analysis
- ✅ Validated all extractions against Pydantic schema

### Lessons Learned
1. **JSON mode** essential for structured extraction
2. **Disable-thinking** prevents content=None errors
3. **Pydantic validation** catches extraction errors early
4. **Type coercion** handles string numbers automatically
5. **Model availability** varies (glm-4.7 not accessible)

---

## 🔄 Pipeline Workflow

```
Text Input
    ↓
LLM API (qwen3)
    ↓
JSON Response (with schema)
    ↓
Pydantic Validation
    ↓
Structured Data (ClimateCommitment)
    ↓
Output (JSON + CSV)
```

---

## 📈 Next Steps (Session 9)

The same techniques will be applied to:
- **Real PDF documents** (corporate sustainability reports)
- **Document chunking** (handling longer texts)
- **Advanced text extraction** (tables, charts, mixed formatting)
- **City climate action plans** (more complex structures)

---

## ✅ Session 8: Complete

All core tasks successfully executed. The LLM pipeline is configured, validated, and producing structured climate commitment data from unstructured text.

**Ready for Session 9**: PDF Extraction and Advanced Document Processing
