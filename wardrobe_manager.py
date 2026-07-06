---
name: outfit_curation
description: >
  Curates a complete outfit (top+bottom or dress, plus outerwear/shoes as
  needed) from a wardrobe inventory, given weather and occasion context.
  Use whenever the user asks "what should I wear" / "plan my outfit" /
  "suggest an outfit for [occasion]".
inputs:
  - wardrobe_items: list of garments with style_tags, formality, warmth_score, season_fit
  - weather: temperature_c, condition, precipitation_chance, season
  - occasion: one of business | athletic | romantic | formal | casual
---

# Outfit Curation Skill

1. Filter the wardrobe to items whose `formality` is within one step of the
   occasion's required formality (see FORMALITY_SCALE in config.py) and
   whose `season_fit` includes the current season.
2. If `temperature_c < 15` or `precipitation_chance > 50`, require an
   `outerwear` item with `warmth_score >= 3`; if `precipitation_chance > 60`,
   note that an umbrella/waterproof layer is recommended.
3. Build one complete look: a base layer (dress, OR top+bottom), optional
   outerwear, and shoes. Prefer garments that share a coherent style_tag
   (e.g. don't pair "gothic" with "cottagecore") unless the wardrobe has no
   coherent option, in which case default to the most neutral pairing
   (monochrome / minimalist) and say so.
4. Rank up to 3 candidate outfits by: (a) style coherence, (b) how recently
   each item was worn (`last_worn_ts` — prefer rotation over repeats),
   (c) weather appropriateness.
5. For each outfit, output a one-sentence rationale referencing the specific
   weather figure and occasion that drove the choice — never a generic
   "this looks nice" justification.
