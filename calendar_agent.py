"""
StyleVisionAgent — Concept 1 (multi-agent system, leaf agent #1).

Given a photo of a single garment, returns structured attributes:
garment_type, style_tags (from config.STYLE_TAXONOMY), dominant_color,
formality, warmth_score, season_fit.

Built as a real `google.adk.agents.Agent` (LlmAgent) with a Gemini
multimodal model. Because Kaggle judges may not have a Gemini key on hand,
MOCK_MODE swaps in a small deterministic heuristic classifier so the whole
pipeline still runs end-to-end offline.
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any

from config import FORMALITY_SCALE, MOCK_MODE, MODEL_NAME, STYLE_TAXONOMY
from security.guardrails import validate_upload

STYLE_VISION_INSTRUCTIONS = f"""
You are a fashion-vision classifier. You will be shown one photo of a single
garment. Respond with STRICT JSON only, matching this schema:

{{
  "garment_type": one of ["dress","top","bottom","outerwear","shoes","accessory","set"],
  "style_tags": 1-3 tags from {STYLE_TAXONOMY},
  "dominant_color": a simple color word,
  "formality": one of {FORMALITY_SCALE},
  "warmth_score": integer 1 (light/summer) to 5 (heavy winter),
  "season_fit": subset of ["spring","summer","fall","winter"]
}}

Never include commentary, markdown fences, or text outside the JSON object.
"""


def _mock_classify(image_path: str) -> dict[str, Any]:
    """Deterministic, filename-seeded fake classifier so demo runs are
    reproducible and don't require a model API key."""
    seed = int(hashlib.sha1(image_path.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    return {
        "garment_type": rng.choice(["dress", "top", "bottom", "outerwear", "shoes", "set"]),
        "style_tags": rng.sample(STYLE_TAXONOMY, k=rng.choice([1, 2])),
        "dominant_color": rng.choice(["black", "white", "coral", "navy", "olive", "blush", "cream"]),
        "formality": rng.choice(FORMALITY_SCALE),
        "warmth_score": rng.randint(1, 5),
        "season_fit": rng.sample(["spring", "summer", "fall", "winter"], k=rng.choice([1, 2, 3])),
    }


def build_vision_agent():
    """Constructs the ADK LlmAgent. Only imported lazily so MOCK_MODE users
    never need google-adk's model backends installed/configured."""
    from google.adk.agents import Agent

    return Agent(
        name="style_vision_agent",
        model=MODEL_NAME,
        instruction=STYLE_VISION_INSTRUCTIONS,
        description="Classifies a single garment photo into structured style attributes.",
    )


def classify_garment(image_path: str) -> dict[str, Any]:
    """Public entry point used by WardrobeManager ingestion. Validates the
    upload (security guard), then routes to the real or mock classifier."""
    validate_upload(image_path)

    if MOCK_MODE:
        return _mock_classify(image_path)

    # --- Live path: run the ADK agent once against the image ---
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = build_vision_agent()
    runner = InMemoryRunner(agent=agent, app_name="closetmuse")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    content = types.Content(
        role="user",
        parts=[
            types.Part(text="Classify this garment."),
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ],
    )
    final_text = ""
    for event in runner.run(user_id="demo_user", session_id="ingest", new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or final_text

    return json.loads(final_text)
