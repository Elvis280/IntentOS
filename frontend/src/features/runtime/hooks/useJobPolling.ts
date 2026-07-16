import { useEffect, useRef } from 'react'
import { agentApi } from '../../../services/agentApi'
import { useRuntimeStore } from '../../../store/runtimeStore'
import { uiEventDispatcher } from '../../../services/uiEventDispatcher'

const TERMINAL_STATUSES = new Set(['completed', 'failed', 'stopped'])
const POLL_INTERVAL_MS = 500

/**
 * Starts a polling loop against GET /agent/status/{jobId} every 500ms.
 * Stops automatically when the job reaches a terminal status.
 * The interval ref is cleaned up on unmount.
 */
export function useJobPolling() {
  const { jobId, isPolling, setJob, setPolling, setError } = useRuntimeStore()
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const clearLoop = () => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  useEffect(() => {
    if (!jobId || !isPolling) {
      clearLoop()
      return
    }

    const tick = async () => {
      try {
        const state = await agentApi.getStatus(jobId)
        setJob(state)
        uiEventDispatcher.dispatchStateChange(state)

        if (TERMINAL_STATUSES.has(state.status)) {
          setPolling(false)
          clearLoop()
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Poll failed'
        setError(msg)
        setPolling(false)
        clearLoop()
      }
    }

    // Run one tick immediately, then set the interval
    void tick()
    intervalRef.current = setInterval(tick, POLL_INTERVAL_MS)

    return clearLoop
  }, [jobId, isPolling, setJob, setPolling, setError])
}
