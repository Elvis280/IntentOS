/**
 * services/api.js
 *
 * Central API client for IntentOS.
 * All backend communication goes through these functions.
 * Components never call fetch/axios directly.
 *
 * Backend base URL is read from the VITE_API_URL env var so it
 * can be changed without rebuilding (defaults to localhost:8000).
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request(method, path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }

  return res.json()
}

// ── Agent control ────────────────────────────────────────────────────────────

/** Start a new agent job. Returns { job_id: string } */
export const startAgent = (goal)           => request('POST', '/agent/start',  { goal })

/** Pause a running job */
export const pauseAgent = (job_id)         => request('POST', `/agent/pause/${job_id}`)

/** Resume a paused job */
export const resumeAgent = (job_id)        => request('POST', `/agent/resume/${job_id}`)

/** Stop a job (terminal) */
export const stopAgent  = (job_id)         => request('POST', `/agent/stop/${job_id}`)

/** Poll live status — call every 500 ms */
export const getStatus  = (job_id)         => request('GET',  `/agent/status/${job_id}`)

/** Fetch the execution history for a job */
export const getHistory = (job_id)         => request('GET',  `/agent/history/${job_id}`)

/** Legacy synchronous endpoint (kept for compatibility) */
export const runAgentSync = (goal)         => request('POST', '/agent/run',    { goal })