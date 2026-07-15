from google import genai

from app.core.llm import client

load_dotenv()

for model in client.models.list():
    print(model.name)
