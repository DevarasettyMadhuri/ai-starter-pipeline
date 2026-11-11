from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_customers():
    response = client.get("/customers")
    assert response.status_code == 200
    payload = response.json()
    assert "total" in payload
    assert "data" in payload
    assert isinstance(payload["data"], list)

def test_clean_record_endpoint():
    sample_payload = {
        "cust_id": 999,
        "name": "tEsT uSeR",
        "state": "WA",
        "raw_address": "100 pine st suite 200, seattle, wa"
    }
    response = client.post("/clean-record", json=sample_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["saved_record"]["cust_id"] == 999
    assert res_data["saved_record"]["clean_name"] == "Test User"
