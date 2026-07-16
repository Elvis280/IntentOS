# IntentOS: Runtime Specification v1.0

## 1. Runtime Philosophy

IntentOS is built around a central, highly deterministic orchestrator known as the **Runtime**. 

The fundamental philosophy of the Runtime is that it **owns execution but does not own intelligence**. Large Language Models (LLMs) and computer vision models participate in the Runtime pipeline to provide cognitive capabilities, but they do not control the lifecycle of the system. The Runtime must remain fully deterministic, predictable, and observable, ensuring that the inherent unpredictability of AI is strictly contained within isolated phases of the execution loop.

## 2. Responsibilities

The Runtime acts as the central nervous system of IntentOS. It is strictly bounded in its responsibilities to ensure modularity and reliability.

**The Runtime IS explicitly responsible for:**
* **Lifecycle Management:** Creating, starting, pausing, resuming, and stopping Jobs and Sessions.
* **Module Orchestration:** Pumping data sequentially through the Observe → Reason → Execute pipeline.
* **State Transitions:** Managing the internal state machine (e.g., transitioning from `Observing` to `Reasoning`).
* **Event Coordination:** Broadcasting internal events to decoupled systems (like the UI and logging layers).
* **Job Execution:** Tracking the progress of individual tasks against maximum step limits.
* **Session Coordination:** Managing the continuous context across multiple sequential or parallel jobs.
* **Runtime Status:** Maintaining the definitive source of truth for "what the system is doing right now."
* **Error Propagation:** Catching exceptions from sub-modules and routing them to the Recovery system or the user.

**The Runtime explicitly DOES NOT DO:**
* **No reasoning:** It does not decide what action to take next.
* **No screenshot analysis:** It does not parse pixels or locate bounding boxes.
* **No desktop interaction:** It does not physically move the mouse or send keystrokes.
* **No verification logic:** It does not decide if an action succeeded.
* **No memory storage:** It does not permanently store learned context (it delegates to Memory).
* **No policy decisions:** It does not decide if an action is safe or optimal.

## 3. Runtime Ownership & State Model

Clear boundaries of ownership are essential to prevent cross-contamination of state.

**Ownership Definitions:**
* **Runtime** owns orchestration and execution flow.
* **Session** owns long-term collaboration context.
* **Job** owns task execution progress and history.
* **World** owns observable physical desktop state.
* **Context** owns the semantic understanding of the workspace.
* **Memory** owns learned information and user preferences.
* **Reasoner** owns proposed actions.
* **Policy** owns deterministic validation and overrides.
* **Executor** owns physical desktop interaction.
* **Verifier** owns outcome validation.

**Runtime State Model:**
The Runtime maintains its own state object, which is entirely separate from the *World State*. The Runtime state represents the *execution* environment:
* `Current Session ID`
* `Current Job ID`
* `Current Stage` (e.g., Reasoning, Verifying)
* `Current Action` (The active payload being processed)
* `Current Thought` (The LLM's current internal monologue)
* `Current Screenshot` (Base64 encoding of the immediate observation)
* `Current World` (Snapshot of the physical state at this exact moment)
* `Current Progress` (Step X of Y)
* `Timeline` (The chronological history of events in the current job)
* `Errors & Warnings`
* `Execution Metrics` (Latency, counts)

## 4. Runtime Execution Loop

The execution loop is a continuous pipeline coordinated sequentially by the Runtime.

```
User Intent
    ↓
Session
    ↓
Job Created
    ↓
Observe (Capture screen, or reuse cached screenshot from previous step)
    ↓
Vision (Process image into semantic blocks)
    ↓
World Update (Commit changes to World Model)
    ↓
Reason (LLM evaluates World vs Goal to propose an action)
    ↓
Policy (Validate action against hardcoded safety/optimization rules)
    ↓
Execute (Translate action into physical machine interaction)
    ↓
Verify (Compare pre/post World states to ensure success, evaluating any generic side-effects)
    ↓
Update Runtime State (Commit history, broadcast events, cache Observation for next step)
    ↓
[Continue to next step or Complete Job]
```

The Runtime coordinates this flow rather than performing the work. It simply calls each module in sequence, takes the output, injects it into the next module, and broadcasts the transition.

## 5. Runtime States

The Runtime operates a strict State Machine.

* **Idle:** 
  * *Purpose:* Awaiting input. 
  * *Transitions:* → `Preparing`.
* **Preparing:** 
  * *Purpose:* Allocating resources and initializing a Job. 
  * *Transitions:* → `Observing`.
* **Observing:** 
  * *Purpose:* Capturing and processing the physical screen. 
  * *Transitions:* → `Reasoning`, `Failed`.
* **Reasoning:** 
  * *Purpose:* Querying the LLM for the next action. 
  * *Transitions:* → `Applying Policy`, `Failed`.
* **Applying Policy:** 
  * *Purpose:* Passing the proposed action through deterministic overrides. 
  * *Transitions:* → `Executing`, `Reasoning` (if REASON_AGAIN is triggered).
* **Executing:** 
  * *Purpose:* Interacting with the operating system. 
  * *Transitions:* → `Verifying`, `Failed`.
* **Verifying:** 
  * *Purpose:* Evaluating the outcome of the execution. 
  * *Transitions:* → `Observing` (next step), `Completed` (if DONE), `Recovering` (if failed).
* **Waiting:** 
  * *Purpose:* Yielding for external factors (e.g., animations to finish, user input). 
  * *Transitions:* → `Observing`.
* **Paused:** 
  * *Purpose:* Frozen orchestration by user request. 
  * *Transitions:* → Previous active state (Resume), `Stopped`.
* **Recovering:** 
  * *Purpose:* Attempting to resolve a verification failure without abandoning the job. 
  * *Transitions:* → `Observing`, `Failed`.
* **Completed:** 
  * *Purpose:* Terminal success state. 
  * *Transitions:* None.
* **Failed:** 
  * *Purpose:* Terminal error state. 
  * *Transitions:* None.
* **Stopped:** 
  * *Purpose:* Terminal cancellation by user. 
  * *Transitions:* None.

## 6. Runtime Events & Timeline

**Internal Event Model:**
To maintain a decoupled architecture (and prepare for WebSockets/multi-agent systems), the Runtime emits internal events at every phase transition. Modules listen to these events rather than calling each other directly.
* `SessionStarted`, `JobCreated`, `ObservationCompleted`, `VisionCompleted`, `WorldUpdated`, `ReasonGenerated`, `PolicyApplied`, `ExecutionStarted`, `ExecutionCompleted`, `VerificationPassed`, `VerificationFailed`, `JobPaused`, `JobResumed`, `JobCompleted`, `SessionEnded`.

**The Runtime Timeline:**
The Timeline is an append-only chronological log of these events. It serves as the primary debugging tool and audit trail. Every meaningful occurrence—observations, thoughts, policy overrides, executions, verifications, and recoveries—is appended to the Timeline with absolute timestamps.

## 7. Lifecycle Management

### 7.1 Job Lifecycle
A Job represents a specific execution goal bounded by a maximum step count.
* `Created` → Acknowledged by the Runtime.
* `Queued` → Waiting for resources.
* `Running` → Actively looping.
* `Paused` → Execution frozen at the next safe boundary.
* `Completed / Archived` → Goal achieved, state serialized and stored.

### 7.2 Session Lifecycle
IntentOS is evolving toward long-term execution. A Session survives the completion of individual Jobs to maintain ongoing workspace context.
* `Session Started`
* `Job 1` (e.g., "Open Excel")
* `Job 2` (e.g., "Format the first row")
* `User Interaction` (User types manually)
* `Job 3` (e.g., "Generate a chart based on this data")
* `Waiting` (Monitoring for next command)
* `Session Closed`

Sessions prevent the Reasoner from suffering "amnesia" between distinct commands, providing the bedrock for continuous collaboration.

## 8. Pause, Resume, and Cancellation

* **Pause:** Pausing must *never* terminate a thread abruptly. It sets a flag that the Runtime checks at every phase boundary (e.g., between Reason and Execute). This freezes orchestration cleanly, leaving the state fully inspectable.
* **Resume:** Clears the pause flag, allowing the loop to continue exactly where it left off.
* **Stop (Cancellation):** Triggers a clean termination flag. The Runtime finishes its current phase, releases resources (vision models, hardware hooks), marks the job as `Stopped`, and transitions back to `Idle`.

## 9. Error Handling & Recovery

**Error Philosophy:**
* **Recoverable Errors:** e.g., A button moved during execution. The Verifier catches it, and the Runtime loops back to `Observe` to try again.
* **Retryable Errors:** e.g., Network timeout to the LLM API. The Runtime automatically retries with exponential backoff.
* **Fatal Errors:** e.g., Out of Memory, OS permission denied. The Runtime transitions immediately to `Failed` and notifies the user.

**Recovery Model (Future):**
When Verification fails repeatedly, the Runtime will trigger Recovery strategies:
* **Retry:** Simply attempt the same action again.
* **Rollback:** Execute an inverse action (e.g., close a popup that accidentally opened).
* **Re-reason:** Inform the LLM that the previous strategy failed and prompt for a completely different approach.

## 10. Metrics

To support future analytics and self-improvement, the Runtime tracks:
* Execution latency per phase.
* Observation and Reasoning counts per Job.
* Verification success rate.
* Policy override frequency.
* Deterministic Skill utilization vs. Raw AI fallback usage.
* Recovery attempt frequency.
These metrics will eventually feed the Reflection system.

## 11. Future Integrations

All future expansions to IntentOS must plug into the Runtime without violating its ownership:
* **Memory & Reflection:** Injected into the prompt payload during the `Preparing` or `Reasoning` phases.
* **Plugins & Application-Specific Skills:** Registered as deterministic handlers in the Policy Engine.
* **Voice & Multi-modal Input:** Operate as external clients generating `JobCreated` events.
* **Cloud Sync:** Synchronizes serialized `Timeline` and `Memory` blobs out-of-band.

## 12. Design Principles

1. **Runtime Owns Orchestration:** Intelligence belongs to the modules; flow belongs to the Runtime.
2. **State is Explicit:** Never rely on implicit side-effects. All state lives in defined models.
3. **Events are First-Class:** Decouple systems through an event bus.
4. **Observable Phases:** The UI must always know exactly which phase the Runtime is in.
5. **Deterministic Execution over AI Guessing:** Fall back to LLM reasoning only when a hardcoded Skill cannot achieve the goal.
6. **Human Control is Absolute:** The ability to pause or stop is guaranteed and instantaneous at phase boundaries.
7. **Extensible by Design:** Add features by plugging into events or registering Skills, never by rewriting the loop.
