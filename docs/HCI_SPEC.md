# IntentOS: Human Interaction Specification v2 — Ambient AI Runtime

## 1. Ambient Computing Philosophy

IntentOS is not software you "open" or "use" in the traditional sense. It is an **Ambient AI Runtime** built on the principles of calm technology. It becomes an invisible, fundamental capability of the operating system, sitting beneath the user’s workflow and surfacing only when explicitly needed.

The interface must disappear whenever possible. The user should spend almost all of their time inside the native applications they already use (PowerPoint, VS Code, Chrome). IntentOS comes to them; they rarely go to IntentOS. 

The aesthetic and behavioral tone is **calm, professional, reliable, and predictable**. It quietly observes, waits, and acts strictly upon request.

## 2. Input Architecture

IntentOS decouples the *origin* of an Intent from its *execution*. All interaction vectors pass through an Input Manager before reaching the Runtime, ensuring the core engine remains ignorant of how the user spoke or typed.

```text
Voice ──────┐
Keyboard ───┼──> [ Input Manager ] ──> [ Intent Engine ] ──> [ Runtime ]
Overlay ────┤
API / Mobile┘
```

This abstraction layer ensures infinite scalability. Whether the user circles a screen element with a stylus in the future, types a command, or shouts across the room, the Runtime processes the same standardized Intent payload.

## 3. Ambient Awareness & Follow Mode

For IntentOS to feel like a true companion, it must eliminate the friction of constantly explaining context. This is achieved through **Ambient Awareness**.

IntentOS continuously understands:
* The currently focused application
* The active document or open tabs
* The user's current mouse selection or text highlight
* The contents of the clipboard
* The physical layout of open windows

**Follow Mode:**
IntentOS quietly "follows" the user's work without requiring activation. If the user clicks on an image in a presentation, IntentOS knows that image is the current semantic target. If the user highlights a paragraph of code, IntentOS knows that code block is the working context. 

* *Privacy & Performance:* Follow Mode requires strict local processing. Visual feedback is zero; the system does not draw boxes around everything the user clicks. It simply maintains an invisible rolling window of context in memory.
* *Control:* Follow Mode can be toggled globally via the Settings or paused temporarily via a system tray icon for privacy-sensitive workflows.

## 4. UI Surface Architecture

IntentOS abandons the traditional "application window" model in favor of a distributed, progressive hierarchy of UI surfaces.

### 4.1 The Contextual Floating Orb

The Floating Orb remains the visual anchor of the system, but it is no longer persistently visible by default. 
* **Behavior:** The Orb utilizes a **Contextual Auto-Hide** model. It rests invisibly in the system tray or off-screen. It materializes instantly when the wake word is spoken, a hotkey is pressed, or execution begins.
* **Why Contextual:** An always-on-top orb distracts from deep work. The user should not have to manually hide it during focused writing or gaming. It appears when invoked, pulses during execution, and fades away when the system returns to Idle.

### 4.2 Mini Cards (New)

Mini Cards are lightweight, ephemeral UI surfaces that appear near the active workspace (or anchored to the Orb). 
* **Purpose:** For low-friction communication that does not require a full Overlay or Mission Control.
* **Use Cases:** "Searching the web...", "Task completed", quick confirmations ("Are you sure you want to delete this folder? [Yes] [No]"), or asking for a simple clarification.
* **Behavior:** They slide in smoothly, present information, and vanish automatically once the interaction concludes. 

### 4.3 Fully Interactive Overlays

When IntentOS needs to interact directly with the workspace, it deploys glassmorphic Overlays drawn over the active application. These are no longer just visual indicators; they are **interactive workspaces**.
* **Use Cases:**
  * **Element Selection:** The user says "Replace that image." IntentOS draws numbered badges over the three visible images. The user says "Number two."
  * **Smart Annotations:** Highlighting specific data points in Excel to explain a reasoning path.
  * **Previews:** Displaying a translucent preview of a code refactor floating next to the original code before it is committed.
* **Collaboration:** Users can interact directly with the Overlay using their mouse or keyboard to adjust bounding boxes, approve changes, or drag elements, bridging the gap between voice and manual control.

### 4.4 Mission Control

The traditional Dashboard is reimagined as **Mission Control**. 
* **Purpose:** It is *not* a workspace. It is an inspection, debugging, and historical recovery tool. 
* **Visibility:** Users should almost never need to open Mission Control for ordinary daily work.
* **When to Open:** 
  * A complex execution failed, and the user wants to read the Timeline and Reasoner logs.
  * The user wants to replay or restore a past Session from History.
  * The user needs to configure Settings, developer flags, or manage Plugins.

## 5. Continuous Voice Interaction

Voice is the primary interaction vector. It is designed as a **continuous conversation**, heavily tolerant of human speech patterns, rather than a sequence of rigid transactional commands.

* **Flow:** The user says the wake word ("Intent..."). The conversation opens and stays open across multiple tasks.
  * *User:* "Create a presentation." (Done)
  * *User:* "Move the image." (Done)
  * *User:* "Make the colors darker." (Done)
* **Natural Interruptions:** The system must respond instantly to corrections.
  * *User:* "Actually, wait, no, don't use that image."
  * *IntentOS:* (Pauses execution instantly, rolls back the insertion, awaits the new image instruction).
* **Context Retention:** The conversation naturally times out after a prolonged period of silence (e.g., 60 seconds), returning to Follow Mode, but the semantic context of the Session remains intact for the next interaction.

## 6. Progressive Disclosure Rules

The UI must reveal information gradually to prevent cognitive overload.

1. **Idle:** Nothing visible. Ambient Awareness is running silently.
2. **User Speaks:** Orb fades in, indicates listening state.
3. **Execution Begins:** Orb pulses. If the action takes time, a Mini Card slides in ("Analyzing document...").
4. **Needs User Input / Disambiguation:** Interactive Overlay appears over the application, requesting a decision.
5. **Deep Inspection Required:** User explicitly opens Mission Control to view the timeline due to an error or complex session review.

## 7. Human Collaboration Principles

IntentOS is a collaborator, not an autonomous drone. The user is the pilot; the AI is the co-pilot.

* **Invisible until needed:** Do not clutter the screen.
* **Stay inside the user's workflow:** Bring the AI to the app, not the app to the AI.
* **Never steal focus unnecessarily:** Execution should happen in the background when possible.
* **Always explain important actions:** Use Mini Cards for transparency without blocking work.
* **Always allow interruption:** "Stop" or "Wait" must halt execution at the millisecond level.
* **Trust through transparency:** The Timeline in Mission Control must log every decision exactly as it occurred.
* **Intent over interfaces:** The user describes the destination; the system navigates the GUI.

## 8. Future Expansion Strategy

The Ambient Runtime architecture provides a seamless path for future capabilities:
* **Memory:** Integrates silently into the Follow Mode context window, allowing the system to remember user preferences without needing a dedicated UI.
* **Plugin Marketplace:** Managed strictly inside Mission Control, ensuring third-party extensions do not clutter the ambient experience.
* **Cloud Sessions / Multi-device:** The Input Architecture allows an Intent initiated on a mobile device to be executed seamlessly by the desktop Runtime.
* **Multiple AI Threads:** The Orb can visually split or spawn satellites to indicate parallel background tasks without opening new windows.

This specification ensures IntentOS feels like a next-generation capability of the operating system itself—an ambient, intelligent layer that empowers the user without ever getting in their way.
