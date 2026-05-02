"""File upload to no-auth public endpoints.

Three providers with different tradeoffs:
- file.io: one-time download (auto-deletes after first access)
- transfer.sh: 14-day retention, direct URL, large files OK
- bashupload.com: minimal, returns wget command
"""
import httpx
import os
from typing import Optional


def upload_file_io(filepath: str) -> Optional[str]:
    """Upload to file.io. File is deleted after first download."""
    with open(filepath, "rb") as f:
        r = httpx.post("https://file.io/",
                       files={"file": (os.path.basename(filepath), f)},
                       timeout=30)
    if r.status_code == 200 and r.json().get("success"):
        return r.json()["link"]
    return None


def upload_transfer_sh(filepath: str) -> Optional[str]:
    """Upload to transfer.sh. 14-day retention, direct download link."""
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = httpx.put(f"https://transfer.sh/{filename}",
                      content=f.read(),
                      timeout=30)
    return r.text.strip() if r.status_code == 200 else None


def upload_bashupload(filepath: str) -> Optional[str]:
    """Upload to bashupload.com. Returns download URL as plain text."""
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = httpx.post(f"https://bashupload.com/{filename}",
                       content=f.read(),
                       timeout=30)
    # Response is like: wget https://bashupload.com/abc/file.txt
    if r.status_code == 200:
        for line in r.text.splitlines():
            if line.startswith("wget "):
                return line.split(" ", 1)[1].strip()
    return None


def upload_with_fallback(filepath: str) -> Optional[str]:
    """Try each upload provider in order."""
    providers = [
        ("file.io",       upload_file_io),
        ("transfer.sh",   upload_transfer_sh),
        ("bashupload.com",upload_bashupload),
    ]
    for name, fn in providers:
        url = fn(filepath)
        if url:
            print(f"Uploaded via {name}: {url}")
            return url
        print(f"{name} failed, trying next...")
    return None


if __name__ == "__main__":
    # Create a test file
    test_file = "/tmp/agent_report.txt"
    with open(test_file, "w") as f:
        f.write("Agent report\n============\nStatus: alive\nTimestamp: now\n")

    url = upload_with_fallback(test_file)
    print(f"\nFinal URL: {url}" if url else "All upload providers failed.")
