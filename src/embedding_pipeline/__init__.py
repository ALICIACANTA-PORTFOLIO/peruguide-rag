"""
Embedding Pipeline Module

Generates vector embeddings for text chunks using sentence-transformers.

Components:
    - models: Embedding model wrappers
    - batch_processor: Batch processing for efficiency

Model: paraphrase-multilingual-mpnet-base-v2 (768-dim)
Justification: Hands-On LLMs p.145 - "Multilingual transformers excel at cross-lingual search"
"""
