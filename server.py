"""
SocketsIO Google AI Toolkit MCP Server
Full-stack AI tools: Translation, OCR, Text-to-Speech, and Sentiment Analysis
powered by Google Cloud APIs via SocketsIO backend.
"""
import os
import httpx
from fastmcp import FastMCP

# ─── Config ───
API_BASE_URL = os.environ.get("SOCKETSIO_API_BASE", "https://api.socketsio.com")
API_KEY = os.environ.get("SOCKETSIO_API_KEY", "")

mcp = FastMCP(
    name="SocketsIO Google AI Toolkit",
    instructions=(
        "Full-stack Google AI toolkit powered by SocketsIO. Provides 7 tools:\n"
        "  • translate — Translate text across 195 languages\n"
        "  • detect — Detect the language of text\n"
        "  • languages — List all 195 supported languages\n"
        "  • bulk_translate — Translate up to 128 texts at once\n"
        "  • ocr — Extract text from images (Google Cloud Vision)\n"
        "  • text_to_speech — Convert text to audio (Google Cloud TTS)\n"
        "  • analyze_sentiment — Analyze text sentiment (Google Cloud NLP)\n\n"
        "Set SOCKETSIO_API_KEY environment variable before use. "
        "Get your free API key at https://socketsio.com/signup (500K free trial credits)."
    ),
)


def _headers() -> dict:
    if not API_KEY:
        raise ValueError(
            "SOCKETSIO_API_KEY is not set. "
            "Get your free API key at https://socketsio.com/signup"
        )
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


# ─── Translation Tools ───

@mcp.tool()
async def translate(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
) -> dict:
    """
    Translate text to the target language using Google Cloud Translation (195 languages).

    Args:
        text: The text to translate.
        target_lang: Target language BCP-47 code (e.g. "zh", "es", "fr", "ja", "de", "ar").
        source_lang: Source language code, or "auto" to detect automatically (default: "auto").

    Returns:
        dict with keys:
          - translated_text: The translated string.
          - detected_source_language: Detected or specified source language code.
          - characters_used: Number of characters consumed.
    """
    payload = {"q": text, "target": target_lang}
    if source_lang and source_lang.lower() != "auto":
        payload["source"] = source_lang

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/translate",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()

    translations = data.get("data", {}).get("translations", [])
    if not translations:
        return {"error": "No translation returned", "raw": data}

    t = translations[0]
    return {
        "translated_text": t.get("translatedText", ""),
        "detected_source_language": t.get("detectedSourceLanguage", source_lang),
        "characters_used": len(text),
    }


@mcp.tool()
async def detect(text: str) -> dict:
    """
    Detect the language of the given text.

    Args:
        text: The text whose language you want to identify.

    Returns:
        dict with keys:
          - language: BCP-47 language code (e.g. "zh", "en", "es").
          - confidence: Confidence score between 0 and 1.
          - is_reliable: Whether the detection is considered reliable.
    """
    payload = {"q": text}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/detect",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()

    detections = data.get("data", {}).get("detections", [])
    if not detections:
        return {"error": "No detection result returned", "raw": data}

    d = detections[0] if isinstance(detections[0], dict) else detections[0][0]
    return {
        "language": d.get("language", ""),
        "confidence": d.get("confidence", 0.0),
        "is_reliable": d.get("isReliable", False),
    }


@mcp.tool()
async def languages(display_language: str = "en") -> dict:
    """
    Get the list of all 195 supported translation languages.

    Args:
        display_language: Language code for language name display (default: "en").
                          E.g. "zh" returns names in Chinese, "es" in Spanish.

    Returns:
        dict with keys:
          - languages: List of {language: code, name: display_name} objects.
          - count: Total number of supported languages.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{API_BASE_URL}/v1/languages",
            params={"target": display_language},
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()

    langs = data.get("data", {}).get("languages", [])
    return {
        "languages": langs,
        "count": len(langs),
    }


@mcp.tool()
async def bulk_translate(
    texts: list[str],
    target_lang: str,
    source_lang: str = "auto",
) -> dict:
    """
    Translate multiple texts to the target language in a single request (max 128 items).

    Args:
        texts: List of strings to translate (max 128 items per call).
        target_lang: Target language BCP-47 code (e.g. "zh", "es", "fr").
        source_lang: Source language code, or "auto" to detect (default: "auto").

    Returns:
        dict with keys:
          - translations: List of {original, translated_text, detected_source_language} objects.
          - count: Number of texts translated.
          - total_characters: Total characters consumed.
    """
    if not texts:
        return {"error": "texts list is empty"}
    if len(texts) > 128:
        return {"error": "Too many texts. Maximum 128 per bulk_translate call."}

    payload = {"q": texts, "target": target_lang}
    if source_lang and source_lang.lower() != "auto":
        payload["source"] = source_lang

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/translate",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()

    raw_translations = data.get("data", {}).get("translations", [])
    results = []
    for i, t in enumerate(raw_translations):
        results.append({
            "original": texts[i] if i < len(texts) else "",
            "translated_text": t.get("translatedText", ""),
            "detected_source_language": t.get("detectedSourceLanguage", source_lang),
        })

    return {
        "translations": results,
        "count": len(results),
        "total_characters": sum(len(t) for t in texts),
    }


# ─── Vision / OCR Tool ───

@mcp.tool()
async def ocr(
    image_url: str = "",
    image_base64: str = "",
    mime_type: str = "image/jpeg",
) -> dict:
    """
    Extract text from an image using Google Cloud Vision API (OCR).

    Provide EITHER image_url (a publicly accessible URL) OR image_base64 (base64-encoded image bytes).

    Args:
        image_url: Public URL of the image to extract text from.
                   Note: The URL must be publicly accessible (not behind auth/Cloudflare).
        image_base64: Base64-encoded image data (alternative to image_url).
        mime_type: MIME type of the base64 image (default: "image/jpeg").
                   Use "image/png" for PNG, "image/webp" for WebP, etc.

    Returns:
        dict with keys:
          - text: Full extracted text from the image.
          - characters_detected: Number of characters found.

    Examples:
        ocr(image_url="https://example.com/receipt.jpg")
        ocr(image_base64="<base64_string>", mime_type="image/png")
    """
    if not image_url and not image_base64:
        return {"error": "Provide either image_url or image_base64"}

    payload: dict = {}
    if image_url:
        payload["image_url"] = image_url
    if image_base64:
        payload["image_base64"] = image_base64
        payload["mime_type"] = mime_type

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/ocr",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


# ─── Text-to-Speech Tool ───

@mcp.tool()
async def text_to_speech(
    text: str,
    language: str = "en-US",
    voice_name: str = "",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    audio_encoding: str = "MP3",
) -> dict:
    """
    Convert text to speech using Google Cloud Text-to-Speech API.
    Returns base64-encoded audio data.

    Args:
        text: The text to synthesize (max 5000 characters).
        language: BCP-47 language code (default: "en-US").
                  Examples: "zh-CN" (Mandarin), "ja-JP" (Japanese), "es-ES" (Spanish),
                  "fr-FR" (French), "de-DE" (German), "ko-KR" (Korean), "ar-XA" (Arabic).
        voice_name: Specific voice name (optional). E.g. "en-US-Wavenet-D", "zh-CN-Wavenet-A".
                    Leave empty to use the default voice for the language.
        speaking_rate: Speaking speed multiplier (0.25 to 4.0, default: 1.0).
        pitch: Voice pitch in semitones (-20 to 20, default: 0.0).
        audio_encoding: Output format — "MP3" (default) or "LINEAR16" (WAV).

    Returns:
        dict with keys:
          - audio_base64: Base64-encoded audio data. Decode to get the raw audio bytes.
          - audio_encoding: The encoding used ("MP3" or "LINEAR16").
          - language: Language code used.
          - characters_synthesized: Number of characters processed.

    Example:
        result = text_to_speech("Hello world", language="zh-CN")
        # Decode: import base64; audio_bytes = base64.b64decode(result["audio_base64"])
    """
    payload: dict = {
        "text": text,
        "language": language,
        "speaking_rate": speaking_rate,
        "pitch": pitch,
        "audio_encoding": audio_encoding,
    }
    if voice_name:
        payload["voice_name"] = voice_name

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/tts",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


# ─── Sentiment Analysis Tool ───

@mcp.tool()
async def analyze_sentiment(
    text: str,
    language: str = "",
) -> dict:
    """
    Analyze the sentiment of text using Google Cloud Natural Language API.

    Returns a sentiment score from -1.0 (very negative) to +1.0 (very positive),
    plus magnitude (intensity) and per-sentence breakdown.

    Args:
        text: The text to analyze (max 10,000 characters).
        language: Optional BCP-47 language hint (e.g. "en", "zh", "es").
                  Leave empty for automatic detection.

    Returns:
        dict with keys:
          - score: Overall sentiment score (-1.0 to 1.0).
                   Positive values = positive sentiment, negative = negative.
          - magnitude: Emotional intensity (0.0+). Higher = stronger emotion.
          - label: Human-readable label: "positive", "negative", or "neutral".
          - language: Detected or specified language code.
          - sentence_count: Number of sentences analyzed.
          - sentences: List of per-sentence sentiment (first 10 sentences).

    Interpretation guide:
      score ≥ 0.25  → positive
      score ≤ -0.25 → negative
      otherwise     → neutral
      magnitude > 3 → strong emotion regardless of direction
    """
    payload: dict = {"text": text}
    if language:
        payload["language"] = language

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/v1/sentiment",
            json=payload,
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    mcp.run()
