import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client=genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_PROMPT="""
You are the VVision Module of IntentOS.
Analyze the Screenshot and return ONLY valid JSON.
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
    response=client.models.generate_content(model="gemini-3.5-flash",
                                            contents=[SYSTEM_PROMPT,image])
    return json.loads(response.text)