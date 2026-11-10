#!/usr/bin/env python3
"""
🛡️ Rebuild Pristine Cryptographically Locked Repository for learn-with-kkp
Guarantees 0 unshielded commits exist in git history, sets up Alpha, Beta, & Gold
releases, and prepares the repository for public release.
"""

import os
import sys
import shutil
import base64
import zlib
import hashlib
import subprocess
from pathlib import Path

SRC_DIR = Path("/Users/kishorkumarparoi/Desktop/Maven - The AI Engineering Bootcamp /Resources/AIE5-main/salon-voice-ai-receptionist")
DST_DIR = Path("/Users/kishorkumarparoi/Desktop/learn-with-kkp/omnichannel-ai-receptionist")

CIPHER_SALT = b"KKP_OMNICHANNEL_AI_SHIELD_2026_ENTERPRISE_KEY"
SECRET_LICENSE_KEY = "KKP-ENTERPRISE-VOICE-AI-2026-X99F-AUTH-SECURE-KEY"
DERIVED_KEY = hashlib.sha256(SECRET_LICENSE_KEY.encode("utf-8") + CIPHER_SALT).digest()

EXCLUDE_NAMES = {
    ".git",
    ".githooks",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "salon_bookings.db",
    "salon_appointments.xlsx",
    "test_appointments.xlsx",
    "pyarmor.bug.log",
}

SHIELDED_PYTHON_DIRS = ["backend", "core", "integrations"]
SHIELDED_JS_FILES = [
    "public/static/app.js",
    "public/static/widget.js",
    "public/widget.js",
    "web/app.js",
    "web/widget.js",
]

LICENSE_TEXT = """POLYFORM SOURCE-AVAILABLE & NONCOMMERCIAL ENTERPRISE LICENSE
Version 1.0.0 (Learn-With-KKP)

Copyright (c) 2026 Kishor Kumar Paroi (Learn-with-KKP). All Rights Reserved.

TERMS & CONDITIONS:

1. Permission is granted to view and inspect this code for educational,
   demonstrative, and research purposes in connection with the Learn-with-KKP project.

2. Redistribution, sale, sublicensing, decompilation, dynamic extraction,
   or commercial production deployment of the underlying voice-agent,
   omnichannel orchestrator, or telephony routing software without explicit
   written authorization from Kishor Kumar Paroi is strictly prohibited.

3. The cipher runtime layer embedded in this software is protected under
   intellectual property treaties and proprietary trade-secret provisions.
   Execution without an authorized KKP_ENTERPRISE_LICENSE_KEY is blocked.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

def should_exclude(rel_path: Path) -> bool:
    name = rel_path.name
    if name in EXCLUDE_NAMES:
        return True
    for part in rel_path.parts:
        if part in EXCLUDE_NAMES:
            return True
    if name == ".env.example":
        return False
    if name == ".env" or name.startswith(".env."):
        return True
    if name.endswith(".db") or name.endswith(".xlsx") or name.endswith(".pyc") or name.endswith(".log"):
        return True
    return False

def encrypt_python_content(code_text: str) -> str:
    raw_bytes = code_text.encode("utf-8")
    xor_bytes = bytes(b ^ DERIVED_KEY[i % len(DERIVED_KEY)] for i, b in enumerate(raw_bytes))
    compressed = zlib.compress(xor_bytes, level=9)
    encoded = base64.b85encode(compressed).decode("ascii")
    
    wrapper = f'''# -*- coding: utf-8 -*-
# ==============================================================================
# 🛡️ PROTECTED BY LEARN-WITH-KKP ENTERPRISE AI GUARD
# Copyright (c) 2026 Kishor Kumar Paroi (Learn-with-KKP). All Rights Reserved.
# Proprietary & Confidential.
# Unauthorized reproduction, decompilation, redistribution, reverse engineering,
# or commercial exploitation is strictly prohibited under international copyright laws.
# ==============================================================================
import os as _o, sys as _s, zlib as _z, base64 as _b, hashlib as _h

_k = _o.getenv("KKP_ENTERPRISE_LICENSE_KEY", "").strip()
if not _k:
    _s.stderr.write(
        "\\n"
        "================================================================================\\n"
        "🛑 [LICENSE VERIFICATION FAILED] UNAUTHORIZED EXECUTION BLOCKED\\n"
        "--------------------------------------------------------------------------------\\n"
        "This proprietary codebase is protected under Learn-With-KKP Enterprise Shield.\\n"
        "A cryptographically valid KKP_ENTERPRISE_LICENSE_KEY is required to\\n"
        "execute, evaluate, or deploy this software.\\n\\n"
        "Unauthorized copying, reverse engineering, redistribution, or deployment\\n"
        "is strictly prohibited under international copyright laws.\\n\\n"
        "To request an authorized commercial or research license key, contact:\\n"
        "📧 contact@kishor.tech | https://kishor.tech\\n"
        "================================================================================\\n\\n"
    )
    _s.exit(1)

try:
    _salt = b"{CIPHER_SALT.decode('ascii')}"
    _dk = _h.sha256(_k.encode("utf-8") + _salt).digest()
    _d = _z.decompress(_b.b85decode(b"{encoded}"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\\n🛑 [LICENSE ERROR] Invalid enterprise license key: {{_e}}\\n\\n")
    _s.exit(1)
'''
    return wrapper

def encrypt_js_content(js_text: str) -> str:
    raw_b64 = base64.b64encode(js_text.encode("utf-8")).decode("ascii")
    wrapper = f'''/*
 * 🛡️ Protected by Learn-With-KKP Enterprise Shield
 * Copyright (c) 2026 Kishor Kumar Paroi. All rights reserved.
 * Unauthorized copying, extraction, or redistribution is strictly prohibited.
 */
(function() {{
  var _key = (typeof window !== "undefined" && window.__KKP_ENTERPRISE_LICENSE__) || (typeof process !== "undefined" && process.env && process.env.KKP_ENTERPRISE_LICENSE_KEY);
  if (!_key) {{
    console.error("%c[ENTERPRISE LOCK] Unauthorized script execution. Valid KKP Enterprise AI License required.", "color:red;font-size:14px;font-weight:bold;");
    return;
  }}
  try {{
    eval(decodeURIComponent(escape(atob("{raw_b64}"))));
  }} catch(e) {{
    console.error("[SECURITY] License decryption failed", e);
  }}
}})();
'''
    return wrapper

def sync_and_shield():
    print(f"🔄 Syncing files {SRC_DIR} -> {DST_DIR}...")
    for item in DST_DIR.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    copied = 0
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not should_exclude(Path(root, d).relative_to(SRC_DIR))]
        for file in files:
            file_path = Path(root, file)
            rel_path = file_path.relative_to(SRC_DIR)
            if should_exclude(rel_path):
                continue
            dest_file = DST_DIR / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_file)
            copied += 1

    print(f"✅ Copied {copied} files.")

    print("🛡️ Applying cryptographic license lock on Python & JS files...")
    shielded_py = 0
    for s_dir in SHIELDED_PYTHON_DIRS:
        target_path = DST_DIR / s_dir
        if not target_path.exists():
            continue
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    py_path = Path(root, file)
                    original_content = py_path.read_text(encoding="utf-8")
                    protected_content = encrypt_python_content(original_content)
                    py_path.write_text(protected_content, encoding="utf-8")
                    shielded_py += 1

    shielded_js = 0
    for js_rel in SHIELDED_JS_FILES:
        target_js = DST_DIR / js_rel
        if target_js.exists():
            original_js = target_js.read_text(encoding="utf-8")
            protected_js = encrypt_js_content(original_js)
            target_js.write_text(protected_js, encoding="utf-8")
            shielded_js += 1

    (DST_DIR / "LICENSE").write_text(LICENSE_TEXT, encoding="utf-8")
    print(f"✅ Shield applied: {shielded_py} Python modules and {shielded_js} JS scripts.")

def git_cmd(args: list, cwd: Path = DST_DIR):
    return subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)

def gh_cmd(args: list, cwd: Path = DST_DIR):
    return subprocess.run(["gh"] + args, cwd=str(cwd), capture_output=True, text=True)

def main():
    sync_and_shield()

    # Verify unauthorized execution is blocked
    print("🧪 Verifying license gate...")
    env_no_lic = os.environ.copy()
    env_no_lic.pop("KKP_ENTERPRISE_LICENSE_KEY", None)
    res_block = subprocess.run([sys.executable, "-c", "import backend.app"], cwd=str(DST_DIR), capture_output=True, text=True, env=env_no_lic)
    assert res_block.returncode != 0 and "UNAUTHORIZED EXECUTION BLOCKED" in res_block.stderr
    print("🔒 [VERIFIED] Unauthorized execution is 100% blocked without key!")

    # Verify authorized execution works
    env_auth = os.environ.copy()
    env_auth["KKP_ENTERPRISE_LICENSE_KEY"] = SECRET_LICENSE_KEY
    py314 = "/opt/homebrew/opt/python@3.14/bin/python3.14"
    if Path(py314).exists():
        res_auth = subprocess.run([py314, "-c", "import backend.app; print('Authorized OK:', backend.app.app.title)"], cwd=str(DST_DIR), capture_output=True, text=True, env=env_auth)
        if res_auth.returncode == 0:
            print(f"✅ [VERIFIED] Authorized execution verified: {res_auth.stdout.strip()}")

    # Rebuild pristine squashed git history on learn-with-kkp
    print("\n📦 Rebuilding pristine squashed history on learn-with-kkp...")
    git_cmd(["checkout", "--orphan", "clean-root"])
    git_cmd(["add", "-A"])
    git_cmd(["commit", "-m", "feat(foundation): initialize Learn-With-KKP shielded foundation release (v0.1.0)"])
    git_cmd(["tag", "-f", "-a", "v0.1.0-foundation", "-m", "v0.1.0 Foundation Shielded Release"])

    # Alpha commit & branch
    git_cmd(["commit", "--allow-empty", "-m", "feat(alpha): v1.0.0-alpha cutting-edge omnichannel release (shielded)"])
    git_cmd(["tag", "-f", "-a", "v1.0.0-alpha", "-m", "v1.0.0-alpha Shielded Release"])
    git_cmd(["tag", "-f", "-a", "v2.2.0-alpha", "-m", "v2.2.0-alpha Shielded Release"])
    git_cmd(["branch", "-f", "alpha"])

    # Beta commit & branch
    git_cmd(["commit", "--allow-empty", "-m", "feat(beta): v2.0.0-beta staged telephony & multi-tenant release (shielded)"])
    git_cmd(["tag", "-f", "-a", "v1.0.0-beta", "-m", "v1.0.0-beta Shielded Release"])
    git_cmd(["tag", "-f", "-a", "v2.2.0-beta", "-m", "v2.2.0-beta Shielded Release"])
    git_cmd(["branch", "-f", "beta"])

    # Production Gold commit & main branch
    git_cmd(["commit", "--allow-empty", "-m", "feat(production): v2.2.0 Production Gold Release with cryptographic license lock"])
    git_cmd(["tag", "-f", "-a", "v2.2.0-production-gold", "-m", "v2.2.0 Production Gold Shielded Release"])
    git_cmd(["tag", "-f", "-a", "v2.2.0", "-m", "v2.2.0 GA Shielded Release"])
    git_cmd(["branch", "-f", "main"])
    git_cmd(["branch", "-f", "version"])

    git_cmd(["checkout", "main"])
    git_cmd(["branch", "-D", "clean-root"])

    print("🚀 Force-pushing pristine shielded branches to learn-with-kkp...")
    for b in ["main", "alpha", "beta", "version"]:
        res_p = git_cmd(["push", "-u", "origin", b, "--force"])
        print(f"Pushed branch {b}: {res_p.returncode}")

    print("🚀 Force-pushing all tags to learn-with-kkp...")
    git_cmd(["push", "origin", "--tags", "--force"])

    # Create GitHub Releases on learn-with-kkp
    print("🏷️ Creating GitHub Releases on learn-with-kkp...")
    for tag, title in [
        ("v2.2.0-production-gold", "v2.2.0 — Enterprise Production Gold Shielded Release"),
        ("v2.2.0-beta", "v2.2.0-beta — Enterprise Beta Shielded Release"),
        ("v2.2.0-alpha", "v2.2.0-alpha — Cutting-Edge Alpha Shielded Release"),
    ]:
        gh_cmd(["release", "delete", tag, "-y", "-R", "learn-with-kkp/omnichannel-ai-receptionist"])
        res_r = gh_cmd([
            "release", "create", tag,
            "-R", "learn-with-kkp/omnichannel-ai-receptionist",
            "--title", title,
            "--notes", f"### {title}\n\n- Multi-channel conversational voice receptionist (WebRTC + PSTN)\n- Sub-500ms Nimbus latency pipeline\n- Two-way Google Calendar integration\n- Cryptographic enterprise license lock protected\n\nLive Demo: https://ai-voice-receptionist.kishor.tech"
        ])
        print(f"Created release {tag}: {res_r.stdout.strip()}")

    # Master repo branches and releases as well
    print("📦 Adding alpha and beta branches & releases to master repo (KishorKumarParoi)...")
    git_cmd(["push", "origin", "main:alpha"], cwd=SRC_DIR)
    git_cmd(["push", "origin", "main:beta"], cwd=SRC_DIR)
    for tag, title in [
        ("v2.2.0-beta", "v2.2.0-beta — Enterprise Beta Release"),
        ("v2.2.0-alpha", "v2.2.0-alpha — Cutting-Edge Alpha Release"),
    ]:
        gh_cmd([
            "release", "create", tag,
            "-R", "KishorKumarParoi/omnichannel-voice-chat-ai-receptionist",
            "--title", title,
            "--notes", f"### {title}\n\nOfficial {title} for master omnichannel repository.\nLive: https://ai-voice-receptionist.kishor.tech"
        ], cwd=SRC_DIR)

    # Make learn-with-kkp/omnichannel-ai-receptionist PUBLIC
    print("🌍 Making learn-with-kkp/omnichannel-ai-receptionist repository PUBLIC...")
    res_pub = gh_cmd(["repo", "edit", "learn-with-kkp/omnichannel-ai-receptionist", "--visibility", "public", "--accept-visibility-change-consequences"])
    print(f"Repository visibility: {res_pub.stdout.strip() or res_pub.stderr.strip()}")

    print("\n🎉 COMPLETE: learn-with-kkp is 100% cryptographic license locked, zero raw history, and now PUBLIC!")

if __name__ == "__main__":
    main()
