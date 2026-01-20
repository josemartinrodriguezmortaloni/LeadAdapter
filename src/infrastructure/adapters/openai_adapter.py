import tiktoken
from openai import AsyncOpenAI

from application.ports.llm_port import LLMPort, LLMResponse
from infrastructure.config.settings import Settings


class OpenAIAdapter(LLMPort):
    def __init__(self, settings: Settings):
        self.client = AsyncOpenAI()
        self.model = settings.openai_model
        self.settings = settings
        self._encoding = tiktoken.get_encoding("cl100k_base")

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1000,
    ) -> LLMResponse:
        response = await self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            temperature=temperature,
            input=prompt,
            max_output_tokens=max_output_tokens,
        )

        if response.usage is None:
            raise ValueError("OpenAI response missing usage data")

        return LLMResponse(
            content=response.output_text,
            prompt_tokens=response.usage.input_tokens,
            response_tokens=response.usage.output_tokens,
            model=response.model,
        )

    async def complete_json(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.3
    ) -> LLMResponse:
        json_instructions = (system_prompt or "") + "\n Respond only with valid JSON"
        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
            instructions=json_instructions,
            temperature=temperature,
            text={"format": {"type": "json_object"}},
        )

        if response.usage is None:
            raise ValueError("OpenAI response missing usage data")

        return LLMResponse(
            content=response.output_text,
            prompt_tokens=response.usage.input_tokens,
            response_tokens=response.usage.output_tokens,
            model=response.model,
        )

    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))
