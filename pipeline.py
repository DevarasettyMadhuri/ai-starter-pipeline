import json
import pandas as pd
from sqlalchemy import create_engine
import ollama

# 1. Sample dirty customer dataset (duplicates, inconsistent casing, messy addresses)
raw_data = [
    {"cust_id": 101, "name": "alice smith", "state": "california", "raw_address": "123 main st, apt 4B, los angeles, ca"},
    {"cust_id": 102, "name": "BOB JONES", "state": "TX", "raw_address": "789 elm street, dallas, tx"},
    {"cust_id": 101, "name": "alice smith", "state": "california", "raw_address": "123 main st, apt 4B, los angeles, ca"},
    {"cust_id": 103, "name": "charlie brown", "state": "NY", "raw_address": "456 broadway suite 12, new york, ny"}
]

print("[1/4] Loading raw data...")
df = pd.DataFrame(raw_data)
print(f"Raw record count: {len(df)}")

# 2. Rule-based Deduplication
print("[2/4] Removing exact duplicates...")
df = df.drop_duplicates(subset=["cust_id"]).reset_index(drop=True)
print(f"Deduplicated count: {len(df)}")

# 3. AI Standardization with local Ollama
print("[3/4] Running local LLM (qwen2.5-coder:1.5b) to standardize records...")

def standardize_record(row):
    prompt = (
        f'Given the messy customer name "{row["name"]}" and address "{row["raw_address"]}", '
        'return ONLY a raw JSON object with keys "clean_name" (Proper Title Case) '
        'and "clean_address" (standardized format). No explanations, no markdown.'
    )
    response = ollama.chat(
        model="qwen2.5-coder:1.5b",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response["message"]["content"].strip()
    try:
        cleaned_json = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned_json)
        return parsed.get("clean_name", row["name"].title()), parsed.get("clean_address", row["raw_address"])
    except Exception:
        return row["name"].title(), row["raw_address"]

cleaned = [standardize_record(row) for _, row in df.iterrows()]
df["clean_name"] = [c[0] for c in cleaned]
df["clean_address"] = [c[1] for c in cleaned]

final_df = df[["cust_id", "clean_name", "clean_address", "state"]]
print("\n--- Processed Curated Records ---")
print(final_df)

# 4. Load into PostgreSQL
print("\n[4/4] Writing to PostgreSQL (devdb)...")
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/devdb")
final_df.to_sql("curated_customers", engine, if_exists="replace", index=False)
print("\nPipeline complete! Records successfully stored in 'curated_customers' table.")
