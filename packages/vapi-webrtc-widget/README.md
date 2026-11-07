# @kishor/vapi-voice-widget

Drop-in WebRTC real-time conversational voice calling widget powered by Vapi and Cartesia Sonic-3.5.

## Installation
```bash
npm install @kishor/vapi-voice-widget
```

## Quick Start
```javascript
import { VapiWidget } from '@kishor/vapi-voice-widget';

const widget = new VapiWidget({
  publicKey: "YOUR_VAPI_PUBLIC_KEY",
  assistantId: "YOUR_ASSISTANT_ID"
});

widget.start();
```
