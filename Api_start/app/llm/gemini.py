from google import genai
from app.config import settings
from app.llm.base import LLMProvider


'''
client = genai.Client(api_key=settings.GEMINI_API_KEY)

models = client.models.list()

for m in models:
    print(m.name)
'''
class GeminiLLMProvider(LLMProvider):

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        print("🔥 GEMINI CALLED")
        return response.text



        