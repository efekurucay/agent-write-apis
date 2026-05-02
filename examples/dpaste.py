"""dpaste.com — no auth required."""
import httpx

def publish(content: str, title: str = "agent-output", expiry_days: int = 365) -> str:
    """Publish text to dpaste.com. Returns public URL."""
    r = httpx.post(
        "https://dpaste.com/api/v2/",
        data={
            "content": content,
            "syntax": "text",
            "expiry_days": expiry_days,
            "title": title,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.text.strip()


if __name__ == "__main__":
    url = publish("Hello from an AI agent!", title="test")
    print(f"Published: {url}")
