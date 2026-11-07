# 🎙️ Vapi Voice WebRTC Widget (`@kishor/vapi-voice-widget`)

[![npm version](https://img.shields.io/badge/npm-v2.2.0-blue.svg)](https://www.npmjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A lightweight, zero-latency WebRTC Audio Voice Widget powered by the **Vapi Web SDK (`@vapi-ai/web`)**. Embed a live conversational AI voice concierge into any website with 1 line of HTML or React code.

## 🚀 Features

- **Direct In-Browser Audio**: Zero phone dial-in or telephony latency. Speaks directly with Cartesia Sonic-3.5 and Deepgram Nova-2.
- **Audio Visualizer**: Live pulsating waveforms reacting dynamically to the assistant's voice and user speech.
- **Microphone VAD & Barge-In**: Instant conversational interruption handling.
- **Session Telemetry**: Real-time transcript streaming, volume levels, and error logging.

## 📦 Installation

```bash
npm install @kishor/vapi-voice-widget @vapi-ai/web
```

## 💻 Vanilla HTML / JavaScript Usage

```html
<script type="module">
  import Vapi from "https://esm.sh/@vapi-ai/web";

  const vapi = new Vapi("YOUR_VAPI_PUBLIC_KEY");

  document.getElementById("startCallBtn").onclick = () => {
    vapi.start("YOUR_VAPI_ASSISTANT_ID");
  };

  vapi.on("speech-start", () => console.log("User speaking..."));
  vapi.on("message", (msg) => console.log("Transcript:", msg));
</script>
```

## ⚛️ React / Next.js Component

```tsx
import React, { useState } from 'react';
import Vapi from '@vapi-ai/web';

export const VoiceReceptionistButton = () => {
  const [connecting, setConnecting] = useState(false);
  const vapi = new Vapi(process.env.NEXT_PUBLIC_VAPI_KEY!);

  const handleCall = () => {
    setConnecting(true);
    vapi.start(process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID!);
  };

  return (
    <button onClick={handleCall} className="vapi-call-btn">
      {connecting ? "🎙️ In Call with Sofia" : "📞 Talk to AI Concierge"}
    </button>
  );
};
```
