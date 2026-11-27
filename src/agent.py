"""LLM agent module using Google Gemini with strict Pydantic structured outputs."""

import os
import time

from google import genai
from google.genai import errors, types

from src.schemas import ProspectReport


SYSTEM_INSTRUCTION = """You are an expert B2B sales engineer and AI automation consultant.
Analyze the scraped website content of a target company and produce an accurate, grounded
intelligence brief. Never invent services or claims not supported by the provided text.
Keep the cold outreach hook concise, specific, and human—never sound spammy."""


def _discover_gemini_models(client: genai.Client, primary: str) -> list[str]:
    """Return candidate Gemini text models available to this API key."""
    candidates = [primary]
    try:
        for m in client.models.list():
            name = (m.name or "").replace("models/", "")
            actions = m.supported_actions or []
            if (
                "gemini" in name
                and "generateContent" in actions
                and name not in candidates
                and not any(skip in name for skip in ("tts", "image", "audio", "robotics", "computer-use"))
            ):
                candidates.append(name)
    except Exception:
        pass
    return candidates


def analyze_prospect(scraped_data: dict[str, str], model: str = "gemini-3.8-flash") -> ProspectReport:
    """Run Gemini structured extraction with retry and dynamic model fallback."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file before running."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""Analyze this company website and generate a structured ProspectReport.

URL: {scraped_data['url']}
Page Title: {scraped_data['title']}
Meta Description: {scraped_data['meta_description']}

Website Copy:
{scraped_data['content']}
"""

    candidates = _discover_gemini_models(client, model)
    last_error: Exception | None = None

    for candidate in candidates[:5]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=candidate,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=ProspectReport,
                        temperature=0.2,
                    ),
                )
                if not response.text:
                    raise RuntimeError(f"Model {candidate} returned an empty response.")
                return ProspectReport.model_validate_json(response.text)
            except errors.ServerError as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(2)
                    continue
                break
            except errors.ClientError as exc:
                last_error = exc
                # 404 (not found) or 429 (rate limit): move to next discovered model
                break

    raise RuntimeError("No available Gemini model succeeded right now.") from last_error
