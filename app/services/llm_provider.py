import httpx

from app.core.config import settings


class LLMProviderError(Exception):
    """Raised when the upstream LLM provider fails."""


class GroqProvider:
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model

    async def generate(self, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )

            if response.is_error:
                raise LLMProviderError(
                    f"LLM provider returned HTTP {response.status_code}"
                )

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "LLM provider request timed out"
            ) from exc

        except httpx.RequestError as exc:
            raise LLMProviderError(
                "Could not connect to the LLM provider"
            ) from exc

        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMProviderError(
                "Invalid response received from the LLM provider"
            ) from exc