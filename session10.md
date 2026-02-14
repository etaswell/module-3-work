# Session 10: Can You Trust What the AI Extracted?

## The big idea

In Session 9, you built a pipeline that extracts structured data from PDFs. It produced numbers, filled in tables, processed hundreds of pages in minutes. 

But here's the question you should be asking: **are those numbers right?**

LLMs confidently produce numbers that aren't in the source document. They mix up units. They grab a number from a table heading instead of a data cell. They hallucinate plausible-sounding values for fields that simply don't exist in the text.

Today you'll learn to systematically assess trust in AI-extracted data. And then you'll package everything into a reusable tool — something that works on any PDF, not just the ones you've already seen.

---

## Before you start

Same setup as Sessions 8–9. You'll be working with the **city climate action plans** this time (a new document type):

```
data/climate-action-plans/
├── oakland-ecap-2020.pdf
├── portland-cap-2015.pdf
├── seattle-cap-2013.pdf
├── austin-climate-equity-2021.pdf
├── annarbor-a2zero-2020.pdf
├── ca-scoping-plan-2022.pdf
└── ipcc-ar6-wg3-spm.pdf
```

These are structurally different from the corporate reports you used in Session 9. They have different language, different formats, different kinds of data. That's intentional — a good tool should work across document types.

---

## Task 1: New document, new schema

**What you're doing:** City climate plans contain different information than corporate sustainability reports. Designing a schema forces you to think about what data you actually want — before you start extracting.

**Ask your coding agent to:**

1. Load `data/climate-action-plans/oakland-ecap-2020.pdf` and extract the text
2. Show you text from a few pages near the beginning (where goals and targets are usually stated)
3. Create a Pydantic schema for a city climate action plan with fields like:
   - City name
   - Plan title
   - Year published
   - Primary GHG reduction target (e.g., "80% below 1990 levels by 2050")
   - Target year
   - Baseline year
   - Interim targets (milestones before the main target)
   - Carbon neutrality or net-zero goal
   - Renewable energy target
   - Transportation strategy
   - Building strategy
   - Equity commitment
   - Current total emissions

Feel free to add or remove fields based on what you see in the document.

**Checkpoint:** You should have a schema with 10–15 fields. Most should be Optional — not every plan will include every field.

**Think about:** How is this schema different from Session 9's corporate report schema? City plans talk about policy strategies (transportation, buildings, equity) while corporate reports focus on operational metrics (Scope 1/2/3, PUE, water). The schema design reflects what questions you're trying to answer.

---

## Task 2: Extract — and then extract again with a different model

**What you're doing:** Here's your first trust test. If you send the same text to two different AI models, do they extract the same data?

**Ask your coding agent to:**

1. Find a data-rich chunk from the Oakland plan (use keyword scoring like Session 9)
2. Send that chunk to `qwen3` and extract data using your schema
3. Send the *exact same chunk* to `glm-4.7` and extract data
4. Display the results side by side, field by field, marking which fields agree and which disagree

**Important:** Remember that `glm-4.7` uses a different parameter to disable thinking (`enable_thinking` instead of `thinking`). Tell your agent to handle both models correctly.

**Checkpoint:** Some fields will match exactly (city_name: "Oakland"). Others will disagree. Look carefully at the disagreements.

**Think about the disagreements.** For example, Oakland's plan has targets at multiple time horizons (2020, 2030, 2050). `qwen3` might pick "36% by 2020" as the primary target while `glm-4.7` picks "83% by 2050." Both numbers are real — they're in the document. The models just made different choices about which one is the "primary" target.

This isn't a bug. It's revealing genuine ambiguity in the source text. When experts disagree about what the "primary" target is, that's information you need to know.

---

## Task 3: Same model, same input, three times

**What you're doing:** Even with temperature set to 0, AI models aren't perfectly deterministic. Let's find out how much variation there is.

**Ask your coding agent to:**

Run the same extraction (same chunk, same model, same schema) three times. Compare the results field by field. Which fields are stable (same answer every time) and which vary?

**Checkpoint:** You should see something like 70–85% of fields are stable across runs. Common sources of variation: slightly different wording of long text fields, different numbers chosen from the same paragraph.

**Think about:** If a field gives you a different answer every time you run it, how much should you trust any single run? This is a real issue for using AI-extracted data in research or policy analysis. What's an acceptable level of reproducibility?

---

## Task 4: Build a confidence score

**What you're doing:** You now have three signals about each field:
1. Do two models agree on it? (from Task 2)
2. Is it stable across multiple runs? (from Task 3)
3. Does the extracted value actually appear in the source text?

Combine these into a confidence score.

**Ask your coding agent to:**

Create a function that takes a field name, its value, the source text, and the results from Tasks 2–3, and returns a confidence score:
- **Multi-model agreement** (0–2 points): Did both models extract the same value?
- **Reproducibility** (0–2 points): Was exactly the same value extracted in all three runs?
- **Source grounding** (0–2 points): Does the extracted value appear verbatim in the source text?

Classify each field as HIGH (5–6 points), MEDIUM (3–4), or LOW (0–2).

Run this on every field from your extraction and display the results.

**Checkpoint:** Simple factual fields (city name, target year) should score HIGH. Interpretive fields (equity commitment, transportation strategy) will likely score MEDIUM or LOW.

**Think about:** Which confidence level is "good enough"? It depends on what you're doing. For a screening analysis ("which cities have net-zero targets?"), MEDIUM is fine. For a research paper claiming "Oakland's 2030 target is 56%," you'd want HIGH — and you'd still verify it by opening the PDF.

---

## Task 5: Full document vs. chunks — does it matter?

**What you're doing:** In Session 9, you broke documents into chunks because AI models used to have small context windows. But qwen3 can handle 262,000 tokens — enough for most entire PDFs. Does sending the whole document at once produce better results?

**Ask your coding agent to:**

1. Take a shorter document — `data/climate-action-plans/ipcc-ar6-wg3-spm.pdf` (the IPCC Summary for Policymakers, about 50 pages)
2. Concatenate all the text into one big string
3. Send the entire document to the AI in a single call and extract your schema
4. Also extract from just the top 5 chunks (the Session 9 approach)
5. Compare the results

**Checkpoint:** The full-document approach should do well on this document — the IPCC SPM is well-structured and not too long. Compare: did the full-document version find things the chunked version missed? Did the chunked version focus more precisely on specific numbers?

**Think about:** Full-document: one API call, sees everything, but may lose detail in dense sections. Chunked: multiple calls, focuses on the best sections, but may miss document-wide context. There isn't a universal winner — it depends on the document and what you're extracting.

---

## Task 6: Build a reusable tool

**What you're doing:** Up until now, you've been doing one-off analysis. Let's turn this into something anyone can use — a function that takes any PDF and any schema and returns structured, validated data.

**Ask your coding agent to:**

Create a function called `extract_document` that takes:
- A path to any PDF file
- A Pydantic schema class (any schema, not hardcoded)
- Optionally: which model to use, how many chunks to process

And returns:
- The extracted data
- Metadata (which file, how many pages, how many chunks had data, which pages the data came from)
- Validation notes (did schema validation pass? were extracted values found in the source text?)

The function should automatically:
- Build the extraction prompt from the schema's field descriptions
- Score chunks using the field names as keywords
- Handle the disable-thinking parameter correctly for the chosen model
- Skip chunks that return no data
- Merge results from multiple chunks

**Checkpoint:** Test it on one of the city climate action plans. You should get back structured data plus metadata and validation notes. Then test it on one of the corporate reports from Session 9 — does it work with a different schema?

**Think about:** This is the difference between "I ran a notebook once" and "I built a tool." The function doesn't know or care what document you give it or what schema you define. That's powerful. This is the kind of function that an AI coding agent could call as a tool.

---

## Task 7: Run across all the city climate plans

**What you're doing:** The real test — apply your tool to all 7 documents in `data/climate-action-plans/` and build a comparison dataset.

**Ask your coding agent to:**

1. Loop through all PDFs in `data/climate-action-plans/`
2. Run `extract_document` on each with your city climate plan schema
3. Collect results into a DataFrame
4. Print a comparison table showing each city's GHG target, target year, and carbon neutrality goal
5. Print a validation report: how many fields were extracted per document, any validation warnings
6. Save the results as JSON and CSV to `output/`

**Checkpoint:** You should have a table with ~7 rows comparing cities. Some documents will extract cleanly; others will have gaps or warnings. The IPCC document isn't really a "city" — interesting to see how the schema handles it.

**Think about:**
- Which cities have the most ambitious targets?
- Which documents extracted cleanly and which didn't? Why?
- How confident are you in any given number in the table? Would you cite it in a report without checking the source PDF?

---

## Wrapping up: What you built this module

Across three sessions, you went from "ask ChatGPT a question" to:

1. **Programmatic AI access** — calling models from code, which means you can scale
2. **Structured extraction** — getting data in columns, not paragraphs
3. **PDF processing** — handling real messy documents, not curated examples
4. **Validation** — knowing which results to trust and which to verify
5. **Multi-model comparison** — using disagreement as a signal of ambiguity
6. **Reproducibility testing** — understanding the limits of AI consistency
7. **A reusable tool** — `extract_document()` works on any PDF with any schema

The pipeline you built can process hundreds of climate documents into a structured dataset. That's a capability that didn't exist before these models — and knowing how to build it, validate it, and trust it appropriately is what separates useful analysis from AI-generated noise.

---

## For your assessment

Your Module 3 assessment asks you to submit a working document extraction pipeline that processes climate PDFs and outputs structured data (JSON/CSV). Your submission should demonstrate:

- PDF loading and intelligent chunking
- A Pydantic schema designed for your chosen domain
- LLM-based structured extraction
- Validation and confidence assessment
- Results saved as JSON and/or CSV

You can build on the code your agent wrote during these sessions, extend it to new documents, design richer schemas, or improve the validation. The `extract_document` tool from Task 6 is a strong starting point — customize it for your specific analysis question.
