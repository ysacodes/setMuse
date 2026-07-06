"""
root_agent — the object `adk web` / `adk run` looks for.

Wraps the Stylist pipeline (agents/stylist_agent.py) as the single exported
agent for the ADK CLI/dev-UI, with the security callbacks from
security/guardrails.py attached. Only constructed in live mode — MOCK_MODE
users interact with the same logic through app.py instead, since building
this object requires google-adk's model backends to be configured.
"""
from __future__ import annotations

from config import MOCK_MODE

if not MOCK_MODE:
    from agents.stylist_agent import build_stylist_pipeline

    root_agent = build_stylist_pipeline()
else:
    root_agent = None  # see app.py for the MOCK_MODE demo entry point
