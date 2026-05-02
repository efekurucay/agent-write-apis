"""ntfy.sh — push notification, zero auth required.

ntfy.sh is a simple HTTP-based pub-sub notification service.
Anyone can publish to any topic — no signup, no tokens.

Docs: https://docs.ntfy.sh/publish/
"""
import httpx

TOPIC = "agent-write-apis-demo"  # Change to your own topic string


def notify(message: str, title: str = "Agent", priority: str = "default",
           tags: list[str] | None = None) -> bool:
    """Send a push notification via ntfy.sh.

    Priority levels: min, low, default, high, urgent
    Tags: emoji shortcodes — e.g. ['white_check_mark', 'robot']
    """
    headers = {
        "Title": title,
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = ",".join(tags)

    r = httpx.post(f"https://ntfy.sh/{TOPIC}",
                   data=message.encode(),
                   headers=headers,
                   timeout=10)
    return r.status_code == 200


if __name__ == "__main__":
    # Basic notification
    ok = notify("Agent is alive and publishing!",
                title="Status Update",
                priority="default",
                tags=["white_check_mark", "robot"])
    print(f"Notification sent: {ok}")
    print(f"Subscribe at: https://ntfy.sh/{TOPIC}")
    print(f"Or via CLI:   ntfy subscribe {TOPIC}")
    print(f"Or in browser: https://ntfy.sh/{TOPIC}")

    # High-priority alert
    ok2 = notify("CRITICAL: agent lost all LLM connections!",
                 title="Agent Alert",
                 priority="urgent",
                 tags=["rotating_light"])
    print(f"\nAlert sent: {ok2}")
