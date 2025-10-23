"""
Evaluation Module

RAGAS-based evaluation for RAG system quality assessment.

Metrics:
    - Faithfulness: Response grounded in retrieved context (>0.85)
    - Answer Relevancy: Response addresses the question (>0.80)
    - Context Precision: Retrieved chunks are relevant (>0.75)
    - Context Recall: All necessary info retrieved (>0.70)

Test Dataset: 100+ curated Q&A pairs with ground truth

Justification: LLM Handbook p.272 - "RAGAS specifically designed for RAG evaluation"
"""
