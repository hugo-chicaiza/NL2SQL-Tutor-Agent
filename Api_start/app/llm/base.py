class LLMProvider:
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError