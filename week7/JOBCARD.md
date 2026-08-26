# Job card

**What it does:** Enriches a scraped book record with an inferred genre, target audience, reading mood, a one-sentence summary, and quality flags.

**Input:**
```json
{
  "title": "string, 1-300 characters",
  "price_gbp": "float >= 0.0",
  "rating_text": "string, 1-20 characters",
  "description": "string or null, max 4000 characters"
}