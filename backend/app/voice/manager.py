import threading
from app.voice.stt import SpeechToTextProvider, MockSTTProvider
from app.voice.intent import IntentParser
from app.runtime.job_manager import job_manager
from app.runtime.loop import run_job

class VoiceManager:
    """
    Orchestrates the Voice Runtime Pipeline.
    Wake Word -> STT -> Intent -> Job Creation
    """
    def __init__(self, stt_provider: SpeechToTextProvider = None):
        self.stt = stt_provider or MockSTTProvider()
        self.intent_parser = IntentParser()
        
    def process_audio(self, audio_data: bytes) -> str:
        """
        Processes audio data, extracts intent, and spawns a Runtime Job if an intent is found.
        Returns the Job ID or a status message.
        """
        # 1. Transcribe
        transcript = self.stt.transcribe(audio_data)
        if not transcript:
            return "NO_TRANSCRIPT"
            
        # 2. Extract Intent
        goal = self.intent_parser.parse(transcript)
        
        if goal == "NO_INTENT":
            return "NO_INTENT"
            
        # 3. Hand off to Runtime by creating a Job
        job = job_manager.create(goal=goal)
        
        # 4. Start the runtime loop in a background thread
        thread = threading.Thread(target=run_job, args=(job,), daemon=True)
        thread.start()
        
        return job.job_id
