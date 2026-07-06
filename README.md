# Project Description
ClosetMuse is a multi-agent AI closet stylist. You photograph the clothes
you already own once; a vision agent tags each item's style (floral,
ruffles, minimalist, streetwear, etc.), formality, warmth, and season fit
into a personal wardrobe database. Every morning, a Weather Agent and a
Calendar Agent run in parallel to gather the day's temperature/precipitation
and infer today's occasion (business, athletic, romantic, formal, casual)
from your calendar events. An Outfit Curator agent then reconciles all three
signals — closet inventory, weather, occasion — against a style-coherence
and wardrobe-rotation heuristic to produce up to three ranked, fully
justified outfit options.

## Architecture (Google ADK):
- ParallelAgent runs the Weather Agent and Calendar Agent concurrently,
  since neither depends on the other's output.
- SequentialAgent feeds their combined context into the Outfit Curator
  LlmAgent, which follows a versioned agent-skill spec
  (skills/outfit_curation.skill.md) rather than an ad-hoc prompt.
- A second skill (skills/style_tagging.skill.md) governs the vision agent's
  photo-tagging behavior, keeping the style taxonomy controlled and
  filterable across the whole closet.
- All four core tools (weather lookup, calendar lookup, wardrobe listing,
  outfit-feedback recording) are also exposed on a standalone MCP server
  (mcp_server/closet_mcp_server.py), so the same data layer is reachable
  from any MCP-compatible client, not just ClosetMuse's own agents.
- Security guardrails (security/guardrails.py) validate every image upload
  before it reaches the vision model, screen calendar text for
  prompt-injection patterns before it's folded into a prompt (calendar
  events are untrusted third-party text — anyone who can invite you to an
  event can write its title), redact PII from model output, and enforce a
  tool call allow-list via ADK's before_tool_callback.

The whole pipeline runs in a MOCK_MODE by default (deterministic mock
vision classifier, seeded mock weather, fixed mock calendar) so it's fully
demoable with zero API keys — flip one flag to go live against Gemini,
OpenWeatherMap, and Google Calendar.

## Rationale

I own more clothes than I can mentally track, and "what fits today's
weather AND today's meetings" costs real decision-making time every single
morning. That's a genuinely agentic problem, not a single-prompt one: it
needs perception (what's actually in my closet, from photos), two
independent live-context lookups (weather, calendar) that don't depend on
each other, and a reasoning step that reconciles all three against personal
style preferences. Modeling it as cooperating agents — rather than one
mega-prompt — let me build, test, and reason about each piece
independently (I can unit-test the outfit-curation logic without ever
calling a model), which is exactly the decomposition this course spent five
days teaching. It's also a project I'll genuinely keep using afterward,
which felt like the right bar for a capstone.
