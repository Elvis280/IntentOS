# IntentOS: Architecture Specification v1.0

## 1. Project Overview

IntentOS is an AI-powered desktop runtime that acts as an intelligent execution layer over the operating system. It translates natural language human intent into deterministic software operation by orchestrating a continuous perception-action loop: **Observe → Understand → Reason → Apply Policy → Execute → Verify → Repeat**.

IntentOS is **not** an operating system, nor is it a simple automation script. It is an **AI Runtime** designed to orchestrate observation, reasoning, execution, verification, and human collaboration across any desktop application. This specification defines the boundaries, responsibilities, data flow, and lifecycle of all internal modules to prevent architectural drift and ensure long-term stability as the system scales.

## 2. State Ownership & Design Constraints

To maintain strict modularity, IntentOS enforces rigid state ownership and design constraints.

**State Ownership:**
* **Runtime:** Owns lifecycle (start, pause, stop).
* **Session:** Owns the context of a continuous collaboration.
* **Job:** Owns the state of a specific execution goal.
* **World Model:** Owns the spatial and structural truth of the desktop.
* **Context:** Owns the semantic understanding of the workspace.
* **Memory:** Owns learned knowledge and preferences.
* **Reasoner:** Owns the proposed action *only*.
* **Executor:** Owns execution *only*.
* **Verifier:** Owns execution validation *only*.

**Architectural Constraints:**
* The Runtime must never perform reasoning or execute actions.
* The Reasoner must never execute actions directly.
* The Executor must never reason or modify world state.
* The Vision module must never execute actions.
* The Policy Engine must never call the LLM; it must remain deterministic.
* The Verifier must never modify Runtime lifecycle.
* Every module must adhere strictly to a Single Responsibility.

## 3. Data Flow

The architecture follows a strict, sequential pipeline orchestrated by the Runtime:

```
User Intent
    ↓
Runtime (Job Initialization)
    ↓
Observe (Screen Capture)
    ↓
Vision (LLM Analysis)
    ↓
World (State Construction)
    ↓
Reasoner (Action Proposal)
    ↓
Policy (Deterministic Overrides)
    ↓
Skills (Workflow Substitution)
    ↓
Executor (System Interaction)
    ↓
Verifier (Action Validation)
    ↓
Runtime (State Evaluation)
    ↓
[Repeat or Terminate]
```

## 4. Component Specifications

### 4.1 Runtime
The Runtime is the central orchestration engine of IntentOS.
* **Purpose:** To drive the continuous perception-action loop.
* **Responsibilities:** Coordinates module execution, manages job states, handles pauses/resumptions, and passes data between decoupled components.
* **Inputs:** Job initialization, external control signals (Pause/Stop).
* **Outputs:** State broadcasts to the Session/UI.
* **What it does NOT do:** The Runtime never reasons about the goal, never analyzes images, and never executes desktop actions.
* **Lifecycle:** `Idle → Observing → Reasoning → Applying Policy → Executing → Verifying → Waiting → Completed/Failed`.

### 4.2 Session Model
IntentOS is transitioning from isolated one-shot executions to long-lived collaborative sessions.
* **Purpose:** To maintain context over prolonged periods of collaboration.
* **Hierarchy:** `Session → Jobs → Actions → Timeline`.
* **Responsibilities:** A Session tracks history, context, and memory across multiple sequential or parallel Jobs. It ensures that an action performed at 10:00 AM informs a reasoning decision made at 2:00 PM.

### 4.3 Job Model
A Job represents a specific, user-requested goal within a Session.
* **Purpose:** To encapsulate the execution state of a single intent.
* **Lifecycle:** `Created → Running → Paused → Running → Completed / Failed → Archived`.
* **Relationship:** The Runtime executes Jobs. Jobs hold the execution history, current progress, and terminal conditions.

### 4.4 Intent Model
IntentOS differentiates cognitive structures to prevent ambiguity:
* **Goal:** The high-level user objective (e.g., "Prepare the quarterly report").
* **Intent:** The immediate conceptual step (e.g., "Extract revenue data").
* **Task:** The specific functional block (e.g., "Copy data from Excel").
* **Action:** The atomic execution primitive (e.g., `CLICK(x, y)`).

### 4.5 Observe & Vision
* **Purpose:** To perceive the physical state of the desktop.
* **Responsibilities:** Captures raw pixel data (Observe) and utilizes multimodal AI to extract bounding boxes, text, and semantic regions (Vision).
* **Outputs:** Raw structured perception data.
* **What it does NOT do:** Vision does not execute actions or reason about the next step.

### 4.6 World Model
* **Purpose:** The single, shared source of truth regarding the desktop's physical state.
* **Responsibilities:** Stores coordinates, UI elements, active applications, and window bounds.
* **Inputs:** Only the Vision module updates the World Model.
* **Outputs:** Read by Reasoner, Policy, and Verifier.
* **Future Evolution:** Will expand beyond `Applications` and `Buttons` to include `Selections`, `Clipboard`, `UI Hierarchy`, `Workspace Semantics`, and `Focused Elements`.

### 4.7 Context
* **Purpose:** To track semantic understanding.
* **Distinction:** If the World Model answers *"What is visible?"*, Context answers *"What is happening?"*
* **Responsibilities:** Maintains the logical state of the user's workflow (e.g., "The user is currently debugging a database connection error"). Context is essential for long-running sessions to prevent the Reasoner from losing the plot.

### 4.8 Reasoner
* **Purpose:** To bridge the gap between high-level Intent and atomic Actions.
* **Responsibilities:** Consumes the Goal, Context, and World Model to propose a single logical next action.
* **Outputs:** An Action proposal (including internal thought processes).
* **What it does NOT do:** The Reasoner never executes the action. It merely proposes it.

### 4.9 Policy Engine
* **Purpose:** To inject deterministic, rule-based logic into the AI pipeline.
* **Responsibilities:** Intercepts proposed actions, validates them against hardcoded rules, ensures safety boundaries, optimizes coordinates, and substitutes raw clicks with robust Skills.
* **Why it is independent of LLM:** LLMs are non-deterministic. Policies enforce absolute rules (e.g., "Never click the power button," or "If opening Chrome, use the OS launch command, not a pixel click").

### 4.10 Skill System
* **Purpose:** To provide highly reliable, deterministic workflows that bypass naive AI reasoning.
* **Responsibilities:** Replaces brittle atomic actions (like clicking a URL bar and typing) with native OS commands or programmatic API calls.
* **Why Deterministic:** Skills guarantee outcomes. If a goal can be achieved via a Skill, it must be; AI is reserved strictly for scenarios where no deterministic skill exists.
* **Future:** Will expose an SDK for third-party Skill registration.

### 4.11 Executor
* **Purpose:** To translate Action structures into actual machine events.
* **Responsibilities:** Triggers mouse movements, keystrokes, application launches, or Skill invocations.
* **What it does NOT do:** The Executor never interprets intent, modifies the World state, or verifies success. It is a blind execution boundary.

### 4.12 Verifier
* **Purpose:** To close the execution loop safely.
* **Responsibilities:** Compares the World Model before and after execution to answer one question: *"Did the intended effect occur?"*
* **Why Separate:** Verification requires a distinct cognitive perspective to prevent the Reasoner from hallucinating success. It grounds the loop in reality.

### 4.13 Memory (Future)
* **Purpose:** To establish continuity.
* **Types:** 
  * *Short-term:* Current job variables.
  * *Session:* Workflow context.
  * *Long-term:* Cross-session persistence.
  * *Semantic:* Knowledge about the user's environment.
  * *Preference:* How the user likes things done.
* **Integration:** Memory will be injected into the Reasoner's prompt context by the Runtime, preserving the Runtime's neutral ownership.

### 4.14 Reflection (Future)
* **Purpose:** Continuous self-improvement.
* **Responsibilities:** Analyzes verification failures to adjust future reasoning decisions.
* **Constraint:** Reflection will inform the Reasoner, but it must never override deterministic Policy.

### 4.15 Recovery (Future)
* **Purpose:** Graceful error handling.
* **Responsibilities:** When verification fails multiple times, Recovery determines how to restore a known-good state (e.g., closing a pop-up) and resume execution without starting over.

## 5. Extension Points

The architecture is designed to integrate future capabilities without requiring a redesign:
* **Memory & Context:** Injected gracefully into the reasoning payload by the Runtime.
* **Plugins & Skills:** Registered into the deterministic Policy/Executor pipeline dynamically.
* **Voice & Multimodal:** Act as alternative inputs generating initial Job Intents.
* **Cloud Sync:** Operates strictly on the serialized Session and Memory models.

## 6. Guiding Architectural Principles

Every future contributor to IntentOS must adhere to these foundational principles:

1. **Single Responsibility:** No module does two things.
2. **Deterministic Execution over AI Guessing:** If a hardcoded rule or API can do it, do not use the LLM.
3. **Observable Runtime:** Every internal state must be transparently broadcastable to the UI.
4. **Human-in-the-Loop:** The architecture must always support pausing, modifying, and resuming.
5. **Composable Modules:** Systems must communicate via standardized data payloads, not tight coupling.
6. **Explicit State Ownership:** State must never be mutated by a module that does not own it.
7. **Reliability Before Autonomy:** Predictable failure is infinitely superior to unpredictable success.
8. **Intent Over Interface:** Optimize for understanding the user's goal, not navigating the current GUI.
9. **Continuous Collaboration:** Design for long-running workflows, not one-shot scripts.
