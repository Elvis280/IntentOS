import json

from app.core.llm import client, MODEL


SYSTEM_PROMPT = """
You are the Vision Module of IntentOS.
Analyze the screenshot and return ONLY valid JSON.

Schema:

{
    "summary":"",
    "active_window":"",
    "applications":[],
    "buttons":[],
    "text":[]
}

Do not include markdown.
Do not explain.
Return JSON only.
"""


def analyze(image):
    response = client.models.generate_content(
        model=MODEL,
        contents=[SYSTEM_PROMPT, image]
    )
    return json.loads(response.text)