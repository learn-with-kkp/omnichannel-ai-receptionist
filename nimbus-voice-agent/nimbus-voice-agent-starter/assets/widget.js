/**
 * Luxe Omnichannel AI Voice & Chat Receptionist - Universal Embeddable Widget
 * Version: 2.1.0
 * 
 * Embed anywhere with:
 * <script src="https://ai-voice-receptionist.kishor.tech/widget.js" data-tenant="salon"></script>
 */
(function() {
  if (window.__SOFIA_WIDGET_LOADED__) return;
  window.__SOFIA_WIDGET_LOADED__ = true;

  // 1. Resolve configuration from script attributes
  const currentScript = document.currentScript || (function() {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const scriptSrc = currentScript ? currentScript.src : '';
  let defaultApiBase = '';
  try {
    const parsed = new URL(scriptSrc);
    defaultApiBase = parsed.origin;
  } catch (e) {
    defaultApiBase = window.location.origin;
  }

  const config = {
    tenantId: (currentScript && currentScript.getAttribute('data-tenant')) || 'salon',
    assistantId: (currentScript && currentScript.getAttribute('data-assistant')) || '',
    assistantName: (currentScript && currentScript.getAttribute('data-assistant-name')) || 'Sofia',
    apiBase: (currentScript && currentScript.getAttribute('data-api-base')) || defaultApiBase || '',
    theme: (currentScript && currentScript.getAttribute('data-theme')) || 'dark',
    position: (currentScript && currentScript.getAttribute('data-position')) || 'right', // 'right' or 'left'
    autoOpen: currentScript && currentScript.hasAttribute('data-auto-open')
  };

  // State
  let isOpen = false;
  let activeTab = 'call'; // 'call' or 'chat'
  let vapi = null;
  let vapiConfig = null;
  let isCallActive = false;
  let isCallConnecting = false;
  let isMuted = false;
  let conversationHistory = [];

  // 2. Inject CSS
  const styleEl = document.createElement('style');
  styleEl.textContent = `
    #luxe-widget-root {
      position: fixed;
      bottom: 24px;
      ${config.position === 'left' ? 'left: 24px;' : 'right: 24px;'}
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: #f8fafc;
      box-sizing: border-box;
      display: none; /* Hidden by default — only unlocked for signed-in VIP users */
    }
    #luxe-widget-root * {
      box-sizing: border-box;
    }

    /* Floating Launcher Button */
    .luxe-launcher-btn {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
      box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.5), 0 8px 10px -6px rgba(99, 102, 241, 0.4);
      border: 2px solid rgba(255, 255, 255, 0.2);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }
    .luxe-launcher-btn:hover {
      transform: scale(1.08) translateY(-2px);
      box-shadow: 0 14px 28px -4px rgba(99, 102, 241, 0.6);
    }
    .luxe-launcher-btn .luxe-icon {
      font-size: 28px;
      transition: transform 0.25s ease;
    }
    .luxe-launcher-badge {
      position: absolute;
      top: -2px;
      right: -2px;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #10b981;
      border: 2px solid #0f172a;
      box-shadow: 0 0 8px #10b981;
    }
    .luxe-launcher-pulse {
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      border: 2px solid rgba(99, 102, 241, 0.6);
      animation: luxePulseRing 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      pointer-events: none;
    }
    @keyframes luxePulseRing {
      0% { transform: scale(0.95); opacity: 0.8; }
      100% { transform: scale(1.35); opacity: 0; }
    }

    /* Widget Container Window */
    .luxe-widget-window {
      position: absolute;
      bottom: 80px;
      ${config.position === 'left' ? 'left: 0;' : 'right: 0;'}
      width: 380px;
      max-width: calc(100vw - 32px);
      height: 580px;
      max-height: calc(100vh - 120px);
      background: #0f172a;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.05);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transform-origin: bottom right;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      opacity: 0;
      pointer-events: none;
      transform: scale(0.92) translateY(12px);
    }
    .luxe-widget-window.open {
      opacity: 1;
      pointer-events: auto;
      transform: scale(1) translateY(0);
    }

    /* Header */
    .luxe-header {
      padding: 16px;
      background: linear-gradient(180deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .luxe-header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .luxe-avatar {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ec4899, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
      position: relative;
    }
    .luxe-avatar::after {
      content: '';
      position: absolute;
      bottom: 0;
      right: 0;
      width: 10px;
      height: 10px;
      background: #10b981;
      border-radius: 50%;
      border: 2px solid #0f172a;
    }
    .luxe-title {
      font-weight: 700;
      font-size: 15px;
      color: #ffffff;
      letter-spacing: -0.2px;
    }
    .luxe-subtitle {
      font-size: 11px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .luxe-close-btn {
      background: rgba(255, 255, 255, 0.06);
      border: none;
      color: #94a3b8;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      transition: background 0.2s ease, color 0.2s ease;
    }
    .luxe-close-btn:hover {
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
    }

    /* Tabs Bar */
    .luxe-tabs {
      display: flex;
      background: rgba(15, 23, 42, 0.6);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding: 6px 12px;
      gap: 8px;
    }
    .luxe-tab-btn {
      flex: 1;
      padding: 8px;
      border-radius: 10px;
      border: none;
      background: transparent;
      color: #94a3b8;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s ease;
    }
    .luxe-tab-btn.active {
      background: rgba(99, 102, 241, 0.2);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.3);
    }

    /* Tab Content Panes */
    .luxe-pane {
      flex: 1;
      display: none;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }
    .luxe-pane.active {
      display: flex;
    }

    /* VOICE TAB */
    .luxe-voice-hero {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      text-align: center;
      background: radial-gradient(circle at 50% 40%, rgba(99, 102, 241, 0.12) 0%, transparent 70%);
    }
    .luxe-call-circle {
      width: 110px;
      height: 110px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
      border: 2px solid rgba(99, 102, 241, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 44px;
      margin-bottom: 20px;
      position: relative;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    .luxe-call-circle:hover {
      transform: scale(1.05);
      border-color: #6366f1;
    }
    .luxe-call-circle.active {
      border-color: #10b981;
      box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
      animation: luxeCallBreathing 2s ease-in-out infinite;
    }
    @keyframes luxeCallBreathing {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.06); }
    }
    .luxe-voice-title {
      font-size: 16px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 6px;
    }
    .luxe-voice-status {
      font-size: 12px;
      color: #94a3b8;
      max-width: 260px;
      line-height: 1.4;
      margin-bottom: 20px;
    }

    /* Sound Wave Bars */
    .luxe-waves {
      display: flex;
      align-items: center;
      gap: 4px;
      height: 24px;
      margin-bottom: 20px;
    }
    .luxe-wave-bar {
      width: 4px;
      height: 6px;
      border-radius: 4px;
      background: #6366f1;
      transition: height 0.1s ease;
    }
    .luxe-wave-bar.animating {
      animation: luxeWaveBounce 1.2s ease-in-out infinite;
    }
    .luxe-wave-bar:nth-child(2) { animation-delay: 0.15s; }
    .luxe-wave-bar:nth-child(3) { animation-delay: 0.3s; }
    .luxe-wave-bar:nth-child(4) { animation-delay: 0.45s; }
    .luxe-wave-bar:nth-child(5) { animation-delay: 0.6s; }
    @keyframes luxeWaveBounce {
      0%, 100% { height: 6px; background: #6366f1; }
      50% { height: 24px; background: #a855f7; }
    }

    /* Call Action Buttons */
    .luxe-call-btn {
      width: 100%;
      max-width: 260px;
      padding: 12px 20px;
      border-radius: 12px;
      border: none;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.25s ease;
    }
    .luxe-call-btn.start {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    .luxe-call-btn.start:hover {
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
      transform: translateY(-1px);
    }
    .luxe-call-btn.hangup {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    }
    .luxe-call-btn.hangup:hover {
      box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
      transform: translateY(-1px);
    }

    .luxe-voice-transcript {
      width: 100%;
      max-height: 80px;
      overflow-y: auto;
      font-size: 11px;
      color: #cbd5e1;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 8px;
      padding: 8px 12px;
      margin-top: 12px;
      text-align: left;
      border-left: 2px solid #6366f1;
    }

    /* CHAT TAB */
    .luxe-chat-feed {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .luxe-bubble {
      max-width: 82%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 13px;
      line-height: 1.45;
      word-break: break-word;
    }
    .luxe-bubble.assistant {
      align-self: flex-start;
      background: #1e293b;
      color: #f1f5f9;
      border-bottom-left-radius: 4px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .luxe-bubble.user {
      align-self: flex-end;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }
    .luxe-bubble.booking-card {
      align-self: flex-start;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      color: #a7f3d0;
      border-radius: 12px;
      padding: 12px;
      font-size: 12px;
    }

    .luxe-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 4px 16px 8px;
    }
    .luxe-chip {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #cbd5e1;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .luxe-chip:hover {
      background: rgba(99, 102, 241, 0.2);
      border-color: #6366f1;
      color: #ffffff;
    }

    /* Chat Input Form */
    .luxe-chat-bar {
      display: flex;
      align-items: center;
      padding: 10px 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(15, 23, 42, 0.95);
      gap: 8px;
    }
    .luxe-chat-input {
      flex: 1;
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 10px;
      padding: 9px 12px;
      color: #ffffff;
      font-size: 13px;
      outline: none;
      transition: border-color 0.2s ease;
    }
    .luxe-chat-input:focus {
      border-color: #6366f1;
    }
    .luxe-send-btn {
      background: #6366f1;
      border: none;
      border-radius: 10px;
      width: 36px;
      height: 36px;
      color: #ffffff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      transition: background 0.2s ease;
    }
    .luxe-send-btn:hover {
      background: #4f46e5;
    }

    /* Footer Branding */
    .luxe-footer {
      padding: 8px 12px;
      background: #090d16;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 10px;
      color: #64748b;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .luxe-footer a {
      color: #818cf8;
      text-decoration: none;
    }
  `;
  document.head.appendChild(styleEl);

  // 3. Render DOM Structure
  const rootEl = document.createElement('div');
  rootEl.id = 'luxe-widget-root';
  rootEl.innerHTML = `
    <!-- Floating Launcher -->
    <div class="luxe-launcher-btn" id="luxeLauncher">
      <div class="luxe-launcher-pulse"></div>
      <div class="luxe-launcher-badge"></div>
      <span class="luxe-icon" id="luxeLauncherIcon">💬</span>
    </div>

    <!-- Widget Window -->
    <div class="luxe-widget-window" id="luxeWindow">
      <!-- Header -->
      <div class="luxe-header">
        <div class="luxe-header-left">
          <div class="luxe-avatar">✨</div>
          <div>
            <div class="luxe-title">Sofia • Luxe Receptionist</div>
            <div class="luxe-subtitle">
              <span style="color:#10b981; font-weight:bold;">●</span> Speaks & Books in Real-Time
            </div>
          </div>
        </div>
        <button class="luxe-close-btn" id="luxeCloseBtn" title="Close">✕</button>
      </div>

      <!-- Navigation Tabs -->
      <div class="luxe-tabs">
        <button class="luxe-tab-btn active" id="luxeTabCall" data-target="call">
          🎙️ Live Voice Call
        </button>
        <button class="luxe-tab-btn" id="luxeTabChat" data-target="chat">
          💬 Instant Chat
        </button>
      </div>

      <!-- Pane 1: Realtime Voice Call -->
      <div class="luxe-pane active" id="luxePaneCall">
        <div class="luxe-voice-hero">
          <div class="luxe-call-circle" id="luxeCallCircle" title="Click to call">
            🎙️
          </div>
          <div class="luxe-voice-title" id="luxeCallTitle">Talk with Sofia</div>
          <div class="luxe-voice-status" id="luxeCallStatus">
            Sub-500ms WebRTC voice conversation. Instant appointment booking synced with Google Calendar.
          </div>
          
          <div class="luxe-waves" id="luxeWaves" style="opacity: 0.3;">
            <div class="luxe-wave-bar"></div>
            <div class="luxe-wave-bar"></div>
            <div class="luxe-wave-bar"></div>
            <div class="luxe-wave-bar"></div>
            <div class="luxe-wave-bar"></div>
          </div>

          <button class="luxe-call-btn start" id="luxeCallActionBtn">
            <span>📞</span> <span id="luxeCallBtnText">Start Real-Time Call</span>
          </button>

          <div class="luxe-voice-transcript" id="luxeCallTranscript" style="display:none;">
            <em>Sofia: "Hi there! Welcome to Luxe Salon. How may I assist you today?"</em>
          </div>
        </div>
      </div>

      <!-- Pane 2: Instant Chat & Booking -->
      <div class="luxe-pane" id="luxePaneChat">
        <div class="luxe-chat-feed" id="luxeChatFeed">
          <div class="luxe-bubble assistant">
            Hi! I'm Sofia, your 24/7 AI Receptionist. Would you like to book an appointment, check stylist availability, or ask about pricing?
          </div>
        </div>

        <div class="luxe-chips" id="luxeChips">
          <button class="luxe-chip" data-msg="I'd like to book a Balayage tomorrow">💇 Balayage ($180)</button>
          <button class="luxe-chip" data-msg="Can I get a Haircut & Blowdry?">✂️ Haircut ($65)</button>
          <button class="luxe-chip" data-msg="What are your hours today?">🕒 Hours & Location</button>
        </div>

        <div class="luxe-chat-bar">
          <input type="text" class="luxe-chat-input" id="luxeChatInput" placeholder="Message Sofia (e.g. 'Book 3pm tomorrow')..." />
          <button class="luxe-send-btn" id="luxeSendBtn">➤</button>
        </div>
      </div>

      <!-- Footer -->
      <div class="luxe-footer">
        <span>⚡ Synchronized with Neon PostgreSQL & Calendar</span>
        <a href="${config.apiBase || '/'}" target="_blank" rel="noopener">Luxe AI</a>
      </div>
    </div>
  `;
  document.body.appendChild(rootEl);

  // 4. Element references
  const launcher = document.getElementById('luxeLauncher');
  const launcherIcon = document.getElementById('luxeLauncherIcon');
  const windowEl = document.getElementById('luxeWindow');
  const closeBtn = document.getElementById('luxeCloseBtn');
  const tabCall = document.getElementById('luxeTabCall');
  const tabChat = document.getElementById('luxeTabChat');
  const paneCall = document.getElementById('luxePaneCall');
  const paneChat = document.getElementById('luxePaneChat');

  // Call elements
  const callCircle = document.getElementById('luxeCallCircle');
  const callTitle = document.getElementById('luxeCallTitle');
  const callStatus = document.getElementById('luxeCallStatus');
  const callActionBtn = document.getElementById('luxeCallActionBtn');
  const callBtnText = document.getElementById('luxeCallBtnText');
  const callTranscript = document.getElementById('luxeCallTranscript');
  const waves = document.getElementById('luxeWaves');

  // Chat elements
  const chatFeed = document.getElementById('luxeChatFeed');
  const chatInput = document.getElementById('luxeChatInput');
  const sendBtn = document.getElementById('luxeSendBtn');
  const chips = document.getElementById('luxeChips');

  // 5. Toggle Widget Window
  function toggleWidget(force) {
    isOpen = typeof force === 'boolean' ? force : !isOpen;
    if (isOpen) {
      windowEl.classList.add('open');
      launcherIcon.textContent = '✕';
      if (activeTab === 'chat') {
        chatInput.focus();
      }
    } else {
      windowEl.classList.remove('open');
      launcherIcon.textContent = '💬';
    }
  }

  launcher.addEventListener('click', () => toggleWidget());
  closeBtn.addEventListener('click', () => toggleWidget(false));

  // --- VIP Authentication Gating (Only show Sofia Luxe Receptionist for signed in users) ---
  function checkIsSignedIn() {
    try {
      if (localStorage.getItem("luxe_vip_user")) return true;
    } catch (e) {}
    if (window.Clerk && window.Clerk.user) return true;
    if (document.body && document.body.classList.contains("vip-signed-in")) return true;
    return false;
  }

  function setWidgetAuthVisibility(isSignedIn) {
    const shouldShow = typeof isSignedIn === 'boolean' ? isSignedIn : checkIsSignedIn();
    rootEl.style.setProperty('display', shouldShow ? 'block' : 'none', 'important');
    if (!shouldShow && isOpen) {
      toggleWidget(false);
    }
  }

  // Initial check
  setWidgetAuthVisibility();

  // Listen for login/logout auth updates
  window.addEventListener('luxe:auth-change', (e) => {
    const isAuth = e && e.detail && typeof e.detail.isSignedIn === 'boolean' ? e.detail.isSignedIn : checkIsSignedIn();
    setWidgetAuthVisibility(isAuth);
  });
  window.setLuxeWidgetVisible = setWidgetAuthVisibility;

  // Switch tabs
  function switchTab(tab) {
    activeTab = tab;
    if (tab === 'call') {
      tabCall.classList.add('active');
      tabChat.classList.remove('active');
      paneCall.classList.add('active');
      paneChat.classList.remove('active');
    } else {
      tabChat.classList.add('active');
      tabCall.classList.remove('active');
      paneChat.classList.add('active');
      paneCall.classList.remove('active');
      chatInput.focus();
    }
  }

  tabCall.addEventListener('click', () => switchTab('call'));
  tabChat.addEventListener('click', () => switchTab('chat'));

  // 6. Dynamically load Vapi Web SDK script with multi-tier resilient fallback
  function ensureVapiSdkLoaded() {
    return new Promise((resolve, reject) => {
      if (window.Vapi) return resolve(window.Vapi);
      if (window.vapiSDK && window.vapiSDK.Vapi) {
        window.Vapi = window.vapiSDK.Vapi;
        return resolve(window.Vapi);
      }

      const candidateUrls = [
        `${config.apiBase || ''}/vapi-sdk.js`,
        `${config.apiBase || ''}/static/vapi-sdk.js`,
        'https://ai-voice-receptionist.kishor.tech/vapi-sdk.js',
        'https://ai-voice-receptionist.kishor.tech/static/vapi-sdk.js'
      ].filter(Boolean);

      let curIdx = 0;
      function attemptLoad() {
        if (curIdx >= candidateUrls.length) {
          return reject(new Error('Failed to load Vapi Web SDK from all self-hosted and CDN endpoints.'));
        }
        const script = document.createElement('script');
        script.src = candidateUrls[curIdx++];
        script.async = true;
        script.onload = () => {
          const cls = window.Vapi || (window.vapiSDK && window.vapiSDK.Vapi);
          if (cls) {
            window.Vapi = cls;
            resolve(cls);
          } else {
            attemptLoad();
          }
        };
        script.onerror = () => attemptLoad();
        document.head.appendChild(script);
      }

      attemptLoad();
    });
  }

  // 7. Load Vapi Configuration
  async function fetchVapiConfig() {
    if (vapiConfig) return vapiConfig;
    const url = `${config.apiBase}/api/voice/vapi-config`;
    const res = await fetch(url);
    const data = await res.json();
    vapiConfig = data;
    return vapiConfig;
  }

  // 8. Start / Hangup Real-time Voice Call
  async function startVapiCall() {
    if (isCallConnecting) return;
    isCallConnecting = true;
    callStatus.textContent = 'Connecting to Sofia via WebRTC...';
    callActionBtn.disabled = true;

    try {
      await ensureVapiSdkLoaded();
      const cfg = await fetchVapiConfig();

      if (!cfg.publicKey || !cfg.assistantId) {
        throw new Error('Vapi credentials not configured on backend.');
      }

      if (!vapi) {
        vapi = new window.Vapi(cfg.publicKey);

        vapi.on('call-start', () => {
          isCallActive = true;
          isCallConnecting = false;
          callCircle.classList.add('active');
          waves.style.opacity = '1';
          document.querySelectorAll('.luxe-wave-bar').forEach(b => b.classList.add('animating'));
          callTitle.textContent = 'In Call with Sofia';
          callStatus.textContent = '🟢 Connected live (Sub-500ms voice). Speak naturally to book or ask questions.';
          callActionBtn.className = 'luxe-call-btn hangup';
          callBtnText.textContent = 'End Voice Call';
          callActionBtn.disabled = false;
          callTranscript.style.display = 'block';
        });

        vapi.on('call-end', () => {
          isCallActive = false;
          isCallConnecting = false;
          callCircle.classList.remove('active');
          waves.style.opacity = '0.3';
          document.querySelectorAll('.luxe-wave-bar').forEach(b => b.classList.remove('animating'));
          callTitle.textContent = 'Call Finished';
          callStatus.textContent = 'Call ended. Appointments have been booked & synced to Google Calendar.';
          callActionBtn.className = 'luxe-call-btn start';
          callBtnText.textContent = 'Start Real-Time Call';
          callActionBtn.disabled = false;
        });

        vapi.on('speech-start', () => {
          waves.style.opacity = '1';
        });

        vapi.on('speech-end', () => {
          waves.style.opacity = '0.6';
        });

        vapi.on('message', (msg) => {
          if (msg.type === 'transcript') {
            const role = msg.role === 'user' ? 'Caller' : 'Sofia';
            callTranscript.innerHTML = `<strong>${role}:</strong> "${escapeHtml(msg.transcript)}"`;
          }
        });

        vapi.on('error', (err) => {
          console.error('[Sofia Widget Error]', err);
          callStatus.textContent = `Call error: ${err.message || 'Microphone error'}`;
          isCallConnecting = false;
          callActionBtn.disabled = false;
        });
      }

      // Resolve assistant target (allows data-assistant to specify 'marcus', 'sophia', 'squad' or custom UUID)
      let targetAssistant = config.assistantId || cfg.assistantId;
      if (targetAssistant === 'marcus' && cfg.marcusId) {
        targetAssistant = cfg.marcusId;
      } else if (targetAssistant === 'sophia' && cfg.assistantId) {
        targetAssistant = cfg.assistantId;
      }

      if (cfg.squadId && targetAssistant !== cfg.marcusId) {
        console.log('[Sofia Widget] Starting in Squad mode for seamless Marcus transfer:', cfg.squadId);
        await vapi.start(undefined, undefined, cfg.squadId);
      } else {
        console.log('[Sofia Widget] Starting direct assistant call:', targetAssistant);
        await vapi.start(targetAssistant);
      }
    } catch (err) {
      console.error('[Sofia Widget Start Error]', err);
      callStatus.textContent = `Could not connect: ${err.message}`;
      isCallConnecting = false;
      callActionBtn.disabled = false;
    }
  }

  function endVapiCall() {
    if (vapi && isCallActive) {
      vapi.stop();
    }
  }

  callActionBtn.addEventListener('click', () => {
    if (isCallActive) {
      endVapiCall();
    } else {
      startVapiCall();
    }
  });

  callCircle.addEventListener('click', () => {
    if (isCallActive) {
      endVapiCall();
    } else {
      startVapiCall();
    }
  });

  // 9. Instant Chat Functionality
  async function sendChatMessage(userText) {
    const text = (userText || chatInput.value || '').trim();
    if (!text) return;

    chatInput.value = '';
    appendChatBubble('user', text);

    // Typing indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'luxe-bubble assistant';
    typingBubble.id = 'luxeTyping';
    typingBubble.innerHTML = '<em>Sofia is typing...</em>';
    chatFeed.appendChild(typingBubble);
    chatFeed.scrollTop = chatFeed.scrollHeight;

    try {
      const url = `${config.apiBase}/api/chat/message`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          tenant_id: config.tenantId,
          channel: 'web_widget',
          history: conversationHistory
        })
      });

      const data = await res.json();
      const typingEl = document.getElementById('luxeTyping');
      if (typingEl) typingEl.remove();

      const reply = data.reply || data.response || data.message || 'Thank you! How else can I assist you?';
      appendChatBubble('assistant', reply);

      conversationHistory.push({ role: 'user', content: text });
      conversationHistory.push({ role: 'assistant', content: reply });

      if (data.suggested_slots && Array.isArray(data.suggested_slots) && data.suggested_slots.length > 0) {
        appendSlotSuggestions(data.suggested_slots);
      }

      if (data.booking_confirmed || data.appointment || data.booking) {
        const appt = data.booking || data.appointment || {};
        appendBookingCard(appt);
      }
    } catch (err) {
      const typingEl = document.getElementById('luxeTyping');
      if (typingEl) typingEl.remove();
      appendChatBubble('assistant', 'Sorry, I had trouble connecting. Please try again or tap Call Sofia to speak live!');
    }
  }

  function appendChatBubble(role, text) {
    const bubble = document.createElement('div');
    bubble.className = `luxe-bubble ${role}`;
    bubble.textContent = text;
    chatFeed.appendChild(bubble);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function appendSlotSuggestions(slots) {
    const container = document.createElement('div');
    container.className = 'luxe-slot-suggestions';
    container.style.cssText = 'display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 10px 0;';
    slots.slice(0, 4).forEach(slot => {
      const btn = document.createElement('button');
      btn.className = 'luxe-chip';
      btn.style.cssText = 'background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.5); color: #c7d2fe; font-size: 11px; padding: 4px 10px; border-radius: 9999px; cursor: pointer; transition: all 0.2s ease;';
      btn.textContent = `📅 ${slot}`;
      btn.onmouseover = () => { btn.style.background = 'rgba(99, 102, 241, 0.4)'; btn.style.color = '#fff'; };
      btn.onmouseout = () => { btn.style.background = 'rgba(99, 102, 241, 0.2)'; btn.style.color = '#c7d2fe'; };
      btn.onclick = () => {
        sendChatMessage(`Book for ${slot} tomorrow`);
      };
      container.appendChild(btn);
    });
    chatFeed.appendChild(container);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function appendBookingCard(appt) {
    const card = document.createElement('div');
    card.className = 'luxe-bubble booking-card';
    const srv = appt.service_name || appt.service || 'Salon Service';
    const time = appt.start_time || appt.datetime || 'As scheduled';
    const stylist = appt.stylist_name || appt.stylist || 'Sofia Premier Stylist';
    const bookingId = appt.booking_id || appt.id || 'CONFIRMED';
    card.innerHTML = `
      <strong style="color: #34d399; font-size: 13px;">✨ Appointment Confirmed!</strong><br>
      • <strong>Service:</strong> ${escapeHtml(srv)}<br>
      • <strong>Time:</strong> ${escapeHtml(time)}<br>
      • <strong>Stylist:</strong> ${escapeHtml(stylist)}<br>
      • <strong>Ref #:</strong> <code>${escapeHtml(bookingId)}</code><br>
      <small style="color: #94a3b8; display: block; margin-top: 4px;">📅 Synced to Google Calendar & Saved to PostgreSQL</small>
    `;
    chatFeed.appendChild(card);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
  }

  sendBtn.addEventListener('click', () => sendChatMessage());
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });

  // Chip click handlers
  chips.addEventListener('click', (e) => {
    const btn = e.target.closest('.luxe-chip');
    if (btn && btn.dataset.msg) {
      sendChatMessage(btn.dataset.msg);
    }
  });

  // 10. Expose Global Programmatic API
  window.SofiaWidget = {
    open: () => toggleWidget(true),
    close: () => toggleWidget(false),
    toggle: () => toggleWidget(),
    startCall: startVapiCall,
    endCall: endVapiCall,
    sendMessage: sendChatMessage
  };

  if (config.autoOpen) {
    setTimeout(() => toggleWidget(true), 1000);
  }
})();

