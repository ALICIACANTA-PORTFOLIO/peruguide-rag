"""
API Module - FastAPI REST API for PeruGuide AI

This module provides RESTful endpoints for interacting with the RAG system.

Routers:
    - query: /api/v1/query - Main RAG query endpoint
    - feedback: /api/v1/feedback - User feedback collection
    - admin: /api/v1/health, /api/v1/metrics - Admin endpoints

Middleware:
    - CORS: Cross-Origin Resource Sharing
    - Rate Limiting: Request throttling
    - Auth: Optional authentication (JWT)
    - Logging: Request/response logging

Usage:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

__version__ = "0.1.0"
