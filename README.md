# Trackzio – Data Scraping & LLM Enrichment Assignment

## Overview
This project implements a complete end-to-end data pipeline for building **high-quality, AI-ready structured datasets** from public antique listings.

The pipeline simulates a real production workflow at Trackzio and focuses on:
- Automated web scraping from public sources
- Data cleaning and normalization
- LLM-based semantic enrichment with structured outputs
- Preparing datasets for downstream AI systems (search, embeddings, ranking)

The emphasis is on **robust engineering, conservative enrichment, and clear reasoning**, rather than UI or polish.

---

## 1. Source Selection

### Source Used
**Public antique listing pages (search-based public listings)**

### Why This Source
- No login or paywall required  
- Rich natural-language descriptions suitable for semantic enrichment  
- Covers multiple antique categories  
- Public, reproducible, and legally accessible  

### Categories Covered
- Furniture  
- Ceramics / Pottery  
- Vintage / Decorative Items  

A total of **30+ unique antique items** were scraped across these categories.

---

## 2. Scraping Approach

### Tools & Libraries
- **Language:** Python  
- **Libraries:** `requests`, `BeautifulSoup`, `pandas`

### Scraping Strategy
- Keyword-based search pages are used instead of brittle category endpoints  
- Individual item detail pages are extracted from search results  
- Fully automated scraping (no manual copying or browser extensions)

### Pagination Handling
- A fixed number of items are collected per category from the first search result pages  
- Pagination support can be extended by iterating page parameters if required

### Rate Limiting & Robustness
- Randomized delays between requests to avoid throttling  
- Graceful handling of:
  - Missing fields  
  - Network timeouts  
  - Blocked or unavailable pages  

Scraping failures do **not crash the pipeline**, ensuring robustness.

---

## 3. Data Cleaning & Normalization

The following deterministic steps are applied:

- Removal of HTML artifacts from raw descriptions  
- Price normalization into numeric values where available  
- Duplicate removal using `item_title + description`  
- Missing values preserved as `None` (no forced inference)  
- Category labels normalized for consistency  

All cleaning logic is **rule-based and reproducible**.

---

## 4. LLM-Based Data Enrichment (Key Evaluation Area)

### Model Used
**Google Gemini – `gemini-3-flash-preview`**

### Why Gemini
- Strong reasoning capability for historical and descriptive text  
- Cost-efficient for batch enrichment  
- Supports structured JSON outputs with schema enforcement  

### Enrichment Strategy
- Input: **item title + cleaned description**
- The model is instructed to act as an **expert antique appraiser**
- Strict schema validation using **Pydantic**
- Low temperature (`0.1`) to minimize hallucinations
- Exponential backoff and retry handling for rate limits

### Example Prompt (Simplified)
You are an expert antique appraiser.
Analyze the following item and return structured JSON fields only.

Antique Item: <item_title>
Description: <item_description>


### Enriched Fields
- `era_or_time_period`
- `estimated_year_range`
- `region_of_origin`
- `functional_use`
- `material`
- `style`
- `short_ai_summary` (2–3 sentences)
- `confidence_score` (0–1)

### Reliability Measures
- Strict response schema enforcement (`response_schema`)
- JSON-only responses (`response_mime_type="application/json"`)
- Retry logic with exponential backoff for `429 / RESOURCE_EXHAUSTED` errors
- Per-item delay to respect API limits

---

## 5. Final Dataset

**Output Format:** CSV  

Each record includes:
- Raw scraped fields  
- Cleaned and normalized fields  
- LLM-enriched semantic fields  

**Output File:**
data/final_enriched_items.csv

## 6. Assumptions & Limitations

- Enrichment is based solely on **textual descriptions** (images are not analyzed)  
- Historical estimates are approximate and conservative  
- Seller-provided descriptions may be incomplete or inconsistent  
- Confidence scores reflect textual evidence strength, not ground truth  

The pipeline prioritizes **precision, explainability, and reproducibility** over speculative inference.

---

## 7. Scaling to 50k–100k Items

To scale this pipeline in production:

### Scraping
- Async scraping (`aiohttp`, Playwright)
- Distributed workers
- Proxy rotation if required

### Enrichment
- Batch LLM requests
- Prompt and response caching
- Confidence-based reprocessing
- Queue-based systems (Celery, SQS)

### Quality Control
- Low-confidence samples routed for human review
- Periodic schema validation and audits
