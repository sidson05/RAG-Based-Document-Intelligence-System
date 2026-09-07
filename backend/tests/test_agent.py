import pytest
import pandas as pd
from backend.app.agent.router import query_router
from backend.app.agent.code_interpreter import code_interpreter
from backend.app.agent.synthesizer import synthesizer
from backend.app.agent.verifier import verifier
from backend.app.core.models import QueryRoute, TableData, BoundingBox, DocumentChunk

def test_query_router():
    assert query_router.route_query("What is the total revenue across all quarters?") == QueryRoute.TABLE_CALCULATION
    assert query_router.route_query("Calculate the percentage increase in net profit") == QueryRoute.TABLE_CALCULATION
    assert query_router.route_query("What does the signature or seal look like in Figure 1?") == QueryRoute.VISUAL_INSPECTION
    assert query_router.route_query("What are the main architectural paradigms discussed?") == QueryRoute.DIRECT_TEXT
    assert query_router.route_query("Compare the introduction with future challenges") == QueryRoute.MULTI_HOP_REASONING

def test_code_interpreter_execution():
    df = pd.DataFrame({
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Revenue": [100.0, 150.0, 200.0, 250.0],
        "Expenses": [80.0, 90.0, 110.0, 130.0]
    })
    
    code = "net_profit = df['Revenue'].sum() - df['Expenses'].sum()\nprint(f'Total Net Profit: {net_profit}')"
    success, output = code_interpreter.execute_code(code, df)
    assert success
    assert "Total Net Profit: 290.0" in output

def test_synthesizer_and_verifier():
    chunk = DocumentChunk(
        chunk_id="chk_1",
        doc_id="doc_1",
        text="The document intelligence survey covers over 300 research papers published between 2021 and 2025.",
        page=1,
        bbox=BoundingBox(x0=50, y0=50, x1=500, y1=100, page=1)
    )
    
    answer, citations = synthesizer.synthesize_answer(
        query="How many papers are reviewed in the survey?",
        retrieved_chunks=[chunk]
    )
    assert len(answer) > 0
    assert "300" in answer
    assert len(citations) >= 1
    assert citations[0].page == 1
    
    # Verify faithfulness
    is_faithful, notes = verifier.verify_faithfulness(
        query="How many papers are reviewed in the survey?",
        answer=answer,
        retrieved_chunks=[chunk]
    )
    assert is_faithful
