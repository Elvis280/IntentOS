import json

from app.core.llm import client, MODEL


SYSTEM_PROMPT = """
You are the UI Locator of IntentOS.

Given a screenshot and a target UI element,
return ONLY JSON.

Example:

{
    "label":"Download button",
    "found":true,
    "x":421,
    "y":287,
    "confidence":0.97
}

If not found:

{
    "label":"Download button",
    "found":false
}
"""


def locate(image, target):

    response = client.models.generate_content(

        model=MODEL,

        contents=[
            SYSTEM_PROMPT,
            f"Locate: {target}",
            image
        ]
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)
