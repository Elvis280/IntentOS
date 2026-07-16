export type JobStatus =
  | 'created'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'stopped'

export interface ActionPayload {
  action: string
  parameters?: Record<string, unknown>
  thought?: string
  reason?: string
}

export interface VerificationResult {
  verified: boolean
  confidence: number
  summary: string
  expected_action: Record<string, unknown>
  executed_action: Record<string, unknown>
  changed_world_objects: Record<string, unknown>
  changed_ui_elements: Record<string, unknown>
  changed_context: Record<string, unknown>
  verification_reason: string
  recommended_recovery?: string
  timestamp: string
}

export interface ReflectionResult {
  execution_summary: string
  confidence: number
  success: boolean
  discovered_changes: string[]
  runtime_notes: string
  memory_updates: Record<string, unknown>[]
  recovery_required: boolean
}

export interface RecoveryResult {
  should_continue: boolean
  strategy: string
  retry_count: number
  confidence: number
  explanation: string
  modified_action?: Record<string, unknown>
  user_clarification_required: boolean
  clarification_question?: string
  runtime_notes: string
  timestamp: string
}

export interface HistoryEntry {
  action: ActionPayload
  verified: VerificationResult | boolean
  reflection?: ReflectionResult
  recovery?: RecoveryResult
  plan_step_id?: string
  plan_step_name?: string
}

export interface PlanStep {
  id: string
  title: string
  description: string
  objective: string
  expected_result: string
  completion_condition: string
  status: 'Pending' | 'Active' | 'Completed' | 'Failed' | 'Skipped' | 'Waiting'
  priority: number
}

export interface ExecutionPlan {
  goal: string
  steps: PlanStep[]
  created_at: string
}

export interface PlanProgress {
  current_step: string | null
  completed_steps: number
  failed_steps: number
  skipped_steps: number
  total_steps: number
  percentage_complete: number
  estimated_remaining_steps: number
}

export interface WorkingMemorySummary {
  current_workspace?: string
  focused_window?: string
  last_successful_action?: ActionPayload
  active_plan_step?: PlanStep
  plan_progress?: PlanProgress
}

export interface JobState {
  job_id: string
  status: JobStatus
  stage: string
  step: number
  max_steps: number
  goal: string
  thought?: string
  action?: ActionPayload
  world?: Record<string, unknown>
  screenshot?: string
  history: HistoryEntry[]
  error?: string
  // Clarification
  clarification_question?: string
  clarification_answer?: string
  // Planning
  plan?: ExecutionPlan
  plan_progress?: PlanProgress
}

export interface SessionSummary {
  job_id: string
  goal: string
  status: JobStatus
  stage: string
  step: number
  max_steps: number
  created_at: string
  error?: string
}

export interface AppSettings {
  api_key: string
  theme: 'system' | 'dark' | 'light'
  enable_voice: boolean
  max_history_jobs: number
  debug_mode: boolean
}
