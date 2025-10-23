"""
Inference Pipeline Module

Orchestrates RAG chain: Retrieval → Context Assembly → LLM Generation → Post-processing

Components:
    - llm: LLM client and prompt templates
    - chains: LangChain RAG orchestration
    - postprocessing: Citation formatting and confidence scoring

LLM: Mistral-7B-Instruct-v0.3
Temperature: 0.3 (factual responses)
Max Tokens: 512

Justification: LLM Handbook p.289 - "Open-source models offer production-grade performance"
"""
