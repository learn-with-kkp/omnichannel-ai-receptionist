# Nimbus Voice Agent

A configurable, end-to-end **voice agent** built on top of the fictional Nimbus
SaaS catalog. Every stage of the pipeline (ASR, RAG, LLM, tools, TTS) is swappable
from the frontend, and every stage reports its latency. Built for the Vizuara
Voice Agents bootcamp.

- **Live site + embedded agent:** https://nimbus-sreedath.vercel.app
- **Playground:** https://nimbus-sreedath.vercel.app/playground/playground.html
- **Voice agent:** https://nimbus-sreedath.vercel.app/playground/voice.html
- **RAG vector viz:** https://nimbus-sreedath.vercel.app/playground/rag.html

> The starter catalog site is from
> [VizuaraAI/nimbus-voice-agent-starter](https://github.com/VizuaraAI/nimbus-voice-agent-starter).
> Nimbus is a made-up company; all names, prices, and policies are invented for teaching.

## What it does

- **Web scraping** of the catalog into clean markdown docs + a single `context.md`.
- **RAG vs RAGless** toggle. RAG uses **FAISS** with a top-k slider, optional
  reranking, and a 2D vector-cluster visualization with a query overlay.
- **Tools** (11): add to cart, cart total, annual pricing, annual-vs-monthly
  savings, sort by price, top-k most expensive, remove/checkout item, clear cart,
  checkout, product lookup. Each tool individually enable/disable-able.
- **LLM** layer: OpenAI (lite/heavy) + Gemini (flash/pro), streaming or batch,
  editable system prompt, response length, conversation history (N verbatim turns
  + a rolling summary of older turns).
- **ASR**: browser (Web Speech), OpenAI, Gemini, ElevenLabs.
- **TTS**: OpenAI, Gemini, ElevenLabs, with playback buffering.
- **Voice loop**: mic VAD endpointing, **barge-in** (echo-aware double-talk
  detector with Off/Low/Medium/High modes), and a **time-to-first-audio** latency
  pie that splits the contribution of each stage.
- **Context inspector**: see the exact prompt sent to the LLM + token count.
- **Embedded site widget**: the finalized voice agent as a chatbox on the landing
  page, sharing settings with the playground and bridged to the site cart.

## Architecture

```
backend/                 FastAPI (Railway). One process; REST + per-stage latency.
  app/
    scraping/            catalog.json -> docs/*.md + context.md
    rag/                 chunk · embed · FAISS index · retrieve · rerank · 2D viz
    llm/                 providers (openai/gemini) · orchestrator · history · prompts
    tools/               the 11 cart/pricing/product tools + registry
    asr/  tts/           provider adapters (audio transcode via bundled ffmpeg)
    audio.py latency.py main.py config.py
  data/                  bundled catalog + generated docs + context.md
playground/              static frontend: playground / voice / rag pages
nimbus-voice-agent-starter/   the Nimbus catalog site + assets/widget.js (the agent)
PLAN.md                  the phased build plan
```

## Run locally

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # then fill in your keys
python -m app.scraping.scrape           # build docs/*.md
python -m app.scraping.build_context    # build context.md
uvicorn app.main:app --reload --port 8100
```

The RAG index builds automatically on startup (or POST `/rag/build`). Keys are
read from `.env`, or sent per-request from the frontend via `X-OpenAI-Key` /
`X-Gemini-Key` / `X-ElevenLabs-Key` headers.

### Frontend

Serve the repo root statically and open the pages, e.g.:

```bash
python3 -m http.server 8081
# http://localhost:8081/playground/playground.html
# http://localhost:8081/nimbus-voice-agent-starter/index.html
```

Set the backend URL + API keys from the in-page "API keys" dialog (stored in
`localStorage`). `playground/runtime-config.js` holds the default backend URL.

## Deploy

- **Backend** -> Railway (`railway.json` + `Procfile`, `EMBEDDING_PROFILE=light`,
  ffmpeg bundled via `imageio-ffmpeg`). Set the three API keys as env vars.
- **Frontend** -> Vercel (static). Point `runtime-config.js` and the landing
  page's `NIMBUS_API_BASE` at the deployed backend URL.

## Notes

- Default agent config: ElevenLabs ASR + TTS, RAG, tools on, batch mode,
  Low-sensitivity barge-in.
- No keys are ever committed or logged; `.env` is git-ignored.
