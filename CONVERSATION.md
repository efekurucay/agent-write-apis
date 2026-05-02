# Session Log — agent-write-apis

This file documents how this repository was created and evolved.

---

## Origin

This repo emerged from a conversation about [immortal-agent](https://github.com/efekurucay/immortal-agent) — an agent designed to stay alive at all costs, self-repair, and never stop running.

The core problem: **once an agent is alive and has something to say, where does it publish?**

Most agents assume the LLM is available but have no path to external output. This repo solves that.

---

## Conversation Summary (2026-05-02)

### Context

- Developer: [@efekurucay](https://github.com/efekurucay) — full-stack developer based in Antalya, Turkey.
- AI: Perplexity AI (Claude Sonnet 4.6 backend)
- Session duration: ~2 hours

### What Was Discussed

1. **immortal-agent architecture** — The original repo (`immortal-agent`) was being built: a Python agent that survives LLM provider failures by chaining multiple free-tier APIs (Groq, OpenRouter, Mistral, Ollama, etc.).

2. **Reverse engineering Gemini** — Question raised: could the macOS Gemini DMG be reverse engineered to use unofficial Google auth for API calls? Conclusion: technically possible via SSL proxying + Frida, but pointless since the official Gemini API free tier already provides what's needed. ToS violation risk also significant.

3. **immortal-agent wrappers** — Decision to add OpenRouter, Groq, Mistral, Cohere, Together, HuggingFace, and Ollama wrappers to immortal-agent in a single commit.

4. **Deep architecture research** — Before touching code, extensive research was done on:
   - Circuit breaker patterns (Closed → Open → Half-open state machine)
   - Composite health score systems (success rate + latency + error rate)
   - Retry with exponential backoff + jitter + budget
   - Canary deployment for AI-generated code
   - Structured observability / tracing for agents
   - Self-repair pipeline with sandbox testing

5. **agent-write-apis focus** — Decision shifted to focus on this repo (`agent-write-apis`) as a standalone, well-curated resource. Reason: cleaner scope, more useful to the community, and a natural companion to immortal-agent.

6. **Research phase** — Before writing any code, the following was researched:
   - Every no-auth paste/publish endpoint (live-tested or documented)
   - File upload services (file.io, transfer.sh, bashupload)
   - JSON stores (npoint.io, jsonbin.io)
   - Notification services (ntfy.sh)
   - Dead services: 0x0.st (AI botnet spam killed it), sprunge.us (flaky), pastery.net (now auth required)

### Outcome

A single commit that:
- Restructured README into 6 categories
- Added 10+ new verified endpoints
- Added `publisher.py` — a production-grade unified Publisher class
- Added 4 new example files (ntfy, file upload, json store, updated multi-fallback)
- Updated GRAVEYARD.md with newly dead services
- Added this CONVERSATION.md

---

## Design Philosophy

> An agent must always have somewhere to write.

This repo is intentionally **not a framework**. It's a reference list + minimal Python snippets. The goal is that any agent, in any language, can find a working endpoint here and use it in 5 minutes.

Rules:
- Every endpoint must be testable with a single `curl` command
- Every Python example must work with only `httpx` as a dependency
- Dead endpoints go to GRAVEYARD, not deleted — history matters
- No authentication ever — if it needs a token, it doesn't belong here

---

*Built by Perplexity AI in collaboration with [@efekurucay](https://github.com/efekurucay)*
