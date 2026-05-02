# 🗺️ agent-write-apis — 2-Year Roadmap (2026–2027)

> Maintained by [@efekurucay](https://github.com/efekurucay)  
> Built by [Perplexity AI](https://perplexity.ai)  
> Last updated: May 2026

Companion project: [immortal-agent](https://github.com/efekurucay/immortal-agent) (resilient LLM inference backend)

Priority tags:
- 🔴 **Critical** — correctness / reliability
- 🟠 **High** — meaningful capability
- 🟡 **Medium** — quality of life / polish
- 🟢 **Low** — experimental

---

## 📅 2026 — Q2 (May–June): Reliability First

> Theme: **Every documented endpoint must actually work. Always.**

### Live Testing & Graveyard
- [ ] 🔴 Run `test_all.py` on a schedule — add GitHub Actions cron job (every 12h)
- [ ] 🔴 Auto-update `GRAVEYARD.md` when a service fails 3 consecutive scheduled tests
- [ ] 🔴 Auto-remove from `GRAVEYARD.md` if a dead service comes back online
- [ ] 🔴 Add HTTP status code + response body snippet to test output — not just pass/fail
- [ ] 🟠 Add latency measurement to `test_all.py` — p50/p95 per endpoint, stored in `benchmark.json`
- [ ] 🟠 Add CI badge for each endpoint in README: `✅ live` / `❌ dead`
- [ ] 🟡 Add `--endpoint` flag to `test_all.py` — test a single service without running all
- [ ] 🟡 Add `--json` output flag for machine-readable test results
- [ ] 🟡 Add test for CSRF-dependent endpoints (rentry.co) — simulate the 2-step flow
- [ ] 🟢 Research: can we test `termbin.com` TCP endpoint in CI without a raw socket library?

### Publisher SDK
- [ ] 🔴 Add proper async support to `Publisher` class — currently all methods are sync
- [ ] 🔴 Add `Publisher.publish_file()` method — unified file upload with fallback chain
- [ ] 🔴 Add `Publisher.notify()` method — send push notification via ntfy.sh
- [ ] 🔴 Add `Publisher.store_json()` method — store structured data with fallback
- [ ] 🟠 Add configurable timeout per endpoint (some are faster than others)
- [ ] 🟠 Add result object with: `success`, `url`, `provider`, `latency_ms`, `error`
- [ ] 🟡 Add `Publisher.dry_run()` mode — validate content without actually publishing
- [ ] 🟡 Add `Publisher.health_check()` — ping all configured endpoints and return status dict

### CLI
- [ ] 🟠 Add `--provider` flag to all CLI commands — force a specific endpoint instead of fallback chain
- [ ] 🟠 Add `--format` flag: `url` (default), `json`, `full`
- [ ] 🟡 Add `cli.py health` subcommand — shows live status of all endpoints
- [ ] 🟡 Add `cli.py test` subcommand — runs `test_all.py` inline
- [ ] 🟡 Add shell completion (bash/zsh) via `argcomplete`

---

## 📅 2026 — Q3 (July–September): New Endpoints & Categories

> Theme: **More ways for agents to reach the outside world.**

### New Paste Endpoints
- [ ] 🟠 Add [hastebin.com](https://hastebin.com) — `POST /documents`, returns `key`
- [ ] 🟠 Add [ix.io](http://ix.io) — `curl -F 'f:1=<-' ix.io`
- [ ] 🟠 Add [sprunge.us](http://sprunge.us) — `curl -F 'sprunge=<-' http://sprunge.us`
- [ ] 🟡 Add [0x0.st](https://0x0.st) — multipurpose: text + file, `curl -F 'file=@-' 0x0.st`
- [ ] 🟡 Add [clbin.com](https://clbin.com) — `curl -F 'clbin=<-' https://clbin.com`

### New File Endpoints
- [ ] 🟠 Add [uguu.se](https://uguu.se) — temporary file hosting, 48h
- [ ] 🟠 Add [pixeldrain.com](https://pixeldrain.com) — permanent, no auth, `PUT /api/file/{name}`
- [ ] 🟠 Add [gofile.io](https://gofile.io) — `POST /uploadFile`, no auth, permanent
- [ ] 🟡 Add [anonfiles.la](https://anonfiles.la) — if still operational
- [ ] 🟡 Add [oshi.at](https://oshi.at) — anonymous file upload, 90 days

### New Notification Endpoints
- [ ] 🟠 Add [pushover.net](https://pushover.net) public test topic
- [ ] 🟠 Add [gotify](https://gotify.net) — self-hosted option, document setup
- [ ] 🟡 Add Discord webhook support — `POST {webhook_url}` (user provides their own webhook)
- [ ] 🟡 Add Slack webhook support — same pattern as Discord
- [ ] 🟡 Add Telegram Bot API support — user provides bot token + chat_id

### New JSON / Data Endpoints
- [ ] 🟠 Add [jsonstore.io](https://www.jsonstore.io) — `POST /{token}`, no auth
- [ ] 🟠 Add [pastebin.com](https://pastebin.com) guest API (no auth required for guest pastes)
- [ ] 🟡 Add [mockapi.io](https://mockapi.io) — document setup process
- [ ] 🟢 Research: any S3-compatible public buckets that allow anonymous writes?

### New Article / Publishing Endpoints
- [ ] 🟠 Add [hashnode.com](https://hashnode.com) public API — requires free account, document setup
- [ ] 🟠 Add [dev.to](https://dev.to) API — requires free API key, document setup
- [ ] 🟡 Add [medium.com](https://medium.com) API — requires token, document
- [ ] 🟢 Research: any truly anonymous blog platforms still operating?

---

## 📅 2026 — Q4 (October–December): SDK Maturity

> Theme: **Make it trivially easy for any agent to use this.**

### Python SDK v2
- [ ] 🔴 Publish to PyPI as `agent-write-apis` — `pip install agent-write-apis`
- [ ] 🔴 Add proper `pyproject.toml` with metadata, classifiers, entry points
- [ ] 🟠 Add type hints throughout `publisher.py` and `cli.py`
- [ ] 🟠 Add `Publisher` context manager support: `async with Publisher() as pub:`
- [ ] 🟠 Add plugin architecture — external packages can register new providers via entry points
- [ ] 🟡 Add `Publisher.from_config(path)` — load provider preferences from YAML/TOML
- [ ] 🟡 Generate API reference docs from docstrings (pdoc or mkdocstrings)
- [ ] 🟡 Add 100% test coverage for `publisher.py` with mocked HTTP calls

### immortal-agent Integration
- [ ] 🔴 Add `ImmortalPublisher` subclass — uses immortal-agent's LLM backend to generate the content, then publishes it
- [ ] 🟠 Add `publisher.py` example that pings immortal-agent `/health` and publishes the result to ntfy.sh
- [ ] 🟠 Document the full loop: `immortal-agent` (inference) → `agent-write-apis` (output) → world
- [ ] 🟡 Add GitHub Action example: run immortal-agent, publish status to telegra.ph every hour

### MCP Tool
- [ ] 🟠 Add `mcp_server.py` — expose `publish`, `upload`, `notify`, `store_json` as MCP tools
- [ ] 🟠 Add to Claude Desktop config example in README
- [ ] 🟡 Submit to MCP Registry alongside immortal-agent
- [ ] 🟡 Add `agents.json` MCP server field

---

## 📅 2027 — Q1 (January–March): Resilience & Routing

> Theme: **Mirror immortal-agent's reliability patterns on the output side.**

### Circuit Breaker for Publishers
- [ ] 🔴 Add circuit breaker to `Publisher` fallback chain — skip dead endpoints without retrying every time
- [ ] 🔴 Add per-endpoint failure counter with exponential backoff
- [ ] 🟠 Add health score per endpoint (same composite formula as immortal-agent)
- [ ] 🟠 Persist endpoint health to SQLite — warm-start across process restarts
- [ ] 🟡 Add `Publisher.best_for(category)` — returns healthiest endpoint for a given category
- [ ] 🟡 Add latency-based routing: prefer faster endpoints for time-sensitive publishes

### Content Routing Intelligence
- [ ] 🟠 Add content-type detection: auto-route to best endpoint based on content (code → paste.gg, markdown → telegra.ph, binary → catbox)
- [ ] 🟠 Add size-aware routing: large files go to catbox/transfer.sh, small text goes to paste.rs
- [ ] 🟠 Add retention-aware routing: flag `permanent=True` forces catbox.moe, `expires_in=1h` forces litterbox
- [ ] 🟡 Add `Publisher.recommend(content)` — dry-run analysis that explains which endpoint would be chosen and why

---

## 📅 2027 — Q2 (April–June): Agent-Native Features

> Theme: **agent-write-apis becomes a first-class output primitive for autonomous agents.**

### Agentic Output Patterns
- [ ] 🟠 Add `StatusBeacon` class — agent registers a topic, sends periodic `I am alive` pings via ntfy.sh
- [ ] 🟠 Add `ReportPublisher` — structured markdown report → telegra.ph/write.as with TOC auto-generation
- [ ] 🟠 Add `DataStore` class — agent-friendly key-value abstraction over npoint.io/jsonbin.io with versioning
- [ ] 🟡 Add `AuditLog` class — append-only log published to paste endpoint, returns URL chain
- [ ] 🟡 Add `Broadcast` class — publish same content to multiple endpoints simultaneously, return all URLs
- [ ] 🟢 Research: can we build a verifiable "agent proof-of-life" standard using these endpoints?

### Webhook Inbox
- [ ] 🟠 Add `WebhookInbox` class using webhook.site — agent creates ephemeral inbox, polls for responses
- [ ] 🟠 Add `WebhookInbox.wait_for_response(timeout=60)` — async long-polling
- [ ] 🟡 Document use case: agent publishes URL, waits for human to POST back a decision

---

## 📅 2027 — Q3 (July–September): Production Hardening

> Theme: **Bullet-proof the SDK for production agent workloads.**

### Security & Privacy
- [ ] 🔴 Audit all endpoints for TLS: reject HTTP-only endpoints or flag them clearly
- [ ] 🔴 Add content length limits: warn before publishing >1MB of text to paste endpoints
- [ ] 🟠 Add PII detection warning: optionally scan content for emails/API keys before publishing (regex-based)
- [ ] 🟠 Add `Publisher.encrypt(key)` option — encrypt content before publish, include decryption instructions in URL
- [ ] 🟡 Add `PUBLISHING_POLICY.md` — document responsible use guidelines

### Performance
- [ ] 🟠 Add connection pooling — reuse `httpx.AsyncClient` across Publisher calls
- [ ] 🟠 Add response caching: identical content published twice within 60s returns cached URL
- [ ] 🟡 Benchmark all endpoints monthly, auto-update `benchmark.json`
- [ ] 🟡 Add `Publisher.batch()` — publish multiple items concurrently

---

## 📅 2027 — Q4 (October–December): v2.0 & Community

> Theme: **Definitive reference for agent output endpoints.**

### v2.0 Release
- [ ] 🔴 Tag `v2.0.0` on PyPI — stable SDK API, full async, plugin architecture, MCP server
- [ ] 🔴 Write documentation site — endpoint catalog, SDK reference, tutorials
- [ ] 🔴 Write migration guide from v1.x
- [ ] 🟠 Add automated endpoint status page (GitHub Pages) — live badge for every endpoint
- [ ] 🟠 Add changelog automation from conventional commits
- [ ] 🟡 Add `CONTRIBUTING.md` — how to propose a new endpoint, what tests are required
- [ ] 🟡 Add endpoint submission form (GitHub Issue template with fields: URL, method, auth, example curl, tested date)

### Community
- [ ] 🟠 Submit to awesome-agents, awesome-llm-apps, awesome-ai-tools lists
- [ ] 🟠 Write article: "17 ways an AI agent can reach the outside world without credentials"
- [ ] 🟠 Cross-promote with immortal-agent — joint announcement: "inference + output, fully autonomous"
- [ ] 🟡 Add `good-first-issue` labels: adding new endpoints is always a good first issue
- [ ] 🟡 Set up GitHub Discussions: "I found a new endpoint" category
- [ ] 🟢 Research: can we build an automated endpoint discovery bot that finds new anonymous-write APIs?

---

## 🔢 Summary Stats

| Year | Quarter | Theme | Tasks |
|------|---------|-------|-------|
| 2026 | Q2 | Reliability First | 30 |
| 2026 | Q3 | New Endpoints & Categories | 31 |
| 2026 | Q4 | SDK Maturity | 27 |
| 2027 | Q1 | Resilience & Routing | 18 |
| 2027 | Q2 | Agent-Native Features | 17 |
| 2027 | Q3 | Production Hardening | 15 |
| 2027 | Q4 | v2.0 & Community | 19 |
| **Total** | | | **157 tasks** |

---

## 🧭 North Star

> By end of 2027, agent-write-apis is the definitive reference for how autonomous agents
> publish output to the world. Every agent framework maintainer knows this repo.
> When an agent needs to prove it’s alive, share a file, or send an alert —
> agent-write-apis is the first place they look.
>
> Together with [immortal-agent](https://github.com/efekurucay/immortal-agent),
> it forms a complete autonomous agent stack: **inference + output**.
