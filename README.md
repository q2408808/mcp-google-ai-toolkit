# SocketsIO Google AI Toolkit — MCP Server

Full-stack Google AI toolkit for AI agents. Provides 7 tools powered by Google Cloud APIs via the SocketsIO unified backend:

| Tool | Description | Powered By |
|------|-------------|------------|
| `translate` | Translate text across 195 languages | Google Cloud Translation |
| `detect` | Detect the language of text | Google Cloud Translation |
| `languages` | List all 195 supported languages | Google Cloud Translation |
| `bulk_translate` | Translate up to 128 texts at once | Google Cloud Translation |
| `ocr` | Extract text from images | Google Cloud Vision |
| `text_to_speech` | Convert text to audio (MP3/WAV) | Google Cloud TTS |
| `analyze_sentiment` | Analyze text sentiment | Google Cloud Natural Language |

---

## Quick Start

### 1. Get an API Key

Sign up at [socketsio.com/signup](https://socketsio.com/signup) — 500K free credits included.

### 2. Install

```bash
pip install fastmcp httpx
```

### 3. Run

```bash
export SOCKETSIO_API_KEY=your-key-here
fastmcp run server.py
```

Or with the Node.js wrapper (after `npm install`):

```bash
export SOCKETSIO_API_KEY=your-key-here
node bin/mcp-google-ai-toolkit.js
```

---

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "socketsio-google-ai-toolkit": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "SOCKETSIO_API_KEY": "your-key-here"
      }
    }
  }
}
```

---

## Tool Reference

### `translate`

Translate text to any of 195 languages.

```python
translate(
    text="Hello, world!",
    target_lang="zh",        # Target language BCP-47 code
    source_lang="auto"       # Optional: auto-detect by default
)
# Returns: {"translated_text": "你好，世界！", "detected_source_language": "en", "characters_used": 13}
```

**Supported language codes:** `zh` (Chinese), `es` (Spanish), `fr` (French), `de` (German), `ja` (Japanese), `ko` (Korean), `ar` (Arabic), `pt` (Portuguese), `ru` (Russian), `hi` (Hindi), and 185 more.

---

### `detect`

Detect the language of text.

```python
detect(text="Bonjour le monde")
# Returns: {"language": "fr", "confidence": 0.99, "is_reliable": true}
```

---

### `languages`

List all 195 supported languages.

```python
languages(display_language="zh")   # Returns names in Chinese
# Returns: {"languages": [{"language": "en", "name": "英语"}, ...], "count": 195}
```

---

### `bulk_translate`

Translate up to 128 texts in a single API call.

```python
bulk_translate(
    texts=["Hello", "Goodbye", "Thank you"],
    target_lang="ja"
)
# Returns: {"translations": [{"original": "Hello", "translated_text": "こんにちは", ...}, ...], "count": 3}
```

---

### `ocr`

Extract text from images using Google Cloud Vision.

```python
# From URL
ocr(image_url="https://example.com/receipt.jpg")

# From base64
import base64
with open("image.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
ocr(image_base64=b64, mime_type="image/png")

# Returns: {"text": "Invoice #1234\nTotal: $99.99", "characters_detected": 26}
```

**Supported formats:** JPEG, PNG, GIF, BMP, WebP, RAW, ICO, PDF, TIFF

---

### `text_to_speech`

Convert text to audio using Google Cloud TTS.

```python
result = text_to_speech(
    text="Welcome to SocketsIO!",
    language="en-US",        # BCP-47 language code
    speaking_rate=1.0,       # 0.25 to 4.0
    pitch=0.0,               # -20 to 20 semitones
    audio_encoding="MP3"     # "MP3" or "LINEAR16"
)

# Decode audio
import base64
audio_bytes = base64.b64decode(result["audio_base64"])
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

**Popular language codes:** `en-US`, `zh-CN`, `ja-JP`, `ko-KR`, `es-ES`, `fr-FR`, `de-DE`, `ar-XA`, `hi-IN`, `pt-BR`

---

### `analyze_sentiment`

Analyze text sentiment using Google Cloud Natural Language API.

```python
analyze_sentiment(
    text="I absolutely love this product! It works perfectly.",
    language="en"   # Optional language hint
)
# Returns:
# {
#   "score": 0.9,           # -1.0 (negative) to +1.0 (positive)
#   "magnitude": 1.8,       # Emotional intensity
#   "label": "positive",    # "positive", "negative", or "neutral"
#   "language": "en",
#   "sentence_count": 2,
#   "sentences": [
#     {"text": "I absolutely love this product!", "score": 0.9, "magnitude": 0.9},
#     {"text": "It works perfectly.", "score": 0.9, "magnitude": 0.9}
#   ]
# }
```

**Sentiment interpretation:**
- `score ≥ 0.25` → positive
- `score ≤ -0.25` → negative
- `-0.25 < score < 0.25` → neutral
- `magnitude > 3.0` → strong emotion

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOCKETSIO_API_KEY` | ✅ Yes | — | Your SocketsIO API key |
| `SOCKETSIO_API_BASE` | No | `https://api.socketsio.com` | API base URL (for self-hosted) |

---

## Pricing

| Tool | Price |
|------|-------|
| translate | $0.005/call |
| detect | $0.002/call |
| languages | Free |
| bulk_translate | $0.005 + $0.001/extra text |
| ocr | $0.01/call |
| text_to_speech | $0.01/call |
| analyze_sentiment | $0.005/call |

Or buy character packs for bulk translation: [socketsio.com/pricing](https://socketsio.com/pricing)

---

## Links

- 🌐 Website: [socketsio.com](https://socketsio.com)
- 📖 API Docs: [socketsio.com/docs](https://socketsio.com/docs)
- 🔑 Get API Key: [socketsio.com/signup](https://socketsio.com/signup)
- 💬 Support: hello@socketsio.com
