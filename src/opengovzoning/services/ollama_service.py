"""Ollama integration utilities for OpenGov Zoning."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
import structlog

from ..core.config import get_settings

logger = structlog.get_logger(__name__)


class OllamaService:
    """Service for managing Ollama LLM operations."""

    def __init__(self):
        """Initialize Ollama service."""
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url

    async def run_model(
        self,
        prompt: str,
        model: str = "llama2:7b",
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Run a model with the given prompt."""
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }

                if options:
                    payload["options"] = options

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            logger.error("Ollama model execution failed", error=str(e))
            raise

    async def pull_model(self, model: str) -> None:
        """Pull a model from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model},
                    timeout=600
                )

                if response.status_code != 200:
                    raise Exception(f"Failed to pull model: {response.status_code}")

        except Exception as e:
            logger.error("Model pull failed", error=str(e))
            raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")

                if response.status_code == 200:
                    result = response.json()
                    return result.get("models", [])
                else:
                    raise Exception(f"Failed to list models: {response.status_code}")

        except Exception as e:
            logger.error("Model listing failed", error=str(e))
            return []

    async def check_connection(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False