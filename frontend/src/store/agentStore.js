/**
 * store/agentStore.js
 *
 * Zustand store — single source of truth for all agent state.
 *
 * Polling loop
 * ------------
 * startPolling(jobId)  → calls GET /agent/status every 500 ms, merges the
 *                        response into the store, and auto-stops when the
 *                        job reaches a terminal state.
 * stopPolling()        → clears the interval (also called on Pause/Stop).
 */

import { create } from 'zustand'
import { startAgent, pauseAgent, resumeAgent, stopAgent, getStatus } from '../services/api'

const POLL_INTERVAL_MS = 500

// Terminal statuses — polling stops automatically when any of these is reached
const TERMINAL = new Set(['completed', 'failed', 'stopped'])

// ── Default / idle state ─────────────────────────────────────────────────────
const IDLE = {
  jobId:      null,
  status:     'idle',
  stage:      'idle',
  step:       0,
  maxSteps:   20,
  progress:   0,
  thought:    '',
  action:     {},
  world: {
    activeWindow:     'Google Chrome',
    applications:     ['Google Chrome', 'Terminal'],
    buttonsDetected:  ['Download for Windows', 'Documentation'],
    visibleText:      ['Code editing. Redefined.'],
  },
  history:    [],
  screenshot: '',
  error:      '',
  systemInfo: {
    cpu:     '14%',
    memory:  '2.4 GB',
    latency: '—',
    model:   'Gemini Flash Lite',
  },
}

// ── Store ─────────────────────────────────────────────────────────────────────
const useAgentStore = create((set, get) => ({
  ...IDLE,

  _pollTimer: null,   // internal — interval handle

  // ── Internal helpers ───────────────────────────────────────────────────────

  _startPolling(jobId) {
    const existing = get()._pollTimer
    if (existing) clearInterval(existing)

    const timer = setInterval(async () => {
      try {
        const t0  = Date.now()
        const data = await getStatus(jobId)
        const latency = `${Date.now() - t0}ms`

        // Map backend snake_case to frontend camelCase
        set({
          status:     data.status,
          stage:      data.stage,
          step:       data.step,
          maxSteps:   data.max_steps,
          progress:   data.progress,
          thought:    data.thought,
          action: {
            type:    data.action?.action ?? '',
            payload: data.action?.parameters ?? {},
          },
          world: _mapWorld(data.world),
          history:    _mapHistory(data.history),
          screenshot: data.screenshot
            ? `data:image/png;base64,${data.screenshot}`
            : get().screenshot,
          error:      data.error ?? '',
          systemInfo: {
            ...get().systemInfo,
            latency,
          },
        })

        // Auto-stop polling when job finishes
        if (TERMINAL.has(data.status)) {
          get()._stopPolling()
        }
      } catch (err) {
        console.error('[Poll] Error fetching status:', err)
      }
    }, POLL_INTERVAL_MS)

    set({ _pollTimer: timer })
  },

  _stopPolling() {
    const timer = get()._pollTimer
    if (timer) {
      clearInterval(timer)
      set({ _pollTimer: null })
    }
  },

  // ── Public actions ─────────────────────────────────────────────────────────

  async run(goal) {
    try {
      set({ status: 'starting', thought: 'Sending goal to agent...', error: '' })
      const { job_id } = await startAgent(goal)
      set({ jobId: job_id, status: 'running' })
      get()._startPolling(job_id)
    } catch (err) {
      set({ status: 'failed', error: err.message })
    }
  },

  async pause() {
    const { jobId } = get()
    if (!jobId) return
    try {
      await pauseAgent(jobId)
      get()._stopPolling()
      set({ status: 'paused' })
    } catch (err) {
      console.error('[Pause] Error:', err)
    }
  },

  async resume() {
    const { jobId } = get()
    if (!jobId) return
    try {
      await resumeAgent(jobId)
      set({ status: 'running' })
      get()._startPolling(jobId)
    } catch (err) {
      console.error('[Resume] Error:', err)
    }
  },

  async stop() {
    const { jobId } = get()
    if (!jobId) return
    get()._stopPolling()
    try {
      await stopAgent(jobId)
    } catch (err) {
      console.error('[Stop] Error:', err)
    }
    set({ status: 'stopped' })
  },

  reset() {
    get()._stopPolling()
    set({ ...IDLE })
  },
}))

// ── Mapping helpers ──────────────────────────────────────────────────────────

function _mapWorld(w) {
  // Guard: return the IDLE shape if the backend hasn't sent a world yet
  if (!w || typeof w !== 'object') return IDLE.world

  // Backend WorldState serialises to:
  //   active_window, applications, buttons, text
  // We normalise once here to camelCase so every component uses one convention.
  return {
    activeWindow:    w.active_window    ?? w.activeWindow    ?? IDLE.world.activeWindow,
    applications:    w.applications     ?? IDLE.world.applications,
    // backend field is `buttons` (not `buttons_detected`)
    buttonsDetected: w.buttons          ?? w.buttons_detected ?? w.buttonsDetected ?? IDLE.world.buttonsDetected,
    // backend field is `text` (not `visible_text`)
    visibleText:     w.text             ?? w.visible_text    ?? w.visibleText     ?? IDLE.world.visibleText,
  }
}

function _mapHistory(arr) {
  if (!Array.isArray(arr)) return []
  return arr.map((item, i) => ({
    id:       i + 1,
    time:     new Date().toLocaleTimeString(),
    text:     _actionLabel(item.action),
    verified: item.verified,
  }))
}

function _actionLabel(action) {
  if (!action) return 'Unknown action'
  const type   = action.action ?? action.type ?? '?'
  const params = action.parameters ?? {}
  if (type === 'OPEN_URL')         return `Open URL: ${params.url ?? ''}`
  if (type === 'OPEN_APPLICATION') return `Open App: ${params.target ?? ''}`
  if (type === 'CLICK')            return `Click (${params.x ?? 0}, ${params.y ?? 0})`
  if (type === 'TYPE')             return `Type: ${params.text ?? ''}`
  if (type === 'PRESS_KEY')        return `Press: ${params.key ?? params.text ?? ''}`
  if (type === 'USE_SKILL')        return `Skill: ${params.skill ?? ''}.${params.function ?? ''}`
  if (type === 'DONE')             return 'Goal completed ✓'
  return type
}

export default useAgentStore
