import { eventBus } from './eventBus'
import type { JobState } from '../types/agent'

// Tauri IPC is available at runtime when running inside Tauri
function tryTauriEmit(event: string, payload: unknown) {
  try {
    // @ts-ignore — __TAURI__ is injected by Tauri at runtime
    if (typeof window !== 'undefined' && window.__TAURI__) {
      // @ts-ignore
      window.__TAURI__.event.emit(event, payload).catch(() => {})
    }
  } catch {
    // Not running in Tauri (e.g. browser dev mode) — silently ignore
  }
}

type OrbState = 'idle' | 'listening' | 'thinking' | 'executing' | 'paused' | 'clarification' | 'completed'

function resolveOrbState(job: JobState): OrbState {
  if (job.status === 'paused') {
    return job.clarification_question ? 'clarification' : 'paused'
  }
  if (job.status === 'completed') return 'completed'
  if (job.status === 'failed' || job.status === 'stopped') return 'idle'
  if (job.stage === 'Reasoning' || job.stage === 'Reflecting' || job.stage === 'Planning') return 'thinking'
  if (job.stage === 'Executing') return 'executing'
  return 'thinking'
}

/**
 * Maps Runtime State changes into UI Events broadcast over the Event Bus
 * AND over Tauri IPC so the Overlay window stays in sync without polling.
 */
export const uiEventDispatcher = {
  dispatchStateChange(job: JobState) {
    const orbState = resolveOrbState(job)

    // Local Event Bus (same window)
    eventBus.emit('runtime:stage', { stage: job.stage, step: job.step, max_steps: job.max_steps })

    // ── Tauri IPC → Overlay window ─────────────────────────────────────
    tryTauriEmit('intentos:orb-state', { orbState, stage: job.stage, status: job.status })

    // Overlay progress card during verification
    if (job.stage === 'Verifying') {
      eventBus.emit('overlay:show', {
        type: 'ProgressOverlay',
        payload: { message: `Verifying step ${job.step}…` },
        position: 'bottom-right'
      })
    }

    // Terminal state cleanup
    if (job.status === 'completed') {
      eventBus.emit('runtime:completed', { jobId: job.job_id })
      eventBus.emit('overlay:hide')
      tryTauriEmit('intentos:orb-state', { orbState: 'completed', stage: 'Completed', status: 'completed' })
    } else if (job.status === 'failed') {
      eventBus.emit('runtime:failed', { error: job.error })
      eventBus.emit('overlay:hide')
      tryTauriEmit('intentos:orb-state', { orbState: 'idle', stage: 'Failed', status: 'failed' })
    }
  },

  dispatchVoiceState(state: 'listening' | 'idle') {
    tryTauriEmit('intentos:orb-state', { orbState: state, stage: state, status: 'created' })
  },

  hideOverlay() {
    eventBus.emit('overlay:hide')
  }
}
