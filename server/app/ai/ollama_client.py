"""
Ollama Client
Wrapper for Ollama API to interact with local LLM (Mistral).
"""

import httpx
import asyncio
import json
import os
from typing import Optional, Dict, Any, AsyncGenerator, List
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "phi3:mini")
    timeout: float = 200.0  # seconds
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 512


class OllamaClient:
    """
    Async client for Ollama API.
    Handles model inference for email response generation.
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(self.config.timeout)
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list:
        """List available models."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception:
            return []

    async def pull_model(self, model_name: str = None) -> bool:
        """Pull a model if not available."""
        model = model_name or self.config.model
        try:
            client = await self._get_client()
            response = await client.post(
                "/api/pull",
                json={"name": model},
                timeout=httpx.Timeout(600.0)  # 10 min for download
            )
            return response.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[list] = None
    ) -> str:
        """
        Generate response from the model.
        
        Args:
            prompt: The user prompt/query
            system_prompt: System instructions for the model
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stop_sequences: Sequences that stop generation
            
        Returns:
            Generated text response
        """
        client = await self._get_client()

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": max_tokens or self.config.max_tokens,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        if stop_sequences:
            payload["options"]["stop"] = stop_sequences

        try:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except httpx.HTTPStatusError as e:
            raise OllamaError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise OllamaError(f"Request error: {str(e)}") from e

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate response with streaming.
        Yields tokens as they are generated.
        """
        client = await self._get_client()

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": max_tokens or self.config.max_tokens,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with client.stream("POST", "/api/generate", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            
        Returns:
            Assistant's response
        """
        client = await self._get_client()

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": max_tokens or self.config.max_tokens,
            }
        }

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPStatusError as e:
            raise OllamaError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise OllamaError(f"Request error: {str(e)}") from e

    async def get_embeddings(self, text: str) -> List[float]:
        """Get text embeddings for semantic comparison."""
        client = await self._get_client()

        payload = {
            "model": self.config.model,
            "prompt": text
        }

        try:
            response = await client.post("/api/embeddings", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
        except Exception:
            return []


class OllamaError(Exception):
    """Custom exception for Ollama errors."""
    pass


# Singleton instance with default config
ollama_client = OllamaClient()


async def ensure_model_available():
    """Ensure the configured model is available, pull if needed."""
    if not await ollama_client.is_available():
        raise OllamaError(
            "Ollama server is not running. "
            "Please start it with: ollama serve"
        )

    models = await ollama_client.list_models()
    model_name = ollama_client.config.model
    
    # Check for model (with or without :latest tag)
    model_available = any(
        m == model_name or m.startswith(f"{model_name}:") 
        for m in models
    )
    
    if not model_available:
        print(f"Pulling model {model_name}...")
        success = await ollama_client.pull_model()
        if not success:
            raise OllamaError(
                f"Failed to pull model {model_name}"
            )
