import os
import asyncio
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from openai import OpenAI

server = Server("openai-bridge")

# ---- Utility: call OpenAI once and return text ----
async def call_openai(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in env")

    client = OpenAI(api_key=api_key)

    # Using Chat Completions for simplicity; swap to Responses API if you prefer.
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_output_tokens,
    )
    return resp.choices[0].message.content or ""

# ---- MCP tool exposed to Claude ----
@server.tool()
async def ask_openai(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
) -> str:
    """Send a prompt to OpenAI and return the response text.

    Args:
        prompt: The user prompt to forward to OpenAI.
        model: OpenAI model name (default: gpt-4o-mini).
        system: Optional system instruction.
        temperature: Sampling temperature.
        max_output_tokens: Optional max tokens for output.
    """
    return await call_openai(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

async def main() -> None:
    transport = await stdio_server()
    await server.run(transport)

if __name__ == "__main__":
    asyncio.run(main())