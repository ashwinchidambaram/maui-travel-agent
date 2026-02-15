# Maui Travel Agent

A travel planning agent that answers one question: **"Is it a good time to go to Maui?"**

However, that question means something different for everyone (even though we've hard-coded a user profile for this project). So the agent doesn't answer right away. It first figures out what "good" actually means for the specific user, gathers the data it needs, and then gives a recommendation it can actually defend.

### Built with Google ADK, FastMCP, and Python.

---

## What It Does

The agent works through six stages before responding:

1. Recognizes the question is underspecified
2. Fetches the user's travel preferences
3. Checks Maui weather against their temperature preferences
4. Searches flights from their home airport, filters out red-eyes and over-budget options
5. Evaluates hotels against their budget and comfort preferences
6. Produces a recommendation with clear reasoning — including why it rejected the other options

---

## Demo Transcript

```
User: Is it a good time to go to Maui?

🔧 Calling tool: get_user_profile
✅ Tool returned data
🔧 Calling tool: get_weather_forecast
✅ Tool returned data
🔧 Calling tool: search_flights
✅ Tool returned data
🔧 Calling tool: search_hotels
✅ Tool returned data

🤖 Agent Response:

---
🌺 MAUI TRAVEL RECOMMENDATION
---

VERDICT: Yes

DATES: 2026-02-14 → 2026-02-23 (9 days)

WEATHER
• Conditions: Overcast conditions expected. Total precipitation: 0.3
  inches over the period.
• Temps: 76°F average (69°F–83°F range)
• Match: Temperatures are slightly warmer than your preferred range of
  70-75°F, but still within an acceptable range.

RECOMMENDED FLIGHT
• Alaska Airlines — $520 round-trip
• 8:00am → 2:00pm (6hrs, direct)
• Why: This direct flight fits your budget, avoids red-eye flights,
  and offers a convenient morning departure.

RECOMMENDED HOTEL
• Kaanapali Beach Hotel — $235/night (Kaanapali)
• Amenities: Free WiFi, Pool, Gym, Direct Beach Access, Restaurant
• Why: This Marriott Autograph Collection hotel meets your brand
  preference, offers an ocean view, has a gym, and is located in a
  less touristy, natural area.

ALTERNATIVES
• Alaska Airlines flight for $410 with one layover — Consider this
  option if budget is a primary concern and you don't mind a longer
  travel time.
• Maui Seaside Hotel for $145/night — Budget-friendly but lacks a
  gym and ocean view.

REJECTED OPTIONS
• Hawaiian Airlines flight — Ruled out due to the red-eye schedule.
• Grand Wailea Resort — Ruled out, significantly over budget.

CAVEATS
• The weather will be slightly warmer than your ideal temperature.
  Overall, this looks like a wonderful trip that fits your
  preferences well!
---
```

---

## Architecture

```
agent/maui_agent.py       ←  Google ADK coordinator
        │
        │  MCP over HTTP
        ▼
tools/server.py           ←  FastMCP tool server (port 9000)
        │
        ▼
core/                     ←  Pure Python, no framework dependencies
  models.py               ←  Pydantic data models
  mock_data.py            ←  User profile
  weather.py              ←  Open-Meteo API
```

The separation matters: `core/` has zero dependencies on ADK, MCP, or any orchestration framework. If this project moved to a different agent framework tomorrow, only `agent/maui_agent.py` would need to change. Everything else stays the same.

---

## Tools

All four tools are exposed through a single FastMCP HTTP server.

**`get_user_profile`**
Returns the user's travel preferences as a structured Pydantic model — temperature range, flight and hotel budgets, trip duration, home airport, comfort preferences. Structured rather than free text so the agent can reason against specific fields without ambiguity. (**Note:** *Has been hardcoded using a Pydantic framework for this project*)

**`get_weather_forecast`**
Pulls real weather data from the Open-Meteo API (free, no API key needed) and returns a short summary. Handles three cases depending on how far out the dates are:

- Within 16 days → real forecast
- Beyond 16 days → 2023 historical baseline (typical seasonal conditions)
- Past dates → historical archive

The raw API response includes arrays of daily values — `core/weather.py` parses those into a single summary before it ever reaches the agent.

**`search_flights`**
Returns three flight options as concise formatted text. Mock data — no free real-time flight API exists. Options are deliberately varied (budget/layover, best value/direct, red-eye) so the agent has real trade-offs to reason about.

**`search_hotels`**
Same approach — three options spanning under budget, best fit, and over budget. Designed so one option clearly matches the user's preferences and the others need to be explained away.

---

## Design Decisions

**Today's date in the system instruction**
Early in testing, the agent invented July 2024 as the trip date. Agents don't have reliable access to the current date, so it guessed — and guessed incorrectly. Injecting today's date as an f-string into the instruction fixed this immediately.

**`home_airport` as a profile field**
Flight search needs an origin. Rather than hardcoding it or letting the agent assume, it lives in the user profile. Makes the agent's reasoning traceable: it searched from SEA because that's what the profile says.

**Text returns for flights and hotels**
The agent reasons about these in natural language anyway, so a clean text summary works better than a JSON object and costs less in context. The brief also penalizes bloated tool outputs — this keeps things tight.

**Mock data for flights and hotels**
No free real-time flight or hotel search API exists. The interesting part of the system is how the agent evaluates options against preferences, not where the data comes from.

**All tools are read-only**
No tool modifies state, so idempotency is inherent — retrying any tool call produces the same result with no side effects. If booking or reservation tools were added in a future version, they would require explicit idempotency keys to prevent duplicate charges on retry.

---

## Getting Started

### Setup

```bash
git clone https://github.com/ashwinchidambaram/maui-travel-agent.git
cd "Project 1 - Travel Agent"
uv sync

cp .env.example .env
# Add your API key to .env
```

### Run

```bash
# Terminal 1 — start the tool server
python -m tools.server

# Terminal 2 — run the agent
python -m agent.maui_agent
```

### LLM Providers

```bash
# .env
LLM_PROVIDER=gemini     # default, needs GOOGLE_API_KEY
LLM_PROVIDER=anthropic  # needs ANTHROPIC_API_KEY
LLM_PROVIDER=ollama     # needs Ollama running locally, set OLLAMA_MODEL too
```

---

## Stack

| | |
|--|--|
| Agent framework | Google ADK |
| Tool protocol | MCP via FastMCP |
| LLM (default) | Gemini 2.0 Flash |
| Weather API | Open-Meteo |
| Data validation | Pydantic v2 |
| Package manager | uv |

---

## Project Structure

```
├── agent/
│   └── maui_agent.py       # coordinator agent
├── core/
│   ├── models.py           # data models
│   ├── mock_data.py        # user profile
│   └── weather.py          # weather logic
├── tools/
│   └── server.py           # MCP tool server
├── .env.example
└── pyproject.toml
```
