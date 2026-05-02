# agent-write-apis 🌐

> A curated list of public HTTP endpoints where AI agents can **write/publish** content — no authentication required.

Built because every agent eventually needs to reach the outside world, and this information is scattered, outdated, or missing entirely.

All entries are **live-tested**. Dead services are documented in [GRAVEYARD.md](./GRAVEYARD.md).

---

## ✅ Working Endpoints

### 📝 Paste / Text

| Service | Method | URL | Notes |
|---|---|---|---|
| [dpaste.com](https://dpaste.com) | `POST /api/v2/` | `https://dpaste.com/api/v2/` | `content=` field. Returns URL. Syntax highlighting, 1-365 day expiry. |
| [paste.rs](https://paste.rs) | `POST /` | `https://paste.rs/` | Raw body = content. Returns URL (HTTP 201). |
| [rentry.co](https://rentry.co) | `POST /api/new` | `https://rentry.co/api/new` | Markdown. CSRF token required (GET first, use `csrftoken` cookie). |
| [termbin.com](https://termbin.com) | `TCP :9999` | `tcp://termbin.com:9999` | `echo hello \| nc termbin.com 9999`. Returns URL. |
| [bpa.st](https://bpa.st) | `POST /` | `https://bpa.st/` | Form field `content=`. Follows redirect to paste URL. |
| [paste.gg](https://paste.gg) | `POST /v1/pastes` | `https://api.paste.gg/v1/pastes` | JSON body. Anonymous = no `Authorization` header. Returns deletion key. |

### 📰 Full Article / Page Publishing

| Service | Method | URL | Notes |
|---|---|---|---|
| [telegra.ph](https://telegra.ph) | `POST /createAccount` → `POST /createPage` | `https://api.telegra.ph/` | No signup. Ephemeral account + rich article. Returns public URL. |
| [write.as](https://write.as) | `POST /api/posts` | `https://write.as/api/posts` | Anonymous post. JSON body `{body, title}`. Returns `data.url`. |

### 🔔 Notifications / Events

| Service | Method | URL | Notes |
|---|---|---|---|
| [ntfy.sh](https://ntfy.sh) | `POST /{topic}` | `https://ntfy.sh/{topic}` | Raw body = message. Headers: `Title`, `Priority`, `Tags`. No auth for public topics. |
| [webhook.site](https://webhook.site) | `POST /{token}` | Create token: `POST https://webhook.site/token` (no auth) | Ephemeral inbox. Agent can verify its own delivery. |

### 📁 File Upload

| Service | Method | URL | Notes |
|---|---|---|---|
| [catbox.moe](https://catbox.moe) | `POST /user/api.php` | `https://catbox.moe/user/api.php` | `reqtype=fileupload`, `fileToUpload=@file`. **Permanent** hosting. Max 200MB. |
| [litterbox.catbox.moe](https://litterbox.catbox.moe) | `POST /resources/internals/api.php` | `https://litterbox.catbox.moe/resources/internals/api.php` | Temporary: 1h / 12h / 24h / 72h. Max 1GB. |
| [file.io](https://file.io) | `POST /` | `https://file.io/` | One-time download (auto-deletes). Max 100MB free. |
| [transfer.sh](https://transfer.sh) | `PUT /{filename}` | `https://transfer.sh/{filename}` | Raw body. 14-day retention. Direct download URL. |
| [bashupload.com](https://bashupload.com) | `POST /{filename}` | `https://bashupload.com/{filename}` | Raw body. Returns `wget` download command. |

### 🗄️ JSON / Key-Value Store

| Service | Method | URL | Notes |
|---|---|---|---|
| [npoint.io](https://npoint.io) | `POST /` | `https://api.npoint.io/` | Body: `{"json": {...}}`. Public GET at `https://api.npoint.io/{id}`. |
| [jsonbin.io](https://jsonbin.io) | `POST /v3/b` | `https://api.jsonbin.io/v3/b` | `Content-Type: application/json`. No auth for public bins. Returns `metadata.id`. |

---

## ⚡ Quick Reference (curl)

```bash
# Simplest paste
echo 'hello from agent' | curl -s -T - https://paste.rs/

# dpaste with syntax
curl -s -X POST https://dpaste.com/api/v2/ -d 'content=hello&syntax=python'

# paste.gg anonymous
curl -s -X POST https://api.paste.gg/v1/pastes \
  -H 'Content-Type: application/json' \
  -d '{"name":"report","files":[{"name":"out.txt","content":{"format":"text","value":"hello"}}]}'

# ntfy.sh push notification
curl -s -d 'Agent alive!' -H 'Title: Status' https://ntfy.sh/my-agent-topic

# catbox.moe permanent file upload
curl -s -F 'reqtype=fileupload' -F 'fileToUpload=@report.txt' https://catbox.moe/user/api.php

# litterbox 24h temp upload
curl -s -F 'reqtype=fileupload' -F 'time=24h' -F 'fileToUpload=@report.txt' \
  https://litterbox.catbox.moe/resources/internals/api.php

# file.io one-time link
curl -s -F 'file=@report.txt' https://file.io/

# transfer.sh 14-day share
curl -s --upload-file report.txt https://transfer.sh/report.txt

# write.as anonymous blog post
curl -s -X POST https://write.as/api/posts \
  -H 'Content-Type: application/json' \
  -d '{"body": "Agent report.", "title": "Status"}'

# npoint.io JSON store
curl -s -X POST https://api.npoint.io/ \
  -H 'Content-Type: application/json' \
  -d '{"json": {"status": "alive", "loop": 42}}'

# telegra.ph article (2-step)
TOKEN=$(curl -s 'https://api.telegra.ph/createAccount?short_name=agent&author_name=Agent' | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['access_token'])")
curl -s "https://api.telegra.ph/createPage?access_token=$TOKEN&title=Report&content=[{\"tag\":\"p\",\"children\":[\"hello\"]}]&return_content=false"
```

---

## 🐍 Python SDK (`publisher.py`)

Unified Publisher with automatic fallback chain:

```python
from publisher import Publisher

pub = Publisher()
result = pub.publish("Agent status: alive.")
print(result)  # ✅ [paste_rs] https://paste.rs/abc (312ms)
```

Fallback order: `paste_rs` → `dpaste` → `rentry` → `telegra_ph` → `write_as` → `ntfy`

---

## 🖥️ CLI

```bash
pip install httpx

# Publish text
python cli.py paste 'Hello from my agent'

# Push notification
python cli.py notify 'Agent is alive!'

# Upload a file
python cli.py upload /path/to/report.txt

# Store JSON
python cli.py json '{"status": "alive", "loop": 42}'

# Try all paste providers
python cli.py all 'Testing all providers'
```

---

## 🧪 Live Test Suite

```bash
python test_all.py
```

Runs every endpoint, reports latency, pass/fail for each. Updates GRAVEYARD automatically if something is dead.

---

## Usage

```bash
pip install httpx

python examples/dpaste.py
python examples/paste_rs.py
python examples/ntfy.py
python examples/file_upload.py
python examples/json_store.py
python examples/catbox.py
python examples/paste_gg.py
python examples/telegra_ph.py
python examples/multi_fallback.py
python publisher.py
```

---

## Why This Exists

AI agents need to reach the outside world — publish results, share files, send alerts, or just prove they're alive. Most agent frameworks handle LLM calls but have no path to external output.

This repo documents every endpoint an agent can call **without credentials**.

> Inspired by [immortal-agent](https://github.com/efekurucay/immortal-agent) — an agent that needed to publish its status and had nowhere to go.

---

## Contributing

- Test before submitting
- Dead endpoint → [GRAVEYARD.md](./GRAVEYARD.md), not deleted
- Include exact `curl` snippet
- Categories: Paste / Article / Notify / File / JSON

---

*Maintained by [@efekurucay](https://github.com/efekurucay) · Built with [Perplexity AI](https://perplexity.ai)*
