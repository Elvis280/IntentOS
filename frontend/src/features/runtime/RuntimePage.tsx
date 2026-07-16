import { agentApi } from '../../services/agentApi'
import { useRuntimeStore } from '../../store/runtimeStore'
import { useJobPolling } from './hooks/useJobPolling'
import { useVoice } from './hooks/useVoice'
import { ScreenshotViewer } from './components/ScreenshotViewer'
import { RuntimeStatePanel } from './components/RuntimeStatePanel'
import { Timeline } from './components/Timeline'
import { ControlBar } from './components/ControlBar'
import { VoiceButton } from './components/VoiceButton'
import { VoiceStatus } from './components/VoiceStatus'
import { TranscriptInput } from './components/TranscriptInput'
import { ClarificationBar } from './components/ClarificationBar'

export function RuntimePage() {
  useJobPolling()

  const {
    jobId, job, goal, isLoading, error,
    setGoal, setJobId, setJob, setLoading, setPolling, setError, reset,
  } = useRuntimeStore()

  const {
    voiceState, transcript, error: voiceError,
    isSupported, startListening, stopListening,
    confirmTranscript, cancelTranscript, setTranscript,
  } = useVoice()

  // ── Runtime controls ────────────────────────────────────────────────────

  const handleStart = async (intentText?: string) => {
    const goalText = (intentText ?? goal).trim()
    if (!goalText) return
    reset()
    setGoal(goalText)
    setLoading(true)
    try {
      const { job_id } = await agentApi.start(goalText)
      setJobId(job_id)
      setPolling(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start')
    } finally {
      setLoading(false)
    }
  }

  const handlePause = async () => {
    if (!jobId) return
    try {
      await agentApi.pause(jobId)
      if (job) setJob({ ...job, status: 'paused' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause')
    }
  }

  const handleResume = async () => {
    if (!jobId) return
    try {
      await agentApi.resume(jobId)
      if (job) setJob({ ...job, status: 'running' })
      setPolling(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume')
    }
  }

  const handleStop = async () => {
    if (!jobId) return
    try {
      await agentApi.stop(jobId)
      setPolling(false)
      if (job) setJob({ ...job, status: 'stopped' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop')
    }
  }

  // ── Voice → Runtime bridge ───────────────────────────────────────────────
  // The Runtime never knows the intent came from voice.

  const handleVoiceSubmit = () => {
    const text = confirmTranscript()
    if (text) void handleStart(text)
  }

  const showTranscriptInput = voiceState === 'ready' && transcript.trim().length > 0

  const history = job?.history ?? []

  return (
    <div className="flex flex-col h-full bg-[#080909]">
      {/* Error banner */}
      {error && (
        <div className="px-4 py-2 text-xs text-red-400 bg-red-950/40 border-b border-red-900/40">
          {error}
        </div>
      )}

      {/* Main workspace */}
      <div className="flex flex-1 gap-3 p-3 min-h-0">
        {/* Center: screenshot */}
        <div className="flex-1 min-w-0">
          <ScreenshotViewer screenshot={job?.screenshot} />
        </div>

        {/* Right: inspector */}
        <div className="w-72 flex-shrink-0">
          <RuntimeStatePanel job={job} goal={goal} />
        </div>
      </div>

      {/* Timeline */}
      <div className="h-48 px-3 pb-0 flex-shrink-0">
        <Timeline history={history} />
      </div>

      {/* Clarification — visible when the Runtime is awaiting user input */}
      {job?.clarification_question && job.status === 'paused' && jobId && (
        <ClarificationBar jobId={jobId} question={job.clarification_question} />
      )}

      {/* Voice transcript confirmation — appears above ControlBar */}
      {showTranscriptInput && (
        <div className="px-4 pb-1">
          <TranscriptInput
            transcript={transcript}
            onTranscriptChange={setTranscript}
            onSubmit={handleVoiceSubmit}
            onCancel={cancelTranscript}
          />
        </div>
      )}

      {/* Bottom bar */}
      <div className="flex items-end gap-2 px-2">
        {/* Goal input + runtime controls (takes remaining width) */}
        <div className="flex-1 min-w-0">
          <ControlBar
            status={job?.status ?? null}
            isLoading={isLoading}
            goal={goal}
            onGoalChange={setGoal}
            onStart={() => void handleStart()}
            onPause={() => void handlePause()}
            onResume={() => void handleResume()}
            onStop={() => void handleStop()}
          />
        </div>

        {/* Voice section */}
        <div className="flex flex-col items-center gap-1 pb-3 pr-3">
          <VoiceButton
            state={voiceState}
            isSupported={isSupported}
            onPressStart={startListening}
            onPressEnd={stopListening}
          />
          <VoiceStatus
            voiceState={voiceState}
            error={voiceError}
            isSupported={isSupported}
          />
        </div>
      </div>
    </div>
  )
}
