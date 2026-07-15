# Changelog

All notable changes to **IntentOS** will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Memory module integration
- World-state diffing
- Frontend UI for goal input and execution trace

---

## [0.7.0] – 2026-07-15

### Added
- `app/skills/` — Introduced a deterministic skills framework to bypass LLM planning for known workflows.
- `app/skills/browser.py` — Deterministic browser workflows: `open_url`, `search_google`, `search_youtube`, `download_file`.
- `app/skills/windows.py` — Deterministic OS workflows: `open_application`, `close_application`, `switch_application`.
- `app/skills/keyboard.py` — Deterministic hardware workflows: `press`, `hotkey`, `type_text`, `copy`, `paste`.

### Changed
- `app/executor/executor.py` — Added a generic `USE_SKILL` action handler that dynamically imports and executes Python functions from `app/skills/`.
- `app/services/policy.py` — Upgraded Rules 1 and 2 to intercept `CLICK`/`PRESS_KEY` actions and map them directly to `USE_SKILL` workflows instead of the legacy `OPEN_URL` / `OPEN_APPLICATION` primitives.
- `app/services/policy.py` — Added a new Rule 5 to intercept natural language "search" goals and route them directly to `browser.search_google`.

---

## [0.6.0] – 2026-07-15

### Added
- `app/services/policy.py` — Deterministic Policy Engine that sits between the Reasoner and Executor to apply hard rules (intercepting taskbar clicks for websites, forcing OPEN_APPLICATION for native apps, handling repeated CLICK failures).
- `app/core/constants.py` — Centralized lists of known `WEBSITE_URLS`, `APP_EXECUTABLES`, `TASKBAR_SIGNALS`, and `BROWSER_SIGNALS`.
- `backend/tests/test_policy.py` — Complete unit test suite for the Policy Engine.

### Changed
- `app/api/agent.py` — Added `REASON_AGAIN` sentinel handling to skip execution and immediately proceed to the next iteration.
- `app/api/agent.py` — Replaced naive dict equality with `fuzzy_duplicate()` (±15px tolerance) for `CLICK` actions to accurately catch repeat loops.
- `app/executor/executor.py` — `PRESS_KEY` now accepts either `"key"` or `"text"` parameters to handle reasoner ambiguities, raising a clear exception if both are missing.
- `app/executor/executor.py` — `WAIT` now logs a warning and gracefully defaults to 1 second if the `"seconds"` parameter is missing.
- `app/services/verifier.py` — Verifier now explicitly ignores the `timestamp` field via a `_comparable()` helper to prevent false-negative verifications on unchanged states.
- `app/services/reasoner.py` — Updated the `SYSTEM_PROMPT` with strict, prioritized action-selection rules (e.g., prefer `OPEN_URL` for websites, `OPEN_APPLICATION` for apps).
- `app/core/llm.py` — Switched the active model to `gemini-flash-lite-latest` to avoid free-tier quota exhaustion.

---

## [0.5.0] – 2026-07-15

### Added
- `app/core/llm.py` — single shared `genai.Client` and `MODEL` constant; all AI modules now import from here instead of each creating their own client
- `app/services/` package — groups all runtime AI service modules:
  - `services/planner.py` (moved from `app/planner/planner.py`)
  - `services/reasoner.py` (moved from `app/reasoner/reasoner.py`)
  - `services/verifier.py` (moved from `app/verifier/verifier.py`)
- `app/experimental/` package — houses non-runtime research components:
  - `experimental/locator.py` (moved from `app/locator/locator.py`)
- `app/schemas/plan.py` — shared Pydantic schemas (`PlanStep`, `TaskPlan`) moved out of the planner module
- `backend/tests/` — test files moved outside the `app` package; `tests/test_capture.py` updated to use shared client
- `__init__.py` added to all packages: `app`, `api`, `core`, `services`, `experimental`, `schemas`, `vision`, `executor`, `world`, `tests`

### Changed
- All `app/api/*.py` routers updated to import from new paths (`app.services.*`, `app.experimental.*`)
- `app/vision/llm.py` refactored to use shared `core.llm` client; fixed typo in system prompt ("VVision" → "Vision")
- `app/api/agent.py` — `import time` moved to top of file (was inline inside loop)
- `app/api/reasoner.py` — added missing `history` argument to `next_action` call
- `requirements.txt` — added `numpy==2.5.1` and `opencv-python==5.0.0.93`
- `.gitignore` — added bare `screenshots/` pattern to cover captures from any working directory

### Removed
- `app/planner/` folder (superseded by `app/services/planner.py`)
- `app/reasoner/` folder (superseded by `app/services/reasoner.py`)
- `app/locator/` folder (superseded by `app/experimental/locator.py`)
- `app/verifier/` folder (superseded by `app/services/verifier.py`)
- `app/tests/` folder (superseded by `backend/tests/`)
- `app/world/state.py` (empty placeholder file)

---

## [0.4.0] – 2026-07-15

### Added
- **Locator Agent** (`app/locator/locator.py` + `POST /locator/find`):
  - Gemini vision model receives the live screenshot and a target element string
  - Returns `label`, `found`, `x`, `y`, `confidence` as JSON
  - Gracefully returns `found: false` when the element is not visible
- **Reasoner Agent** (`app/reasoner/reasoner.py` + `POST /reasoner/next`):
  - Single-step decision maker — given the goal, current world state, and screenshot, returns the one next action to take
  - Response schema: `thought`, `action`, `target`, `text`, `x`, `y`, `reason`
  - Returns `DONE` when the goal is detected as complete
  - Endpoint guards against an empty world model (requires `/vision/analyze` first)
- Both new routers registered in `app/api/router.py`

### Changed
- `PlanStep` schema (`planner/schemas.py`) now requires `expected_result: str` on every step
- Planner system prompt (`planner/planner.py`) updated:
  - Renamed role to *"Planner Agent of IntentOS"*
  - JSON schema example now includes `expected_result`
  - Rules tightened: every step must have `expected_result`, return JSON only, never invent action names
- `POST /agent/run` now logs `expected_result` for each step after execution (`print(f"Expected: ...")`)

---

## [0.3.0] – 2026-07-15

### Added
- Full **perception-action loop** in `POST /agent/run`:
  - After each executor step, captures the screen (`mss`), sends it to Gemini vision (`analyze`), builds a `WorldState` from the response (`build_world`), and updates the world manager
  - Each step result now includes a `"verified"` boolean from the verifier
  - Execution halts early if verification fails (`if not verified: break`)
- `verifier` singleton exported from `app/verifier/verifier.py` for shared use across the API layer

### Changed
- `Verifier.verify()` now safely handles `world=None` (returns `False`) instead of raising an `AttributeError`
- `OPEN_APPLICATION` check in `Verifier` refactored from a `for` loop to a concise `any()` expression
- `requirements.txt` synced to actual venv state:
  - **Added:** `google-genai`, `google-auth`, `mss`, `pillow`, `httpx`, `requests`, `tenacity`, `cryptography` and their transitive deps
  - **Removed:** `pymongo`, `ortools`, `numpy`, `pandas`, `pymupdf`, `APScheduler` and other unused packages
  - **Bumped:** `uvicorn` 0.50 → 0.51, `websockets` 16.0 → 16.1, `anyio` 4.14.1 → 4.14.2

---

## [0.2.0] – 2026-07-15

### Added
- Desktop automation support via `pyautogui`, `pygetwindow`, and `pyperclip`
- `backend/requirements.txt` with all pinned Python dependencies
- Root-level `.gitignore` covering Python, Node, secrets, and editor artefacts
- `backend/.env.example` documenting all required environment variables
- `CHANGELOG.md` (this file)

---

## [0.1.0] – 2026-07-15

### Added
- FastAPI backend (`IntentOS`) with Uvicorn server
- CORS middleware allowing Vite dev server (`localhost:5173`)
- Modular API router with five sub-routers:
  - `/vision` – screen capture and LLM vision pipeline
  - `/planner` – Gemini-powered goal-to-plan generation
  - `/executor` – step execution engine
  - `/agent` – end-to-end goal runner (`POST /agent/run`)
  - `/verifier` – plan verification
- Gemini API integration (`google-genai`) used by planner and vision modules
- React 19 + Vite 8 frontend with Tailwind CSS v4, Zustand, Axios, React Router v7
- `screenshots/` directory for runtime screen captures (git-ignored)

---

<!-- Releases -->
[Unreleased]: https://github.com/Elvis280/IntentOS/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/Elvis280/IntentOS/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Elvis280/IntentOS/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Elvis280/IntentOS/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Elvis280/IntentOS/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Elvis280/IntentOS/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Elvis280/IntentOS/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Elvis280/IntentOS/releases/tag/v0.1.0
