import json

from app.core.llm import client, MODEL


SYSTEM_PROMPT = """
You are the Planner Agent of IntentOS.

Convert the user's goal into executable steps.

Use ONLY these actions:

OPEN_APPLICATION
OPEN_URL
CLICK
TYPE
PRESS_KEY
WAIT
VERIFY
SCROLL

Return ONLY valid JSON.

Schema:

{
    "goal":"...",
    "steps":[
        {
            "step":1,
            "action":"OPEN_APPLICATION",
            "target":"Chrome",
            "description":"Launch Google Chrome",
            "expected_result":"Google Chrome is visible on the screen."
        }
    ]
}

Rules:

- Never invent action names.
- Every step MUST have an expected_result.
- Return JSON only.
"""


def create_plan(goal: str):

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            SYSTEM_PROMPT,
            goal
        ]
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)
