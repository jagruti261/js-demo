# Specification: hello-world-agent

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-agent.md](../guidelines-agent.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [x] Read the project input (`product-requirements-document.md`, `intent.md`, or the user prompt that triggered this specification)
- [x] Bootstrap agent code in `assets/hello-world-agent/` using skill `sap-agent-bootstrap` (invoke from inside `assets/hello-world-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

## Hello World Agent Logic

- [x] Implement the agent's system prompt to always respond with "Hello World" regardless of the user's input question
- [x] Ensure the agent handler always returns "Hello World" as the response text
- [x] The agent must NOT call any external APIs or MCP servers — it is a self-contained, deterministic agent
- [x] No tools or connectors are needed — remove any template tools and keep only the static response logic

## Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD:
  - M1: Question received → log `M1.achieved: question received by agent` on success, `M1.missed: no question payload received` on failure
  - M2: Response generated → log `M2.achieved: hello world response generated` on success, `M2.missed: response generation failed` on failure
  - M3: Response delivered → log `M3.achieved: hello world response delivered to user` on success, `M3.missed: response delivery failed` on failure
- [x] Use structured logging with pattern `[MILESTONE_ID].[achieved|missed]: [description]`
- [x] Add OpenTelemetry custom spans for each milestone step
- [x] Extract business logic from `stream()` into a plain async helper (e.g. `_run_agent()`) — never wrap `yield` inside `with tracer.start_as_current_span(...)`
- [x] Verify `auto_instrument()` is called at top of `main.py` before any AI framework imports

## Cleanup

- [x] Delete the template runtime skill: `rm -rf assets/hello-world-agent/app/skills/template-skill/`

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true` — this causes the agent to run with mock MCP tool results during tests
- [x] Write one unit test verifying the agent always returns "Hello World" for any input question
- [x] Write one integration test executing the end-to-end agent flow calling the agent's `invoke` function
- [x] Run `pytest` from `assets/hello-world-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Verify `assets/hello-world-agent/app/agent.py` has exactly 3 decorated functions (`@agent_model`, `@agent_config` for temperature, `@prompt_section`) — run `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/hello-world-agent/app/agent.py` and confirm it returns 3
- [x] Run `pytest` again from `assets/hello-world-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/hello-world-agent/` — if not, run pytest again until it does
