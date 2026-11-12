import pandas as pd
import numpy as np

# [1/4] Loading raw data (Now with corrupted records!)
print("[1/4] Loading raw data...")
raw_data = [
    {"cust_id": 101, "name": "Alice Smith", "state": "california", "raw_address": "123 Main St, CA"},
    {"cust_id": 102, "name": "Bob Jones", "state": "TX", "raw_address": "789 Elm Street, TX"},
    {"cust_id": 103, "name": "Charlie Brown", "state": "NY", "raw_address": "456 Broadway, NY"},
    {"cust_id": 101, "name": "Alice Smith", "state": "california", "raw_address": "123 Main St, CA"}, # Exact Duplicate
    {"cust_id": None, "name": "Ghost User", "state": "NV", "raw_address": "Secret Base"}, # NULL ID
    {"cust_id": 105, "name": "", "state": "WA", "raw_address": "No Name St"}, # Empty Name
    {"cust_id": "ABC", "name": "Bad Type", "state": "FL", "raw_address": "String ID St"} # Wrong Data Type
]
df = pd.DataFrame(raw_data)

# [2/4] Data Quality & Validation Layer
print("[2/4] Running Data Quality Checks...")

# A. Deduplication
df = df.drop_duplicates()

# B. Enforce Non-Null Constraints (Drop missing IDs or addresses)
df = df.dropna(subset=["cust_id", "raw_address"])

# C. Enforce Business Rules (Name cannot be empty or just whitespace)
df["name"] = df["name"].replace(r'^\s*$', np.nan, regex=True)
df = df.dropna(subset=["name"])

# D. Enforce Data Types & Catch Type Mismatches
# We force cust_id to numeric. If it's a string like "ABC", it becomes NaN, which we then drop.
df["cust_id"] = pd.to_numeric(df["cust_id"], errors="coerce")

# Separate the good data from the bad
good_records = df.dropna(subset=["cust_id"]).copy()
good_records["cust_id"] = good_records["cust_id"].astype(int) # Safely cast to INT

# The "Dead Letter Queue" (DLQ) - Records that failed validation
bad_records_count = len(raw_data) - len(good_records)

print(f"  -> Passed Validation: {len(good_records)}")
print(f"  -> Failed Validation (Dropped/DLQ): {bad_records_count}")

# Now pass ONLY `good_records` to the LLM step...
# (Update your LLM loop below to iterate over good_records instead of df)