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
[Unreleased]: https://github.com/Elvis280/IntentOS/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Elvis280/IntentOS/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Elvis280/IntentOS/releases/tag/v0.1.0
