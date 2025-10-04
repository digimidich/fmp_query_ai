#!/usr/bin/env python
# server.py — FastMCP with OpenAI → FileMaker (curl+jq) workflow + logs to STDERR
import os, sys, time, json, signal, logging, shlex, subprocess
from typing import Optional
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# ---------- Logging (STDERR so we don't break MCP STDOUT) ----------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("openai-bridge")

# Optional file log (tail -f /tmp/openai-bridge.log)
if os.environ.get("LOG_FILE", ""):
    from logging.handlers import RotatingFileHandler
    fh = RotatingFileHandler(os.environ["LOG_FILE"], maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    fh.setLevel(log.level)
    log.addHandler(fh)
    log.info("File logging enabled at %s", os.environ["LOG_FILE"])

mcp = FastMCP("openai-bridge")

# ---------- OpenAI helpers ----------
def _openai_client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    return OpenAI(api_key=key)

KEYWORD_SYSTEM_PROMPT = (
    "You are a keyword extraction specialist. Extract search keywords from natural "
    "language and return ONLY a valid JSON object in this format: "
    '{"scriptParameterValue": "keyword1 keyword2 keyword3"}. Remove common words '
    "like 'the', 'from', 'for', 'all'. Keep names, dates, and specific terms. "
    "Never include explanations, only the JSON."
)

def extract_keywords_json(natural_query: str,
                          model: str = "gpt-4o-mini") -> dict:
    """Calls OpenAI and returns a dict like: {"scriptParameterValue": "..."}"""
    log.info("⇢ OpenAI keyword extract | model=%s | prompt='%s'",
             model, (natural_query[:240] + (" …" if len(natural_query) > 240 else "")))
    client = _openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": KEYWORD_SYSTEM_PROMPT},
            {"role": "user", "content": natural_query},
        ],
        temperature=0.0,
        max_tokens=120,
    )
    content = resp.choices[0].message.content or ""
    # Strip code fences if the model adds them
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        # try to remove leading "json\n"
        if "\n" in content:
            content = content.split("\n", 1)[1]
    try:
        obj = json.loads(content)
        if not isinstance(obj, dict) or "scriptParameterValue" not in obj:
            raise ValueError("Missing 'scriptParameterValue'")
        log.info("← OpenAI JSON ok | %d chars", len(obj["scriptParameterValue"]))
        return obj
    except Exception:
        log.exception("✖ OpenAI response was not valid JSON: %r", content)
        raise

# ---------- FileMaker OData via curl | jq ----------
FM_URL = os.environ.get(
    "FM_SCRIPT_URL",
    'https://digimidi.fmcloud.fm/fmi/odata/v4/DIGIMIDI_DEV/Script.search_pet_n8n'
)
FM_AUTH_BASIC = os.environ.get(
    "FM_AUTH_BASIC",
    # You can set this in env. The example below is from your message; override in env for safety.
    "YW50b2luZToxMjMh"  # base64(user:pass)
)

def run_filemaker_script(script_param_value: str) -> str:
    """
    Executes EXACTLY the example pipeline:
      curl -sS -X POST "<URL>" \
        -H "Content-Type: application/json" \
        -H "Authorization: Basic <FM_AUTH_BASIC>" \
        --data '{"scriptParameterValue":"<openai reply>"}' \
      | jq -r '.scriptResult.resultParameter | split("\\r")[0] | fromjson'
    Returns the jq-parsed JSON (as a string).
    """
    # Build the --data payload EXACTLY like the example (single quotes outside)
    payload = {"scriptParameterValue": script_param_value}
    data_literal = json.dumps(payload, ensure_ascii=False)  # -> {"scriptParameterValue":"..."}
    log.info("→ FileMaker via curl | url=%s | data=%s", FM_URL, data_literal)

    # We’ll run the two-stage pipeline: curl -> jq, without touching stdout ourselves
    curl_cmd = [
        "curl", "-sS", "-X", "POST", FM_URL,
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Basic {FM_AUTH_BASIC}",
        "--data", data_literal
    ]
    jq_expr = '.scriptResult.resultParameter | split("\\r")[0] | fromjson'
    jq_cmd = ["jq", "-r", jq_expr]

    # Start curl
    curl_proc = subprocess.Popen(
        curl_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Pipe into jq
    jq_proc = subprocess.Popen(
        jq_cmd,
        stdin=curl_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    curl_proc.stdout.close()  # allow curl to receive SIGPIPE if jq exits
    out, err = jq_proc.communicate()
    curl_err = curl_proc.stderr.read()
    curl_proc.stderr.close()
    curl_ret = curl_proc.wait()
    jq_ret = jq_proc.returncode

    if curl_ret != 0:
        log.error("curl failed (code %s): %s", curl_ret, curl_err.strip())
        raise RuntimeError(f"curl failed: {curl_err.strip()}")
    if jq_ret != 0:
        log.error("jq failed (code %s): %s", jq_ret, err.strip())
        raise RuntimeError(f"jq failed: {err.strip()}")

    out = (out or "").strip()
    log.info("← FileMaker jq output | %d chars", len(out))
    return out  # this is the final JSON string from FileMaker

# ---------- MCP tools ----------
@mcp.tool()
def ask_openai(prompt: str,
               model: str = "gpt-4o-mini",
               system: Optional[str] = None,
               temperature: float = 0.7,
               max_output_tokens: Optional[int] = None) -> str:
    """Simple pass-through to OpenAI (unchanged)."""
    log.info("⇢ Received tool call: ask_openai")
    client = _openai_client()
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=temperature,
        max_tokens=max_output_tokens,
    )
    text = resp.choices[0].message.content or ""
    log.info("⇠ Sending tool result | %d chars", len(text))
    return text

@mcp.tool()
def search_pet(natural_query: str,
               openai_model: str = "gpt-4o-mini") -> str:
    """
    Workflow:
      1) OpenAI extracts keywords → {"scriptParameterValue": "..."} (STRICT JSON)
      2) POST that JSON to FileMaker via curl (exact example) and pipe to jq
      3) Return the jq-parsed JSON string (what FileMaker script returned)
    """
    log.info("⇢ Received tool call: search_pet | query='%s'",
             (natural_query[:240] + (" …" if len(natural_query) > 240 else "")))
    kw = extract_keywords_json(natural_query, model=openai_model)  # dict
    # Build exact {"scriptParameterValue":"..."} for curl
    script_param = kw["scriptParameterValue"]
    result_json = run_filemaker_script(script_param)
    log.info("⇠ search_pet done")
    return result_json  # keep as string so Claude gets raw JSON text

# ---------- Graceful lifecycle ----------
def _on_signal(name: str):
    def handler(signum, frame):
        log.info("Caught %s, shutting down…", name)
        raise KeyboardInterrupt()
    return handler

if __name__ == "__main__":
    log.info("Server starting (FastMCP, stdio mode).")
    signal.signal(signal.SIGINT, _on_signal("SIGINT"))
    signal.signal(signal.SIGTERM, _on_signal("SIGTERM"))
    try:
        mcp.run()
    finally:
        log.info("Server stopped.")