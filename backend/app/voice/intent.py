from app.core.llm import client, MODEL

INTENT_PROMPT = """
You are the Intent Parser for IntentOS.
You receive a raw voice transcript.
Your job is to extract the core user goal.
Ignore filler words, stutters, or casual conversation.
If the transcript does not contain a clear actionable goal, return "NO_INTENT".
Otherwise, return the clear, concise goal.

Example:
Transcript: "uh hey intent os can you um open powerpoint and make a presentation about AI"
Output: "Create a PowerPoint presentation about AI"

Example:
Transcript: "hey what's up"
Output: "NO_INTENT"
"""

class IntentParser:
    def parse(self, transcript: str) -> str:
        if not transcript or not transcript.strip():
            return "NO_INTENT"
            
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                INTENT_PROMPT,
                f"Transcript: {transcript}"
            ]
        )
        return response.text.strip()
