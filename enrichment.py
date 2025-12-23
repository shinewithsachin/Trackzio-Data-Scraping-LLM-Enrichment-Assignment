import pandas as pd
import json
import time
import os
import random
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class AntiqueEnrichment(BaseModel):
    era_or_time_period: str
    estimated_year_range: str
    region_of_origin: str
    functional_use: str
    material: str
    style: str
    short_ai_summary: str
    confidence_score: float

def enrich_item_with_retry(title, description, max_retries=5):
    """Enriches data with exponential backoff for 429 errors."""
    
    wait_time = 35 

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"Antique Item: {title}\nDescription: {description}",
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert antique appraiser. Provide structured data based on the item provided.",
                    response_mime_type="application/json",
                    response_schema=AntiqueEnrichment, # Enforces strict JSON structure
                    temperature=0.1,
                )
            )
            return json.loads(response.text)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                jitter = random.uniform(1, 5)
                total_wait = wait_time + jitter
                print(f"\n[Attempt {attempt+1}] Rate limit hit. Waiting {int(total_wait)}s...")
                time.sleep(total_wait)
                wait_time *= 2 
            else:
                print(f"\n[!] Unexpected Error: {error_str}")
                return None
    return None

def run_pipeline():
    try:
        df = pd.read_csv("data/clean_items.csv")
    except FileNotFoundError:
        print("Error: data/clean_items.csv not found.")
        return

    enriched_rows = []
    print(f"Starting enrichment for {len(df)} items...")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        result = enrich_item_with_retry(row["item_title"], row["description_clean"])
        
        if result:
            enriched_rows.append({**row.to_dict(), **result})
        
        time.sleep(15)

    if enriched_rows:
        final_df = pd.DataFrame(enriched_rows)
        final_df.to_csv("data/final_enriched_items.csv", index=False)
        print(f"\n✅ Pipeline completed! Saved to data/final_enriched_items.csv")

if __name__ == "__main__":
    run_pipeline()