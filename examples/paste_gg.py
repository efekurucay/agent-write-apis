"""paste.gg — anonymous paste with deletion key.

Docs: https://github.com/ascclemens/paste/blob/master/api.md
Base: https://api.paste.gg/v1/

Anonymous paste = no Authorization header.
A deletion key is returned so you can delete it later.
"""
import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class PasteGGResult:
    url: str
    id: str
    deletion_key: Optional[str]

    def __str__(self):
        dk = f" (deletion_key: {self.deletion_key})" if self.deletion_key else ""
        return f"{self.url}{dk}"


def publish_paste_gg(
    content: str,
    filename: str = "output.txt",
    name: str = "Agent Report",
    description: str = "",
    expires: Optional[str] = None,  # ISO 8601, e.g. "2026-12-31T00:00:00Z"
) -> Optional[PasteGGResult]:
    """Create an anonymous paste on paste.gg.

    Args:
        content:     Text content.
        filename:    File name shown in the paste (extension determines syntax highlighting).
        name:        Paste title.
        description: Optional description.
        expires:     Optional ISO 8601 expiry datetime.

    Returns:
        PasteGGResult with URL and deletion key, or None on failure.
    """
    payload: dict = {
        "name": name,
        "files": [
            {
                "name": filename,
                "content": {
                    "format": "text",
                    "value": content,
                },
            }
        ],
    }
    if description:
        payload["description"] = description
    if expires:
        payload["expires"] = expires

    r = httpx.post(
        "https://api.paste.gg/v1/pastes",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    if r.status_code == 201:
        data = r.json().get("result", {})
        paste_id = data.get("id", "")
        return PasteGGResult(
            url=f"https://paste.gg/p/anonymous/{paste_id}",
            id=paste_id,
            deletion_key=data.get("deletion_key"),
        )
    return None


def delete_paste_gg(paste_id: str, deletion_key: str) -> bool:
    """Delete a paste using the deletion key returned at creation time."""
    r = httpx.delete(
        f"https://api.paste.gg/v1/pastes/{paste_id}",
        headers={"Authorization": f"Key {deletion_key}"},
        timeout=10,
    )
    return r.status_code == 204


if __name__ == "__main__":
    result = publish_paste_gg(
        content="# Agent Report\n\nStatus: alive\nLoop: 42",
        filename="report.md",
        name="Agent Status Report",
    )
    if result:
        print(f"Published: {result}")
        print(f"URL:          {result.url}")
        print(f"Deletion key: {result.deletion_key}")
    else:
        print("Failed.")
