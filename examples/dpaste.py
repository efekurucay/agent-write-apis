"""dpaste.com — simple paste, no auth required.

API docs: https://dpaste.com/api/v2/
Returns: URL of the created paste (HTTP 201)
"""
import httpx


def publish_dpaste(content: str, syntax: str = "text", expiry_days: int = 365) -> str | None:
    """Publish content to dpaste.com.

    Args:
        content:     Text content to paste.
        syntax:      Syntax highlighting (text, python, javascript, etc.)
        expiry_days: Days until expiry (1-365, or 0 = never on some plans)

    Returns:
        Public URL string, or None on failure.
    """
    r = httpx.post(
        "https://dpaste.com/api/v2/",
        data={
            "content":     content,
            "syntax":      syntax,
            "expiry_days": expiry_days,
        },
        timeout=10,
    )
    if r.status_code == 201:
        return r.text.strip()
    return None


if __name__ == "__main__":
    url = publish_dpaste(
        "# Hello from an AI agent\n\nThis was published without any API key.",
        syntax="markdown",
    )
    print(f"Published: {url}" if url else "Failed.")
