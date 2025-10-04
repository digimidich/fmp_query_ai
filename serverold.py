# server.py — FastMCP with terminal logging (to STDERR)
import os
import sys
import time
import signal
import logging
from typing import Optional

from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# ---------- Logging config (to STDERR) ----------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    stream=sys.stderr,  # IMPORTANT: STDERR, not STDOUT
)
log = logging.getLogger("openai-bridge")

mcp = FastMCP("openai-bridge")

def _truncate(s: str, n: int = 240) -> str:
    return s if len(s) <= n else (s[:n] + " …[truncated]")

def _call_openai(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
) -> str:
    start = time.perf_counter()
    api_key_present = bool(os.environ.get("OPENAI_API_KEY"))
    if not api_key_present:
        log.error("OPENAI_API_KEY not set")
        raise RuntimeError("Missing OPENAI_API_KEY")

    # Safe, minimal request log
    log.info("→ OpenAI request | model=%s temp=%.2f max_out=%s | prompt='%s' system=%s",
             model, temperature, max_output_tokens, _truncate(prompt), bool(system))

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )
        text = resp.choices[0].message.content or ""
        dur = (time.perf_counter() - start) * 1000
        log.info("← OpenAI response | %.0f ms | %d chars", dur, len(text))
        return text
    except Exception:
        dur = (time.perf_counter() - start) * 1000
        log.exception("✖ OpenAI call failed after %.0f ms", dur)
        raise

@mcp.tool()
def ask_openai(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Send a prompt to OpenAI and return the text response.
    Logs:
      - receipt of request from Claude (with prompt truncated)
      - backend call duration and size of response
    """
    log.info("⇢ Received tool call: ask_openai | prompt='%s'", _truncate(prompt))
    out = _call_openai(prompt, model, system, temperature, max_output_tokens)
    log.info("⇠ Sending tool result | %d chars", len(out))
    return out

def _on_signal(name: str):
    def handler(signum, frame):
        log.info("Caught %s, shutting down…", name)
        # Let FastMCP / anyio unwind normally
        raise KeyboardInterrupt()
    return handler

if __name__ == "__main__":
    # lifecycle logs
    log.info("Server starting (FastMCP, stdio mode).")
    signal.signal(signal.SIGINT, _on_signal("SIGINT"))
    signal.signal(signal.SIGTERM, _on_signal("SIGTERM"))
    try:
        mcp.run()  # blocks; logs stay in STDERR
    finally:
        log.info("Server stopped.")