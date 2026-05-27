# app/llm/openrouter.py

import httpx

from app.config import settings
from app.llm.base import LLMProvider


class OpenRouterLLMProvider(LLMProvider):

    def __init__(self):

        self.api_key = settings.OPENROUTER_API_KEY

        self.base_url = (
            "https://openrouter.ai/api/v1/chat/completions"
        )

        # Recommended for NL2SQL
        self.model = (
            "deepseek/deepseek-chat"
        )

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    async def generate(
        self,
        prompt: str
    ) -> str:

        headers = {

            "Authorization":
                f"Bearer {self.api_key}",

            "Content-Type":
                "application/json"
        }

        payload = {

            "model": self.model,

            "messages": [
                {
                    "role": "system",

                    "content": (
                        "You are an expert PostgreSQL "
                        "NL2SQL generation engine. "
                        "Always return valid JSON."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            "temperature": 0.1,

            "max_tokens": 4000
        }

        async with httpx.AsyncClient(
            timeout=120
        ) as client:

            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )

            # -------------------------------------------------
            # ERROR HANDLING
            # -------------------------------------------------

            if response.status_code != 200:

                raise Exception(
                    f"OpenRouter API Error: "
                    f"{response.status_code} | "
                    f"{response.text}"
                )

            data = response.json()

            # -------------------------------------------------
            # SAFETY VALIDATION
            # -------------------------------------------------

            if "choices" not in data:

                raise Exception(
                    "Invalid OpenRouter response"
                )

            if not data["choices"]:

                raise Exception(
                    "OpenRouter returned "
                    "empty choices"
                )

            content = (

                data["choices"][0]
                ["message"]
                ["content"]
            )

            if not content:

                raise Exception(
                    "Empty LLM response"
                )

            return content.strip()