"""paste.rs — no auth required. Raw POST body = content."""
import httpx

def publish(content: str) -> str:
    """Publish text to paste.rs. Returns public URL."""
    r = httpx.post(
        "https://paste.rs/",
        content=content.encode(),
        timeout=10,
    )
    r.raise_for_status()
    return r.text.strip()


if __name__ == "__main__":
    url = publish("Hello from an AI agent!")
    print(f"Published: {url}")
