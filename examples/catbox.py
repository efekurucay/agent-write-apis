"""catbox.moe + litterbox.catbox.moe — no-auth file hosting.

catbox.moe:  Permanent hosting. Max 200MB. Anonymous uploads cannot be deleted.
litterbox:   Temporary hosting. 1h / 12h / 24h / 72h. Max 1GB.

API docs:
  https://catbox.moe/tools.php
  https://litterbox.catbox.moe/tools.php
"""
import httpx
import os
from typing import Optional, Literal

LITTERBOX_TIME = Literal["1h", "12h", "24h", "72h"]


def upload_catbox(filepath: str) -> Optional[str]:
    """Upload file to catbox.moe (permanent, max 200MB).

    Returns direct URL like https://files.catbox.moe/abc123.txt
    WARNING: anonymous uploads cannot be deleted.
    """
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = httpx.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (filename, f)},
            timeout=60,
        )
    return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None


def upload_litterbox(filepath: str, time: str = "24h") -> Optional[str]:
    """Upload file to litterbox.catbox.moe (temporary, max 1GB).

    Args:
        filepath: Local path to file.
        time:     Expiry: '1h', '12h', '24h', or '72h'.

    Returns direct URL.
    """
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = httpx.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={"reqtype": "fileupload", "time": time},
            files={"fileToUpload": (filename, f)},
            timeout=60,
        )
    return r.text.strip() if r.status_code == 200 and r.text.startswith("https://") else None


def upload_with_fallback(filepath: str) -> Optional[str]:
    """Try catbox (permanent) then litterbox (24h temp) then file.io."""
    providers = [
        ("catbox.moe",         lambda p: upload_catbox(p)),
        ("litterbox (24h)",    lambda p: upload_litterbox(p, "24h")),
    ]
    for name, fn in providers:
        url = fn(filepath)
        if url:
            print(f"✅ Uploaded via {name}: {url}")
            return url
        print(f"❌ {name} failed, trying next...")
    return None


if __name__ == "__main__":
    import tempfile

    # Create a small test file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("Hello from agent-write-apis!\nThis file was uploaded without authentication.\n")
        tmp = f.name

    print(f"Test file: {tmp}")
    url = upload_with_fallback(tmp)
    print(f"\nResult: {url}" if url else "\nAll providers failed.")
    os.unlink(tmp)
