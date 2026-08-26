"""MarketVoice SEA — FastAPI Microservice Layer.

Phase 11: Operational Automation & Inference Service.
Exposes NLP inference (Aspect/Issue classification, sentiment/rating proxy)
and contextual Decision Support System (DSS) priority scoring via REST endpoints.
"""
from marketvoice.api.application import create_app

__all__ = ["create_app"]
