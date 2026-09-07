import re
from ..core.models import QueryRoute

class QueryRouter:
    """
    Intelligent Query Classifier & Router (Ke et al. Agentic Paradigm).
    Routes queries to specialized agentic tools:
    - TABLE_CALCULATION: For arithmetic, aggregations, percentages on tables
    - VISUAL_INSPECTION: For charts, diagrams, signatures, layout appearance
    - DIRECT_TEXT: Standard textual information extraction
    - MULTI_HOP_REASONING: For cross-section comparisons
    """
    
    CALC_KEYWORDS = {
        "calculate", "sum", "total", "average", "mean", "percentage", "growth",
        "ratio", "difference", "increase", "decrease", "minimum", "maximum",
        "median", "count", "net profit", "revenue", "how much", "how many"
    }
    
    VISUAL_KEYWORDS = {
        "chart", "diagram", "figure", "graph", "plot", "signature", "stamp",
        "logo", "image", "visual", "layout", "color", "photo", "drawing"
    }
    
    MULTI_HOP_KEYWORDS = {
        "compare", "contrast", "relationship between", "difference between",
        "how does section", "both", "across the document", "overall trend"
    }

    def route_query(self, query: str, has_table_context: bool = False) -> QueryRoute:
        q_lower = query.lower()
        words = set(re.findall(r"\b\w+\b", q_lower))
        
        # Check visual first
        if any(vk in q_lower for vk in self.VISUAL_KEYWORDS):
            return QueryRoute.VISUAL_INSPECTION
            
        # Check calculation (especially if query has arithmetic terms and table is present)
        if any(ck in q_lower for ck in self.CALC_KEYWORDS):
            return QueryRoute.TABLE_CALCULATION
            
        # Check multi-hop
        if any(mk in q_lower for mk in self.MULTI_HOP_KEYWORDS):
            return QueryRoute.MULTI_HOP_REASONING
            
        if has_table_context and ("what is" in q_lower or "value of" in q_lower):
            # Might be table lookup
            return QueryRoute.TABLE_CALCULATION
            
        return QueryRoute.DIRECT_TEXT

query_router = QueryRouter()
