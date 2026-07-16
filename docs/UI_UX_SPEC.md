# IntentOS: UI/UX Design Specification v1.0

---

## 1. Design Philosophy

### 1.1 The Core Experience

IntentOS is a desktop runtime, not a chatbot. The experience must reflect that distinction at every layer of the interface. The user is not having a conversation; they are **directing an intelligent system** and **observing it work** in real time.

The interface should feel like the cockpit of a sophisticated machine — a **Mission Control center** where every panel is informative, every status indicator is meaningful, and every control is purposeful.

The primary emotional tone is: **calm confidence**. The user should feel in complete control of a powerful system without being overwhelmed by its complexity.

### 1.2 Design Pillars

1. **Transparency:** The user must always know what the runtime is doing, why, and what it found.
2. **Observability:** Every phase of execution is visible. Nothing is hidden.
3. **Trust:** The system earns trust through consistent behavior, clear explanations, and legible state.
4. **Control:** Pause, stop, and redirect are always one gesture away.
5. **Continuity:** Work persists. Sessions survive. The user picks up where they left off.

### 1.3 Reference Aesthetic

The design draws from:

- **Cursor** — minimal, technical, focused on the work
- **Raycast** — keyboard-first, fast, precise command interface
- **Claude Desktop** — clean typography, thoughtful prose, calm interactions
- **Linear** — structured, high-information-density, powerful

**Deliberately avoiding:**
- Chat bubble UI (ChatGPT paradigm)
- Consumer app aesthetics (large cards, emoji status icons)
- Marketing dashboard aesthetics (colorful charts for their own sake)
- Toy-like, playful rounding and fonts

---

## 2. Information Architecture

### 2.1 Top-Level Navigation

```
IntentOS
├── Dashboard          (What is happening right now?)
├── Runtime            (Mission Control — the primary workspace)
├── Sessions           (Ongoing collaborative work contexts)
├── History            (Completed jobs, archived timelines)
├── Settings           (Configuration, models, skills, permissions)
└── [Memory]           (Future — reserved, grayed out in nav)
```

### 2.2 Hierarchy of Concepts

The navigation mirrors the architectural concepts defined in the Intent Model:

```
Session
  └── Job
        └── Step (Observe / Reason / Execute / Verify)
              └── Action
```

Each level of the hierarchy maps to a corresponding UI surface. Sessions are navigated from the Sessions screen; Jobs are inspected in the Runtime or History screens; individual Steps are visible in the Timeline.

---

## 3. Navigation Design

### 3.1 Primary Sidebar

A fixed, narrow sidebar (56px collapsed, 220px expanded) sits on the left. It contains:

- **Logo / Wordmark** at the top.
- **Primary Navigation Links:** Dashboard, Runtime, Sessions, History.
- **Separator.**
- **Settings** (bottom-pinned).
- **[Memory]** (bottom-pinned, visually muted/grayed, labeled "Coming Soon").

The sidebar should support two states:
- **Collapsed:** Icon-only with tooltip on hover.
- **Expanded:** Icon + Label.

The sidebar uses subtle `layoutId` transitions so the active indicator slides smoothly between items.

### 3.2 Secondary Navigation (Contextual)

Within screens like Settings, a secondary sub-navigation panel appears. This prevents nesting deep menus into the primary sidebar.

---

## 4. Screen-by-Screen Breakdown

### 4.1 Dashboard

**Purpose:** A single-glance overview of the system status.

**Layout:** Single column, card-grid layout. Maximum content width of ~1200px, centered.

**Top Row — Status Bar (Full width):**
- Runtime Status pill (Idle / Running / Paused)
- Current Session name
- Active Job title
- Last Observed Application
- Elapsed session time

**Second Row — Primary Metric Cards (4 columns):**
1. `Active Jobs` — count with sparkline trend
2. `Completed Today` — count
3. `Verification Rate` — percentage (success / total)
4. `Skills Utilized` — count vs. raw AI fallback ratio

**Third Row — Live Runtime Preview (left, 60%) + Recent Activity (right, 40%):**
- Left: A reduced, non-interactive version of the Runtime screen showing the current stage and last screenshot thumbnail.
- Right: An activity feed showing the last 10 timeline events across all sessions, with timestamps.

**Bottom Row — Quick Actions:**
- Start New Intent (primary CTA)
- Resume Last Session
- View Latest Job
- Open Settings

**Empty State (No jobs yet):**
A centered, quiet illustration with the tagline: *"Tell IntentOS what you want to accomplish."* and a prominent Intent Bar.

---

### 4.2 Runtime Screen

This is the **most important screen**. Users spend the majority of their time here during active execution. It should feel alive, informative, and fully in control.

**Layout: Three-Panel with Bottom Timeline**

```
┌────────┬────────────────────────┬────────────────┐
│        │                        │                │
│  Nav   │   SCREENSHOT PANEL     │   INSPECTOR    │
│        │   (Live Desktop View)  │   (Runtime     │
│        │                        │    State)      │
│        │                        │                │
│        ├────────────────────────┴────────────────┤
│        │         TIMELINE (Execution Log)        │
└────────┴─────────────────────────────────────────┘
│                   INTENT BAR                     │
└──────────────────────────────────────────────────┘
```

**Center Panel — Screenshot Viewer (primary visual):**
- Takes up ~60% of the width.
- Displays the last captured desktop screenshot.
- Subtle pulsing border glow during "Observing" phase.
- Future: Overlaid bounding boxes, highlighted click targets, cursor trail.
- A scan-line animation sweeps vertically during Observation to signal activity.
- Phase-specific tinting: a barely visible blue wash while Observing, amber while Reasoning, green after Verify-success.

**Right Panel — Runtime Inspector (primary information):**
- Takes up ~30% of the width.
- Fixed width, scrollable vertically.
- Sections (collapsible):
  - **Status:** Current Stage with animated icon, elapsed time in current stage.
  - **Thought:** Full text of the Reasoner's current reasoning monologue. Renders like a prose paragraph, not a bullet list.
  - **Action:** Structured display of the current action (type + parameters), shown as a code-like block.
  - **Policy:** Whether Policy modified the proposed action, and why (one line).
  - **Verification:** Pass/Fail badge with a one-line description of what changed.
  - **Current Intent:** The active user goal, rendered prominently.
  - **Progress:** Step X of Y with a thin progress bar.
  - **Workspace:** Current Application name + window title.

**Bottom Panel — Execution Timeline:**
- Horizontal or vertical scrolling event list.
- Each event is a compact row: `[icon] [timestamp] [event type] [short description]`.
- Events are color-coded by type:
  - **Blue:** Observe / Vision
  - **Amber:** Reason
  - **Purple:** Policy
  - **Green:** Execute / Verify Pass
  - **Red:** Verify Fail / Recovery
  - **Gray:** Pause / Resume / System
- Each event is expandable (click to expand) revealing full payload.
- Future: Replay controls, filter by event type, search.

**Bottom — Intent Bar:**
- Always visible at the bottom of the Runtime screen.
- A full-width, minimal text input field.
- Placeholder: *"What would you like IntentOS to do?"*
- Keyboard shortcut hint displayed inline (e.g., `⌘K` or `Ctrl+K`).
- To the right of the input: `Run` (primary) and control buttons `⏸ Pause`, `⏹ Stop`.
- When active, the bar glows faintly blue.
- Supports command history (arrow keys cycle through previous intents).

---

### 4.3 Sessions Screen

**Purpose:** View and manage ongoing collaborative work contexts.

**Layout:** Two-column. Left: Session list. Right: Session detail.

**Session List (Left, 320px):**
- Search field at top.
- Each Session Card:
  - Session title (auto-generated from the first intent, editable).
  - Active Application icon(s).
  - Status: Active / Paused / Idle.
  - Job count (e.g., "4 jobs").
  - Last activity timestamp.
  - Color-coded left border indicating status.
- "New Session" button pinned to top.

**Session Detail (Right):**
- Session title (editable inline).
- Active application context (breadcrumb).
- List of all Jobs within the session, in chronological order.
  - Each job shows: title, status, step count, duration.
  - Clicking a job opens the History screen filtered to that job.
- "Resume Session" primary action.
- "View Full Timeline" secondary action.
- "Archive Session" tertiary/destructive action.

---

### 4.4 History Screen

**Purpose:** A searchable, filterable archive of all completed jobs.

**Layout:** Full-width table/list view with filter sidebar.

**Filter Sidebar (left, 240px):**
- Date range picker.
- Status filter: All / Completed / Failed / Stopped.
- Application filter (multi-select).
- Session filter.

**Job List (main area):**
- Table rows, each showing: Job title, Session, Status badge, Application, Steps, Duration, Timestamp.
- Clicking a row expands an inline preview showing the Timeline for that job.
- A "Inspect" button opens a full-screen job detail view.

**Job Detail View (full-screen modal or drawer):**
- Full Timeline (all events).
- Before/After screenshot comparison (if screenshots are available).
- Reasoner's thought log.
- Policy decisions applied.
- Final verification outcome.
- Future: Export as JSON, replay controls.

---

### 4.5 Settings Screen

**Layout:** Two-column. Left: Settings navigation. Right: Settings panel.

**Settings Navigation (left, 220px):**
- General
- Runtime
- Models
- Skills
- Appearance
- Hotkeys
- Permissions
- Privacy
- Developer Mode

**Settings Panels:**
- **General:** Application language, startup behavior, update channel.
- **Runtime:** Max steps per job, auto-pause after failure, observation delay.
- **Models:** Primary LLM selection, Vision model selection, API key management.
- **Skills:** Installed skills list, enable/disable toggles, future marketplace CTA.
- **Appearance:** Theme (Dark / Light / System), font size, sidebar density.
- **Hotkeys:** Customizable keyboard shortcuts table.
- **Permissions:** Desktop control, screenshot access, file system access indicators.
- **Privacy:** Local-only mode toggle, telemetry opt-out, session data retention.
- **Developer Mode:** Enable verbose logging, expose raw API payloads, event log export.

---

### 4.6 Memory Screen (Future — Reserved)

A placeholder screen is visible in the navigation but disabled. It displays:
- A centered illustration.
- Headline: *"Memory is coming."*
- Subtext: *"IntentOS will remember your preferences, workflows, and workspace context across sessions."*

This communicates the product roadmap without shipping incomplete features.

---

## 5. Component Hierarchy

```
App
├── AppShell
│   ├── Sidebar
│   │   ├── NavItem (active / inactive states)
│   │   └── NavSection (with separator)
│   └── ContentArea
│
├── Dashboard
│   ├── StatusBar
│   ├── MetricCard (×4)
│   ├── LiveRuntimePreview
│   ├── ActivityFeed
│   │   └── ActivityFeedItem
│   └── QuickActions
│
├── RuntimeScreen
│   ├── ScreenshotPanel
│   │   ├── ScanAnimation (Observing state)
│   │   └── PhaseOverlay (state-specific tint + glow)
│   ├── RuntimeInspector
│   │   ├── StatusSection
│   │   ├── ThoughtSection
│   │   ├── ActionSection
│   │   ├── PolicySection
│   │   ├── VerificationSection
│   │   ├── IntentSection
│   │   ├── ProgressSection
│   │   └── WorkspaceSection
│   ├── ExecutionTimeline
│   │   ├── TimelineEvent (expandable)
│   │   └── TimelineFilter (future)
│   └── IntentBar
│       ├── TextInput
│       ├── RunButton
│       ├── PauseButton
│       └── StopButton
│
├── SessionsScreen
│   ├── SessionList
│   │   ├── SessionCard (active / paused / idle states)
│   │   └── NewSessionButton
│   └── SessionDetail
│       ├── JobList
│       │   └── JobItem
│       └── SessionActions
│
├── HistoryScreen
│   ├── FilterSidebar
│   └── JobTable
│       └── JobRow (expandable)
│           └── JobDetailDrawer
│               ├── FullTimeline
│               ├── ScreenshotComparison
│               └── VerificationSummary
│
├── SettingsScreen
│   ├── SettingsNav
│   └── SettingsPanel (swapped by route)
│
└── GlobalComponents
    ├── CommandPalette (Ctrl+K)
    ├── NotificationToast
    ├── ConfirmationDialog
    ├── StatusPill
    ├── ProgressRing
    ├── PhaseIcon (animated per stage)
    └── ErrorBanner
```

---

## 6. User Flows

### 6.1 Primary Flow — Start to Completion

```
User opens IntentOS
    ↓
Lands on Dashboard (Idle state)
    ↓
Focuses the Intent Bar (Ctrl+K or click)
    ↓
Types intent: "Prepare the quarterly review in PowerPoint"
    ↓
Presses Enter / clicks Run
    ↓
[Runtime Screen activates]
    ↓
Screenshot Panel shows desktop
Scan animation begins
Inspector shows "Observing..."
Timeline logs: Observation Started
    ↓
Inspector updates: "Reasoning..."
Thought section displays LLM monologue
    ↓
Inspector updates: "Executing..."
Action section shows CLICK or USE_SKILL
    ↓
Inspector updates: "Verifying..."
Verification badge shows Pass / Fail
    ↓
Loop repeats until DONE
    ↓
Status transitions to "Completed"
Green banner: "Goal achieved."
Job archived to History
```

### 6.2 Pause / Modify / Resume Flow

```
User is watching execution
    ↓
Clicks ⏸ Pause (or Ctrl+P)
    ↓
Runtime enters Paused state at next safe boundary
Inspector shows "Paused"
Pause button becomes Resume
    ↓
User edits intent: "Also use a dark theme"
    ↓
Clicks Resume
    ↓
Runtime continues with updated intent context
Timeline logs: "Intent Modified - Dark Theme Added"
```

### 6.3 Session Flow

```
User opens Sessions screen
    ↓
Clicks "New Session"
    ↓
Names the session (or accepts auto-name)
    ↓
Types first intent in Intent Bar
    ↓
Execution begins (Job 1)
    ↓
Job 1 completes
    ↓
Session remains open ("Waiting" state)
    ↓
User types next intent (Job 2 created within same session)
    ↓
Session accumulates jobs and context
    ↓
User closes session → archived
```

### 6.4 History Inspection Flow

```
User opens History
    ↓
Filters by Application: "PowerPoint" + Date: "Last 7 days"
    ↓
Sees list of matching jobs
    ↓
Clicks a failed job
    ↓
Inline timeline expands
User identifies where verification failed
    ↓
Clicks "Inspect" → opens full-screen detail
    ↓
Views before/after screenshot, reasoner thoughts, policy decisions
    ↓
User understands the failure point
```

---

## 7. Layout Specifications

### 7.1 Grid System

- **Base unit:** 4px
- **Spacing scale:** 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64
- **Column grid:** 12-column, 24px gutter
- **Content max-width:** 1440px
- **Sidebar collapsed:** 56px
- **Sidebar expanded:** 220px
- **Runtime Inspector width:** 320px (fixed)

### 7.2 Breakpoints

The application is desktop-first. Minimum supported width is 1024px. Tauri window constraints prevent sub-minimum sizing.

---

## 8. Design System

### 8.1 Color Palette

**Dark Mode (Primary):**
- **Background:** Near-black, slightly warm. e.g., `#0D0E0F`
- **Surface (cards, panels):** `#141516`
- **Surface Elevated:** `#1C1D1F`
- **Border:** Subtle, low contrast. e.g., `#2A2B2D`
- **Foreground (primary text):** `#F0F0F0`
- **Foreground Muted:** `#6E7175`

**Semantic Colors:**
- **Primary (actions, links):** `#4A9EFF` — a clear, professional blue
- **Success (verified, completed):** `#3ECA78` — confident green
- **Warning (policy override, paused):** `#F5A623` — amber
- **Danger (error, failed, stopped):** `#E85454` — controlled red
- **Reasoning (LLM active):** `#9B8EFF` — a muted indigo/purple

### 8.2 Typography

- **Primary Font:** `Inter` — for all UI text, labels, and prose.
- **Monospace Font:** `JetBrains Mono` or `Geist Mono` — for action payloads, code blocks, timeline event details, and technical fields.
- **Scale:**
  - `xs`: 11px / 16px
  - `sm`: 13px / 20px (default body)
  - `base`: 15px / 24px
  - `lg`: 18px / 28px
  - `xl`: 22px / 32px
  - `2xl`: 28px / 36px (page headlines)

### 8.3 Iconography

- **Icon Set:** Lucide React — thin, geometric, consistent stroke weight.
- **Sizes:** 14px (inline), 18px (nav items), 22px (status cards).
- **Phase Icons:** Each runtime phase has an associated animated icon.
  - Observing: Scanning eye
  - Reasoning: Pulsing brain
  - Executing: Play icon with motion
  - Verifying: Checkmark with ring

### 8.4 Corner Radius

- **Small (chips, badges):** 4px
- **Default (inputs, cards):** 8px
- **Large (modals, main panels):** 12px

### 8.5 Elevation & Depth

Depth is conveyed through **border contrast and background lightness**, not drop shadows. The darker the background, the lower the layer. Elevated panels are slightly lighter, not shadow-lifted.

### 8.6 Animation Principles

- **Transition duration:** Fast (150ms) for micro-interactions; Medium (250ms) for panel transitions; Slow (400ms) for page-level changes.
- **Easing:** Ease-out for entrances; Ease-in-out for transitions.
- **Phase transitions:** Use `layoutId` springs so the active state indicator and panel focus slide naturally.
- **Data updates (Inspector):** Text fades in with a subtle upward slide (12px → 0) on every new value. Never flicker.
- **Scan animation (Screenshot Panel):** A 3px horizontal gradient line sweeps from top to bottom over ~1.5 seconds on repeat while Observing.
- **Timeline events:** Animate in from the bottom with staggered entrance.
- **No infinite spinners** except for the Reasoning phase, which uses a subtle pulsing dot indicator.

### 8.7 State Vocabulary

Every interactive element has defined states:
- **Default, Hover, Active, Focus, Disabled**
- Every async operation has: **Loading, Success, Error, Empty**
- Every data panel has: **Populated, Empty (with message), Loading (skeleton), Error**

### 8.8 Accessibility

- **Minimum contrast ratio:** 4.5:1 for all body text.
- **Focus rings:** Visible, 2px offset, primary color.
- **Keyboard navigation:** All core actions reachable without a mouse.
- **ARIA labels:** All icons and icon-only buttons must have descriptive aria-labels.
- **Reduced motion:** Respect `prefers-reduced-motion` — disable scan animations and transitions.

---

## 9. Interaction Principles

1. **Keyboard-first.** Every primary action has a keyboard shortcut. A shortcut legend is accessible via `?`.
2. **Intent Bar is the primary input.** Always accessible via `Ctrl+K` / `⌘K` from any screen.
3. **Pause is never destructive.** Pausing freezes the loop at the next safe boundary. It never terminates a thread.
4. **No confirmation dialogs for observation.** The only confirmation gates are for Stop (which is terminal) and destructive Settings changes.
5. **Information hierarchy:** The most recent event is always the most prominent. Historical data fades in visual priority.
6. **The runtime always speaks.** When the system is active, the Inspector always shows something. "Observing..." is content. Never show a blank Inspector during execution.
7. **Failed states are informative.** A failure banner must always explain what failed, not just that something failed.

---

## 10. Future Expansion Strategy

The design is built to accommodate the roadmap without redesign:

- **Memory:** A dedicated screen is reserved in the navigation today. The Inspector will gain a "Memory Context" collapsible section that shows which memories influenced the current reasoning.
- **Plugins:** The Settings > Skills screen will evolve into a Skills & Plugins Marketplace panel.
- **Voice:** A microphone button appears next to the Intent Bar when Voice is enabled. It does not replace the text input; it populates it.
- **Multiple Sessions:** The Sessions screen supports a tabbed or split-pane view.
- **Analytics:** A future Analytics section in Settings can surface aggregated metrics from the History database.
- **Developer Tools:** The Developer Mode in Settings activates a draggable developer overlay panel (similar to React DevTools) that shows raw module payloads in real time.
- **Multi-Agent:** Future Runtime screen supports a "Threads" indicator at the bottom of the Inspector when parallel agents are running.
