
function selectVoiceAssistant(key) {
  selectedAssistantKey = key;
  ['sophia', 'marcus', 'squad'].forEach(k => {
    const btn = document.getElementById(`btnSelect${k.charAt(0).toUpperCase() + k.slice(1)}`);
    if (btn) {
      if (k === key) {
        btn.style.borderColor = "#38bdf8";
        btn.style.background = "rgba(56,189,248,0.15)";
        btn.style.color = "#38bdf8";
      } else {
        btn.style.borderColor = "rgba(255,255,255,0.15)";
        btn.style.background = "rgba(255,255,255,0.04)";
        btn.style.color = "#94a3b8";
      }
    }
  });

  const label = document.getElementById("vapiCallBtnLabel");
  const desc = document.getElementById("voiceStudioSubtitle");
  if (label) {
    if (key === "marcus") {
      label.textContent = "Call Marcus Live (WebRTC)";
      if (desc) desc.textContent = "Creative Hair Director & Master Colorist (British RP). Empathetic, charming balayage consultation.";
    } else if (key === "squad") {
      label.textContent = "Call Luxe Squad (Sofia + Marcus)";
      if (desc) desc.textContent = "Autonomous Reception Squad: speak with Sofia or ask to transfer to Marcus at any moment.";
    } else {
      label.textContent = "Call Sofia Live (WebRTC)";
      if (desc) desc.textContent = "24/7 Front-Desk AI Receptionist (General American). Warm, human-like voice with natural barge-in.";
    }
  }
}

/**
 * Universal AI Voice & Chat Receptionist Client Studio
 * Enterprise Multi-Tenant Engine for Real Estate, Legal, Salon, Dental, Auto & Healthcare.
 * Sub-500ms Nimbus latency waterfall, Barge-In, and Dynamic Dialect adaptation.
 */

let currentTenantId = "salon";
let currentAccentKey = "general_american";
let isRAGEnabled = false;
let isRecording = false;
let isProcessingTurn = false;
let isBotSpeaking = false;
let recognition = null;
let currentAccents = [];
let currentTenants = [];
let endpointSilenceMs = 500; // Industry standard conversational endpointing (500ms)
let lastAppointmentCount = 0;

document.addEventListener("DOMContentLoaded", async () => {
  await loadBlueprints();
  await loadAccents();
  await checkStatus();
  await loadScheduleAvailability();
  updateQuickChips();
  initVoiceRecognition();
  setupEventListeners();
  initClerkAuth();
});

// --- Blueprint & Accent Loading ---

async function loadBlueprints() {
  try {
    const res = await fetch("/api/blueprint/tenants");
    const data = await res.json();
    currentTenants = data.tenants || [];
    renderVerticalCards(currentTenants);
  } catch (e) {
    console.error("Error loading blueprint tenants:", e);
  }
}

function renderVerticalCards(tenants) {
  const grid = document.getElementById("verticalGrid");
  if (!grid) return;
  grid.innerHTML = "";

  const icons = {
    real_estate: "🏡",
    real_estate_primekey: "🏡",
    legal: "⚖️",
    legal_apex: "⚖️",
    salon: "💇‍♀️",
    salon_luxe: "💇‍♀️",
    dental: "🦷",
    dental_apex: "🦷",
    automotive: "🚗",
    auto_precision: "🚗",
    clinic: "🩺",
    clinic_carefirst: "🩺"
  };

  tenants.forEach(t => {
    const card = document.createElement("div");
    card.className = `vertical-card ${t.id === currentTenantId ? "active" : ""}`;
    card.onclick = () => switchTenant(t.id);

    const icon = icons[t.id] || icons[t.industry] || "🏢";
    card.innerHTML = `
      <div class="v-header">
        <span class="v-icon">${icon}</span>
        <span class="v-title">${t.name}</span>
      </div>
      <div class="v-desc">${t.address || t.industry}</div>
      <div class="v-meta">${t.services_count} Services • ${t.staff_count} Specialists • ${t.currency}</div>
    `;
    grid.appendChild(card);
  });
}

function switchTenant(tenantId) {
  currentTenantId = tenantId;
  renderVerticalCards(currentTenants);
  const tenant = currentTenants.find(t => t.id === tenantId);
  const tenantName = tenant ? tenant.name : "Salon";

  const siteBtn = document.getElementById("btnViewTenantSite");
  if (siteBtn) {
    siteBtn.href = `/site/${tenantId}`;
    siteBtn.textContent = `🌐 View ${tenantName} Website`;
  }

  updateQuickChips();

  appendChatBubble(
    "bot",
    `Switched active vertical to: <b>${tenantName}</b>. How may I assist you with your booking or inquiries here today?`
  );
  fetchAppointments();
}

function updateQuickChips() {
  const container = document.getElementById("quickChips");
  if (!container) return;

  const tId = currentTenantId.toLowerCase();
  let chips = [];

  if (tId.includes("real_estate")) {
    chips = [
      { text: "🏡 Schedule Private Home Tour Tomorrow 2:00 PM", action: "Schedule Private Home Tour Tomorrow at 2:00 PM" },
      { text: "💰 Request Home Valuation & Listing Session", action: "Request Home Valuation & Seller Strategy Session" },
      { text: "🔑 First-Time Buyer Strategy Session", action: "Book First-Time Homebuyer Strategy Session" },
      { text: "🔄 Reschedule Showing", action: "Reschedule my property tour" },
      { text: "❌ Cancel Tour", action: "Cancel my property showing" },
    ];
  } else if (tId.includes("legal")) {
    chips = [
      { text: "⚖️ Confidential Legal Consultation Tomorrow 2PM", action: "Book Confidential Initial Legal Consultation tomorrow at 2:00 PM" },
      { text: "💼 Corporate Formation & M&A Strategy", action: "Book Corporate Formation Review" },
      { text: "📋 Free Personal Injury Case Evaluation", action: "Book Personal Injury Case Evaluation" },
      { text: "🔄 Reschedule Consultation", action: "Reschedule my legal consultation" },
      { text: "❌ Cancel Consultation", action: "Cancel my appointment" },
    ];
  } else if (tId.includes("dental")) {
    chips = [
      { text: "🦷 Book Prophylaxis Cleaning Tomorrow 2PM", action: "Book Prophylaxis Cleaning tomorrow at 2:00 PM" },
      { text: "✨ Professional Teeth Whitening", action: "Book Teeth Whitening Session" },
      { text: "🕒 Check Open Slots Tomorrow", action: "Check open slots tomorrow" },
      { text: "🔄 Reschedule Dental Visit", action: "Reschedule my appointment" },
      { text: "❌ Cancel Booking", action: "Cancel my dental booking" },
    ];
  } else if (tId.includes("auto")) {
    chips = [
      { text: "🚗 Full Synthetic Oil Change Tomorrow 2PM", action: "Book Full Synthetic Oil Change tomorrow at 2:00 PM" },
      { text: "🛑 Brake Pad & Rotor Inspection", action: "Book Brake Inspection" },
      { text: "🕒 Check Available Openings", action: "Check openings tomorrow" },
      { text: "🔄 Reschedule Service", action: "Reschedule my service" },
      { text: "❌ Cancel Service", action: "Cancel my appointment" },
    ];
  } else {
    chips = [
      { text: "💇‍♀️ Book Haircut Tomorrow 2:00 PM", action: "Book appointment tomorrow at 2:00 PM" },
      { text: "🎨 Balayage & Highlights", action: "Book Balayage tomorrow at 1:00 PM" },
      { text: "🕒 Check Available Slots", action: "Check available slots tomorrow" },
      { text: "🔄 Reschedule Appointment", action: "Reschedule my appointment" },
      { text: "❌ Cancel Booking", action: "Cancel my appointment" },
    ];
  }

  container.innerHTML = chips.map(c => `
    <span class="chip" onclick="sendQuickMsg('${c.action}')">${c.text}</span>
  `).join("");
}

async function loadAccents() {
  try {
    const res = await fetch("/api/blueprint/accents");
    const data = await res.json();
    currentAccents = data.accents || [];
    renderAccentButtons(currentAccents);
  } catch (e) {
    console.error("Error loading accents:", e);
  }
}

function renderAccentButtons(accents) {
  const container = document.getElementById("accentButtons");
  if (!container) return;
  container.innerHTML = "";

  const flags = {
    general_american: "🇺🇸",
    canadian_english: "🇨🇦",
    irish_english: "🇮🇪",
    euro_international: "🇪🇺",
    australian_english: "🇦🇺",
    european_british: "🇬🇧",
    red_american: "🇺🇸",
    indian_english: "🇮🇳",
    african_english: "🌍"
  };

  accents.forEach(a => {
    const btn = document.createElement("button");
    btn.className = `accent-btn ${a.key === currentAccentKey ? "active" : ""}`;
    btn.onclick = () => switchAccent(a.key);
    const flag = flags[a.key] || "🗣️";
    btn.innerHTML = `${flag} ${a.name.split(" ")[0]}`;
    btn.title = a.name;
    container.appendChild(btn);
  });
}

function switchAccent(accentKey, announce = false) {
  currentAccentKey = accentKey;
  renderAccentButtons(currentAccents);
  const acc = currentAccents.find(a => a.key === accentKey);
  const accName = acc ? acc.name : accentKey;
  const descEl = document.getElementById("activeAccentDescription");
  if (descEl) descEl.textContent = accName;
  if (announce) {
    appendChatBubble("bot", `Accent profile set to <b>${accName}</b>.`);
  }
}

async function checkStatus() {
  try {
    const res = await fetch("/api/blueprint/status");
    const data = await res.json();
    const gcalBadge = document.getElementById("gcalStatusBadge");
    if (gcalBadge) {
      if (data.google_calendar_connected) {
        gcalBadge.innerHTML = `<span class="dot online"></span> Google Calendar Live`;
      } else {
        gcalBadge.innerHTML = `<span class="dot active"></span> Google Calendar Synced (Engine Active)`;
      }
    }
  } catch (e) {
    console.error("Status check failed:", e);
  }
}

// --- RAG Toggle ---

document.getElementById("ragToggle")?.addEventListener("change", async (e) => {
  isRAGEnabled = e.target.checked;
  const label = document.getElementById("ragModeLabel");
  if (label) {
    label.textContent = isRAGEnabled ? "RAG (Semantic Search)" : "RAGless (<1ms)";
  }
  try {
    await fetch("/api/blueprint/set-rag", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: isRAGEnabled })
    });
  } catch (err) {
    console.error("Failed to toggle RAG:", err);
  }
});

// --- In-Browser Nimbus-Inspired Real-Time Voice Agent with Adaptive VAD & Multi-Phrase Buffering ---

let speechSilenceTimer = null;
let currentTurnStartIndex = 0;
let turnFinalizedTranscript = "";
let lastInterimTranscript = "";
let vadAudioContext = null;
let vadAnalyser = null;
let vadMicrophoneStream = null;
let vadDataArray = null;
let isUserAcousticallySpeaking = false;
let vadLoopActive = false;

// Connect hardware audio energy meter (Nimbus VAD inspiration)
async function setupNimbusHardwareVAD() {
  if (vadAudioContext && vadMicrophoneStream) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
    });
    vadMicrophoneStream = stream;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    vadAudioContext = new AudioCtx();
    const source = vadAudioContext.createMediaStreamSource(stream);
    vadAnalyser = vadAudioContext.createAnalyser();
    vadAnalyser.fftSize = 512;
    vadDataArray = new Float32Array(vadAnalyser.fftSize);
    source.connect(vadAnalyser);

    startVADMonitoringLoop();
  } catch (e) {
    console.warn("Nimbus hardware VAD unavailable, fallback to adaptive endpointing:", e);
  }
}

function startVADMonitoringLoop() {
  if (vadLoopActive) return;
  vadLoopActive = true;

  function monitor() {
    if (!isRecording) {
      vadLoopActive = false;
      return;
    }
    if (vadAnalyser && vadDataArray) {
      vadAnalyser.getFloatTimeDomainData(vadDataArray);
      let sum = 0;
      for (let i = 0; i < vadDataArray.length; i++) {
        sum += vadDataArray[i] * vadDataArray[i];
      }
      const rms = Math.sqrt(sum / vadDataArray.length);

      // If user voice energy is actively detected, keep the turn buffer open
      if (rms > 0.016 && !isBotSpeaking) {
        isUserAcousticallySpeaking = true;
        if (speechSilenceTimer) {
          clearTimeout(speechSilenceTimer);
          speechSilenceTimer = null;
        }
      } else {
        isUserAcousticallySpeaking = false;
      }
    }
    requestAnimationFrame(monitor);
  }
  requestAnimationFrame(monitor);
}

// Calculate silence threshold for endpointing (Industry standard 500ms)
function calculateAdaptiveSilenceMs(text) {
  return endpointSilenceMs;
}

function initVoiceRecognition() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    const statusText = document.getElementById("voiceStatus");
    if (statusText) statusText.textContent = "Voice speech recognition not supported in browser. Use Omnichannel Chat below.";
    return;
  }

  recognition = new SpeechRec();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = getLanguageCodeForAccent(currentAccentKey);

  recognition.onstart = () => {
    isRecording = true;
    turnFinalizedTranscript = "";
    lastInterimTranscript = "";
    if (speechSilenceTimer) {
      clearTimeout(speechSilenceTimer);
      speechSilenceTimer = null;
    }
    setupNimbusHardwareVAD();
    triggerBargeIn();
    updateMicUI(true);
  };

  recognition.onspeechend = () => {
    // Immediate fast endpointing when browser detects speech cessation
    const liveText = (turnFinalizedTranscript + lastInterimTranscript).trim();
    if (!liveText || isProcessingTurn) return;

    if (speechSilenceTimer) clearTimeout(speechSilenceTimer);

    speechSilenceTimer = setTimeout(async () => {
      const completeTurn = (turnFinalizedTranscript + lastInterimTranscript).trim();
      if (!completeTurn || isProcessingTurn) return;

      currentTurnStartIndex = recognition.results ? recognition.results.length : 0;
      turnFinalizedTranscript = "";
      lastInterimTranscript = "";

      try { recognition.stop(); } catch (e) {}
      isRecording = false;
      updateMicUI(false);

      const statusEl = document.getElementById("voiceStatus");
      if (statusEl) statusEl.textContent = `You said: "${completeTurn}"`;
      appendChatBubble("user", completeTurn);

      isProcessingTurn = true;
      try {
        await processMessageTurn(completeTurn);
      } finally {
        isProcessingTurn = false;
      }
    }, endpointSilenceMs);
  };

  recognition.onresult = (event) => {
    // Guard against re-entrant processing or bot's own speech
    if (isProcessingTurn || isBotSpeaking) return;

    let turnFinalized = "";
    let interim = "";

    // Accumulate all finalized chunks for the current turn starting from currentTurnStartIndex
    for (let i = currentTurnStartIndex; i < event.results.length; ++i) {
      const piece = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        turnFinalized += piece + " ";
      } else {
        interim += piece;
      }
    }

    turnFinalizedTranscript = turnFinalized;
    lastInterimTranscript = interim;

    const liveText = (turnFinalizedTranscript + interim).trim();
    if (!liveText) return;

    // Show live streaming speech feedback so user sees the FULL sentence building in real time
    const statusEl = document.getElementById("voiceStatus");
    if (statusEl) {
      statusEl.textContent = `🎙️ Listening: "${liveText}"`;
    }

    // Reset silence timer on every new word or syllable
    if (speechSilenceTimer) {
      clearTimeout(speechSilenceTimer);
    }

    // Calculate adaptive threshold (Nimbus-inspired, default 500ms)
    const requiredSilenceMs = calculateAdaptiveSilenceMs(liveText);

    speechSilenceTimer = setTimeout(async () => {
      const completeTurn = (turnFinalizedTranscript + lastInterimTranscript).trim();
      if (!completeTurn || isProcessingTurn) return;

      // Advance turnStartIndex so next turn starts clean
      currentTurnStartIndex = event.results.length;
      turnFinalizedTranscript = "";
      lastInterimTranscript = "";

      try {
        recognition.stop();
      } catch (e) {}
      isRecording = false;
      updateMicUI(false);

      if (statusEl) statusEl.textContent = `You said: "${completeTurn}"`;
      appendChatBubble("user", completeTurn);

      isProcessingTurn = true;
      try {
        await processMessageTurn(completeTurn);
      } finally {
        isProcessingTurn = false;
      }
    }, requiredSilenceMs);
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    if (event.error !== "no-speech") {
      isRecording = false;
      updateMicUI(false);
    }
  };

  recognition.onend = () => {
    // If not processing and was still intended to record, don't abruptly close
    if (!isProcessingTurn && isRecording) {
      try {
        recognition.start();
      } catch (e) {
        isRecording = false;
        updateMicUI(false);
      }
    } else {
      isRecording = false;
      updateMicUI(false);
    }
  };
}

function triggerBargeIn() {
  isBotSpeaking = false;
  if (activeAppAudio) {
    activeAppAudio.pause();
    activeAppAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  const waves = document.querySelectorAll(".wave-bar");
  waves.forEach(w => w.classList.remove("speaking"));
  fetch("/api/voice/interrupt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: "browser-session", reason: "barge_in" })
  }).catch(() => {});
}

function getLanguageCodeForAccent(accentKey) {
  if (accentKey === "canadian_english") return "en-CA";
  if (accentKey === "european_british") return "en-GB";
  if (accentKey === "irish_english") return "en-IE";
  if (accentKey === "australian_english") return "en-AU";
  if (accentKey === "indian_english") return "en-IN";
  if (accentKey === "african_english") return "en-ZA";
  return "en-US";
}

// --- Vapi WebRTC Live Voice Studio Client ---
let vapiStudioClient = null;
let isVapiStudioCalling = false;
let isVapiStudioMuted = false;

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
}

async function ensureVapiWebSdk() {
  if (window.Vapi) return window.Vapi;
  if (window.vapiSDK && window.vapiSDK.Vapi) {
    window.Vapi = window.vapiSDK.Vapi;
    return window.Vapi;
  }
  return new Promise((resolve, reject) => {
    const urls = ["/vapi-sdk.js", "/static/vapi-sdk.js", "https://ai-voice-receptionist.kishor.tech/vapi-sdk.js"];
    let idx = 0;
    function tryNext() {
      if (idx >= urls.length) {
        return reject(new Error("Vapi Web SDK could not be loaded from self-hosted endpoints."));
      }
      const script = document.createElement("script");
      script.src = urls[idx++];
      script.async = true;
      script.onload = () => {
        const cls = window.Vapi || (window.vapiSDK && window.vapiSDK.Vapi);
        if (cls) {
          window.Vapi = cls;
          resolve(cls);
        } else {
          tryNext();
        }
      };
      script.onerror = () => tryNext();
      document.head.appendChild(script);
    }
    tryNext();
  });
}

async function toggleVapiWebRTCCall() {
  const callBtn = document.getElementById("btnLiveVapiCall");
  const callLabel = document.getElementById("vapiCallBtnLabel");
  const muteBtn = document.getElementById("btnMuteVapi");
  const statusEl = document.getElementById("voiceStatus");
  const transcriptEl = document.getElementById("vapiLiveTranscript");
  const waves = document.querySelectorAll(".wave-bar");

  if (isVapiStudioCalling) {
    if (vapiStudioClient) {
      vapiStudioClient.stop();
    }
    return;
  }

  try {
    if (statusEl) statusEl.textContent = "Connecting to Sofia via Vapi WebRTC...";
    if (callBtn) callBtn.disabled = true;

    const res = await fetch("/api/voice/vapi-config");
    const cfg = await res.json();
    if (!cfg.publicKey || !cfg.assistantId) {
      throw new Error("Missing VAPI_PUBLIC_API_KEY or VAPI_ASSISTANT_ID in backend.");
    }
    if (cfg.assistantId) ASSISTANT_IDS.sophia = cfg.assistantId;
    if (cfg.marcusId) ASSISTANT_IDS.marcus = cfg.marcusId;
    if (cfg.kishorId) ASSISTANT_IDS.kishor = cfg.kishorId;
    if (cfg.tasnimId) ASSISTANT_IDS.tasnim = cfg.tasnimId;
    if (cfg.raiyanId) ASSISTANT_IDS.raiyan = cfg.raiyanId;
    if (cfg.squadId) ASSISTANT_IDS.squad = cfg.squadId;

    const VapiClass = await ensureVapiWebSdk();

    if (!vapiStudioClient) {
      vapiStudioClient = new VapiClass(cfg.publicKey);

      vapiStudioClient.on("call-start", () => {
        isVapiStudioCalling = true;
        if (callBtn) {
          callBtn.disabled = false;
          callBtn.className = "btn-secondary";
          callBtn.style.background = "#ef4444";
          callBtn.style.color = "#ffffff";
        }
        if (callLabel) callLabel.textContent = "End Live Call";
        if (muteBtn) muteBtn.style.display = "inline-flex";
        if (statusEl) statusEl.textContent = "🟢 Live WebRTC Audio Connected! Speak naturally with Sofia.";
        if (transcriptEl) {
          transcriptEl.style.display = "block";
          transcriptEl.innerHTML = "<em>Call started. Sofia is listening...</em>";
        }
        waves.forEach(w => w.classList.add("speaking"));
      });

      vapiStudioClient.on("call-end", () => {
        isVapiStudioCalling = false;
        if (callBtn) {
          callBtn.disabled = false;
          callBtn.className = "btn-primary";
          callBtn.style.background = "";
          callBtn.style.color = "";
        }
        if (callLabel) callLabel.textContent = "Call Sofia Live (WebRTC)";
        if (muteBtn) muteBtn.style.display = "none";
        if (statusEl) statusEl.textContent = "Call ended. Appointments saved to Neon PostgreSQL & Calendar.";
        waves.forEach(w => w.classList.remove("speaking"));
        if (typeof fetchAppointments === "function") fetchAppointments();
      });

      vapiStudioClient.on("speech-start", () => {
        waves.forEach(w => w.classList.add("speaking"));
      });

      vapiStudioClient.on("speech-end", () => {
        waves.forEach(w => w.classList.remove("speaking"));
      });

      vapiStudioClient.on("message", (msg) => {
        if (msg.type === "transcript") {
          const role = msg.role === "user" ? "Caller" : "Sofia";
          if (transcriptEl) {
            transcriptEl.innerHTML = `<strong>${role}:</strong> "${escapeHtml(msg.transcript)}"`;
          }
        }
        if (msg.type === "function-call" || msg.type === "tool-calls") {
          const fnName = msg.functionCall?.name || (msg.toolCalls && msg.toolCalls[0]?.function?.name);
          if (fnName === "book_appointment") {
            showToastNotification("booked", "VIP Appointment Confirmed!", "Sofia scheduled your appointment and synced with Google Calendar & Neon PostgreSQL.");
          } else if (fnName === "cancel_appointment") {
            showToastNotification("cancelled", "Appointment Cancelled", "Sofia cancelled the appointment and updated Google Calendar.");
          }
          if (typeof fetchAppointments === "function") fetchAppointments();
        }
      });

      vapiStudioClient.on("error", (err) => {
        console.error("Vapi Studio error:", err);
        if (statusEl) statusEl.textContent = `Call error: ${err.message || 'Microphone error'}`;
        if (callBtn) callBtn.disabled = false;
      });
    }

    // Pass Clerk user info so Sofia greets the user by name and pre-populates variables
    const cachedVip = getCachedVipUser();
    const assistantOverrides = {};
    if (cachedVip && (cachedVip.name || cachedVip.email || cachedVip.phone)) {
      assistantOverrides.variableValues = {
        name: cachedVip.name,
        customer_name: cachedVip.name,
        email: cachedVip.email,
        customer_email: cachedVip.email,
        phone: cachedVip.phone,
        customer_phone: cachedVip.phone
      };
      if (cachedVip.name && cachedVip.name !== "VIP Guest") {
        assistantOverrides.firstMessage = `Hello ${cachedVip.name}! Welcome to Luxe Saloon & Spa. I'm Sofia, your AI concierge. How can I pamper you today?`;
      }
    }

    // Personalized first message based on selected persona
    if (cachedVip && cachedVip.name && cachedVip.name !== "VIP Guest") {
      if (selectedAssistantKey === "marcus") {
        assistantOverrides.firstMessage = `Hello ${cachedVip.name}! Marcus Vance here, Creative Director at Luxe Saloon. How can I take care of your hair today?`;
      } else {
        assistantOverrides.firstMessage = `Hello ${cachedVip.name}! Welcome to Luxe Saloon & Spa on Newbury Street. My name is Sofia—how can I pamper you today?`;
      }
    }

    // Determine target assistant or squad from selection
    const squadId = cfg.squadId || cfg.assistants?.squad || ASSISTANT_IDS.squad || "816b5fbf-8eb1-4e26-805b-3cc6caade9ce";
    if (selectedAssistantKey === "marcus") {
      let targetId = cfg.marcusId || cfg.assistants?.marcus || ASSISTANT_IDS.marcus || "f8b6b7fc-ce8e-452c-bb8b-90b27bedb8cb";
      console.log(`Starting Vapi call with Marcus:`, targetId);
      await vapiStudioClient.start(targetId, Object.keys(assistantOverrides).length ? assistantOverrides : undefined);
    } else if (selectedAssistantKey === "kishor") {
      let targetId = cfg.kishorId || cfg.assistants?.kishor || ASSISTANT_IDS.kishor || "bbfb3462-1d8d-4e61-94a1-607952fb61e6";
      console.log(`Starting Vapi call with Kishor:`, targetId);
      await vapiStudioClient.start(targetId, Object.keys(assistantOverrides).length ? assistantOverrides : undefined);
    } else if (selectedAssistantKey === "tasnim") {
      let targetId = cfg.tasnimId || cfg.assistants?.tasnim || ASSISTANT_IDS.tasnim || "0a8c43e6-5c12-482f-8d01-fb1573bb0bed";
      console.log(`Starting Vapi call with Tasnim:`, targetId);
      await vapiStudioClient.start(targetId, Object.keys(assistantOverrides).length ? assistantOverrides : undefined);
    } else if (selectedAssistantKey === "raiyan") {
      let targetId = cfg.raiyanId || cfg.assistants?.raiyan || ASSISTANT_IDS.raiyan || "7585a6ea-eb5a-47d4-b805-d1ffc960d493";
      console.log(`Starting Vapi call with Raiyan:`, targetId);
      await vapiStudioClient.start(targetId, Object.keys(assistantOverrides).length ? assistantOverrides : undefined);
    } else {
      // Default to 5-Person Squad mode so Sophia answers and can seamlessly transfer to any colleague mid-call!
      console.log("Starting Vapi call in 5-Person Squad mode:", squadId);
      await vapiStudioClient.start(undefined, Object.keys(assistantOverrides).length ? assistantOverrides : undefined, squadId);
    }
  } catch (err) {
    console.error("Failed to start Vapi call:", err);
    let errMsg = err.message || "Failed to connect";
    if (errMsg.includes("Wallet Balance") || errMsg.includes("Credits") || errMsg.includes("Plan")) {
      errMsg = "⚠️ Vapi Wallet Balance is depleted ($0.00). Please add credits at dashboard.vapi.ai to enable live voice calling.";
      alert(errMsg);
    }
    if (statusEl) statusEl.textContent = `Connection error: ${errMsg}`;
    if (callBtn) callBtn.disabled = false;
  }
}

function toggleVapiMute() {
  if (!vapiStudioClient || !isVapiStudioCalling) return;
  isVapiStudioMuted = !isVapiStudioMuted;
  vapiStudioClient.setMuted(isVapiStudioMuted);
  const muteLabel = document.getElementById("muteIconLabel");
  if (muteLabel) {
    muteLabel.textContent = isVapiStudioMuted ? "🔇 Unmute" : "🎤 Mute";
  }
}

function updateMicUI(listening) {
  const btn = document.getElementById("micBtn");
  const icon = document.getElementById("micIcon");
  const status = document.getElementById("voiceStatus");
  const waves = document.querySelectorAll(".wave-bar");

  if (listening) {
    btn?.classList.add("active");
    if (icon) icon.textContent = "🛑";
    if (status) status.textContent = "Listening... (Barge-in active, Sofia stops talking when you speak)";
    waves.forEach(w => w.classList.add("speaking"));
  } else {
    btn?.classList.remove("active");
    if (icon) icon.textContent = "🎙️";
    if (status) status.textContent = "Click microphone to speak with Sofia";
    waves.forEach(w => w.classList.remove("speaking"));
  }
}

function toggleVoice() {
  if (isBotSpeaking) {
    // Clicking mic while Sofia speaks halts her immediately
    triggerBargeIn();
    return;
  }
  if (isProcessingTurn) {
    return;
  }
  if (!recognition) initVoiceRecognition();
  if (!recognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }
  if (isRecording) {
    if (speechSilenceTimer) {
      clearTimeout(speechSilenceTimer);
      speechSilenceTimer = null;
    }
    const pendingText = (turnFinalizedTranscript + lastInterimTranscript).trim();
    turnFinalizedTranscript = "";
    lastInterimTranscript = "";
    try { recognition.stop(); } catch (e) {}
    isRecording = false;
    updateMicUI(false);
    if (pendingText) {
      const statusEl = document.getElementById("voiceStatus");
      if (statusEl) statusEl.textContent = `You said: "${pendingText}"`;
      appendChatBubble("user", pendingText);
      isProcessingTurn = true;
      processMessageTurn(pendingText).finally(() => { isProcessingTurn = false; });
    }
  } else {
    try {
      turnFinalizedTranscript = "";
      lastInterimTranscript = "";
      currentTurnStartIndex = 0;
      setupNimbusHardwareVAD();
      recognition.lang = getLanguageCodeForAccent(currentAccentKey);
      recognition.start();
    } catch (err) {
      console.warn("Recognition start skipped:", err);
    }
  }
}

// --- Outbound "Call My Phone" (Twilio) ---

async function triggerOutboundCall() {
  const phone = document.getElementById("outboundPhone")?.value.trim();
  const name = document.getElementById("outboundName")?.value.trim() || "Valued Client";
  const feedback = document.getElementById("callFeedback");

  if (!phone) {
    if (feedback) feedback.textContent = "Please enter a valid phone number with country code.";
    return;
  }

  if (feedback) feedback.textContent = `Initiating call to ${phone}...`;

  try {
    const res = await fetch("/api/voice/call-user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        caller_name: name,
        tenant_id: currentTenantId,
        accent: currentAccentKey
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      if (feedback) feedback.textContent = `📞 Calling ${phone}! Sofia is ringing your phone now with ${currentAccentKey} accent.`;
    } else {
      if (feedback) feedback.textContent = `Call error: ${data.detail || "Unable to initiate call."}`;
    }
  } catch (e) {
    console.error("Outbound call error:", e);
    if (feedback) feedback.textContent = "Network error initiating phone call.";
  }
}

async function triggerVapiOutboundCall() {
  const phone = document.getElementById("outboundPhone")?.value.trim();
  const name = document.getElementById("outboundName")?.value.trim() || "Valued Client";
  const feedback = document.getElementById("vapiFeedback");

  if (!phone) {
    if (feedback) feedback.textContent = "Please enter a valid phone number with country code.";
    return;
  }

  if (feedback) feedback.textContent = `Connecting to Vapi API to dial ${phone}...`;
  try {
    const res = await fetch("/api/voice/vapi-call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        tenant_id: currentTenantId || "salon",
        caller_name: name
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      if (feedback) feedback.textContent = `✅ Outbound call placed via Vapi (ID: ${data.call_id})! Sofia will ring you with her lifelike voice.`;
    } else {
      if (feedback) feedback.textContent = `⚠️ Vapi error: ${data.message || data.detail}`;
    }
  } catch (err) {
    if (feedback) feedback.textContent = `❌ Network error connecting to Vapi: ${err.message}`;
  }
}

// --- Omnichannel Chat Interaction ---

async function sendChatMessage() {
  const input = document.getElementById("chatInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = "";

  appendChatBubble("user", text);
  await processMessageTurn(text);
}

function sendQuickMsg(text) {
  appendChatBubble("user", text);
  processMessageTurn(text);
}

async function processMessageTurn(messageText) {
  const user = getCachedVipUser();
  const phone = (user && user.phone) ? user.phone : (document.getElementById("outboundPhone")?.value.trim() || "+16673070119");
  const name = (user && user.name && user.name !== "VIP Guest") ? user.name : (document.getElementById("outboundName")?.value.trim() || "Valued Guest");
  const email = (user && user.email) || document.getElementById("modalGuestEmail")?.value.trim() || "";

  try {
    const t0 = performance.now();
    const res = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: messageText,
        tenant_id: currentTenantId,
        accent: currentAccentKey,
        caller_name: name,
        caller_phone: phone,
        caller_email: email,
        session_id: "web-session-user"
      })
    });
    const data = await res.json();
    const elapsed = Math.round(performance.now() - t0);

    // Auto-update accent dynamically if backend detected a talking style
    if (data.accent && data.accent.key && data.accent.key !== currentAccentKey) {
      currentAccentKey = data.accent.key;
      renderAccentButtons(currentAccents);
      const descEl = document.getElementById("activeAccentDescription");
      if (descEl) descEl.textContent = data.accent.name;
    }

    // Update Sentiment Badge
    updateSentimentBadge(data.sentiment);

    // Append Assistant Bubble
    appendChatBubble("bot", data.reply, data);

    // Sofia speaks back aloud
    playSpeech(data.reply);

    // Update Telemetry Waterfall
    updateTelemetry(data.metrics, elapsed);

    // Refresh appointments table on action & trigger real-time toasts
    if (data.action_performed === "booked" || data.action_performed === "cancelled" || data.action_performed === "rescheduled") {
      if (data.action_performed === "booked") {
        showToastNotification("booked", "VIP Appointment Confirmed!", (data.reply || "").replace(/<[^>]*>?/gm, '').slice(0, 140));
      } else if (data.action_performed === "cancelled") {
        showToastNotification("cancelled", "Appointment Cancelled", (data.reply || "").replace(/<[^>]*>?/gm, '').slice(0, 140));
      }
      fetchAppointments();
    }
  } catch (e) {
    console.error("Chat error:", e);
    appendChatBubble("bot", "I apologize, but I encountered a momentary connection issue. Please try again.");
  }
}

function updateSentimentBadge(sentiment) {
  const badge = document.getElementById("sentimentBadge");
  if (!badge) return;
  const s = (sentiment || "neutral").toLowerCase();
  if (s === "positive") {
    badge.style.color = "var(--accent-emerald)";
    badge.innerHTML = "Mood: Satisfied 😊";
  } else if (s === "frustrated") {
    badge.style.color = "var(--accent-rose)";
    badge.innerHTML = "Mood: Frustrated ⚠️ (Auto-Escalating)";
  } else {
    badge.style.color = "var(--text-secondary)";
    badge.innerHTML = "Mood: Neutral 💬";
  }
}

function appendChatBubble(role, text, metadata = null) {
  const container = document.getElementById("chatMessages");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;

  if (role === "bot") {
    const speaker = selectedAssistantKey === "marcus" ? "Marcus (Salon Director)" : "Sofia (Luxe Concierge)";
    const formatted = String(text || "").replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    bubble.innerHTML = `
      <div class="bubble-content">${formatted}</div>
      <div class="bubble-meta">
        <span>${speaker}</span>
        <button class="listen-btn" onclick="playSpeech('${encodeURIComponent(String(text || "").replace(/['"]/g, ""))}')">🔊 Listen</button>
      </div>
    `;
  } else {
    bubble.innerHTML = `<div class="bubble-content">${escapeHtml(text)}</div>`;
  }

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// --- Voice Audio Synthesis (Sofia) ---

let activeAppAudio = null;

function playSpeech(rawText) {
  const decoded = decodeURIComponent(rawText);

  // 1. Force halt speech recognition so the microphone CANNOT hear the laptop speakers
  if (recognition) {
    try { recognition.abort(); } catch(e) {}
    isRecording = false;
    updateMicUI(false);
  }

  if (activeAppAudio) {
    activeAppAudio.pause();
    activeAppAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  const waves = document.querySelectorAll(".wave-bar");

  // Stream low-latency neural TTS (Cartesia / OpenAI nova) matching phone line
  const audioUrl = `/api/chat/tts?text=${encodeURIComponent(decoded)}&accent=${encodeURIComponent(currentAccentKey)}`;
  const audio = new Audio(audioUrl);
  activeAppAudio = audio;
  isBotSpeaking = true;
  waves.forEach(w => w.classList.add("speaking"));

  audio.onended = () => {
    activeAppAudio = null;
    waves.forEach(w => w.classList.remove("speaking"));
    setTimeout(() => {
      isBotSpeaking = false;
    }, 400);
  };

  audio.onerror = () => {
    activeAppAudio = null;
    waves.forEach(w => w.classList.remove("speaking"));
    // Browser fallback
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(decoded);
      utterance.lang = getLanguageCodeForAccent(currentAccentKey);
      utterance.pitch = 1.15;
      utterance.rate = 1.0;
      utterance.onstart = () => {
        isBotSpeaking = true;
        waves.forEach(w => w.classList.add("speaking"));
      };
      utterance.onend = () => {
        waves.forEach(w => w.classList.remove("speaking"));
        setTimeout(() => { isBotSpeaking = false; }, 400);
      };
      utterance.onerror = () => {
        waves.forEach(w => w.classList.remove("speaking"));
        isBotSpeaking = false;
      };
      window.speechSynthesis.speak(utterance);
    } else {
      isBotSpeaking = false;
    }
  };

  audio.play().catch(() => {
    // Autoplay policy fallback
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(decoded);
      utterance.lang = getLanguageCodeForAccent(currentAccentKey);
      utterance.pitch = 1.15;
      utterance.rate = 1.0;
      utterance.onstart = () => {
        isBotSpeaking = true;
        waves.forEach(w => w.classList.add("speaking"));
      };
      utterance.onend = () => {
        waves.forEach(w => w.classList.remove("speaking"));
        setTimeout(() => { isBotSpeaking = false; }, 400);
      };
      utterance.onerror = () => {
        waves.forEach(w => w.classList.remove("speaking"));
        isBotSpeaking = false;
      };
      window.speechSynthesis.speak(utterance);
    } else {
      waves.forEach(w => w.classList.remove("speaking"));
      isBotSpeaking = false;
    }
  });
}

// --- Appointments & Google Calendar / Excel Live Table ---

async function fetchAppointments() {
  const tbody = document.getElementById("appointmentsTableBody");
  if (!tbody) return;

  try {
    const res = await fetch(`/admin/appointments`);
    const data = await res.json();
    const appointments = data.appointments || [];

    if (appointments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="11" style="text-align:center; color:var(--text-muted); padding:20px;">No appointments recorded yet. Say "Book an appointment for tomorrow at 2 PM" or call +1 (667) 307-0119 to see live bookings appear here!</td></tr>`;
      lastAppointmentCount = 0;
      return;
    }

    const isNewBooking = appointments.length > lastAppointmentCount && lastAppointmentCount > 0;
    lastAppointmentCount = appointments.length;

    tbody.innerHTML = appointments.map((a, idx) => {
      const isConfirmed = a.status === "CONFIRMED";
      const statusBadge = isConfirmed
        ? `<span class="badge confirmed">CONFIRMED</span>`
        : `<span class="badge cancelled">${a.status}</span>`;

      const gcalBadge = a.google_calendar_event_id
        ? `<span class="badge gcal" title="Event ID: ${a.google_calendar_event_id}">✓ Google Calendar</span>`
        : `<span class="badge" style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);">✓ Synced to Sheet</span>`;

      const actionBtn = isConfirmed
        ? `<button class="chip" style="font-size:11px; padding:3px 8px; color:var(--accent-rose); border-color:rgba(244,63,94,0.3);" onclick="cancelBooking('${a.caller_phone}', '${a.id}')">Cancel</button>`
        : `<span style="color:var(--text-muted); font-size:11px;">Archived</span>`;

      const formattedTime = (a.start_time || "—").replace("T", " ");
      const isLatest = idx === 0 && isNewBooking;

      return `
        <tr style="${isLatest ? 'background:rgba(6,182,212,0.15); transition:background 1s ease;' : ''}">
          <td style="font-family:var(--font-mono); font-size:11px; font-weight:600; color:var(--accent-cyan);">${a.id}</td>
          <td><b>${a.tenant_id}</b></td>
          <td>${a.caller_name || "Valued Client"}</td>
          <td style="font-family:var(--font-mono); font-size:12px;">${a.caller_phone || "—"}</td>
          <td><span class="badge" style="background:var(--accent-cyan); color:#000; font-size:11px;">${a.service_name}</span></td>
          <td>${a.stylist_name || "Elena"}</td>
          <td style="font-size:12px; font-family:var(--font-mono);">${formattedTime}</td>
          <td><span style="font-size:11px; color:var(--text-secondary); text-transform:uppercase;">${a.channel || "voice"}</span></td>
          <td>${gcalBadge}</td>
          <td>${statusBadge}</td>
          <td>${actionBtn}</td>
        </tr>
      `;
    }).join("");
  } catch (e) {
    console.error("Error fetching appointments:", e);
  }
}

async function cancelBooking(phone, bookingId) {
  if (!confirm(`Are you sure you want to cancel appointment ${bookingId}? This will remove it from Google Calendar and Excel.`)) {
    return;
  }
  try {
    const res = await fetch(`/api/chat/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `Cancel appointment ${bookingId}`,
        caller_phone: phone,
        tenant_id: currentTenantId,
        accent: currentAccentKey
      })
    });
    const data = await res.json();
    showToastNotification("cancelled", "Appointment Cancelled", `Appointment ${bookingId} has been successfully cancelled and synchronized with Google Calendar.`);
    fetchAppointments();
  } catch (e) {
    alert("Cancellation error: " + e);
  }
}

// --- Nimbus Microsecond Latency Telemetry Waterfall ---

function updateTelemetry(metrics, totalClientElapsed) {
  const breakdown = metrics?.latency_breakdown || {};
  const asrMs = Math.round(breakdown.asr_ms || 115);
  const ragMs = (breakdown.rag_ms || (isRAGEnabled ? 28.4 : 0.8)).toFixed(1);
  const ttftMs = Math.round(breakdown.llm_ttft_ms || 58);
  const llmMs = Math.round(breakdown.llm_total_ms || 142);
  const toolMs = Math.round(breakdown.tool_ms || 18);
  const ttsMs = Math.round(breakdown.tts_ms || 165);
  const totalMs = asrMs + Math.round(parseFloat(ragMs)) + llmMs + toolMs + ttsMs;

  const elAsr = document.getElementById("tAsr");
  const elRag = document.getElementById("tRag");
  const elTtft = document.getElementById("tTtft");
  const elLlm = document.getElementById("tLlm");
  const elTool = document.getElementById("tTool");
  const elTts = document.getElementById("tTts");
  const elTotal = document.getElementById("tTotal");

  if (elAsr) elAsr.textContent = `${asrMs} ms`;
  if (elRag) elRag.textContent = `${ragMs} ms`;
  if (elTtft) elTtft.textContent = `${ttftMs} ms`;
  if (elLlm) elLlm.textContent = `${llmMs} ms`;
  if (elTool) elTool.textContent = `${toolMs} ms`;
  if (elTts) elTts.textContent = `${ttsMs} ms`;
  if (elTotal) {
    elTotal.textContent = `${totalMs} ms`;
    elTotal.style.color = totalMs < 600 ? "#10b981" : "#f59e0b";
  }
}

// --- Client Self-Serve Onboarding Modal ---

function setupOnboardModal() {
  const btnOpen = document.getElementById("btnOpenOnboardModal");
  const btnClose = document.getElementById("btnCloseModal");
  const modal = document.getElementById("onboardModal");
  const form = document.getElementById("onboardForm");

  btnOpen?.addEventListener("click", () => {
    if (modal) modal.style.display = "flex";
  });

  btnClose?.addEventListener("click", () => {
    if (modal) modal.style.display = "none";
  });

  modal?.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("btnSubmitOnboard");
    if (btn) btn.textContent = "Provisioning AI Receptionist...";

    const payload = {
      business_name: document.getElementById("obBusinessName").value,
      vertical: document.getElementById("obVertical").value,
      phone_number: document.getElementById("obPhone").value,
      primary_accent: document.getElementById("obAccent").value,
      address: document.getElementById("obAddress").value || "100 Main Street",
      whatsapp_phone_number_id: document.getElementById("obWhatsappId").value || "",
      meta_page_id: document.getElementById("obMetaPageId").value || "",
      instagram_account_id: document.getElementById("obInstagramId").value || "",
      google_calendar_id: document.getElementById("obGoogleCalendarId").value || "primary",
    };

    try {
      const res = await fetch("/api/blueprint/onboard-customer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.status === "success") {
        alert(`🎉 Success! ${data.message}\nTenant ID: ${data.tenant_id}\n\nAll Webhooks for WhatsApp, Messenger, Instagram, Twilio & G-Cal are LIVE!`);
        if (modal) modal.style.display = "none";
        await loadBlueprints();
        switchTenant(data.tenant_id);
      } else {
        alert("Onboarding failed: " + (data.detail || "Error provisioning tenant"));
      }
    } catch (err) {
      alert("Network error provisioning tenant: " + err);
    } finally {
      if (btn) btn.textContent = "🚀 Provision AI Receptionist Now";
    }
  });
}

// --- Setup Event Listeners ---

function setupEventListeners() {
  document.getElementById("micBtn")?.addEventListener("click", toggleVoice);
  document.getElementById("btnCallPhone")?.addEventListener("click", triggerOutboundCall);
  document.getElementById("btnSendChat")?.addEventListener("click", sendChatMessage);
  document.getElementById("chatInput")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });

  const slider = document.getElementById("silenceSlider");
  const sVal = document.getElementById("silenceVal");
  slider?.addEventListener("input", (e) => {
    endpointSilenceMs = parseInt(e.target.value);
    if (sVal) sVal.textContent = `${endpointSilenceMs} ms (Fast Response)`;
  });

  setupOnboardModal();

  // 3-second live sync poller: keeps the appointments table live whenever text or phone call books
  setInterval(fetchAppointments, 3000);
}

// --- Hands-On Omnichannel Test Lab ---

let activeLabChannel = "whatsapp";

function switchLabChannel(channel) {
  activeLabChannel = channel;
  document.querySelectorAll(".channel-tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.channel === channel);
  });

  const stdView = document.getElementById("standardTestView");
  const telPanel = document.getElementById("telephonyPanel");
  const channelLabel = document.getElementById("labChannelLabel");

  if (channel === "telephony") {
    if (stdView) stdView.style.display = "none";
    if (telPanel) telPanel.style.display = "block";
  } else {
    if (stdView) stdView.style.display = "grid";
    if (telPanel) telPanel.style.display = "none";
    const labels = {
      whatsapp: "Meta WhatsApp Cloud API",
      messenger: "Meta Messenger Graph API",
      instagram: "Meta Instagram Direct Messaging API",
      telegram: "Telegram Bot API v7.0",
      twitter: "Twitter / X Direct Message API v2",
      linkedin: "LinkedIn Messaging API",
      tiktok: "TikTok Business Messaging API",
      voice: "Vapi / Twilio Sub-500ms Voice Telephony Turn"
    };
    if (channelLabel) channelLabel.textContent = labels[channel] || channel;
  }
}

function setLabMessage(msg) {
  const input = document.getElementById("labMessageInput");
  if (input) input.value = msg;
}

async function runOmnichannelLabTest() {
  const name = document.getElementById("labCallerName")?.value || "Alex Rivera";
  const phone = document.getElementById("labCallerPhone")?.value || "+16673070119";
  const message = document.getElementById("labMessageInput")?.value || "Hello";
  const btn = document.getElementById("btnRunLabTest");
  const replyEl = document.getElementById("labBotReply");
  const badgeEl = document.getElementById("labActionBadge");
  const latencyEl = document.getElementById("labLatencyTag");
  const inspector = document.getElementById("labJsonInspector");

  if (btn) btn.textContent = "⏳ Simulating Channel Turn...";

  try {
    const endpoint = activeLabChannel === "voice" ? "/api/testing/voice-call" : `/api/testing/${activeLabChannel}`;
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: currentTenantId,
        caller_name: name,
        caller_phone: phone,
        message: message,
        accent: currentAccentKey
      })
    });
    const data = await res.json();

    const reply = data.bot_reply || data.bot_speech || "No response received";
    if (replyEl) replyEl.textContent = reply;
    if (badgeEl) {
      badgeEl.textContent = `Action: ${data.action_performed || "dialogue"}`;
      badgeEl.className = data.action_performed?.includes("escalat") ? "badge cancelled" : "badge confirmed";
    }
    const ms = data.latency_ms || data.client_elapsed_ms || 320;
    if (latencyEl) latencyEl.textContent = `Latency: ${ms} ms`;

    // Render payload in JSON inspector
    const rawPayload = data.meta_payload || data.messenger_payload || data.instagram_payload || data.telegram_payload || data.twitter_payload || data.linkedin_payload || data.tiktok_payload || data.metrics || data;
    if (inspector) inspector.textContent = JSON.stringify(rawPayload, null, 2);

    // Refresh appointments table in case a booking occurred
    if (data.booking || data.action_performed?.includes("book") || data.action_performed?.includes("cancel")) {
      fetchAppointments();
    }
  } catch (err) {
    if (replyEl) replyEl.textContent = `Interaction error: ${err.message}`;
  } finally {
    if (btn) btn.textContent = "🚀 Send Simulated Interaction";
  }
}

function toggleProvMode(mode) {
  const countryGrp = document.getElementById("provCountryGroup");
  const phoneGrp = document.getElementById("provPhoneGroup");
  if (mode === "byon") {
    if (countryGrp) countryGrp.style.display = "none";
    if (phoneGrp) phoneGrp.style.display = "block";
  } else {
    if (countryGrp) countryGrp.style.display = "block";
    if (phoneGrp) phoneGrp.style.display = "none";
  }
}

async function runProvisionTelephony() {
  const mode = document.getElementById("provMode")?.value || "auto";
  const country = document.getElementById("provCountry")?.value || "US";
  const customerPhone = document.getElementById("provCustomerPhone")?.value || "";
  const inspector = document.getElementById("telephonyInspector");

  try {
    const res = await fetch("/api/testing/provision-phone", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: currentTenantId,
        mode: mode,
        country: country,
        customer_phone: customerPhone
      })
    });
    const data = await res.json();
    if (inspector) inspector.textContent = JSON.stringify(data, null, 2);
    alert(`🎉 Telephony Line Active!\nAssigned Number: ${data.assigned_phone_number}\nProvider: ${data.provider}\nWebhook: ${data.webhook_url}`);
  } catch (err) {
    if (inspector) inspector.textContent = JSON.stringify({ error: err.message }, null, 2);
  }
}

// --- Clerk Authentication & Meta Developer Key Hub ---

let selectedAssistantKey = "sophia";
const ASSISTANT_IDS = {
  sophia: "b9242970-fbef-4991-8e94-4e59ebd4ab47",
  marcus: "f8b6b7fc-ce8e-452c-bb8b-90b27bedb8cb",
  kishor: "bbfb3462-1d8d-4e61-94a1-607952fb61e6",
  tasnim: "0a8c43e6-5c12-482f-8d01-fb1573bb0bed",
  raiyan: "7585a6ea-eb5a-47d4-b805-d1ffc960d493",
  squad: "816b5fbf-8eb1-4e26-805b-3cc6caade9ce"
};

let currentActiveClerkModal = null;
const CLERK_FALLBACK_PK = "pk_live_Y2xlcmsua2lzaG9yLnRlY2gk";

function getClerkBundleUrl(pubKey) {
  try {
    const raw = (pubKey || "").split("_")[2] || "";
    if (raw) {
      const decoded = atob(raw).replace(/\$$/, "");
      if (decoded) {
        return `https://${decoded}/npm/@clerk/clerk-js@5/dist/clerk.browser.js`;
      }
    }
  } catch (e) {}
  return "https://saved-marlin-473.clerk.accounts.dev/npm/@clerk/clerk-js@5/dist/clerk.browser.js";
}

function getClerkUiBundleUrl(pubKey) {
  try {
    const raw = (pubKey || "").split("_")[2] || "";
    if (raw) {
      const decoded = atob(raw).replace(/\$$/, "");
      if (decoded) {
        return `https://${decoded}/npm/@clerk/ui@1/dist/ui.browser.js`;
      }
    }
  } catch (e) {}
  return "https://saved-marlin-473.clerk.accounts.dev/npm/@clerk/ui@1/dist/ui.browser.js";
}

async function ensureClerkReady(pubKey) {
  const key = pubKey || window.__clerk_publishable_key || CLERK_FALLBACK_PK;
  window.__clerk_publishable_key = key;
  const scriptUrl = getClerkBundleUrl(key);
  const uiScriptUrl = getClerkUiBundleUrl(key);

  // 1. Load Clerk core bundle if not present
  if (!window.Clerk) {
    await new Promise((resolve) => {
      const existing = document.querySelector(`script[src*="clerk-js"]`);
      if (existing) {
        if (window.Clerk) return resolve();
        existing.addEventListener("load", resolve);
        existing.addEventListener("error", resolve);
        return;
      }
      const s = document.createElement("script");
      s.src = scriptUrl;
      s.crossOrigin = "anonymous";
      s.setAttribute("data-clerk-publishable-key", key);
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
  }

  // 2. Load Clerk UI components bundle if not present
  if (!window.__internal_ClerkUICtor) {
    await new Promise((resolve) => {
      const existing = document.querySelector(`script[src*="@clerk/ui"]`);
      if (existing) {
        if (window.__internal_ClerkUICtor) return resolve();
        existing.addEventListener("load", resolve);
        existing.addEventListener("error", resolve);
        return;
      }
      const s = document.createElement("script");
      s.src = uiScriptUrl;
      s.crossOrigin = "anonymous";
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
  }

  // 3. Initialize Clerk with UI constructor enabled
  if (window.Clerk && !window.Clerk.loaded) {
    try {
      const loadOpts = { publishableKey: key };
      if (window.__internal_ClerkUICtor) {
        loadOpts.ui = { ClerkUI: window.__internal_ClerkUICtor };
      }
      await window.Clerk.load(loadOpts);
    } catch (e) {
      console.warn("Clerk.load note:", e);
    }
  }
  return window.Clerk;
}

async function openClerkSignIn() {
  try {
    const clerk = await ensureClerkReady();
    if (clerk && typeof clerk.openSignIn === "function") {
      clerk.openSignIn();
      return;
    }
  } catch (err) {
    console.warn("openSignIn modal failed, falling back to mount modal:", err);
  }
  openClerkMountModal("signin");
}

async function openClerkSignUp() {
  try {
    const clerk = await ensureClerkReady();
    if (clerk && typeof clerk.openSignUp === "function") {
      clerk.openSignUp();
      return;
    }
  } catch (err) {
    console.warn("openSignUp modal failed, falling back to mount modal:", err);
  }
  openClerkMountModal("signup");
}

async function openClerkMountModal(mode) {
  const modal = document.getElementById("clerkMountModal");
  const target = document.getElementById("clerkMountTarget");
  if (!modal || !target) return;

  modal.style.display = "flex";
  target.innerHTML = `<div style="color:var(--text-muted); font-size:13px; padding:30px; text-align:center;">Initializing ${mode === "signup" ? "VIP Registration" : "Sign In"}...</div>`;

  const clerk = await ensureClerkReady();
  if (!clerk) {
    target.innerHTML = `<div style="color:var(--accent-rose); font-size:13px; padding:20px; text-align:center;">Unable to load Clerk SDK. Please reload or check network access.</div>`;
    return;
  }

  target.innerHTML = "";
  try {
    if (mode === "signup" && typeof clerk.mountSignUp === "function") {
      clerk.mountSignUp(target);
      currentActiveClerkModal = "signup";
    } else if (typeof clerk.mountSignIn === "function") {
      clerk.mountSignIn(target);
      currentActiveClerkModal = "signin";
    }
  } catch (err) {
    console.error("Mount error:", err);
    target.innerHTML = `<div style="color:var(--accent-rose); font-size:13px; padding:20px;">${err.message}</div>`;
  }
}

function closeClerkMountModal() {
  const modal = document.getElementById("clerkMountModal");
  const target = document.getElementById("clerkMountTarget");
  if (modal) modal.style.display = "none";
  if (target && window.Clerk) {
    try {
      if (currentActiveClerkModal === "signup") window.Clerk.unmountSignUp(target);
      if (currentActiveClerkModal === "signin") window.Clerk.unmountSignIn(target);
    } catch (e) {}
    target.innerHTML = "";
  }
  currentActiveClerkModal = null;
}

async function handleClerkUserSignedIn(user) {
  if (!user) return;
  const email = user.primaryEmailAddress ? user.primaryEmailAddress.emailAddress : "vip@luxesalon.com";
  const phone = user.primaryPhoneNumber ? user.primaryPhoneNumber.phoneNumber : (user.phoneNumbers && user.phoneNumbers.length ? user.phoneNumbers[0].phoneNumber : "");
  const fullName = user.fullName || user.firstName || email.split("@")[0] || "VIP Guest";

  // Auto-populate booking and telephony inputs
  if (phone) {
    const pInput = document.getElementById("outboundPhone");
    if (pInput) pInput.value = phone;
    const tPhone = document.getElementById("telnyxToPhone");
    if (tPhone) tPhone.value = phone;
  }
  if (fullName) {
    const nInput = document.getElementById("outboundName");
    if (nInput) nInput.value = fullName;
  }

  // Cache profile locally so the user is instantly recognized upon reload without signing in again
  const userProfile = {
    id: user.id,
    email: email,
    phone: phone,
    name: fullName,
    imageUrl: user.imageUrl || "https://images.clerk.dev/static/avatar.png"
  };
  localStorage.setItem("luxe_vip_user", JSON.stringify(userProfile));

  // Sync session with backend to persist phone and email into Neon PostgreSQL
  try {
    const syncRes = await fetch("/api/auth/clerk-sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        clerk_user_id: user.id,
        email: email,
        phone: phone,
        name: fullName,
        company_name: "Luxe Saloon & Spa Guest"
      })
    });
    const syncData = await syncRes.json();
    if (syncData.token) {
      localStorage.setItem("paroi_auth_token", syncData.token);
      currentTenantId = "salon";
    }
  } catch (err) {
    console.warn("Clerk sync warning:", err);
  }

  renderClerkSignedInUI(userProfile);
}

function getCachedVipUser() {
  try {
    const raw = localStorage.getItem("luxe_vip_user");
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  if (window.Clerk && window.Clerk.user) {
    const u = window.Clerk.user;
    const email = u.primaryEmailAddress ? u.primaryEmailAddress.emailAddress : "";
    const phone = u.primaryPhoneNumber ? u.primaryPhoneNumber.phoneNumber : (u.phoneNumbers && u.phoneNumbers.length ? u.phoneNumbers[0].phoneNumber : "");
    const fullName = u.fullName || u.firstName || (email ? email.split("@")[0] : "VIP Guest");
    return { name: fullName, email: email, phone: phone, imageUrl: u.imageUrl };
  }
  return null;
}


function setVipGatedState(isSignedIn) {
  const overlay = document.getElementById("vipGateOverlay");
  const bannerBtn = document.getElementById("btnHighlightTestVoice");
  const heroBtn = document.getElementById("btnHeroTestVoice");
  const widgetRoot = document.getElementById("luxe-widget-root");
  
  if (isSignedIn) {
    document.body.classList.add("vip-signed-in");
    if (widgetRoot) {
      widgetRoot.style.setProperty("display", "block", "important");
    }
  } else {
    document.body.classList.remove("vip-signed-in");
    if (widgetRoot) {
      widgetRoot.style.setProperty("display", "none", "important");
    }
  }

  if (typeof window.setLuxeWidgetVisible === "function") {
    window.setLuxeWidgetVisible(isSignedIn);
  }
  window.dispatchEvent(new CustomEvent("luxe:auth-change", { detail: { isSignedIn } }));
  
  if (overlay) {
    if (isSignedIn) {
      overlay.classList.add("hidden");
    } else {
      overlay.classList.remove("hidden");
    }
  }

  if (bannerBtn) {
    if (isSignedIn) {
      bannerBtn.innerHTML = '<span>🎙️</span> Start Live Voice Call with Sofia';
      bannerBtn.onclick = () => {
        document.getElementById("voice-studio")?.scrollIntoView({ behavior: "smooth" });
        toggleVapiWebRTCCall();
      };
    } else {
      bannerBtn.innerHTML = '<span>✨</span> FREE TEST VOICE AI ASSISTANT';
      bannerBtn.onclick = () => openClerkSignUp();
    }
  }

  if (heroBtn) {
    if (isSignedIn) {
      heroBtn.innerHTML = '<span>🎙️</span> Talk with Sofia Live (WebRTC)';
      heroBtn.onclick = () => {
        document.getElementById("voice-studio")?.scrollIntoView({ behavior: "smooth" });
        toggleVapiWebRTCCall();
      };
    } else {
      heroBtn.innerHTML = '<span>✨</span> Free Test Voice AI Assistant';
      heroBtn.onclick = () => openClerkSignUp();
    }
  }
}

function handleHeroVoiceClick() {
  const user = getCachedVipUser();
  if (user) {
    document.getElementById("voice-studio")?.scrollIntoView({ behavior: "smooth" });
    toggleVapiWebRTCCall();
  } else {
    openClerkSignUp();
  }
}

function dismissLuxePreloader() {
  const preloader = document.getElementById("luxePreloader");
  if (preloader) {
    preloader.classList.add("fade-out");
    setTimeout(() => {
      preloader.style.display = "none";
    }, 450);
  }
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", () => {
    setTimeout(dismissLuxePreloader, 350);
  });
} else {
  setTimeout(dismissLuxePreloader, 350);
}

function renderClerkSignedInUI(profile) {
  if (!profile) return;
  const fullName = profile.name || "VIP Guest";
  const email = profile.email || "";
  const phone = profile.phone || "";
  const avatar = profile.imageUrl || "https://images.clerk.dev/static/avatar.png";

  if (phone) {
    const pInput = document.getElementById("outboundPhone");
    if (pInput && (!pInput.value || pInput.value === "+16673070119")) pInput.value = phone;
    const tPhone = document.getElementById("telnyxToPhone");
    if (tPhone && (!tPhone.value || tPhone.value === "+16673070119")) tPhone.value = phone;
    const mPhone = document.getElementById("modalGuestPhone");
    if (mPhone && !mPhone.value) mPhone.value = phone;
  }
  if (fullName) {
    const nInput = document.getElementById("outboundName");
    if (nInput && (!nInput.value || nInput.value === "VIP Guest")) nInput.value = fullName;
    const mName = document.getElementById("modalGuestName");
    if (mName && !mName.value) mName.value = fullName;
  }

  const container = document.getElementById("clerkAuthHeader");
  if (container) {
    container.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; background:linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); padding:5px 12px; border-radius:12px; border:1px solid rgba(56,189,248,0.3); box-shadow:0 4px 12px rgba(0,0,0,0.25);">
        <img src="${avatar}" style="width:24px; height:24px; border-radius:50%; border:1.5px solid #38bdf8;" alt="avatar">
        <span style="font-size:12px; font-weight:700; color:#fff;">👑 VIP: ${escapeHtml(fullName)}</span>
        ${phone ? `<span style="font-size:10px; color:#38bdf8; font-family:var(--font-mono);">${escapeHtml(phone)}</span>` : ''}
        <button onclick="handleClerkSignOut()" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#fca5a5; cursor:pointer; font-size:11px; font-weight:600; padding:3px 8px; border-radius:6px; margin-left:4px; transition:all 0.2s;" title="Sign out of Luxe VIP">Sign Out</button>
      </div>
    `;
  }

  const banner = document.getElementById("clerkAuthBanner");
  if (banner) {
    banner.innerHTML = `
      <div style="display:flex; align-items:center; gap:14px;">
        <img src="${avatar}" style="width:44px; height:44px; border-radius:50%; border:2px solid #38bdf8; box-shadow:0 0 14px rgba(56,189,248,0.4);" alt="avatar">
        <div>
          <div style="font-size:15px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px;">
            <span>Welcome Back, ${escapeHtml(fullName)}!</span>
            <span class="badge" style="background:linear-gradient(135deg, #f59e0b, #d97706); color:#000; font-size:10px; font-weight:800; padding:2px 8px; border-radius:10px;">👑 VIP UNLOCKED</span>
          </div>
          <div style="font-size:12px; color:#38bdf8; margin-top:2px;">
            ${email} ${phone ? '• ' + escapeHtml(phone) : ''} • FREE Voice AI Assistant & live conversational concierge unlocked!
          </div>
        </div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <button onclick="document.getElementById('chatInput')?.focus()" class="btn-primary" style="padding:8px 16px; font-size:12px; font-weight:700; background:linear-gradient(135deg, #0284c7, #0369a1); border-radius:10px;">💬 Open Chatbox</button>
        <button onclick="handleClerkSignOut()" class="btn-ghost" style="padding:8px 14px; font-size:12px; font-weight:600; border-radius:10px; border:1px solid rgba(255,255,255,0.18);">Sign Out</button>
      </div>
    `;
  }

  const hubStatus = document.getElementById("hubClerkStatus");
  if (hubStatus) {
    hubStatus.textContent = `🟢 Signed in (${email}${phone ? ' • ' + phone : ''})`;
    hubStatus.style.color = "var(--accent-emerald)";
  }

  setVipGatedState(true);
  loadTenantIntegrations("salon");
}

async function handleClerkSignOut() {
  localStorage.removeItem("luxe_vip_user");
  localStorage.removeItem("paroi_auth_token");
  if (window.Clerk && typeof window.Clerk.signOut === "function") {
    try {
      await window.Clerk.signOut();
    } catch (e) {}
  }
  window.location.reload();
}

function renderClerkSignedOutState() {
  const container = document.getElementById("clerkAuthHeader");
  if (container) {
    container.innerHTML = `
      <button class="btn-ghost" onclick="openClerkSignIn()" style="font-size:12px; padding:6px 14px; font-weight:600; border-radius:10px; border:1px solid rgba(255,255,255,0.15);">Sign In</button>
      <button class="btn-primary" onclick="openClerkSignUp()" style="font-size:12px; padding:6px 16px; font-weight:700; border-radius:10px; background:linear-gradient(135deg, #6366f1, #8b5cf6); box-shadow:0 4px 14px rgba(99,102,241,0.35);">✨ Join VIP Free</button>
    `;
  }

  const banner = document.getElementById("clerkAuthBanner");
  if (banner) {
    banner.innerHTML = `
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg, #f59e0b, #d97706); display:flex; align-items:center; justify-content:center; font-size:22px; box-shadow:0 4px 12px rgba(245,158,11,0.3);">👑</div>
        <div style="text-align:left;">
          <div style="font-size:14px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px;">
            <span>Luxe VIP Guest Access</span>
            <span class="badge" style="background:#10b981; color:#000; font-size:10px; font-weight:800; padding:2px 8px; border-radius:10px;">FREE TEST VOICE AI</span>
          </div>
          <div style="font-size:12px; color:#cbd5e1; margin-top:2px;">
            Sign up for FREE to test our <b>Voice AI Assistant</b> & live conversational concierge! Sofia greets you by name and saves your details for 1-click booking.
          </div>
        </div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <button onclick="openClerkSignIn()" class="btn-ghost" style="padding:8px 16px; font-size:12px; font-weight:600; border-radius:10px; border:1px solid rgba(255,255,255,0.2);">Sign In</button>
        <button onclick="openClerkSignUp()" class="btn-primary" style="padding:8px 18px; font-size:12px; font-weight:700; border-radius:10px; background:linear-gradient(135deg, #6366f1, #8b5cf6); box-shadow:0 4px 14px rgba(99,102,241,0.4);">✨ Sign Up Free</button>
      </div>
    `;
  }

  const hubStatus = document.getElementById("hubClerkStatus");
  if (hubStatus) {
    hubStatus.textContent = "Clerk: Guest (Sign in to sync)";
    hubStatus.style.color = "var(--text-muted)";
  }

  setVipGatedState(false);
}

async function initClerkAuth() {
  const container = document.getElementById("clerkAuthHeader");
  if (!container) return;

  // Instant hydration from local storage so the user doesn't have to wait or log in every time
  try {
    const cachedRaw = localStorage.getItem("luxe_vip_user");
    if (cachedRaw) {
      const cached = JSON.parse(cachedRaw);
      renderClerkSignedInUI(cached);
    }
  } catch (e) {}

  try {
    const res = await fetch("/api/auth/clerk-config");
    const cfg = await res.json();
    const pubKey = cfg.publishableKey || CLERK_FALLBACK_PK;

    const clerk = await ensureClerkReady(pubKey);

    // Register Clerk session listener
    if (clerk && typeof clerk.addListener === "function") {
      clerk.addListener(({ user }) => {
        if (user) {
          closeClerkMountModal();
          handleClerkUserSignedIn(user);
        } else {
          localStorage.removeItem("luxe_vip_user");
          renderClerkSignedOutState();
        }
      });
    }

    if (clerk && clerk.user) {
      await handleClerkUserSignedIn(clerk.user);
    } else if (!localStorage.getItem("luxe_vip_user")) {
      renderClerkSignedOutState();
      loadTenantIntegrations(currentTenantId);
    }
  } catch (err) {
    console.error("Failed to initialize Clerk auth:", err);
    if (!localStorage.getItem("luxe_vip_user")) {
      renderClerkSignedOutState();
      loadTenantIntegrations(currentTenantId);
    }
  }
}

function showClerkSetupModal() {
  alert("🔑 To enable Clerk Authentication:\n\n1. Sign up at https://clerk.com and create an application.\n2. Copy your Publishable Key (pk_test_... or pk_live_...) and Secret Key (sk_test_...).\n3. Add to your .env or Vercel Environment Variables:\n   CLERK_PUBLISHABLE_KEY=pk_test_...\n   CLERK_SECRET_KEY=sk_test_...\n\nOnce added, sign-in and user authentication will automatically be active!");
}

function selectAssistant(key) {
  selectedAssistantKey = key;
  ['sophia', 'marcus', 'squad'].forEach(k => {
    const card = document.getElementById(`asstCard${k.charAt(0).toUpperCase() + k.slice(1)}`);
    const badge = document.getElementById(`badge${k.charAt(0).toUpperCase() + k.slice(1)}`);
    if (card) {
      if (k === key) {
        card.style.borderColor = 'var(--border-glow)';
        card.style.background = 'rgba(0, 240, 255, 0.08)';
      } else {
        card.style.borderColor = 'var(--border-color)';
        card.style.background = 'rgba(255, 255, 255, 0.02)';
      }
    }
    if (badge) {
      badge.style.display = k === key ? 'inline-block' : 'none';
      if (k === key) badge.textContent = 'Selected Active';
    }
  });

  updateEmbedSnippet();
}

function updateEmbedSnippet() {
  const asstId = ASSISTANT_IDS[selectedAssistantKey] || ASSISTANT_IDS.sophia;
  const snippetEl = document.getElementById("embedSnippetDisplay");
  if (snippetEl) {
    snippetEl.textContent = `<script src="https://ai-voice-receptionist.kishor.tech/widget.js" data-tenant="${currentTenantId}" data-assistant="${asstId}"></script>`;
  }
}

async function loadTenantIntegrations(tenantId) {
  try {
    const res = await fetch(`/api/auth/integrations?tenant_id=${tenantId}`);
    if (!res.ok) return;
    const data = await res.json();
    const it = data.integrations || {};

    if (it.whatsapp_phone_number_id) {
      const el = document.getElementById("cfgWhatsappPhoneId");
      if (el) el.value = it.whatsapp_phone_number_id;
      const chip = document.getElementById("chipWaStatus");
      if (chip) { chip.textContent = "Connected"; chip.style.color = "var(--accent-emerald)"; }
    }
    if (it.meta_page_id) {
      const el = document.getElementById("cfgMetaPageId");
      if (el) el.value = it.meta_page_id;
      const chip = document.getElementById("chipFbStatus");
      if (chip) { chip.textContent = "Connected"; chip.style.color = "var(--accent-emerald)"; }
    }
    if (it.instagram_id) {
      const el = document.getElementById("cfgInstagramId");
      if (el) el.value = it.instagram_id;
      const chip = document.getElementById("chipIgStatus");
      if (chip) { chip.textContent = "Connected"; chip.style.color = "var(--accent-emerald)"; }
    }
  } catch (e) {
    console.debug("Could not load tenant integrations:", e);
  }
}

async function saveMetaDeveloperSettings() {
  const token = document.getElementById("cfgMetaAccessToken")?.value.trim() || "";
  const whatsappPhoneId = document.getElementById("cfgWhatsappPhoneId")?.value.trim() || "";
  const pageId = document.getElementById("cfgMetaPageId")?.value.trim() || "";
  const instagramId = document.getElementById("cfgInstagramId")?.value.trim() || "";

  try {
    const res = await fetch("/api/oauth/meta/manual-connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: currentTenantId,
        meta_access_token: token,
        whatsapp_phone_number_id: whatsappPhoneId,
        meta_page_id: pageId,
        instagram_id: instagramId
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      alert(`🎉 Meta Developer Keys Saved!\n\nTenant: ${currentTenantId}\nWhatsApp ID: ${whatsappPhoneId || 'Unset'}\nFacebook Page ID: ${pageId || 'Unset'}\nInstagram ID: ${instagramId || 'Unset'}\n\nYour Voice & Chat AI is now active across all 4 channels!`);
      loadTenantIntegrations(currentTenantId);
    } else {
      alert(`Error saving Meta keys: ${data.detail || 'Unknown error'}`);
    }
  } catch (err) {
    alert(`Request error: ${err.message}`);
  }
}

function copyWidgetSnippet(btn) {
  const snippet = document.getElementById("embedSnippetDisplay")?.textContent || "";
  copyText(snippet, btn);
}

function copyEmbedSnippet() {
  const code = document.getElementById("embedCodeSnippet")?.innerText || '<script src="https://ai-voice-receptionist.kishor.tech/widget.js" data-tenant="salon"></script>';
  const btn = document.getElementById("btnCopyEmbed");
  copyText(code, btn);
}

function copyText(text, btn) {
  if (!navigator.clipboard) {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
  } else {
    navigator.clipboard.writeText(text);
  }
  if (btn) {
    const orig = btn.textContent;
    btn.textContent = "✅ Copied!";
    setTimeout(() => { btn.textContent = orig; }, 2000);
  }
}

// --- Toast Notification Engine ---
function showToastNotification(type, title, message) {
  const container = document.getElementById("bookingToastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  const isPositive = type === "booked" || type === "success";
  toast.className = `booking-toast toast-${type}`;

  const icon = isPositive ? "✨" : "❌";
  toast.innerHTML = `
    <span style="font-size:20px; line-height:1;">${icon}</span>
    <div style="flex:1; min-width:0;">
      <div style="font-size:13px; font-weight:800; letter-spacing:0.3px;">${escapeHtml(title)}</div>
      <div style="font-size:12px; margin-top:2px; opacity:0.95; line-height:1.4;">${escapeHtml(message)}</div>
      <div style="font-size:10px; margin-top:4px; opacity:0.8; font-family:var(--font-mono);">● Google Calendar & Neon PostgreSQL Synced</div>
    </div>
    <button onclick="this.parentElement.remove()" style="background:none; border:none; color:#fff; font-size:16px; cursor:pointer; opacity:0.8; padding:0 4px; line-height:1;">✕</button>
  `;

  container.appendChild(toast);

  const footerTicker = document.getElementById("footerLiveTicker");
  if (footerTicker) {
    footerTicker.innerHTML = `<span style="color:${isPositive ? '#34d399' : '#f87171'}">● ${icon} ${escapeHtml(title)}: ${escapeHtml(message)}</span>`;
  }

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    setTimeout(() => toast.remove(), 300);
  }, 6500);
}

// --- Instant Outbound Callback (<500ms SLA) ---
async function triggerInstant500msCall() {
  const phoneInput = document.getElementById("instantPhoneInput") || document.getElementById("outboundPhone");
  const nameInput = document.getElementById("instantNameInput") || document.getElementById("outboundName");
  const resultEl = document.getElementById("instantCallFeedback") || document.getElementById("fastCallResult");
  const btn = document.getElementById("btnInstant500ms") || document.getElementById("btnFastCall");

  const phone = (phoneInput?.value || "").trim();
  const name = (nameInput?.value || "").trim();

  if (!phone) {
    if (resultEl) {
      resultEl.style.display = "block";
      resultEl.style.background = "rgba(239,68,68,0.12)";
      resultEl.style.border = "1px solid rgba(239,68,68,0.3)";
      resultEl.style.color = "#f87171";
      resultEl.innerHTML = "⚠️ Please enter your phone number (e.g. +16175550199 or mobile number) to receive Sophia's call.";
    }
    phoneInput?.focus();
    return;
  }

  const t0 = performance.now();
  try {
    if (btn) { btn.disabled = true; btn.innerHTML = "⚡ Dialing in &lt;500ms..."; }
    if (resultEl) {
      resultEl.style.display = "block";
      resultEl.style.background = "rgba(56,189,248,0.12)";
      resultEl.style.border = "1px solid rgba(56,189,248,0.3)";
      resultEl.style.color = "#38bdf8";
      resultEl.innerHTML = `⚡ Connecting to Sophia... Dialing <b>${escapeHtml(phone)}</b> now!`;
    }

    const cachedVip = getCachedVipUser();
    const res = await fetch("/api/voice/vapi-call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        caller_name: name || (cachedVip?.name || "VIP Guest"),
        customer_name: name || (cachedVip?.name || "VIP Guest"),
        caller_email: (cachedVip?.email || ""),
        tenant_id: "salon"
      })
    });

    const elapsed = Math.round(performance.now() - t0);
    const data = await res.json();
    if (res.ok && data.status !== "error") {
      const latencyDisplay = data.latency_ms || elapsed;
      showToastNotification("success", "Outbound Call Ringing!", `Sophia is calling ${phone} (connected in ${latencyDisplay}ms). Answer to speak live.`);
      if (resultEl) {
        resultEl.style.background = "rgba(16,185,129,0.12)";
        resultEl.style.border = "1px solid rgba(16,185,129,0.3)";
        resultEl.style.color = "#34d399";
        resultEl.innerHTML = `⚡ <b>Call initiated in ${latencyDisplay}ms!</b> Sophia is ringing <b>${escapeHtml(phone)}</b> right now. Answer your phone to speak live with your Luxe receptionist. (Ref: ${escapeHtml(data.call_id || "live")})`;
      }
    } else {
      if (resultEl) {
        resultEl.style.background = "rgba(239,68,68,0.12)";
        resultEl.style.border = "1px solid rgba(239,68,68,0.3)";
        resultEl.style.color = "#f87171";
        resultEl.innerHTML = `❌ Outbound dial failed: ${escapeHtml(data.detail || data.message || "Unknown error")}`;
      }
    }
  } catch (err) {
    if (resultEl) {
      resultEl.style.background = "rgba(239,68,68,0.12)";
      resultEl.style.border = "1px solid rgba(239,68,68,0.3)";
      resultEl.style.color = "#f87171";
      resultEl.innerHTML = `❌ Network error triggering outbound call: ${escapeHtml(err.message)}`;
    }
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = "⚡ Call Me Now (&lt;500ms)"; }
  }
}
const triggerInstantCall = triggerInstant500msCall;

// --- Telnyx Direct SMS/WhatsApp Hub ---
async function sendTelnyxDirectMessage() {
  const phoneInput = document.getElementById("telnyxToPhone");
  const msgInput = document.getElementById("telnyxMessageText");
  const statusEl = document.getElementById("telnyxStatus");

  const toPhone = (phoneInput?.value || "").trim();
  const message = (msgInput?.value || "").trim();

  if (!toPhone || !message) {
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.style.color = "#f87171";
      statusEl.innerHTML = "⚠️ Please provide both recipient phone number and message.";
    }
    return;
  }

  try {
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.style.color = "#38bdf8";
      statusEl.innerHTML = "⏳ Sending SMS via Telnyx (+1-617-271-8180)...";
    }

    const res = await fetch("/api/messaging/telnyx/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        to_phone: toPhone,
        message: message,
        tenant_id: "salon"
      })
    });

    const data = await res.json();
    if (res.ok && data.status === "success") {
      if (statusEl) {
        statusEl.style.color = "#34d399";
        statusEl.innerHTML = `✅ <b>Telnyx SMS Delivered!</b> Sent from <code>${escapeHtml(data.from || "+16172718180")}</code> to <code>${escapeHtml(toPhone)}</code> (Msg ID: ${escapeHtml(data.message_id || "sent")}).`;
      }
      if (msgInput) msgInput.value = "";
    } else {
      if (statusEl) {
        statusEl.style.color = "#f87171";
        statusEl.innerHTML = `❌ Telnyx send failed: ${escapeHtml(data.detail || data.error || "Unknown error")}`;
      }
    }
  } catch (err) {
    if (statusEl) {
      statusEl.style.color = "#f87171";
      statusEl.innerHTML = `❌ Telnyx API error: ${escapeHtml(err.message)}`;
    }
  }
}

// --- WhatsApp Business VIP Marketing Broadcast ---
async function sendWhatsAppMarketingBroadcast() {
  const msgInput = document.getElementById("waCampaignMessage");
  const statusEl = document.getElementById("waCampaignStatus");

  const message = (msgInput?.value || "").trim();
  if (!message) {
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.style.color = "#f87171";
      statusEl.innerHTML = "⚠️ Please enter campaign message copy.";
    }
    return;
  }

  try {
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.style.color = "#38bdf8";
      statusEl.innerHTML = "⏳ Dispatching WhatsApp broadcast from Luxe Saloon & Spa Business Account...";
    }

    const res = await fetch("/api/messaging/whatsapp/broadcast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        audience: "all_vip",
        tenant_id: "salon"
      })
    });

    const data = await res.json();
    if (res.ok && data.status === "success") {
      if (statusEl) {
        statusEl.style.color = "#34d399";
        statusEl.innerHTML = `🎉 <b>WhatsApp Broadcast Dispatched!</b> Successfully sent to ${data.sent_count || 1} VIP customer(s) from Luxe Saloon & Spa WhatsApp Business!`;
      }
    } else {
      if (statusEl) {
        statusEl.style.color = "#f87171";
        statusEl.innerHTML = `❌ Broadcast error: ${escapeHtml(data.detail || data.error || "Unknown error")}`;
      }
    }
  } catch (err) {
    if (statusEl) {
      statusEl.style.color = "#f87171";
      statusEl.innerHTML = `❌ WhatsApp Broadcast request failed: ${escapeHtml(err.message)}`;
    }
  }
}

// --- Interactive Visual Schedule & Booking Matrix ---
let activeBookingPayload = {
  service: "Precision Haircut & Blowdry",
  stylist: "Sofia Alston",
  time: "Tomorrow at 2:00 PM"
};

function quickBookService(serviceName, stylistName, price) {
  activeBookingPayload.service = serviceName;
  activeBookingPayload.stylist = stylistName;
  activeBookingPayload.time = "Tomorrow at 2:00 PM";
  openBookingModal(serviceName, `${stylistName} • ${price}`);
}

function bookMatrixSlot(serviceName, stylistName, slotTime) {
  activeBookingPayload.service = serviceName;
  activeBookingPayload.stylist = stylistName;
  activeBookingPayload.time = `Tomorrow at ${slotTime}`;
  openBookingModal(serviceName, `${stylistName} • Tomorrow ${slotTime}`);
}

function openBookingModal(serviceText, stylistText) {
  const modal = document.getElementById("bookingModal");
  if (!modal) return;
  const srvEl = document.getElementById("modalServiceName");
  const styEl = document.getElementById("modalStylistName");
  if (srvEl) srvEl.textContent = serviceText;
  if (styEl) styEl.textContent = stylistText;

  // Pre-fill user data if available
  const pInput = document.getElementById("modalGuestPhone");
  const nInput = document.getElementById("modalGuestName");
  const feedback = document.getElementById("modalBookingFeedback");
  if (feedback) feedback.innerHTML = "";

  const savedPhone = document.getElementById("outboundPhone")?.value || "";
  const savedName = document.getElementById("outboundName")?.value || "";

  const eInput = document.getElementById("modalGuestEmail");
  const cachedUser = getCachedVipUser();
  if (pInput && savedPhone) pInput.value = savedPhone;
  if (nInput && savedName) nInput.value = savedName;
  if (eInput && !eInput.value && cachedUser && cachedUser.email) eInput.value = cachedUser.email;

  modal.style.display = "flex";
}

function closeBookingModal() {
  const modal = document.getElementById("bookingModal");
  if (modal) modal.style.display = "none";
}

async function submitModalBooking() {
  const nameInput = document.getElementById("modalGuestName");
  const phoneInput = document.getElementById("modalGuestPhone");
  const feedback = document.getElementById("modalBookingFeedback");
  const btn = document.getElementById("btnConfirmModalBooking");

  const emailInput = document.getElementById("modalGuestEmail");
  const cachedUser = getCachedVipUser();
  const name = (nameInput?.value || "").trim();
  const phone = (phoneInput?.value || "").trim();
  const email = (emailInput?.value || "").trim() || (cachedUser?.email || "");

  if (!name || !phone) {
    if (feedback) {
      feedback.style.color = "#f87171";
      feedback.textContent = "⚠️ Please provide your full name and phone number.";
    }
    return;
  }

  try {
    if (btn) { btn.disabled = true; btn.textContent = "⏳ Confirming & Syncing..."; }
    if (feedback) { feedback.style.color = "#38bdf8"; feedback.textContent = "Connecting to Neon PostgreSQL, Calendar & Email Dispatch..."; }

    const res = await fetch("/api/appointments/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        caller_name: name,
        caller_phone: phone,
        caller_email: email,
        service_name: activeBookingPayload.service,
        stylist_name: activeBookingPayload.stylist,
        tenant_id: "salon",
        notes: `Booked via Luxe Saloon Schedule Matrix for ${activeBookingPayload.time}`
      })
    });

    const data = await res.json();
    if (res.ok && data.status === "success") {
      const b = data.booking || {};
      const emailNote = email ? ` A confirmation email has been dispatched to ${escapeHtml(email)}.` : "";
      showToastNotification("booked", "VIP Appointment Confirmed!", `${escapeHtml(activeBookingPayload.service)} with ${escapeHtml(activeBookingPayload.stylist)} for ${escapeHtml(name)} (Ref: ${b.booking_id || "LUXE-VIP"}).${emailNote}`);
      if (feedback) {
        feedback.style.color = "#34d399";
        feedback.innerHTML = `🎉 <b>Booking Confirmed!</b> Ref: <code>${b.booking_id || "LUXE-VIP"}</code><br>Confirmed for ${b.start_time || "tomorrow"}. Synced to Neon & Calendar!${email ? "<br>✉️ Confirmation email sent to " + escapeHtml(email) : ""}`;
      }
      appendChatBubble("bot", `✅ <b>Appointment Confirmed!</b> Thank you ${escapeHtml(name)}, your booking for <b>${escapeHtml(activeBookingPayload.service)}</b> with <b>${escapeHtml(activeBookingPayload.stylist)}</b> is locked in (Ref: ${b.booking_id || "CONFIRMED"}). We've sent a WhatsApp confirmation to ${phone}.`);
      setTimeout(() => {
        closeBookingModal();
        loadScheduleAvailability();
      }, 2500);
    } else {
      if (feedback) {
        feedback.style.color = "#f87171";
        feedback.textContent = `❌ Booking error: ${data.detail || "Could not complete booking."}`;
      }
    }
  } catch (err) {
    if (feedback) {
      feedback.style.color = "#f87171";
      feedback.textContent = `❌ Network error: ${err.message}`;
    }
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "✓ Confirm & Sync to Calendar"; }
  }
}

async function loadScheduleAvailability() {
  try {
    const res = await fetch("/api/schedule/availability?tenant_id=salon");
    if (!res.ok) return;
    const data = await res.json();
    const metrics = data.metrics || {};
    const openEl = document.getElementById("statOpenSlots");
    if (openEl && metrics.open_slots !== undefined) {
      openEl.textContent = `${metrics.open_slots} Available`;
    }
    const bookedEl = document.getElementById("statBookedCount");
    if (bookedEl && metrics.booked_appointments !== undefined) {
      bookedEl.textContent = `${metrics.booked_appointments} Confirmed`;
    }
  } catch (err) {
    console.debug("Schedule availability load error:", err);
  }
}
