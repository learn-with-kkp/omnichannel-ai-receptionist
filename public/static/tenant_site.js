/**
 * Tenant Custom Website Driver
 * Dynamically binds any tenant (Salon, Real Estate, Legal, Dental, Auto, Clinic, or Custom)
 * into a high-converting customer website with embedded Sofia Voice Concierge.
 */

const urlParams = new URLSearchParams(window.location.search);
let activeTenantId = urlParams.get("site") || urlParams.get("tenant_id") || "salon";
let tenantData = null;
let recognition = null;
let isRecording = false;
let isProcessingTurn = false;
let isBotSpeaking = false;

document.addEventListener("DOMContentLoaded", async () => {
  await loadTenantData();
  setupSiteVoice();
});

async function loadTenantData() {
  try {
    const res = await fetch(`/api/blueprint/tenants/${activeTenantId}`);
    const data = await res.json();
    tenantData = data.tenant;
    renderTenantUI(tenantData);
  } catch (e) {
    console.error("Failed to load tenant data:", e);
  }
}

function renderTenantUI(t) {
  if (!t) return;
  document.getElementById("siteTitle").textContent = `${t.name} | AI Concierge`;
  document.getElementById("navBusinessName").textContent = t.name;
  document.getElementById("navBusinessPhone").textContent = `📞 ${t.phone}`;
  document.getElementById("heroTitle").textContent = t.name;
  document.getElementById("heroTagline").textContent = t.tagline || `Welcome to ${t.name}. Sofia, our 24/7 AI virtual concierge, is ready to assist you.`;
  document.getElementById("chatTenantName").textContent = t.name;
  document.getElementById("telDisplay").textContent = t.phone;
  document.getElementById("btnTelLink").href = `tel:${t.phone}`;

  const icons = {
    real_estate: "🏡",
    legal: "⚖️",
    salon: "💇‍♀️",
    dental: "🦷",
    automotive: "🚗",
    clinic: "🩺"
  };
  document.getElementById("siteLogo").textContent = icons[t.industry] || "✨";

  // Render Services Catalog
  const sGrid = document.getElementById("servicesGrid");
  if (sGrid) {
    sGrid.innerHTML = t.services.map(s => `
      <div class="service-card">
        <div>
          <div style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">${s.category}</div>
          <h3 style="font-size:17px; font-weight:700; margin:6px 0 8px;">${s.name}</h3>
          <p style="font-size:13px; color:var(--text-secondary); margin-bottom:14px; line-height:1.4;">${s.description}</p>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:14px; margin-top:10px;">
          <div>
            <span class="service-price">${s.price > 0 ? `$${s.price}` : 'Complimentary'}</span>
            <span style="font-size:11px; color:var(--text-muted);"> / ${s.duration_minutes} min</span>
          </div>
          <button class="btn-primary" style="width:auto; padding:6px 14px; font-size:12px;" onclick="prefillBooking('${s.name}')">
            Book with Sofia
          </button>
        </div>
      </div>
    `).join("");
  }

  // Render Staff Specialists
  const staffGrid = document.getElementById("staffGrid");
  if (staffGrid) {
    staffGrid.innerHTML = t.staff.map(st => `
      <div class="staff-card">
        <div class="staff-avatar">👤</div>
        <h4 style="font-size:15px; font-weight:700;">${st.name}</h4>
        <div style="font-size:12px; color:var(--accent-cyan); margin-bottom:8px;">${st.role}</div>
        <button class="chip" style="font-size:11px; margin-top:6px;" onclick="prefillBooking('with ${st.name}')">
          Request ${st.name.split(' ')[0]}
        </button>
      </div>
    `).join("");
  }

  // Render Quick Chips
  const chipContainer = document.getElementById("siteQuickChips");
  if (chipContainer && t.services.length > 0) {
    chipContainer.innerHTML = t.services.slice(0, 3).map(s => `
      <span class="chip" onclick="prefillBooking('${s.name}')">📅 Book ${s.name}</span>
    `).join("") + `
      <span class="chip" onclick="sendSiteChatText('Check available slots tomorrow')">🕒 Check Open Slots</span>
      <span class="chip" onclick="sendSiteChatText('Cancel my appointment')">❌ Cancel Booking</span>
    `;
  }
}

function prefillBooking(serviceOrStaff) {
  const input = document.getElementById("siteChatInput");
  if (input) {
    input.value = `I would like to book an appointment for ${serviceOrStaff} tomorrow at 2:00 PM`;
    input.focus();
    sendSiteChat();
  }
}

// --- Voice Recognition with Smart Silence Detection & Barge-In for Custom Site ---

let siteSpeechSilenceTimer = null;
let siteTurnStartIndex = 0;
let siteFinalizedTranscript = "";
let siteLastInterimTranscript = "";

function calculateSiteAdaptiveSilenceMs(text) {
  return 500; // Industry standard fast response (500ms)
}

function setupSiteVoice() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) return;

  recognition = new SpeechRec();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    isRecording = true;
    siteFinalizedTranscript = "";
    siteLastInterimTranscript = "";
    if (siteSpeechSilenceTimer) {
      clearTimeout(siteSpeechSilenceTimer);
      siteSpeechSilenceTimer = null;
    }
    if (activeSiteAudio) {
      activeSiteAudio.pause();
      activeSiteAudio = null;
    }
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      fetch("/api/voice/interrupt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: "site-session", reason: "barge_in" })
      }).catch(() => {});
    }
    updateSiteMicUI(true);
  };

  recognition.onspeechend = () => {
    const liveText = (siteFinalizedTranscript + siteLastInterimTranscript).trim();
    if (!liveText || isProcessingTurn) return;

    if (siteSpeechSilenceTimer) clearTimeout(siteSpeechSilenceTimer);

    siteSpeechSilenceTimer = setTimeout(async () => {
      const completeTurn = (siteFinalizedTranscript + siteLastInterimTranscript).trim();
      if (!completeTurn || isProcessingTurn) return;

      siteTurnStartIndex = recognition.results ? recognition.results.length : 0;
      siteFinalizedTranscript = "";
      siteLastInterimTranscript = "";

      try { recognition.stop(); } catch (e) {}
      isRecording = false;
      updateSiteMicUI(false);

      const statusEl = document.getElementById("siteVoiceStatus");
      if (statusEl) statusEl.textContent = `You: "${completeTurn}"`;
      appendSiteChatBubble("user", completeTurn);

      isProcessingTurn = true;
      try {
        await processSiteTurn(completeTurn);
      } finally {
        isProcessingTurn = false;
      }
    }, 500);
  };

  recognition.onresult = (event) => {
    if (isProcessingTurn || isBotSpeaking) return;

    let turnFinalized = "";
    let interim = "";

    for (let i = siteTurnStartIndex; i < event.results.length; ++i) {
      const piece = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        turnFinalized += piece + " ";
      } else {
        interim += piece;
      }
    }

    siteFinalizedTranscript = turnFinalized;
    siteLastInterimTranscript = interim;

    const liveText = (siteFinalizedTranscript + interim).trim();
    if (!liveText) return;

    const statusEl = document.getElementById("siteVoiceStatus");
    if (statusEl) {
      statusEl.textContent = `🎙️ Listening: "${liveText}"`;
    }

    if (siteSpeechSilenceTimer) {
      clearTimeout(siteSpeechSilenceTimer);
    }

    const adaptiveSilenceMs = calculateSiteAdaptiveSilenceMs(liveText);

    siteSpeechSilenceTimer = setTimeout(async () => {
      const completeTurn = (siteFinalizedTranscript + siteLastInterimTranscript).trim();
      if (!completeTurn || isProcessingTurn) return;

      siteTurnStartIndex = event.results.length;
      siteFinalizedTranscript = "";
      siteLastInterimTranscript = "";

      try {
        recognition.stop();
      } catch (e) {}
      isRecording = false;
      updateSiteMicUI(false);

      if (statusEl) statusEl.textContent = `You: "${completeTurn}"`;
      appendSiteChatBubble("user", completeTurn);

      isProcessingTurn = true;
      try {
        await processSiteTurn(completeTurn);
      } finally {
        isProcessingTurn = false;
      }
    }, adaptiveSilenceMs);
  };

  recognition.onerror = (event) => {
    if (event.error !== "no-speech") {
      isRecording = false;
      updateSiteMicUI(false);
    }
  };

  recognition.onend = () => {
    if (!isProcessingTurn && isRecording) {
      try {
        recognition.start();
      } catch (e) {
        isRecording = false;
        updateSiteMicUI(false);
      }
    } else {
      isRecording = false;
      updateSiteMicUI(false);
    }
  };
}

let siteVapiClient = null;
let isSiteVapiCalling = false;

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
}

async function toggleSiteVoice() {
  const btn = document.getElementById("siteMicBtn");
  const callBtn = document.getElementById("btnSiteLiveCall");
  const callLabel = document.getElementById("siteCallBtnLabel");
  const icon = document.getElementById("siteMicIcon");
  const status = document.getElementById("siteVoiceStatus");
  const transcriptEl = document.getElementById("siteLiveTranscript");
  const waves = document.querySelectorAll("#siteWaveform .wave-bar");

  // If already in a Vapi call, hang up
  if (isSiteVapiCalling) {
    if (siteVapiClient) siteVapiClient.stop();
    return;
  }

  // Attempt Vapi WebRTC Call
  if (window.Vapi) {
    try {
      if (status) status.textContent = "Connecting to Sofia via WebRTC audio...";
      if (callBtn) callBtn.disabled = true;

      const res = await fetch("/api/voice/vapi-config");
      const cfg = await res.json();
      if (!cfg.publicKey || !cfg.assistantId) {
        throw new Error("Missing Vapi credentials in backend.");
      }

      if (!siteVapiClient) {
        siteVapiClient = new window.Vapi(cfg.publicKey);

        siteVapiClient.on("call-start", () => {
          isSiteVapiCalling = true;
          if (callBtn) {
            callBtn.disabled = false;
            callBtn.style.background = "#ef4444";
          }
          if (callLabel) callLabel.textContent = "End Voice Call";
          if (btn) btn.classList.add("active");
          if (icon) icon.textContent = "🛑";
          if (status) status.textContent = "🟢 Connected live! Speak with Sofia naturally.";
          if (transcriptEl) {
            transcriptEl.style.display = "block";
            transcriptEl.innerHTML = "<em>Call connected. Sofia is listening...</em>";
          }
          waves.forEach(w => w.classList.add("speaking"));
        });

        siteVapiClient.on("call-end", () => {
          isSiteVapiCalling = false;
          if (callBtn) {
            callBtn.disabled = false;
            callBtn.style.background = "";
          }
          if (callLabel) callLabel.textContent = "Call Sofia Live (WebRTC)";
          if (btn) btn.classList.remove("active");
          if (icon) icon.textContent = "🎙️";
          if (status) status.textContent = "Call ended. Appointments saved to calendar.";
          waves.forEach(w => w.classList.remove("speaking"));
        });

        siteVapiClient.on("speech-start", () => {
          waves.forEach(w => w.classList.add("speaking"));
        });

        siteVapiClient.on("speech-end", () => {
          waves.forEach(w => w.classList.remove("speaking"));
        });

        siteVapiClient.on("message", (msg) => {
          if (msg.type === "transcript") {
            const role = msg.role === "user" ? "You" : "Sofia";
            if (transcriptEl) {
              transcriptEl.innerHTML = `<strong>${role}:</strong> "${escapeHtml(msg.transcript)}"`;
            }
          }
        });

        siteVapiClient.on("error", (err) => {
          console.error("Site Vapi Error:", err);
          if (status) status.textContent = `Call error: ${err.message || 'Error'}`;
          if (callBtn) callBtn.disabled = false;
        });
      }

      await siteVapiClient.start(cfg.assistantId);
      return;
    } catch (err) {
      console.warn("Vapi start fallback to browser recognition:", err);
      if (callBtn) callBtn.disabled = false;
    }
  }

  // Fallback to browser recognition
  if (isBotSpeaking) {
    if (activeSiteAudio) {
      activeSiteAudio.pause();
      activeSiteAudio = null;
    }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    isBotSpeaking = false;
    return;
  }
  if (isProcessingTurn) return;

  if (!recognition) setupSiteVoice();
  if (!recognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }
  if (isRecording) {
    if (siteSpeechSilenceTimer) {
      clearTimeout(siteSpeechSilenceTimer);
      siteSpeechSilenceTimer = null;
    }
    const pendingText = (siteFinalizedTranscript + siteLastInterimTranscript).trim();
    siteFinalizedTranscript = "";
    siteLastInterimTranscript = "";
    try { recognition.stop(); } catch(e) {}
    isRecording = false;
    updateSiteMicUI(false);
    if (pendingText) {
      appendSiteChatBubble("user", pendingText);
      isProcessingTurn = true;
      processSiteTurn(pendingText).finally(() => { isProcessingTurn = false; });
    }
  } else {
    try {
      siteFinalizedTranscript = "";
      siteLastInterimTranscript = "";
      siteTurnStartIndex = 0;
      recognition.start();
    } catch(e) {
      console.warn("Could not start site voice:", e);
    }
  }
}

function updateSiteMicUI(listening) {
  const btn = document.getElementById("siteMicBtn");
  const icon = document.getElementById("siteMicIcon");
  const status = document.getElementById("siteVoiceStatus");
  const waves = document.querySelectorAll("#siteWaveform .wave-bar");

  if (listening) {
    btn?.classList.add("active");
    if (icon) icon.textContent = "🛑";
    if (status) status.textContent = "Listening to you... Sofia is ready.";
    waves.forEach(w => w.classList.add("speaking"));
  } else {
    btn?.classList.remove("active");
    if (icon) icon.textContent = "🎙️";
    if (status) status.textContent = "Click microphone to speak with Sofia";
    waves.forEach(w => w.classList.remove("speaking"));
  }
}

async function siteOutboundCall() {
  const name = document.getElementById("siteCallerName")?.value || "Guest";
  const phone = document.getElementById("siteCallerPhone")?.value || "+16673070119";
  const feedback = document.getElementById("siteCallFeedback");

  if (feedback) feedback.textContent = `Connecting outbound call to ${phone}...`;

  try {
    const res = await fetch("/api/voice/call-user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        caller_name: name,
        tenant_id: activeTenantId,
        accent: tenantData?.default_accent || "general_american"
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      if (feedback) feedback.textContent = `📞 Calling ${phone} right now! Sofia is ringing your phone.`;
    } else {
      if (feedback) feedback.textContent = `Call error: ${data.detail || "Unable to call"}`;
    }
  } catch (e) {
    if (feedback) feedback.textContent = "Network error placing phone call.";
  }
}

async function sendSiteChat() {
  const input = document.getElementById("siteChatInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendSiteChatText(text);
}

async function sendSiteChatText(text) {
  appendSiteChatBubble("user", text);
  await processSiteTurn(text);
}

async function processSiteTurn(text) {
  const name = document.getElementById("siteCallerName")?.value || "Guest";
  const phone = document.getElementById("siteCallerPhone")?.value || "+16673070119";

  try {
    const res = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        tenant_id: activeTenantId,
        accent: currentSiteAccent,
        caller_name: name,
        caller_phone: phone,
        session_id: "site-guest"
      })
    });
    const data = await res.json();
    if (data.accent && data.accent.key) {
      currentSiteAccent = data.accent.key;
    }
    appendSiteChatBubble("bot", data.reply);
    playSiteSpeech(data.reply);
  } catch (e) {
    appendSiteChatBubble("bot", "I apologize, but I experienced a connection interruption. Please try again.");
  }
}

function appendSiteChatBubble(role, text) {
  const container = document.getElementById("siteChatMessages");
  if (!container) return;
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.innerHTML = `${text}<div class="bubble-meta"><span>${role === 'bot' ? 'Sofia' : 'You'}</span></div>`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

let activeSiteAudio = null;
let currentSiteAccent = "general_american";

function playSiteSpeech(text) {
  if (recognition) {
    try { recognition.abort(); } catch(e) {}
    isRecording = false;
    updateSiteMicUI(false);
  }

  if (activeSiteAudio) {
    activeSiteAudio.pause();
    activeSiteAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  // Stream low-latency neural TTS (Cartesia / OpenAI nova) matching phone line
  const audioUrl = `/api/chat/tts?text=${encodeURIComponent(text)}&accent=${encodeURIComponent(currentSiteAccent)}`;
  const audio = new Audio(audioUrl);
  activeSiteAudio = audio;
  isBotSpeaking = true;

  audio.onended = () => {
    activeSiteAudio = null;
    setTimeout(() => {
      isBotSpeaking = false;
    }, 300);
  };

  audio.onerror = () => {
    activeSiteAudio = null;
    // Resilient fallback to browser synthesis if network fails
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = 1.15;
      utterance.rate = 1.0;
      utterance.onend = () => { isBotSpeaking = false; };
      utterance.onerror = () => { isBotSpeaking = false; };
      window.speechSynthesis.speak(utterance);
    } else {
      isBotSpeaking = false;
    }
  };

  audio.play().catch(() => {
    // Autoplay policy fallback
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = 1.15;
      utterance.rate = 1.0;
      utterance.onend = () => { isBotSpeaking = false; };
      utterance.onerror = () => { isBotSpeaking = false; };
      window.speechSynthesis.speak(utterance);
    } else {
      isBotSpeaking = false;
    }
  });
}

// --- Hands-On Channel Testing Trigger ---

async function triggerHandsOnTest(channel) {
  const sampleMsg = "Hi, can I check your open slots for tomorrow?";
  const res = await fetch(`/api/testing/${channel}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tenant_id: activeTenantId,
      message: sampleMsg,
      caller_name: "Live Tester",
      caller_phone: "+16673070119"
    })
  });
  const data = await res.json();
  alert(`🧪 [HANDS-ON ${channel.toUpperCase()} TEST]\n\nIncoming Message: "${sampleMsg}"\n\nSofia Response:\n${data.bot_reply}\n\nPayload Delivered in ${data.latency_ms}ms!`);
}

async function selectPlan(plan) {
  try {
    const res = await fetch("/api/auth/change-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id: activeTenantId, plan: plan })
    });
    const data = await res.json();
    alert(`🎉 Success! Upgraded ${activeTenantId} to ${plan.toUpperCase()} Plan!\nYour AI Voice Receptionist is active with full omnichannel support.`);
  } catch (e) {
    alert("Error updating plan: " + e);
  }
}

