"""
Retrieval Pipeline Module

Handles document retrieval and optional reranking.

Components:
    - retrievers: Dense and hybrid retrieval strategies
    - rerankers: Cross-encoder reranking for precision

Configuration:
    - Top-K: 5 documents
    - Threshold: 0.7 similarity score
    - Metric: Cosine similarity

Justification: Hands-On LLMs p.198 - "Top-k=5 balances precision/recall"
"""
