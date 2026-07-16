class SpeechToTextProvider:
    """
    Abstract interface for Speech-To-Text engines.
    """
    def transcribe(self, audio_data: bytes) -> str:
        raise NotImplementedError("STT provider must implement transcribe().")

class MockSTTProvider(SpeechToTextProvider):
    """
    Mock STT provider for initial testing.
    """
    def transcribe(self, audio_data: bytes) -> str:
        # In a real scenario, this would send audio_data to Whisper or a cloud API.
        return "create a powerpoint presentation about AI"
