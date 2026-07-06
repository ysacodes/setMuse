"""
StylistAgent — the orchestrator that ties the whole multi-agent system
together. This is the core "multi-agent systems built with ADK" concept:

                     ┌────────────────────┐
                     │   RootAgent (you)  │
                     └─────────┬──────────┘
                               │  SequentialAgent
              ┌────────────────┴────────────────┐
              │        ParallelAgent             │
              │  ┌───────────────┐ ┌───────────┐ │
              │  │ WeatherAgent  │ │CalendarAgt│ │  <- run concurrently,
              │  └───────────────┘ └───────────┘ │     independent context
              └────────────────┬──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   OutfitCuratorAgent │  <- applies outfit_curation
                    │  (LlmAgent + skill)  │     skill against wardrobe DB
                    └──────────────────────┘

Weather and calendar lookups don't depend on each other, so they're modeled
as an ADK `ParallelAgent`; the result is then handed sequentially to the
curator agent via an ADK `SequentialAgent`. In MOCK_MODE we run the same
logical pipeline with plain Python calls (no model needed) so the full
happy-path is exercised in `app.py` without any API key.
"""
from __future__ import annotations

from typing import Any

from agents.calendar_agent import get_todays_calendar_events
from agents.wardrobe_manager import Garment, WardrobeManager
from agents.weather_agent import get_weather_forecast
from config import FORMALITY_SCALE, MOCK_MODE


def _formality_distance(a: str, b: str) -> int:
    try:
        return abs(FORMALITY_SCALE.index(a) - FORMALITY_SCALE.index(b))
    except ValueError:
        return 99


_OCCASION_TO_FORMALITY = {
    "business": "business",
    "athletic": "casual",
    "romantic": "smart-casual",
    "formal": "formal",
    "casual": "casual",
}


def curate_outfits(
    wardrobe: WardrobeManager,
    weather: dict[str, Any],
    calendar_ctx: dict[str, Any],
    max_outfits: int = 3,
) -> list[dict[str, Any]]:
    """Pure-Python implementation of the `outfit_curation` skill (see
    skills/outfit_curation.skill.md) — used directly in MOCK_MODE and also
    callable as the deterministic fallback if the LLM curator errors out."""
    target_formality = _OCCASION_TO_FORMALITY.get(calendar_ctx["occasion"], "casual")
    season = weather["season"]
    needs_warmth = weather["temperature_c"] < 15
    needs_rain_layer = weather["precipitation_chance"] > 50

    items = wardrobe.list_garments()
    candidates = [
        g for g in items
        if season in g.season_fit and _formality_distance(g.formality, target_formality) <= 1
    ]

    bases = [g for g in candidates if g.garment_type in ("dress", "set")]
    tops = [g for g in candidates if g.garment_type == "top"]
    bottoms = [g for g in candidates if g.garment_type == "bottom"]
    outerwear = [g for g in candidates if g.garment_type == "outerwear" and g.warmth_score >= 3]
    shoes = [g for g in candidates if g.garment_type == "shoes"]

    outfits: list[dict[str, Any]] = []

    def _score(pieces: list[Garment]) -> float:
        # Reward tag overlap (coherence) and reward items worn less recently.
        all_tags = [t for p in pieces for t in p.style_tags]
        coherence = len(all_tags) - len(set(all_tags))  # more shared tags -> lower is fine here
        rotation_bonus = -sum(p.times_worn for p in pieces)
        return coherence * 2 + rotation_bonus

    def _finalize(pieces: list[Garment]) -> dict[str, Any]:
        if (needs_warmth or needs_rain_layer) and outerwear:
            best_outer = max(outerwear, key=lambda g: g.warmth_score)
            pieces = pieces + [best_outer]
        if shoes:
            pieces = pieces + [min(shoes, key=lambda g: g.times_worn)]
        rationale = (
            f"{weather['temperature_c']}°C and {weather['condition']} today, "
            f"with a '{calendar_ctx['occasion']}' occasion ({', '.join(calendar_ctx['events'])}) "
            f"→ picked {target_formality} pieces rated for {season}."
        )
        if needs_warmth:
            rationale += " Added a warmer outer layer for the cooler temperature."
        if needs_rain_layer:
            rationale += f" {weather['precipitation_chance']}% chance of rain, so bring a weatherproof layer."
        return {
            "pieces": [g.garment_type + ": " + g.dominant_color + " (" + ", ".join(g.style_tags) + ")" for g in pieces],
            "image_paths": [g.image_path for g in pieces],
            "rationale": rationale,
            "score": _score(pieces),
        }

    seen = set()
    for base in sorted(bases, key=lambda g: g.times_worn):
        combo = _finalize([base])
        key = tuple(combo["image_paths"])
        if key not in seen:
            outfits.append(combo)
            seen.add(key)

    for top in sorted(tops, key=lambda g: g.times_worn):
        for bottom in sorted(bottoms, key=lambda g: g.times_worn):
            combo = _finalize([top, bottom])
            key = tuple(combo["image_paths"])
            if key not in seen:
                outfits.append(combo)
                seen.add(key)

    outfits.sort(key=lambda o: o["score"], reverse=True)
    return outfits[:max_outfits]


def plan_todays_outfits(
    wardrobe: WardrobeManager, location: str, date_iso: str
) -> dict[str, Any]:
    """End-to-end pipeline entry point used by app.py."""
    weather = get_weather_forecast(location, date_iso)
    calendar_ctx = get_todays_calendar_events(date_iso)
    outfits = curate_outfits(wardrobe, weather, calendar_ctx)
    return {"weather": weather, "calendar": calendar_ctx, "outfits": outfits}


def build_stylist_pipeline():
    """Builds the real ADK Sequential(Parallel(...), CuratorAgent) pipeline
    for live (non-mock) execution. See module docstring for the diagram."""
    from google.adk.agents import Agent, ParallelAgent, SequentialAgent
    from google.adk.tools import FunctionTool

    from agents.calendar_agent import build_calendar_agent
    from agents.weather_agent import build_weather_agent
    from security.guardrails import after_model_callback, before_tool_callback

    context_gatherer = ParallelAgent(
        name="context_gatherer",
        sub_agents=[build_weather_agent(), build_calendar_agent()],
    )

    curator = Agent(
        name="outfit_curator_agent",
        model="gemini-2.5-flash",
        instruction=open("skills/outfit_curation.skill.md").read(),
        tools=[FunctionTool(_list_wardrobe_items_tool)],
        before_tool_callback=before_tool_callback,
        after_model_callback=after_model_callback,
        description="Curates ranked outfit options from the closet given weather+occasion.",
    )

    return SequentialAgent(
        name="closetmuse_stylist",
        sub_agents=[context_gatherer, curator],
    )


def _list_wardrobe_items_tool() -> list[dict[str, Any]]:
    """Tool function exposed to the curator LlmAgent (and mirrored on the
    MCP server as `list_wardrobe_items`)."""
    wardrobe = WardrobeManager()
    return [g.to_row() | {"id": g.id} for g in wardrobe.list_garments()]
