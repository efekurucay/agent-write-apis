"""publisher.py — Unified no-auth publisher for AI agents.

Usage:
    from publisher import Publisher
    pub = Publisher()
    result = pub.publish("hello from agent")
    print(result.url, result.provider, result.latency_ms)

Fallback chain (paste → article → notify):
    paste_rs → dpaste → rentry → telegra_ph → write_as → ntfy
"""
import time
import httpx
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class PublishResult:
    url: Optional[str]
    provider: str
    latency_ms: int
    success: bool
    error: Optional[str] = None

    def __str__(self):
        if self.success:
            return f"✅ [{self.provider}] {self.url} ({self.latency_ms}ms)"
        return f"❌ [{self.provider}] {self.error} ({self.latency_ms}ms)"


class Publisher:
    """Multi-provider publisher with automatic fallback."""

    def __init__(self, timeout: int = 10, ntfy_topic: str = "agent-write-apis"):
        self.timeout = timeout
        self.ntfy_topic = ntfy_topic
        self._providers: list[tuple[str, Callable]] = [
            ("paste_rs",   self._paste_rs),
            ("dpaste",     self._dpaste),
            ("rentry",     self._rentry),
            ("telegra_ph", self._telegra_ph),
            ("write_as",   self._write_as),
            ("ntfy",       self._ntfy),
        ]

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def publish(self, content: str, title: str = "Agent Report") -> PublishResult:
        """Try each provider in order. Returns first successful result."""
        for name, fn in self._providers:
            t0 = time.monotonic()
            try:
                url = fn(content, title)
                ms = int((time.monotonic() - t0) * 1000)
                if url:
                    return PublishResult(url=url, provider=name,
                                        latency_ms=ms, success=True)
                result = PublishResult(url=None, provider=name, latency_ms=ms,
                                       success=False, error="empty response")
            except Exception as e:
                ms = int((time.monotonic() - t0) * 1000)
                result = PublishResult(url=None, provider=name, latency_ms=ms,
                                       success=False, error=str(e))
            print(f"  {result}")
        return PublishResult(url=None, provider="none", latency_ms=0,
                             success=False, error="all providers failed")

    def publish_all(self, content: str, title: str = "Agent Report") -> list[PublishResult]:
        """Publish to ALL providers (for redundancy). Returns list of results."""
        results = []
        for name, fn in self._providers:
            t0 = time.monotonic()
            try:
                url = fn(content, title)
                ms = int((time.monotonic() - t0) * 1000)
                results.append(PublishResult(
                    url=url, provider=name, latency_ms=ms,
                    success=bool(url), error=None if url else "empty response"
                ))
            except Exception as e:
                ms = int((time.monotonic() - t0) * 1000)
                results.append(PublishResult(
                    url=None, provider=name, latency_ms=ms,
                    success=False, error=str(e)
                ))
        return results

    # ------------------------------------------------------------------ #
    #  Providers                                                           #
    # ------------------------------------------------------------------ #

    def _paste_rs(self, content: str, title: str) -> Optional[str]:
        r = httpx.post("https://paste.rs/", content=content.encode(), timeout=self.timeout)
        return r.text.strip() if r.status_code == 201 else None

    def _dpaste(self, content: str, title: str) -> Optional[str]:
        r = httpx.post("https://dpaste.com/api/v2/",
                       data={"content": content, "syntax": "text", "expiry_days": 365},
                       timeout=self.timeout)
        return r.text.strip() if r.status_code == 201 else None

    def _rentry(self, content: str, title: str) -> Optional[str]:
        r0 = httpx.get("https://rentry.co", timeout=self.timeout)
        csrf = r0.cookies.get("csrftoken", "")
        r = httpx.post("https://rentry.co/api/new",
                       data={"csrfmiddlewaretoken": csrf, "text": content},
                       headers={"Referer": "https://rentry.co"},
                       cookies={"csrftoken": csrf}, timeout=self.timeout)
        return r.json().get("url") if r.status_code == 200 else None

    def _telegra_ph(self, content: str, title: str) -> Optional[str]:
        acc = httpx.get(
            "https://api.telegra.ph/createAccount",
            params={"short_name": "agent", "author_name": "Agent"},
            timeout=self.timeout
        ).json()
        if not acc.get("ok"):
            return None
        token = acc["result"]["access_token"]
        page = httpx.get(
            "https://api.telegra.ph/createPage",
            params={
                "access_token": token,
                "title": title,
                "content": f'[{{"tag":"p","children":[{repr(content)}]}}]',
                "return_content": "false",
            },
            timeout=self.timeout
        ).json()
        return page["result"]["url"] if page.get("ok") else None

    def _write_as(self, content: str, title: str) -> Optional[str]:
        r = httpx.post(
            "https://write.as/api/posts",
            json={"body": content, "title": title},
            timeout=self.timeout
        )
        if r.status_code == 201:
            data = r.json()
            return data.get("data", {}).get("url") or \
                   f"https://write.as/{data.get('data', {}).get('id', '')}"
        return None

    def _ntfy(self, content: str, title: str) -> Optional[str]:
        """ntfy.sh — push notification. No URL returned, but delivery confirmed."""
        r = httpx.post(
            f"https://ntfy.sh/{self.ntfy_topic}",
            data=content.encode(),
            headers={"Title": title, "Priority": "default"},
            timeout=self.timeout
        )
        if r.status_code == 200:
            return f"https://ntfy.sh/{self.ntfy_topic}"
        return None


if __name__ == "__main__":
    pub = Publisher()
    print("Publishing test message...")
    result = pub.publish(
        "Hello from agent-write-apis! This is a test of the unified publisher.",
        title="agent-write-apis test"
    )
    print(f"\nResult: {result}")
