import { create } from 'zustand'
import type { JobState } from '../types/agent'

interface RuntimeStore {
  /* ── job state ───────────────────────────────────────────── */
  jobId: string | null
  job: JobState | null
  goal: string

  /* ── ui state ────────────────────────────────────────────── */
  isLoading: boolean
  isPolling: boolean
  error: string | null

  /* ── actions ─────────────────────────────────────────────── */
  setGoal: (goal: string) => void
  setJobId: (id: string | null) => void
  setJob: (job: JobState) => void
  setLoading: (loading: boolean) => void
  setPolling: (polling: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const initialState = {
  jobId: null,
  job: null,
  goal: '',
  isLoading: false,
  isPolling: false,
  error: null,
}

export const useRuntimeStore = create<RuntimeStore>((set) => ({
  ...initialState,

  setGoal: (goal) => set({ goal }),
  setJobId: (jobId) => set({ jobId }),
  setJob: (job) => set({ job }),
  setLoading: (isLoading) => set({ isLoading }),
  setPolling: (isPolling) => set({ isPolling }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}))
