import pytest
from fastapi.testclient import TestClient
from backend.app.api.main import app

client = TestClient(app)
SAMPLE_PDF = "data/sample_docs/benchmark_paper.pdf"

def test_e2e_pipeline():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    
    # 2. Upload and index benchmark document
    with open(SAMPLE_PDF, "rb") as f:
        upload_res = client.post(
            "/api/upload",
            files={"file": ("benchmark_paper.pdf", f, "application/pdf")}
        )
    assert upload_res.status_code == 200, f"Upload error: {upload_res.text}"
    meta = upload_res.json()
    assert meta["num_pages"] == 3
    assert meta["num_tables"] >= 1
    assert meta["num_chunks"] > 0
    doc_id = meta["doc_id"]
    
    # 3. Test Direct Text Query
    query_text = "What is the focus of document intelligence and how many papers are surveyed?"
    q_res = client.post("/api/query", json={"query": query_text, "doc_id": doc_id})
    assert q_res.status_code == 200
    data = q_res.json()
    assert len(data["answer"]) > 0
    assert len(data["citations"]) > 0
    assert data["citations"][0]["page"] == 1
    assert data["verification_passed"] is True
    
    # 4. Test Tabular Calculation Query
    calc_query = "Calculate the total revenue from Q1 to Q4 from the table"
    c_res = client.post("/api/query", json={"query": calc_query, "doc_id": doc_id})
    assert c_res.status_code == 200
    calc_data = c_res.json()
    assert calc_data["route_taken"] == "table_calculation"
    assert calc_data["calculation_code"] is not None
    # Q1(120.5) + Q2(145.0) + Q3(180.2) + Q4(210.0) = 655.7
    assert "655.7" in str(calc_data["calculation_result"]) or "655.7" in calc_data["answer"]
    assert len(calc_data["citations"]) > 0
    assert calc_data["citations"][0]["page"] == 2
    
    # 5. Test Citation Highlighting endpoint
    cite_bbox = calc_data["citations"][0]["bbox"]
    h_res = client.post(f"/api/documents/{doc_id}/highlight", json={"bbox": cite_bbox})
    assert h_res.status_code == 200
    assert h_res.headers["content-type"] == "image/png"
    assert len(h_res.content) > 1000
