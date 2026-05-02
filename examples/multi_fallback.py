"""Multi-provider fallback publisher — tries each endpoint in order.

This is the pattern immortal-agent uses: if one publish target is down,
fall back to the next one automatically.

Updated with all providers discovered in the agent-write-apis research.
"""
import httpx
from typing import Optional


def publish_paste_rs(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://paste.rs/", content=content.encode(), timeout=8)
        return r.text.strip() if r.status_code == 201 else None
    except Exception:
        return None


def publish_dpaste(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://dpaste.com/api/v2/",
            data={"content": content, "syntax": "text", "expiry_days": 365}, timeout=8)
        return r.text.strip() if r.status_code == 201 else None
    except Exception:
        return None


def publish_rentry(content: str) -> Optional[str]:
    try:
        r0 = httpx.get("https://rentry.co", timeout=8)
        csrf = r0.cookies.get("csrftoken", "")
        r = httpx.post("https://rentry.co/api/new",
            data={"csrfmiddlewaretoken": csrf, "text": content},
            headers={"Referer": "https://rentry.co"},
            cookies={"csrftoken": csrf}, timeout=8)
        return r.json().get("url") if r.status_code == 200 else None
    except Exception:
        return None


def publish_telegra_ph(content: str) -> Optional[str]:
    try:
        acc = httpx.get(
            "https://api.telegra.ph/createAccount",
            params={"short_name": "agent", "author_name": "Agent"}, timeout=8
        ).json()
        if not acc.get("ok"):
            return None
        token = acc["result"]["access_token"]
        page = httpx.get(
            "https://api.telegra.ph/createPage",
            params={
                "access_token": token,
                "title": "Agent Report",
                "content": f'[{{"tag":"p","children":[{repr(content)}]}}]',
                "return_content": "false",
            }, timeout=8
        ).json()
        return page["result"]["url"] if page.get("ok") else None
    except Exception:
        return None


def publish_write_as(content: str) -> Optional[str]:
    try:
        r = httpx.post("https://write.as/api/posts",
            json={"body": content, "title": "Agent Report"}, timeout=8)
        if r.status_code == 201:
            data = r.json().get("data", {})
            return data.get("url") or f"https://write.as/{data.get('id', '')}"
        return None
    except Exception:
        return None


def publish_ntfy(content: str, topic: str = "agent-write-apis-fallback") -> Optional[str]:
    try:
        r = httpx.post(f"https://ntfy.sh/{topic}",
            data=content.encode(),
            headers={"Title": "Agent Report", "Priority": "default"}, timeout=8)
        return f"https://ntfy.sh/{topic}" if r.status_code == 200 else None
    except Exception:
        return None


PROVIDERS = [
    publish_paste_rs,
    publish_dpaste,
    publish_rentry,
    publish_telegra_ph,
    publish_write_as,
    publish_ntfy,
]


def publish(content: str) -> Optional[str]:
    """Try each provider in order. Returns first successful URL."""
    for provider in PROVIDERS:
        url = provider(content)
        if url:
            print(f"✅ Published via {provider.__name__}: {url}")
            return url
        print(f"❌ {provider.__name__} failed, trying next...")
    return None


if __name__ == "__main__":
    url = publish("Hello from an AI agent — multi-provider fallback with 6 providers!")
    print(f"\nFinal URL: {url}" if url else "\nAll providers failed.")
