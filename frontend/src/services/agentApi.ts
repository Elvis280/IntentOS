import axios from 'axios'
import type { JobState, SessionSummary, AppSettings } from '../types/agent'

const http = axios.create({
  baseURL: '/',   // Vite proxy forwards /agent/* → http://localhost:8000
  timeout: 10_000,
})

export const agentApi = {
  /** Start a new job and return the job_id. */
  start: async (goal: string): Promise<{ job_id: string }> => {
    const res = await http.post<{ job_id: string }>('/agent/start', { goal })
    return res.data
  },

  /** Poll the live state of a running job. */
  getStatus: async (jobId: string): Promise<JobState> => {
    const res = await http.get<JobState>(`/agent/status/${jobId}`)
    return res.data
  },

  /** Pause execution at the next safe phase boundary. */
  pause: async (jobId: string): Promise<void> => {
    await http.post(`/agent/pause/${jobId}`)
  },

  /** Resume a paused job. */
  resume: async (jobId: string): Promise<void> => {
    await http.post(`/agent/resume/${jobId}`)
  },

  /** Terminate a job cleanly. */
  stop: async (jobId: string): Promise<void> => {
    await http.post(`/agent/stop/${jobId}`)
  },

  /** Submit a clarification answer for a paused job. */
  clarify: async (jobId: string, answer: string): Promise<void> => {
    await http.post(`/agent/${jobId}/clarify`, { answer })
  },

  /** List all archived sessions. */
  getSessions: async (): Promise<{ sessions: SessionSummary[] }> => {
    const res = await http.get<{ sessions: SessionSummary[] }>('/sessions')
    return res.data
  },

  /** Get a single session's full data. */
  getSession: async (jobId: string): Promise<JobState> => {
    const res = await http.get<JobState>(`/sessions/${jobId}`)
    return res.data
  },

  /** Read current settings. */
  getSettings: async (): Promise<AppSettings> => {
    const res = await http.get<AppSettings>('/settings')
    return res.data
  },

  /** Persist new settings. */
  updateSettings: async (settings: AppSettings): Promise<AppSettings> => {
    const res = await http.post<AppSettings>('/settings', settings)
    return res.data
  },
}
