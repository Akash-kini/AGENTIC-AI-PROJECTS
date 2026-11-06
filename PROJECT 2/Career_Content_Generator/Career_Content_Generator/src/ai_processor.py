
import json
import re
import time

from google import genai
from google.genai import types

import config

try:  # The SDK exposes API errors here; be defensive about version differences.
    from google.genai import errors as genai_errors
except ImportError:  # pragma: no cover
    genai_errors = None


class AIProcessingError(Exception):
    """Raised when the AI step cannot produce a usable result."""


_client = None

# --------------------------------------------------------------------------- #
# Low-level Gemini helpers
# --------------------------------------------------------------------------- #
def ensure_api_key():
    
    if not config.API_KEY_IS_SET:
        raise AIProcessingError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and paste your "
            "key into it (get one at https://aistudio.google.com/apikey)."
        )


def _get_client():
    global _client
    if _client is None:
        ensure_api_key()
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def parse_json_response(raw_text):
    if raw_text is None or not str(raw_text).strip():
        raise ValueError("The AI returned an empty response.")
    text = str(raw_text).strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("The AI response did not contain a JSON object.")
        data = json.loads(text[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("The AI response JSON was not an object.")
    return data


def _response_text(response):
    try:
        text = response.text
    except Exception:  
        text = None
    if text and text.strip():
        return text
    reason = ""
    feedback = getattr(response, "prompt_feedback", None)
    if feedback is not None and getattr(feedback, "block_reason", None):
        reason = f" (blocked: {feedback.block_reason})"
    raise ValueError("The AI returned no text" + reason + ".")


def _classify_error(exc):
    """Return (category, message). Categories: auth, not_found, transient, fatal."""
    code = getattr(exc, "code", None)
    message = str(getattr(exc, "message", None) or exc)
    lowered = message.lower()
    is_api_error = genai_errors is not None and isinstance(exc, genai_errors.APIError)

    if is_api_error:
        if code == 404:
            return "not_found", f"Model not found: {message}"
        if code in (408, 429, 500, 502, 503, 504):
            return "transient", f"Temporary Gemini API problem (HTTP {code}): {message}"
        if code in (401, 403) or "api key" in lowered or "api_key" in lowered:
            return "auth", f"Gemini rejected the API key or access was denied: {message}"
        return "fatal", f"Gemini API error (HTTP {code}): {message}"

    
    network_hints = ("connect", "timeout", "timed out", "network", "name resolution",
                     "temporarily", "reset by peer", "ssl")
    if any(hint in type(exc).__name__.lower() or hint in lowered for hint in network_hints):
        return "transient", f"Network problem while contacting Gemini: {message}"
    return "fatal", f"Unexpected error while calling Gemini: {type(exc).__name__}: {message}"


def generate_json(system_instruction, user_prompt):
    
    client = _get_client()
    models = [config.MODEL_NAME] + [m for m in config.FALLBACK_MODELS if m != config.MODEL_NAME]
    gen_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=config.TEMPERATURE,
        response_mime_type="application/json",
    )
    last_problem = "Unknown error."

    for model in models:
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model, contents=user_prompt, config=gen_config)
            except Exception as exc:  # noqa: BLE001 - classified below
                category, message = _classify_error(exc)
                last_problem = message
                if category in ("auth", "fatal"):
                    raise AIProcessingError(message) from exc
                if category == "not_found":
                    print(f"  [!] Model '{model}' is unavailable; trying the next one...")
                    break
                if attempt < config.MAX_RETRIES:
                    delay = config.RETRY_BASE_DELAY_SECONDS * attempt
                    print(f"  [!] {message}\n      Retrying in {delay}s "
                          f"(attempt {attempt}/{config.MAX_RETRIES})...")
                    time.sleep(delay)
                    continue
                print(f"  [!] Giving up on model '{model}' after {attempt} attempts.")
                break

            try:
                return parse_json_response(_response_text(response)), model
            except ValueError as exc:
                last_problem = f"Invalid AI response: {exc}"
                if attempt < config.MAX_RETRIES:
                    print(f"  [!] {last_problem} Retrying ({attempt}/{config.MAX_RETRIES})...")
                    time.sleep(1)
                    continue
                break

    raise AIProcessingError(f"Could not get a valid response from Gemini. Last problem: {last_problem}")
