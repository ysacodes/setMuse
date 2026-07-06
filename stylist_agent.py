"""
WardrobeManager — persistence layer for the user's closet library.

Not an "agent" in the ADK sense; it's the tool-backing store that the vision
agent writes into and the stylist agent reads from. Kept as plain SQLite so
the whole capstone runs with zero external services.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any

from config import WARDROBE_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS garments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    garment_type TEXT NOT NULL,      -- e.g. dress, top, bottom, outerwear, shoes, accessory
    style_tags TEXT NOT NULL,        -- JSON list, e.g. ["floral", "ruffles"]
    dominant_color TEXT,
    formality TEXT,                  -- one of FORMALITY_SCALE
    warmth_score INTEGER,            -- 1 (light) - 5 (heavy winter)
    season_fit TEXT,                 -- JSON list e.g. ["spring", "summer"]
    times_worn INTEGER DEFAULT 0,
    last_worn_ts REAL,
    created_ts REAL
);
"""


@dataclass
class Garment:
    id: int | None
    image_path: str
    garment_type: str
    style_tags: list[str]
    dominant_color: str
    formality: str
    warmth_score: int
    season_fit: list[str]
    times_worn: int = 0
    last_worn_ts: float | None = None
    created_ts: float = field(default_factory=time.time)

    def to_row(self) -> dict[str, Any]:
        return {
            "image_path": self.image_path,
            "garment_type": self.garment_type,
            "style_tags": json.dumps(self.style_tags),
            "dominant_color": self.dominant_color,
            "formality": self.formality,
            "warmth_score": self.warmth_score,
            "season_fit": json.dumps(self.season_fit),
            "times_worn": self.times_worn,
            "last_worn_ts": self.last_worn_ts,
            "created_ts": self.created_ts,
        }

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Garment":
        return Garment(
            id=row["id"],
            image_path=row["image_path"],
            garment_type=row["garment_type"],
            style_tags=json.loads(row["style_tags"]),
            dominant_color=row["dominant_color"],
            formality=row["formality"],
            warmth_score=row["warmth_score"],
            season_fit=json.loads(row["season_fit"]),
            times_worn=row["times_worn"],
            last_worn_ts=row["last_worn_ts"],
            created_ts=row["created_ts"],
        )


class WardrobeManager:
    def __init__(self, db_path: str = WARDROBE_DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def add_garment(self, garment: Garment) -> int:
        row = garment.to_row()
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" * len(row))
        cur = self._conn.execute(
            f"INSERT INTO garments ({cols}) VALUES ({placeholders})", tuple(row.values())
        )
        self._conn.commit()
        return cur.lastrowid

    def list_garments(self, garment_type: str | None = None) -> list[Garment]:
        if garment_type:
            rows = self._conn.execute(
                "SELECT * FROM garments WHERE garment_type = ?", (garment_type,)
            ).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM garments").fetchall()
        return [Garment.from_row(r) for r in rows]

    def mark_worn(self, garment_id: int) -> None:
        self._conn.execute(
            "UPDATE garments SET times_worn = times_worn + 1, last_worn_ts = ? WHERE id = ?",
            (time.time(), garment_id),
        )
        self._conn.commit()

    def seed_demo_closet(self) -> None:
        """Populates a small demo closet so app.py runs out of the box."""
        if self.list_garments():
            return
        demo_items = [
            ("closet/floral_wrap_dress.jpg", "dress", ["floral", "bohemian"], "coral", "smart-casual", 2, ["spring", "summer"]),
            ("closet/white_ruffle_blouse.jpg", "top", ["ruffles", "romantic"], "white", "business-casual", 1, ["spring", "summer", "fall"]),
            ("closet/black_blazer.jpg", "outerwear", ["minimalist", "business-casual"], "black", "business", 3, ["fall", "winter", "spring"]),
            ("closet/denim_jacket.jpg", "outerwear", ["denim", "streetwear"], "blue", "casual", 2, ["spring", "fall"]),
            ("closet/tailored_trousers.jpg", "bottom", ["minimalist", "business-casual"], "charcoal", "business", 2, ["fall", "winter", "spring"]),
            ("closet/pastel_knit_sweater.jpg", "top", ["pastel", "cottagecore"], "lavender", "casual", 3, ["fall", "winter"]),
            ("closet/leather_ankle_boots.jpg", "shoes", ["monochrome", "vintage"], "brown", "smart-casual", 3, ["fall", "winter"]),
            ("closet/linen_sundress.jpg", "dress", ["minimalist", "pastel"], "cream", "casual", 1, ["summer"]),
            ("closet/athleisure_set.jpg", "set", ["athleisure"], "grey", "casual", 2, ["spring", "summer", "fall", "winter"]),
            ("closet/gothic_lace_top.jpg", "top", ["gothic", "vintage"], "black", "smart-casual", 2, ["fall", "winter"]),
        ]
        for image_path, gtype, tags, color, formality, warmth, seasons in demo_items:
            self.add_garment(Garment(
                id=None, image_path=image_path, garment_type=gtype, style_tags=tags,
                dominant_color=color, formality=formality, warmth_score=warmth, season_fit=seasons,
            ))
