# 🗣️ Voice Dialect Engine (`voice-dialect-engine`)

[![PyPI version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Real-time (<1ms) lexical, cultural, and geographic dialect detection engine that dynamically switches TTS voice models and acoustic properties to match user talking styles naturally without caricatures.

## 🌎 Supported Talking Styles & Dialects

- **General American**: Neutral US / West Coast (OpenAI Nova / Cartesia Sonic-3.5)
- **Latino-American**: Warm bilingual hospitality & Spanish loanword sensitivity
- **Red American / Southern**: Warm southern hospitality colloquialisms
- **African-American / Urban Contemporary**: Rhythmic cadence & urban idioms
- **European / British English**: London Received Pronunciation & British idioms
- **Canadian English**: Polite North American raising & hospitality
- **Australian English**: Sydney breezy cadence & colloquial phrases
- **Indian English**: Polite honorifics, syntax, and South Asian phone country codes (+91)
- **Irish English**: Dublin melodic warmth & cadence

## 💻 Usage

```python
from voice_dialect_engine import DialectDetector

detector = DialectDetector()

# Detects Latino-American dialect profile in <0.2ms
accent = detector.detect_talking_style("Hola amigo, what are your available slots tomorrow?")
print(f"Selected Dialect: {accent.name} | Voice Model: {accent.openai_voice}")
```
