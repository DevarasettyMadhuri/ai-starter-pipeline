import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
import pandas as pd
import ollama

app = FastAPI(title="Curated Customer AI Service")
DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/devdb"
engine = create_engine(DB_URL)

class RawCustomerInput(BaseModel):
    cust_id: int
    name: str
    state: str
    raw_address: str

@app.get("/")
def root():
    return {"status": "online", "message": "AI Data Pipeline Service Running"}

@app.get("/customers")
def get_customers():
    try:
        df = pd.read_sql("SELECT * FROM public.curated_customers ORDER BY cust_id ASC", engine)
        return {"total": len(df), "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean-record")
def process_record(customer: RawCustomerInput):
    prompt = (
        f'Given the messy customer name "{customer.name}" and address "{customer.raw_address}", '
        'return ONLY a raw JSON object with keys "clean_name" (Proper Title Case) '
        'and "clean_address" (standardized format). No explanations, no markdown.'
    )
    try:
        response = ollama.chat(
            model="qwen2.5-coder:1.5b",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["message"]["content"].strip()
        cleaned_json = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned_json)
        clean_name = parsed.get("clean_name", customer.name.title())
        clean_address = parsed.get("clean_address", customer.raw_address)
    except Exception:
        clean_name = customer.name.title()
        clean_address = customer.raw_address

    new_row = pd.DataFrame([{
        "cust_id": customer.cust_id,
        "clean_name": clean_name,
        "clean_address": clean_address,
        "state": customer.state
    }])

    new_row.to_sql("curated_customers", engine, if_exists="append", index=False)

    return {
        "status": "success",
        "saved_record": {
            "cust_id": customer.cust_id,
            "clean_name": clean_name,
            "clean_address": clean_address,
            "state": customer.state
        }
    }
