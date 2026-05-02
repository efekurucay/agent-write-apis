# Graveyard ⚰️

Endpoints that used to work but are now dead, require auth, or are unreliable.

| Service | Last Working | Reason | Notes |
|---|---|---|---|
| [0x0.st](https://0x0.st) | ~2024 | Disabled uploads due to AI botnet spam | May return. Check status at the URL. |
| [ix.io](http://ix.io) | ~2024 | Offline / on a break | Was: `POST http://ix.io` with `f:1=<content>` |
| [hastebin.com](https://hastebin.com) | ~2023 | Now requires Toptal auth token | `POST /documents` returns 401 |
| [clbin.com](https://clbin.com) | ~2023 | SSL/TLS broken | `POST https://clbin.com/` with `clbin=<content>` |
| [bin.gy](https://bin.gy) | Unknown | DNS not resolving | |
| [p.ip.fi](https://p.ip.fi) | Unknown | 500 Internal Server Error | |
| [sprunge.us](http://sprunge.us) | ~2024 | Intermittent — flaky responses | Was: `curl -F 'sprunge=@file' http://sprunge.us` |
| [pastery.net](https://pastery.net) | ~2024 | Now requires API key (free tier still exists but no anon) | |
| [ghostbin.co](https://ghostbin.co) | ~2023 | Site down | Was a popular anon pastebin |
| [bpaste.net](https://bpaste.net) | ~2022 | Shutdown | Replaced by newer services |
