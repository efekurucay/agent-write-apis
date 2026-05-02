"""paste.rs — minimal paste service, no auth, raw body upload.

The entire request body becomes the paste content.
Returns: URL of the paste (HTTP 201)
"""
import httpx


def publish_paste_rs(content: str) -> str | None:
    """Publish content to paste.rs.

    Args:
        content: Text content to paste.

    Returns:
        Public URL string, or None on failure.
    """
    r = httpx.post(
        "https://paste.rs/",
        content=content.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    if r.status_code == 201:
        return r.text.strip()
    return None


if __name__ == "__main__":
    url = publish_paste_rs(
        "Hello from an AI agent!\nPublished to paste.rs with no authentication."
    )
    print(f"Published: {url}" if url else "Failed.")
