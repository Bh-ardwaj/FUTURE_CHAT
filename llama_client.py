# backend/llama_client.py
import asyncio
from typing import AsyncGenerator

async def stream_llamacpp(cmd: list, prompt: str) -> AsyncGenerator[str, None]:
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        proc.stdin.write((prompt + "\n").encode("utf-8"))
        await proc.stdin.drain()
    except Exception:
        pass

    try:
        while True:
            chunk = await proc.stdout.read(1024)
            if not chunk:
                break
            yield chunk.decode("utf-8", errors="ignore")
    finally:
        try:
            proc.kill()
        except Exception:
            pass
