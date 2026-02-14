# Session 8: From Chat to Code

## The big idea

You already know how to ask an AI a question about a document. Upload a PDF, type a question, get an answer. That works — but it only works once, for one document, and you can't build on it.

Today you'll learn to do the same thing from code. That means you can do it a thousand times. You can do it on a folder full of documents. You can collect the answers in a table instead of copying and pasting.

You won't write the code yourself — your coding agent will. Your job is to tell it what you want, check that it's doing the right thing, and think critically about the results.

---

## Before you start

Make sure your workspace is set up:

1. You should have the `module-3-template` folder open in VS Code
2. The PDFs should be downloaded (run `bash download_data.sh` in the terminal if you haven't)
3. Run `uv sync` in the terminal to install Python packages
4. Set your API credentials in the terminal:

```bash
export OPENAI_BASE_URL="https://ellm.nrp-nautilus.io/v1"
export OPENAI_API_KEY="your-key-here"
export OPENAI_MODEL="qwen3"
```

If any of this doesn't make sense, ask your coding agent: *"Help me set up the environment variables for the NRP LLM endpoint."*

---

## Task 1: Say hello to the API

**What you're doing:** Making your first API call from Python. Instead of typing into a chat window, your code will send a message to an AI model and get a response back.

**Ask your coding agent to:**

Create a Python script that connects to the LLM API using the OpenAI library, sends a simple climate-related question (like "What are the main sources of greenhouse gas emissions?"), and prints the response.

**Important details to mention:**
- The API endpoint and key should come from environment variables (not hardcoded)
- The model name should also come from an environment variable
- This is an OpenAI-compatible API, not the actual OpenAI service

**Checkpoint:** You should see a text response printed in your terminal — a paragraph answering your climate question. If you get an error about authentication or connection, check your environment variables.

**Think about:** What you just did is the same as typing into ChatGPT — but from code. Why does that matter? What can you do with this that you couldn't do in a chat window?

---

## Task 2: Get structured data, not paragraphs

**What you're doing:** When you ask an AI a question in chat, you get a paragraph. Paragraphs don't go into spreadsheets. Now you'll tell the AI exactly what *shape* you want the answer in.

**Read this text:**

> *Apple has committed to becoming carbon neutral across its entire supply chain and product life cycle by 2030, using a 2015 baseline. The commitment covers Scope 1, 2, and 3 emissions. Apple has already achieved carbon neutrality for its global corporate operations.*

If you were building a table comparing different companies' climate commitments, what columns would you need? Probably something like: company name, what they committed to, target year, baseline year, which emission scopes are covered.

**Ask your coding agent to:**

Define a data schema (using a Python library called Pydantic) for a company's climate commitment. It should include:
- Company name (text, required)
- Commitment description — what they actually pledged (text)
- Target year (number, might not be mentioned)
- Baseline year (number, might not be mentioned)
- Which emission scopes are covered (text, might not be mentioned)
- Whether they claim to have already achieved any milestone (text, might not be mentioned)

Then send the Apple text above to the API and extract data matching this schema, using JSON mode.

**Important details to mention:**
- Use `response_format={"type": "json_object"}` for JSON mode
- Put the schema description in the system prompt so the model knows what fields to extract
- The model is a reasoning model — for JSON extraction, disable thinking with `extra_body={"chat_template_kwargs": {"thinking": False}}`
- Don't set `max_tokens`
- Use `temperature=0.0` for consistent results

**Checkpoint:** You should get back a JSON object (structured data), not a paragraph. The target year should be 2030. The baseline year should be 2015. Scopes should mention 1, 2, and 3.

If you got a paragraph instead of JSON, or if the model returned nothing, make sure JSON mode and disable-thinking are both set.

**Think about:** Look at the baseline_year field. Is 2015 actually in the text? (Yes.) What if the text hadn't mentioned a baseline year? Would the AI leave it blank, or make one up? This is exactly the problem we'll wrestle with all module.

---

## Task 3: What happens with ambiguous text?

**What you're doing:** The Apple text was clean and direct. Real documents are messier. Let's see what happens.

**Try this text:**

> *Google has maintained carbon neutrality for its global operations since 2007 through the purchase of carbon offsets. In 2020, the company set a goal to operate on 24/7 carbon-free energy at every data center by 2030. Google's long-term aspiration is to achieve net-zero emissions across all operations and value chain by 2030.*

**Ask your coding agent to:**

Run the same extraction on this Google text using the same schema.

**Checkpoint:** You should get results — but look carefully. Google claims *both* "carbon neutral since 2007" *and* "net-zero by 2030." Those are different things. What did the model pick for the target year? What did it pick for the commitment description? Did it capture both claims or just one?

**Think about:** This is deliberately ambiguous. There's no single "right" answer for `target_year` here — 2007 and 2030 are both defensible. This is why structured extraction from real documents is hard: the AI has to make choices, and you need to understand what choices it made.

---

## Task 4: Ask a different model the same question

**What you're doing:** Different AI models sometimes extract different things from the same text. If two models disagree, that tells you the information is ambiguous — you need to check by hand.

**Ask your coding agent to:**

Run the same extraction on the Google text, but using the model `glm-4.7` instead of `qwen3`.

**Important detail:** `glm-4.7` disables thinking differently — it uses `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` (note: `enable_thinking` instead of `thinking`). Ask your agent to handle this.

**Checkpoint:** Compare the two results side by side. Did both models pick the same target year? The same commitment description? The same scopes?

**Think about:** When two models agree, that's a good sign. When they disagree, it doesn't mean one is "wrong" — it often means the source text is genuinely ambiguous. Which fields had the most agreement? Which had the least?

---

## Task 5: Process multiple companies

**What you're doing:** The whole point of doing this from code is scale. Let's extract from three companies in a loop and build a comparison table.

**Here are three text passages:**

> **Amazon:** *Amazon's Climate Pledge commits the company to reaching net-zero carbon emissions by 2040 — 10 years ahead of the Paris Agreement. The commitment covers the company's full business operations, including the transportation network, packaging, and buildings.*

> **BP:** *BP's new strategy aims to become a net zero company by 2050 or sooner, covering Scope 1 and 2 emissions from operations. BP also aims to cut the carbon intensity of the products it sells by 50% by 2050, addressing a portion of its Scope 3 emissions.*

> **Apple:** *Apple has committed to becoming carbon neutral across its entire supply chain and product life cycle by 2030, using a 2015 baseline. The commitment covers Scope 1, 2, and 3 emissions.*

**Ask your coding agent to:**

Loop through all three passages, extract structured data from each using the same schema, and put the results into a pandas DataFrame (a table). Print the table.

**Checkpoint:** You should see a table with 3 rows (Amazon, BP, Apple) and columns for each field. Target years should be 2040, 2050, and 2030 respectively.

**Think about:** You just did in a few seconds what would take someone 15 minutes copying and pasting from a chat window. And this was only 3 companies. The exact same pattern works for 50 or 500 — which is what we'll do with real PDFs in Session 9.

---

## What you built today

- A connection to an AI model from Python (not a chat window)
- A schema that defines exactly what data you want
- Structured extraction that returns JSON, not paragraphs
- A multi-model comparison that reveals ambiguity
- A batch pipeline that processes multiple sources into a table

The code your agent wrote is the foundation for everything in Sessions 9 and 10.

**Save your work.** Make sure the Python file your agent created is saved in your workspace. You'll build on these patterns next session.
