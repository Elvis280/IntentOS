import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


SYSTEM_PROMPT = """
You are the planning module of IntentOS.

Your job is to convert the user's goal into executable steps.

You MUST use ONLY these actions:

OPEN_APPLICATION
OPEN_URL
CLICK
TYPE
PRESS_KEY
WAIT
VERIFY
SCROLL

Never invent new action names.

Return ONLY valid JSON.

Example:

{
  "goal":"Open Chrome",
  "steps":[
    {
      "step":1,
      "action":"OPEN_APPLICATION",
      "target":"Chrome",
      "description":"Launch Google Chrome"
    }
  ]
}
"""


def create_plan(goal: str):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
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