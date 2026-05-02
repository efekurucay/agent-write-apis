#!/usr/bin/env python3
"""test_all.py — Live integration test for every endpoint in agent-write-apis.

Runs every provider, measures latency, reports pass/fail.
Useful for:
  - Verifying endpoints are still alive
  - Benchmarking latency across providers
  - CI/CD health checks

Usage:
    python test_all.py
    python test_all.py --fast   # skip slow providers (catbox, transfer.sh)
    python test_all.py --json   # output machine-readable JSON
"""
import sys
import time
import json
import httpx
import tempfile
import os
from dataclasses import dataclass, field
from typing import Optional


# ------------------------------------------------------------------ #
#  Colours                                                             #
# ------------------------------------------------------------------ #
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


@dataclass
class TestResult:
    name: str
    category: str
    passed: bool
    url: Optional[str] = None
    latency_ms: int = 0
    error: Optional[str] = None


TEST_CONTENT = "agent-write-apis live test | github.com/efekurucay/agent-write-apis"
TEST_JSON    = {"test": True, "source": "agent-write-apis", "ts": int(time.time())}
results: list[TestResult] = []


def test(name: str, category: str):
    """Decorator to register and time a test function."""
    def decorator(fn):
        def wrapper():
            t0 = time.monotonic()
            try:
                url = fn()
                ms = int((time.monotonic() - t0) * 1000)
                r = TestResult(name=name, category=category,
                               passed=bool(url), url=url, latency_ms=ms)
            except Exception as e:
                ms = int((time.monotonic() - t0) * 1000)
                r = TestResult(name=name, category=category,
                               passed=False, latency_ms=ms, error=str(e))
            results.append(r)
            status = f"{GREEN}PASS{RESET}" if r.passed else f"{RED}FAIL{RESET}"
            url_str = f"  → {CYAN}{r.url}{RESET}" if r.url else ""
            err_str = f"  ! {r.error}" if r.error else ""
            print(f"  [{status}] {name:<28} {r.latency_ms:>5}ms{url_str}{err_str}")
        return wrapper
    return decorator


# ------------------------------------------------------------------ #
#  Paste tests                                                         #
# ------------------------------------------------------------------ #

@test("paste.rs", "Paste")
def t_paste_rs():
    r = httpx.post("https://paste.rs/", content=TEST_CONTENT.encode(), timeout=10)
    return r.text.strip() if r.status_code == 201 else None

@test("dpaste.com", "Paste")
def t_dpaste():
    r = httpx.post("https://dpaste.com/api/v2/",
                   data={"content": TEST_CONTENT, "syntax": "text", "expiry_days": 1}, timeout=10)
    return r.text.strip() if r.status_code == 201 else None

@test("rentry.co", "Paste")
def t_rentry():
    r0 = httpx.get("https://rentry.co", timeout=10)
    csrf = r0.cookies.get("csrftoken", "")
    r = httpx.post("https://rentry.co/api/new",
                   data={"csrfmiddlewaretoken": csrf, "text": TEST_CONTENT},
                   headers={"Referer": "https://rentry.co"},
                   cookies={"csrftoken": csrf}, timeout=10)
    return r.json().get("url") if r.status_code == 200 else None

@test("paste.gg (anonymous)", "Paste")
def t_paste_gg():
    r = httpx.post("https://api.paste.gg/v1/pastes",
                   json={"name": "test",
                         "files": [{"name": "test.txt",
                                    "content": {"format": "text", "value": TEST_CONTENT}}]},
                   timeout=10)
    if r.status_code == 201:
        paste_id = r.json().get("result", {}).get("id", "")
        return f"https://paste.gg/p/anonymous/{paste_id}"
    return None


# ------------------------------------------------------------------ #
#  Article tests                                                       #
# ------------------------------------------------------------------ #

@test("telegra.ph", "Article")
def t_telegraph():
    acc = httpx.get("https://api.telegra.ph/createAccount",
                    params={"short_name": "agent", "author_name": "Agent"}, timeout=10).json()
    if not acc.get("ok"):
        return None
    token = acc["result"]["access_token"]
    page = httpx.get("https://api.telegra.ph/createPage",
                     params={"access_token": token, "title": "test",
                             "content": '[{"tag":"p","children":["test"]}]',
                             "return_content": "false"}, timeout=10).json()
    return page["result"]["url"] if page.get("ok") else None

@test("write.as", "Article")
def t_write_as():
    r = httpx.post("https://write.as/api/posts",
                   json={"body": TEST_CONTENT, "title": "test"}, timeout=10)
    if r.status_code == 201:
        data = r.json().get("data", {})
        return data.get("url") or f"https://write.as/{data.get('id', '')}"
    return None


# ------------------------------------------------------------------ #
#  Notification tests                                                  #
# ------------------------------------------------------------------ #

@test("ntfy.sh", "Notify")
def t_ntfy():
    r = httpx.post("https://ntfy.sh/agent-write-apis-test",
                   data=b"live test",
                   headers={"Title": "test", "Priority": "min"}, timeout=10)
    return "https://ntfy.sh/agent-write-apis-test" if r.status_code == 200 else None


# ------------------------------------------------------------------ #
#  File upload tests                                                   #
# ------------------------------------------------------------------ #

@test("file.io", "File")
def t_file_io():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write(TEST_CONTENT)
        tmp = f.name
    try:
        with open(tmp, "rb") as f:
            r = httpx.post("https://file.io/", files={"file": ("test.txt", f)}, timeout=20)
        if r.status_code == 200 and r.json().get("success"):
            return r.json()["link"]
        return None
    finally:
        os.unlink(tmp)

@test("transfer.sh", "File")
def t_transfer_sh():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write(TEST_CONTENT)
        tmp = f.name
    try:
        with open(tmp, "rb") as fh:
            r = httpx.put("https://transfer.sh/test.txt", content=fh.read(), timeout=30)
        return r.text.strip() if r.status_code == 200 else None
    finally:
        os.unlink(tmp)

@test("catbox.moe", "File")
def t_catbox():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write(TEST_CONTENT)
        tmp = f.name
    try:
        with open(tmp, "rb") as fh:
            r = httpx.post("https://catbox.moe/user/api.php",
                           data={"reqtype": "fileupload"},
                           files={"fileToUpload": ("test.txt", fh)},
                           timeout=60)
        return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None
    finally:
        os.unlink(tmp)

@test("litterbox (1h)", "File")
def t_litterbox():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write(TEST_CONTENT)
        tmp = f.name
    try:
        with open(tmp, "rb") as fh:
            r = httpx.post("https://litterbox.catbox.moe/resources/internals/api.php",
                           data={"reqtype": "fileupload", "time": "1h"},
                           files={"fileToUpload": ("test.txt", fh)},
                           timeout=60)
        return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None
    finally:
        os.unlink(tmp)


# ------------------------------------------------------------------ #
#  JSON store tests                                                    #
# ------------------------------------------------------------------ #

@test("npoint.io", "JSON")
def t_npoint():
    r = httpx.post("https://api.npoint.io/", json={"json": TEST_JSON}, timeout=10)
    if r.status_code == 200:
        bin_id = r.json().get("id")
        return f"https://api.npoint.io/{bin_id}" if bin_id else None
    return None

@test("jsonbin.io", "JSON")
def t_jsonbin():
    r = httpx.post("https://api.jsonbin.io/v3/b",
                   json=TEST_JSON,
                   headers={"Content-Type": "application/json",
                             "X-Bin-Name": "agent-write-apis-test",
                             "X-Bin-Private": "false"}, timeout=10)
    if r.status_code == 200:
        bin_id = r.json().get("metadata", {}).get("id")
        return f"https://api.jsonbin.io/v3/b/{bin_id}/latest" if bin_id else None
    return None


# ------------------------------------------------------------------ #
#  Runner                                                              #
# ------------------------------------------------------------------ #

ALL_TESTS = [
    t_paste_rs, t_dpaste, t_rentry, t_paste_gg,
    t_telegraph, t_write_as,
    t_ntfy,
    t_file_io, t_transfer_sh, t_catbox, t_litterbox,
    t_npoint, t_jsonbin,
]

FAST_SKIP = {"catbox.moe", "litterbox (1h)", "transfer.sh"}


def main():
    fast_mode   = "--fast" in sys.argv
    json_output = "--json" in sys.argv

    if not json_output:
        print(f"\n{BOLD}agent-write-apis — Live Endpoint Test{RESET}")
        print(f"Running {'fast ' if fast_mode else ''}tests...\n")

    categories = {}
    for fn in ALL_TESTS:
        # Recover test metadata from closure
        name     = fn.__closure__[0].cell_contents if fn.__closure__ else fn.__name__
        category = fn.__closure__[1].cell_contents if fn.__closure__ and len(fn.__closure__) > 1 else ""

        if fast_mode and name in FAST_SKIP:
            continue

        if not json_output:
            if category not in categories:
                print(f"{BOLD}{CYAN}  {category}{RESET}")
                categories[category] = True

        fn()

    passed = sum(1 for r in results if r.passed)
    total  = len(results)
    avg_ms = int(sum(r.latency_ms for r in results if r.passed) / max(passed, 1))

    if json_output:
        out = [
            {"name": r.name, "category": r.category,
             "passed": r.passed, "url": r.url,
             "latency_ms": r.latency_ms, "error": r.error}
            for r in results
        ]
        print(json.dumps(out, indent=2))
        return

    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}Results: {passed}/{total} passed · avg latency {avg_ms}ms{RESET}")
    print()

    dead = [r for r in results if not r.passed]
    if dead:
        print(f"{YELLOW}Failed endpoints (consider moving to GRAVEYARD.md):{RESET}")
        for r in dead:
            print(f"  ⚰️  {r.name}" + (f" — {r.error}" if r.error else ""))
    else:
        print(f"{GREEN}All endpoints alive! 🎉{RESET}")
    print()


if __name__ == "__main__":
    main()
