# agent-write-apis 🌐

> A curated list of public HTTP endpoints where AI agents can **write/publish** content without any authentication.

Built because every agent eventually needs to reach the outside world — and this information is scattered, outdated, or missing entirely.

All entries are **live-tested**. Dead services are documented in [GRAVEYARD.md](./GRAVEYARD.md).

---

## ✅ Working Endpoints

### 📝 Paste / Text

| Service | Method | URL | Notes |
|---|---|---|---|
| [dpaste.com](https://dpaste.com) | `POST /api/v2/` | `https://dpaste.com/api/v2/` | Returns URL in body. Syntax highlighting. |
| [paste.rs](https://paste.rs) | `POST /` | `https://paste.rs/` | Raw body = content. Returns URL. |
| [rentry.co](https://rentry.co) | `POST /api/new` | `https://rentry.co/api/new` | Markdown support. CSRF token required (fetch from GET first). |

### 📰 Full Article / Page Publishing

| Service | Method | URL | Notes |
|---|---|---|---|
| [telegra.ph](https://telegra.ph) | `POST /createAccount` + `POST /createPage` | `https://api.telegra.ph/` | No signup. Create ephemeral account, then publish. Returns public URL. |

---

## ❌ Graveyard (Tested, Dead or Auth Required)

See [GRAVEYARD.md](./GRAVEYARD.md)

---

## Usage

See the [`examples/`](./examples/) folder for ready-to-use Python snippets.

```bash
# Quick test
python examples/dpaste.py
python examples/telegra_ph.py
```

---

## Why This Exists

AI agents need to reach the outside world — to publish results, share reports, or just prove they're alive. Most agents assume the LLM is available but have no path to external output.

This repo documents every endpoint an agent can call without credentials.

> Inspired by a real problem: [immortal-agent](https://github.com/efekurucay/immortal-agent) needed to publish its status and had nowhere to go.

---

## Contributing

- Test the endpoint before submitting a PR
- If it's dead, add it to GRAVEYARD.md instead
- Include the exact `curl` or Python snippet that works

---

*Maintained by [@efekurucay](https://github.com/efekurucay)*
