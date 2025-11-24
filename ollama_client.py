# backend/ollama_client.py
import httpx
import json
from typing import AsyncGenerator

OLLAMA_URL = "http://localhost:11434/api/generate"

async def stream_ollama(model: str, prompt: str) -> AsyncGenerator[str, None]:
    payload = {"model": model, "prompt": prompt, "stream": True}
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
            async for chunk in resp.aiter_text():
                if not chunk:
                    continue
                for line in chunk.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    yield line
