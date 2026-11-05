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

// --- Voice Recognition & Barge-In for Custom Site ---

function setupSiteVoice() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) return;

  recognition = new SpeechRec();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    isRecording = true;
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

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("siteVoiceStatus").textContent = `You: "${transcript}"`;
    appendSiteChatBubble("user", transcript);
    await processSiteTurn(transcript);
  };

  recognition.onerror = () => {
    isRecording = false;
    updateSiteMicUI(false);
  };

  recognition.onend = () => {
    isRecording = false;
    updateSiteMicUI(false);
  };
}

function toggleSiteVoice() {
  if (!recognition) setupSiteVoice();
  if (!recognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }
  if (isRecording) {
    recognition.stop();
  } else {
    recognition.start();
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
        accent: tenantData?.default_accent || "general_american",
        caller_name: name,
        caller_phone: phone,
        session_id: "site-guest"
      })
    });
    const data = await res.json();
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

function playSiteSpeech(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.pitch = 1.15;
  utterance.rate = 1.0;
  window.speechSynthesis.speak(utterance);
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
