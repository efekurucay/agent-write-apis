#!/usr/bin/env python3
"""cli.py — Command-line interface for agent-write-apis.

Usage:
    python cli.py paste  'your text here'
    python cli.py notify 'your message'
    python cli.py upload /path/to/file.txt
    python cli.py json   '{"key": "value"}'
    python cli.py all    'text to publish everywhere'

Requires: pip install httpx
"""
import sys
import json as _json
import httpx
from typing import Optional


# ------------------------------------------------------------------ #
#  Colour helpers                                                      #
# ------------------------------------------------------------------ #
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"{GREEN}✅ {msg}{RESET}")
def err(msg):  print(f"{RED}❌ {msg}{RESET}")
def info(msg): print(f"{YELLOW}ℹ️  {msg}{RESET}")


# ------------------------------------------------------------------ #
#  Providers                                                           #
# ------------------------------------------------------------------ #

def _paste_rs(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://paste.rs/", content=content.encode(), timeout=10)
        return r.text.strip() if r.status_code == 201 else None
    except Exception:
        return None

def _dpaste(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://dpaste.com/api/v2/",
                       data={"content": content, "syntax": "text", "expiry_days": 365}, timeout=10)
        return r.text.strip() if r.status_code == 201 else None
    except Exception:
        return None

def _rentry(content: str) -> Optional[str]:
    try:
        r0 = httpx.get("https://rentry.co", timeout=10)
        csrf = r0.cookies.get("csrftoken", "")
        r = httpx.post("https://rentry.co/api/new",
                       data={"csrfmiddlewaretoken": csrf, "text": content},
                       headers={"Referer": "https://rentry.co"},
                       cookies={"csrftoken": csrf}, timeout=10)
        return r.json().get("url") if r.status_code == 200 else None
    except Exception:
        return None

def _paste_gg(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://api.paste.gg/v1/pastes",
                       json={"name": "Agent Report",
                             "files": [{"name": "output.txt",
                                        "content": {"format": "text", "value": content}}]},
                       timeout=10)
        if r.status_code == 201:
            paste_id = r.json().get("result", {}).get("id", "")
            return f"https://paste.gg/p/anonymous/{paste_id}"
        return None
    except Exception:
        return None

def _write_as(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://write.as/api/posts",
                       json={"body": content, "title": "Agent Report"}, timeout=10)
        if r.status_code == 201:
            data = r.json().get("data", {})
            return data.get("url") or f"https://write.as/{data.get('id', '')}"
        return None
    except Exception:
        return None

def _ntfy(message: str, topic: str = "agent-write-apis") -> Optional[str]:
    try:
        r = httpx.post(f"https://ntfy.sh/{topic}",
                       data=message.encode(),
                       headers={"Title": "Agent", "Priority": "default"}, timeout=10)
        return f"https://ntfy.sh/{topic}" if r.status_code == 200 else None
    except Exception:
        return None

def _catbox(filepath: str) -> Optional[str]:
    try:
        import os
        with open(filepath, "rb") as f:
            r = httpx.post("https://catbox.moe/user/api.php",
                           data={"reqtype": "fileupload"},
                           files={"fileToUpload": (os.path.basename(filepath), f)},
                           timeout=60)
        return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None
    except Exception:
        return None

def _litterbox(filepath: str) -> Optional[str]:
    try:
        import os
        with open(filepath, "rb") as f:
            r = httpx.post("https://litterbox.catbox.moe/resources/internals/api.php",
                           data={"reqtype": "fileupload", "time": "24h"},
                           files={"fileToUpload": (os.path.basename(filepath), f)},
                           timeout=60)
        return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None
    except Exception:
        return None

def _transfer_sh(filepath: str) -> Optional[str]:
    try:
        import os
        with open(filepath, "rb") as f:
            r = httpx.put(f"https://transfer.sh/{os.path.basename(filepath)}",
                          content=f.read(), timeout=30)
        return r.text.strip() if r.status_code == 200 else None
    except Exception:
        return None

def _npoint(data: dict) -> Optional[str]:
    try:
        r = httpx.post("https://api.npoint.io/", json={"json": data}, timeout=10)
        if r.status_code == 200:
            bin_id = r.json().get("id")
            return f"https://api.npoint.io/{bin_id}" if bin_id else None
        return None
    except Exception:
        return None


# ------------------------------------------------------------------ #
#  Commands                                                            #
# ------------------------------------------------------------------ #

PASTE_PROVIDERS = [
    ("paste.rs",  _paste_rs),
    ("dpaste",    _dpaste),
    ("rentry",    _rentry),
    ("paste.gg",  _paste_gg),
    ("write.as",  _write_as),
    ("ntfy",      _ntfy),
]

UPLOAD_PROVIDERS = [
    ("catbox.moe",      _catbox),
    ("litterbox (24h)", _litterbox),
    ("transfer.sh",     _transfer_sh),
]


def cmd_paste(text: str):
    print(f"{BOLD}Publishing text (fallback chain)...{RESET}")
    for name, fn in PASTE_PROVIDERS:
        url = fn(text)
        if url:
            ok(f"{name}: {url}")
            return
        err(f"{name} failed")
    err("All paste providers failed.")


def cmd_notify(message: str, topic: str = "agent-write-apis"):
    print(f"{BOLD}Sending notification to ntfy.sh/{topic}...{RESET}")
    url = _ntfy(message, topic)
    if url:
        ok(f"Delivered: {url}")
        info(f"Subscribe: https://ntfy.sh/{topic}")
    else:
        err("ntfy.sh failed.")


def cmd_upload(filepath: str):
    import os
    if not os.path.exists(filepath):
        err(f"File not found: {filepath}")
        sys.exit(1)
    print(f"{BOLD}Uploading {os.path.basename(filepath)}...{RESET}")
    for name, fn in UPLOAD_PROVIDERS:
        url = fn(filepath)
        if url:
            ok(f"{name}: {url}")
            return
        err(f"{name} failed")
    err("All upload providers failed.")


def cmd_json(json_str: str):
    try:
        data = _json.loads(json_str)
    except _json.JSONDecodeError as e:
        err(f"Invalid JSON: {e}")
        sys.exit(1)
    print(f"{BOLD}Storing JSON...{RESET}")
    url = _npoint(data)
    if url:
        ok(f"npoint.io: {url}")
    else:
        err("npoint.io failed.")


def cmd_all(text: str):
    print(f"{BOLD}Publishing to ALL paste providers...{RESET}")
    any_ok = False
    for name, fn in PASTE_PROVIDERS:
        url = fn(text)
        if url:
            ok(f"{name}: {url}")
            any_ok = True
        else:
            err(f"{name} failed")
    if not any_ok:
        err("All providers failed.")


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

HELP = f"""{BOLD}agent-write-apis CLI{RESET}

Usage:
  python cli.py paste  <text>          Publish text (fallback chain)
  python cli.py notify <message>       Push notification via ntfy.sh
  python cli.py upload <filepath>      Upload file (catbox → litterbox → transfer.sh)
  python cli.py json   <json_string>   Store JSON at npoint.io
  python cli.py all    <text>          Publish to every paste provider
  python cli.py help                   Show this help
"""

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "-h", "--help"):
        print(HELP)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    arg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if not arg and cmd != "help":
        err(f"Missing argument for '{cmd}'.")
        print(HELP)
        sys.exit(1)

    dispatch = {
        "paste":  cmd_paste,
        "notify": cmd_notify,
        "upload": cmd_upload,
        "json":   cmd_json,
        "all":    cmd_all,
    }

    fn = dispatch.get(cmd)
    if fn is None:
        err(f"Unknown command: '{cmd}'")
        print(HELP)
        sys.exit(1)

    fn(arg)
