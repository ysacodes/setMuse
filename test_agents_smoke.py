"""
ClosetMuse — shared configuration.

MOCK_MODE lets every agent and tool in this project run end-to-end with zero
API keys, which is what judges/reviewers will hit the first time they clone
the repo. Set the real keys in .env and flip MOCK_MODE=false to go live.
"""
import os
from dataclasses import dataclass

MOCK_MODE = os.getenv("CLOSETMUSE_MOCK_MODE", "true").lower() == "true"

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "")

MODEL_NAME = os.getenv("CLOSETMUSE_MODEL", "gemini-2.5-flash")

WARDROBE_DB_PATH = os.getenv("CLOSETMUSE_DB", "wardrobe.db")

MAX_UPLOAD_MB = 8
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}

STYLE_TAXONOMY = [
    "floral", "ruffles", "minimalist", "streetwear", "athleisure",
    "formal", "business-casual", "bohemian", "preppy", "denim",
    "monochrome", "pastel", "vintage", "gothic", "cottagecore",
]

FORMALITY_SCALE = ["loungewear", "casual", "smart-casual", "business", "formal", "black-tie"]


@dataclass(frozen=True)
class Theme:
    """UI theme tokens — kept here so the (future) web front-end and the
    mockup generator in ui_mockups/ share a single source of truth."""
    cream: str = "#F0EDDC"
    tan: str = "#B9AC8C"
    espresso: str = "#845F4A"
    blush: str = "#DFA0AA"
    heading_font: str = "Lavonia"          # decorative display font (logo/H1)
    body_font: str = "Nunito"              # UI body font


THEME = Theme()
