"""No-auth JSON key-value store endpoints.

Useful when an agent needs to persist structured data that
other systems or agents can read back via public URL.

Providers:
- npoint.io: simple JSON bins, instant public GET
- jsonbin.io: feature-rich, public bins without API key
"""
import httpx
from typing import Optional


def store_npoint(data: dict) -> Optional[str]:
    """Store JSON at npoint.io. Returns public read URL.

    Write: POST https://api.npoint.io/   body: {"json": {...}}
    Read:  GET  https://api.npoint.io/{id}
    """
    r = httpx.post("https://api.npoint.io/",
                   json={"json": data},
                   timeout=10)
    if r.status_code == 200:
        bin_id = r.json().get("id")
        return f"https://api.npoint.io/{bin_id}" if bin_id else None
    return None


def store_jsonbin(data: dict, name: str = "agent-data") -> Optional[str]:
    """Store JSON at jsonbin.io. Returns public read URL.

    No API key required for public bins.
    Write: POST https://api.jsonbin.io/v3/b
    Read:  GET  https://api.jsonbin.io/v3/b/{id}/latest
    """
    r = httpx.post("https://api.jsonbin.io/v3/b",
                   json=data,
                   headers={
                       "Content-Type": "application/json",
                       "X-Bin-Name": name,
                       "X-Bin-Private": "false",
                   },
                   timeout=10)
    if r.status_code == 200:
        bin_id = r.json().get("metadata", {}).get("id")
        return f"https://api.jsonbin.io/v3/b/{bin_id}/latest" if bin_id else None
    return None


if __name__ == "__main__":
    import time

    payload = {
        "agent": "immortal-agent",
        "status": "alive",
        "timestamp": int(time.time()),
        "loop": 42,
        "providers_healthy": ["groq", "openrouter", "mistral"],
    }

    print("Storing agent state...")

    url1 = store_npoint(payload)
    print(f"npoint.io: {url1}")

    url2 = store_jsonbin(payload, name="immortal-agent-state")
    print(f"jsonbin.io: {url2}")

    if url1:
        import json
        read_back = httpx.get(url1, timeout=10).json()
        print(f"\nRead back from npoint: {json.dumps(read_back, indent=2)}")
