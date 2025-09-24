"""AI agent orchestration for OpenGov Zoning."""

import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
import structlog
from openai import AsyncOpenAI
from openai.types.beta import Thread
from openai.types.beta.threads import Run

from ..core.config import get_settings

logger = structlog.get_logger(__name__)


class AgentService:
    """Coordinate between OpenAI Agents API, Ollama, and mock fallbacks."""

    def __init__(self):
        self.settings = get_settings()
        self.openai_client: Optional[AsyncOpenAI] = None
        if self.settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def run_analysis(
        self,
        prompt: str,
        model: str = "gpt-4",
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """Run AI analysis."""
        try:
            if provider == "openai" and self.openai_client:
                return await self._run_openai_agents(prompt, model)
            if provider == "ollama":
                return await self._run_ollama_analysis(prompt, model)
            return await self._run_mock_analysis(prompt)
        except Exception as exc:
            logger.error("analysis_failed", error=str(exc), provider=provider)
            return await self._run_mock_analysis(prompt)

    async def _run_openai_agents(self, prompt: str, model: str) -> Dict[str, Any]:
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        assistants_client = self.openai_client.beta

        assistant = await assistants_client.assistants.create(
            name="OpenGov Zoning Analyst",
            instructions=(
                "You are an expert municipal planner delivering zoning intelligence."
                " Return JSON with keys analysis, permits, risks, recommendations,"
                " and timeline summarizing the request."
            ),
            model=model,
            tools=[{"type": "code_interpreter"}],
        )

        thread: Thread = await assistants_client.threads.create()
        await assistants_client.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )

        run: Run = await assistants_client.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        while run.status in {"queued", "in_progress", "requires_action"}:
            await asyncio.sleep(0.5)
            run = await assistants_client.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )

        if run.status != "completed":
            raise RuntimeError(f"Agents run failed with status {run.status}")

        messages = await assistants_client.threads.messages.list(thread_id=thread.id)
        ai_messages = [m for m in messages.data if m.role == "assistant"]
        if not ai_messages:
            raise RuntimeError("Agents run completed without assistant messages")

        content = ai_messages[0].content[0].text.value
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            payload = {"analysis": content}

        payload.update({"provider": "openai-agents", "model": model})
        return payload

    async def _run_ollama_analysis(self, prompt: str, model: str) -> Dict[str, Any]:
        """Run analysis using Ollama."""
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    try:
                        return json.loads(result.get("response", "{}"))
                    except json.JSONDecodeError:
                        return {
                            "analysis": result.get("response", ""),
                            "provider": "ollama",
                            "model": model
                        }
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as exc:
            logger.error("ollama_analysis_failed", error=str(exc))
            return await self._run_mock_analysis(prompt)

    async def _run_mock_analysis(self, prompt: str) -> Dict[str, Any]:
        """Run mock analysis for testing."""
        return {
            "analysis": "Mock analysis result",
            "confidence": 0.85,
            "provider": "mock",
            "model": "mock-analysis",
        }

    async def chat(self, message: str) -> str:
        """Interactive chat with AI agent."""
        try:
            if not self.openai_client:
                return "AI chat is not available. Please set up OpenAI API credentials."

            assistant = await self.openai_client.beta.assistants.create(
                name="OpenGov Zoning Chat",
                instructions="Answer as a municipal zoning specialist.",
                model="gpt-4o",
            )
            thread = await self.openai_client.beta.threads.create()
            await self.openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message,
            )
            run = await self.openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )
            while run.status in {"queued", "in_progress", "requires_action"}:
                await asyncio.sleep(0.5)
                run = await self.openai_client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id,
                )

            if run.status != "completed":
                return f"Chat unavailable (status={run.status})."

            messages = await self.openai_client.beta.threads.messages.list(thread_id=thread.id)
            for entry in messages.data:
                if entry.role == "assistant" and entry.content:
                    return entry.content[0].text.value
            return "No assistant response received."
        except Exception as exc:
            logger.error("chat_failed", error=str(exc))
            return f"Chat error: {exc}"