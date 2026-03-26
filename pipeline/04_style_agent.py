"""
Style Agent — artistic style prompt generator.
Receives a style entry from styles.json and uses the LLM to generate
a detailed style descriptor optimized for image generation.
Called by batch_runner.py.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at writing artistic style descriptors for AI image generation.
You will receive a style name and a base description. Your task is to expand it into a precise,
detailed style prompt optimized for image generation models like Stable Diffusion and FLUX.
Rules:
- Write a compact list of comma-separated style tags and descriptors
- Include lighting style, color palette, line quality, and rendering technique
- Stay faithful to the given style — do not mix with other styles
- Output only the style descriptor tags, nothing else"""


def generate_style_prompt(style: dict) -> str:
    """Generate a detailed style descriptor from a styles.json entry.

    Args:
        style: Style dict from styles.json with keys: id, name, style_prompt.

    Returns:
        A detailed style descriptor string optimized for image generation.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    user_prompt = (
        f"Style name: {style['name']}\n"
        f"Base description: {style['style_prompt']}\n\n"
        f"Expand this into a detailed style descriptor for image generation."
    )

    # ----
    # Step 2 – Call Ollama API
    # ----
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("style_agent failed for style '%s': %s", style["id"], e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the style descriptor
    # ----
    return response.json()["message"]["content"].strip()
