"""rentry.co — no auth required. Markdown supported. Requires CSRF token from GET."""
import httpx

def publish(markdown_content: str) -> dict:
    """Publish markdown to rentry.co. Returns dict with url and edit_code."""
    # Step 1: get CSRF token
    r0 = httpx.get("https://rentry.co", timeout=10)
    csrf = r0.cookies.get("csrftoken", "")

    # Step 2: create paste
    r = httpx.post(
        "https://rentry.co/api/new",
        data={"csrfmiddlewaretoken": csrf, "text": markdown_content},
        headers={"Referer": "https://rentry.co"},
        cookies={"csrftoken": csrf},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()  # {"url": "...", "edit_code": "..."}


if __name__ == "__main__":
    result = publish("# Hello\n\nHello from an AI agent!")
    print(f"Published: {result['url']}")
    print(f"Edit code: {result['edit_code']}")
