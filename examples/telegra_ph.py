"""telegra.ph — no auth required. Full article publishing with rich content."""
import httpx

def create_account(short_name: str = "ai-agent", author_name: str = "AI Agent", author_url: str = "") -> str:
    """Create an ephemeral Telegraph account. Returns access_token."""
    r = httpx.post(
        "https://api.telegra.ph/createAccount",
        params={"short_name": short_name, "author_name": author_name, "author_url": author_url},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    assert data["ok"], f"Telegraph error: {data}"
    return data["result"]["access_token"]


def publish(title: str, text: str, author_name: str = "AI Agent", author_url: str = "") -> str:
    """Create a Telegraph account and publish a page. Returns public URL."""
    token = create_account(author_name=author_name, author_url=author_url)

    # Content is a list of Node objects
    content = [{"tag": "p", "children": [paragraph]}
               for paragraph in text.split("\n\n") if paragraph.strip()]

    r = httpx.post(
        "https://api.telegra.ph/createPage",
        json={
            "access_token": token,
            "title": title,
            "author_name": author_name,
            "author_url": author_url,
            "content": content,
            "return_content": False,
        },
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    assert data["ok"], f"Telegraph error: {data}"
    return data["result"]["url"]


if __name__ == "__main__":
    url = publish(
        title="Hello from an AI agent",
        text="This page was published programmatically with zero authentication.\n\nBuilt with agent-write-apis: https://github.com/efekurucay/agent-write-apis",
        author_name="immortal-agent",
        author_url="https://github.com/efekurucay/immortal-agent",
    )
    print(f"Published: {url}")
