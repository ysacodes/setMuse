"""
WeatherAgent — Concept 1 (leaf agent #2) + Concept 2 (MCP server).

`get_weather_forecast` is defined once as a plain Python function and is
exposed two ways:
  1. Wrapped as an ADK FunctionTool for the in-process WeatherAgent.
  2. Registered on the MCP server in mcp_server/closet_mcp_server.py, so any
     external MCP-compatible client (Claude Desktop, another ADK app, the
     MCP Inspector) can call the exact same tool.

MOCK_MODE returns a small deterministic seasonal forecast so the agent chain
runs without an OpenWeather API key.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random
from typing import Any

from config import MOCK_MODE, OPENWEATHER_API_KEY


def _season_for(date: dt.date) -> str:
    month = date.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def get_weather_forecast(location: str, date_iso: str) -> dict[str, Any]:
    """Tool function: returns forecast + derived season for `location` on
    `date_iso` (YYYY-MM-DD). Real implementation calls OpenWeatherMap;
    MOCK_MODE fabricates a plausible, reproducible forecast instead.

    Args:
        location: city name or "lat,lon" string.
        date_iso: ISO date string for the outfit day.
    Returns:
        dict with temperature_c, condition, precipitation_chance, season.
    """
    date = dt.date.fromisoformat(date_iso)
    season = _season_for(date)

    if MOCK_MODE or not OPENWEATHER_API_KEY:
        seed = int(hashlib.sha1(f"{location}{date_iso}".encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        base_temp = {"winter": 8, "spring": 17, "summer": 29, "fall": 18}[season]
        return {
            "location": location,
            "date": date_iso,
            "temperature_c": round(base_temp + rng.uniform(-4, 4), 1),
            "condition": rng.choice(["clear", "partly cloudy", "overcast", "light rain", "windy"]),
            "precipitation_chance": rng.randint(0, 70),
            "season": season,
            "source": "mock",
        }

    import requests
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    first = data["list"][0]
    return {
        "location": location,
        "date": date_iso,
        "temperature_c": first["main"]["temp"],
        "condition": first["weather"][0]["main"].lower(),
        "precipitation_chance": int(first.get("pop", 0) * 100),
        "season": season,
        "source": "openweathermap",
    }


def build_weather_agent():
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool

    return Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        instruction=(
            "Call get_weather_forecast for the requested location/date and "
            "summarize it in one sentence useful for choosing clothing "
            "(temperature, precipitation, wind if notable)."
        ),
        tools=[FunctionTool(get_weather_forecast)],
        description="Fetches and summarizes the weather for the outfit day.",
    )
