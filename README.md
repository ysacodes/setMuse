"""
CalendarAgent — Concept 1 (leaf agent #3).

Reads the day's calendar events and infers an "occasion" that the Stylist
agent uses to pick formality/vibe (e.g. "1:1 with VP" -> business,
"yoga class" -> athleisure, "dinner reservation" -> smart-casual).

Calendar event text is untrusted (anyone can put arbitrary text in an event
title if they can invite you), so every event summary is passed through
`screen_for_injection` before it reaches a prompt — this is the other half
of the security-guardrail story alongside upload validation.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from config import GOOGLE_CALENDAR_CREDENTIALS, MOCK_MODE
from security.guardrails import screen_for_injection

_OCCASION_KEYWORDS = {
    "business": ["meeting", "client", "interview", "board", "review", "1:1", "standup"],
    "athletic": ["gym", "yoga", "run", "workout", "pilates", "hike"],
    "romantic": ["date night", "anniversary", "dinner reservation"],
    "formal": ["wedding", "gala", "ceremony"],
    "casual": ["brunch", "coffee", "errands", "shopping"],
}

_MOCK_CALENDARS = {
    "monday": ["9:00 Team Standup", "14:00 Client Presentation"],
    "tuesday": ["7:00 Yoga Class", "18:00 Dinner Reservation - Anniversary"],
    "wednesday": ["10:00 1:1 with Manager", "no other events"],
    "thursday": ["12:00 Coffee with Priya", "16:00 Gym Session"],
    "friday": ["No meetings", "19:00 Friends Brunch (moved to evening)"],
    "saturday": ["Free day"],
    "sunday": ["11:00 Family Brunch"],
}


def get_todays_calendar_events(date_iso: str) -> dict[str, Any]:
    """Tool function: returns raw event titles + an inferred primary
    occasion for `date_iso`. Real implementation calls the Google Calendar
    API; MOCK_MODE uses a fixed weekly pattern so demos are reproducible.

    Args:
        date_iso: ISO date string (YYYY-MM-DD).
    Returns:
        dict with events (list[str]) and occasion (str).
    """
    date = dt.date.fromisoformat(date_iso)
    weekday = date.strftime("%A").lower()

    if MOCK_MODE or not GOOGLE_CALENDAR_CREDENTIALS:
        events = _MOCK_CALENDARS.get(weekday, ["Free day"])
    else:
        events = _fetch_real_calendar(date_iso)

    safe_events = [screen_for_injection(e) for e in events]
    occasion = _infer_occasion(safe_events)
    return {"date": date_iso, "events": safe_events, "occasion": occasion}


def _infer_occasion(events: list[str]) -> str:
    joined = " ".join(events).lower()
    for occasion, keywords in _OCCASION_KEYWORDS.items():
        if any(kw in joined for kw in keywords):
            return occasion
    return "casual"


def _fetch_real_calendar(date_iso: str) -> list[str]:  # pragma: no cover
    """Placeholder for the real Google Calendar API integration.
    Swap in google-api-python-client's `events().list()` call here using
    GOOGLE_CALENDAR_CREDENTIALS (OAuth token / service account path)."""
    raise NotImplementedError(
        "Wire up google-api-python-client here; see README 'Going live' section."
    )


def build_calendar_agent():
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool

    return Agent(
        name="calendar_agent",
        model="gemini-2.5-flash",
        instruction=(
            "Call get_todays_calendar_events for the requested date and state "
            "the inferred occasion plus a one-line justification."
        ),
        tools=[FunctionTool(get_todays_calendar_events)],
        description="Infers today's occasion/dress-code context from the calendar.",
    )
