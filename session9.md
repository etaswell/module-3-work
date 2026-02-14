# Session 9: Real PDFs, Real Problems

## The big idea

In Session 8, you extracted structured data from short text passages you pasted into your code. That was training wheels. Real climate data lives in PDFs — 100-page corporate sustainability reports, city climate action plans, federal energy studies.

Today you'll build a pipeline that opens a real PDF, extracts the text, breaks it into manageable pieces, sends those pieces to an AI model, and collects the results into a structured dataset. By the end, you'll have a comparison table across four major companies — the kind of analysis that would take a human analyst a full day.

---

## Before you start

Make sure:
- Your environment variables are set (same as Session 8)
- The PDFs are downloaded (`bash download_data.sh` if needed)
- You have these reports in `data/corporate-sustainability/`:
  - `google-env-2024.pdf`
  - `apple-env-2024.pdf`
  - `amazon-sustainability-2023.pdf`
  - `bp-sustainability-2023.pdf`

---

## Task 1: Look inside a PDF

**What you're doing:** Before you can extract data from a PDF, you need to understand what the AI will actually see. PDF text extraction is imperfect — headers and footers get mixed in, table columns get merged, charts disappear entirely.

**Ask your coding agent to:**

Open `data/corporate-sustainability/google-env-2024.pdf` using PyMuPDF (the library is called `fitz`), extract the text from each page, and print the text from page 10.

**Checkpoint:** You should see a wall of text. It won't be perfectly formatted — you'll see stray characters, broken table layouts, headers mixed into body text. This is normal. Every PDF is different.

**Think about:** Look at the raw text. Could you find Google's Scope 1 emissions in here? Probably — but you'd have to scroll through a lot of noise. That's why we need to be strategic about which parts we send to the AI.

---

## Task 2: Break the document into chunks

**What you're doing:** These PDFs are 68–113 pages long. That's tens of thousands of words. While modern AI models can handle very long inputs, sending the entire document for every question is wasteful and noisy. Instead, we break it into smaller pieces ("chunks") and only process the most relevant ones.

**Ask your coding agent to:**

Split the Google report's text into overlapping chunks of about 4,000 characters each, with 200 characters of overlap between consecutive chunks. Use the `RecursiveCharacterTextSplitter` from `langchain_text_splitters`.

Print how many chunks were created, and show the first chunk.

**Checkpoint:** You should get somewhere around 30–60 chunks depending on the document. Each chunk should be a readable block of text, not random fragments.

**Think about:** Why overlap? Because if an important sentence falls right at the boundary between two chunks, the overlap ensures it appears in at least one chunk completely. Try changing the chunk size — what happens with smaller chunks? Larger ones?

---

## Task 3: Find the data-rich chunks

**What you're doing:** Most of a sustainability report is narrative text — "we believe in a sustainable future" etc. The numbers you actually want (emissions, targets, energy data) are concentrated in specific sections. Let's find those sections automatically.

**Ask your coding agent to:**

Score each chunk by counting how many data-relevant keywords appear in it. Good keywords: "emissions", "Scope 1", "Scope 2", "Scope 3", "renewable", "target", "GHG", "tCO2", "MWh", "percent", "carbon neutral", "net zero". Show the top 5 highest-scoring chunks with their page numbers.

**Checkpoint:** The highest-scoring chunks should come from the data sections of the report — emissions inventories, target descriptions, energy disclosures. If the top chunks are from the table of contents or executive summary, the keyword list may need adjusting.

**Think about:** This is a simple but effective filter. You *could* send every chunk to the AI, but that's slow and expensive. By pre-filtering, you focus the AI's attention on the parts that actually contain data.

---

## Task 4: Design a sustainability report schema

**What you're doing:** In Session 8, you had a simple schema with 5–6 fields. A real sustainability report contains much more. You'll design a schema that captures the key metrics investors and policymakers actually care about.

**Ask your coding agent to:**

Create Pydantic schemas for a sustainability report extraction. Think about what data you'd want to compare across companies. Here's a starting point:

- **Emissions data:** Scope 1 emissions, Scope 2 emissions (ideally both market-based and location-based), Scope 3 emissions, total emissions, units (tCO2e usually), reporting year
- **Energy data:** total energy consumption, renewable energy percentage
- **Climate targets:** target description, target year, baseline year, scope coverage
- **Water data** (if you want): total water withdrawal, water consumption

The schema should handle the fact that many fields might not be present in every report — use Optional fields with sensible descriptions.

**Checkpoint:** You should have Pydantic model(s) defined.  The key is that every field has a description that tells the AI what to look for. Clear descriptions = better extraction.

---

## Task 5: Extract data from one report

**What you're doing:** Now you'll put it all together — load a PDF, chunk it, find the best chunks, send them to the AI, and collect structured data.

**Ask your coding agent to:**

Build a function that:
1. Takes a PDF path
2. Loads and chunks the text
3. Scores chunks and selects the top 8–10
4. Sends each chunk to the AI with your schema
5. Merges the results (first non-null value for each field wins)
6. Returns the combined extraction

Run it on the Google report and print the results.

**Important details to mention:**
- Use JSON mode (`response_format={"type": "json_object"}`)
- Disable thinking for JSON extraction
- Use `temperature=0.0`
- Add a short pause (`time.sleep(0.5)`) between API calls to avoid overwhelming the server
- Handle cases where the AI returns nothing (content is None) — just skip that chunk

**Checkpoint:** You should get a JSON object with actual numbers from Google's report. Look for:
- Scope 2 emissions should be in the millions of tCO2e range
- Renewable energy percentage should be high (Google is a big renewable buyer)
- Total energy consumption should be in the millions of MWh range

If you're getting nulls for everything, the schema descriptions might not be clear enough, or the keyword scoring might not be finding the right chunks.

---

## Task 6: Process all four reports

**What you're doing:** The payoff — running the same pipeline across multiple companies and building a comparison dataset.

**Ask your coding agent to:**

Loop through all four reports (Google, Apple, Amazon, BP), run the extraction function on each, and collect the results into a pandas DataFrame. Print the comparison table.

**Checkpoint:** You should have a table with 4 rows and columns for each metric. It will probably take 2–5 minutes to process all four (depending on API speed). Some fields will be null for some companies — that's normal, not every report includes every metric.

**Look for interesting patterns:**
- Which company reports the highest total emissions?
- Which company has the most ambitious target year?
- Does anyone report Scope 3? (Hint: Scope 3 is typically much larger than Scope 1+2, but many companies don't report it)

---

## Task 7: Validate the results

**What you're doing:** Here's the part most people skip — and the part that matters most. LLMs confidently produce numbers that aren't in the source document. You need to check.

**Ask your coding agent to:**

Write validation checks for the extracted data:
- Is Scope 3 > Scope 1? (It almost always should be for large companies)
- Does Scope 1 + Scope 2 roughly equal the reported total? (If total is reported)
- Is renewable energy percentage between 0 and 100?
- Is the target year in the future (or at least after 2020)?
- Are emissions values in a plausible range? (Millions of tCO2e for large companies, not billions, not hundreds)

Run the validation on all four companies and flag any issues.

**Checkpoint:** You will almost certainly find issues. That's the point. Maybe one company's emissions are off by a factor of 1000 (unit confusion — tonnes vs. metric tonnes vs. kilotonnes). Maybe the AI pulled a number from a table header instead of a data cell.

**Think about:** This is the most important lesson of the session. The extraction pipeline runs quickly and produces plausible-looking numbers. But "plausible-looking" isn't the same as "correct." How would you verify a number you're unsure about? (Open the PDF, go to the page, and look.)

---

## Task 8: Save your results

**Ask your coding agent to:**

Save the extraction results as both JSON (with all the detail) and CSV (just the comparison table) to the `output/` directory.

**Checkpoint:** You should have two files in `output/` — one JSON, one CSV.

---

## What you built today

- A PDF processing pipeline that handles real sustainability reports
- Smart chunking with keyword-based relevance scoring
- Multi-field extraction using Pydantic schemas
- A batch comparison across four major companies
- Validation checks that flag suspicious results

Next session, you'll push further: Can you trust these numbers? Do different models agree? What happens when you run the same extraction twice? And you'll turn this pipeline into a reusable tool.
