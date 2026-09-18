# Specification: weather-greeting-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md` at the solution root)
- [x] Bootstrap agent code in `assets/weather-greeting-agent/` using instructions from the sap-agent-bootstrap section
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> No complex multi-step workflows or domain-specific compliance rules are required. Runtime skills are not needed — greeting logic fits comfortably in the system prompt.

---

## Project-Specific Tasks

### Weather Tool Implementation

- [x] Create `assets/weather-greeting-agent/app/tools/weather_tool.py` with async `get_weather(city)` tool using Open-Meteo API
- [x] Create `assets/weather-greeting-agent/app/tools/location_tool.py` with async `resolve_location(text)` tool

### Agent System Prompt

- [x] Updated `@prompt_section` in `app/agent.py` with full greeting instructions, fallback behaviour, and guardrails

### Wire Tools into Agent Graph

- [x] Register `get_weather` and `resolve_location` in `agent_executor.py`
- [x] `requirements.txt` includes `httpx`

---

## Business Instrumentation

- [x] Implemented M1–M4 milestones with structured logging and OpenTelemetry spans via `_run_agent()` helper
- [x] Verified `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Not applicable — agent uses only public REST APIs (Open-Meteo). No SAP MCP servers required.

---

## Testing

- [x] `conftest.py` sets `IBD_TESTING=true`
- [x] Unit tests: `tests/test_weather_tool.py` — 4 tests, all passing
- [x] Unit tests: `tests/test_location_tool.py` — 6 tests, all passing
- [x] Integration test: `tests/test_agent_integration.py` — 3 tests, all passing
- [x] `pytest` run: 119 total tests, 118 passed (1 fails only when pylint not installed — environment constraint)
- [x] Verified exactly 9 decorated functions in `app/agent.py`
- [x] `test_report.json` exists in `assets/weather-greeting-agent/`
