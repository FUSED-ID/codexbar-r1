# CodexBar for Rabbit R1

**Your AI-coding usage limits — Codex + Claude, across every machine — on your Rabbit R1.**

A tiny [Rabbit R1](https://www.rabbit.tech) Creation that shows
[CodexBar](https://codexbar.app) usage at a glance: session & weekly windows,
reset countdowns, and headroom bars for Codex and Claude — with **one tab per
machine** (e.g. M4 / M1).

> Unofficial. Not affiliated with or endorsed by CodexBar or rabbit. See [CREDITS](CREDITS.md).

---

## How it works

CodexBar already does the hard part: its bundled CLI (`codexbar serve`) serves
`/usage` and `/cost` as JSON. But that server binds to `127.0.0.1` only — no
auth, no TLS, no CORS — so an R1 (a locked WebView device on the public
internet) can't reach it. This repo adds a small **shim** that fixes exactly
that, and fans out across machines.

```
 Rabbit R1  ──(one fetch)─▶  Tailscale Funnel (https)
                               │
                               ▼
                     shim  (FastAPI, hub = M4, :8088)
                     • bearer token   • CORS   • Host rewrite
                     • aggregates every machine, tags by name
                          │                         │
                          ▼                         ▼
            codexbar serve (M4, loopback)   codexbar serve (M1, tailnet)
```

The R1 makes **one** request; the shim merges all machines server-side and
returns `{ "machines": { "M4": …, "M1": … } }`. The Creation renders a tab per
machine — labels colour-coded **Codex blue** / **Anthropic orange**, active tab
in rabbit orange.

See [`docs/mockup.html`](docs/mockup.html) for a 1:1 model of the 240×282 screen
vs the real CodexBar menu bar.

## Repo layout

```
shim/        FastAPI aggregating proxy + .env.example
creation/    R1 Creation (index.html) + QR install page (install.html)
deploy/      launchd plists for codexbar serve + the shim
docs/        DEPLOY.md · TEST-PLAN.md · mockup.html
```

## Quick start

```bash
# 1. CodexBar → Settings → Advanced → Install CLI  (on each machine)
codexbar serve --port 8080                # both machines

# 2. Shim on the hub (M4)
cd shim && pip install -r requirements.txt
export CODEXBAR_SHIM_TOKEN=$(openssl rand -hex 16)
export CODEXBAR_UPSTREAMS='{"M4":"http://127.0.0.1:8080","M1":"http://m1:8080"}'
python3 codexbar_shim.py

# 3. Publish + install
tailscale funnel --bg --https=443 127.0.0.1:8088
open creation/install.html                # enter Funnel URL + token, scan QR on R1
```

Full runbook: **[docs/DEPLOY.md](docs/DEPLOY.md)** · Tests + on-device feedback
loop: **[docs/TEST-PLAN.md](docs/TEST-PLAN.md)**.

## R1 Creation constraints (handled)
- Exactly **240×282 px**, **Canvas 2D / DOM only** (no WebGL).
- HTTPS origin (Funnel) so there's no mixed-content.
- Hardware bridges: **side button** cycles machine tabs, **long-press** forces refresh.

## Security
- Only the **token-gated shim** is public; `codexbar serve` stays loopback / tailnet.
- The token rides in the install QR URL — treat as low-trust, rotate if leaked.
- Leak risk is your **usage stats**, not credentials.

## License
[MIT](LICENSE) © 2026 Leon-Gerard Vandenberg / FUSED-ID.

## Credits
- **CodexBar** & its `serve` CLI — **Peter Steinberger** ([@steipete](https://github.com/steipete)). The data engine this is built on.
- **Rabbit R1 / creations stack** — **rabbit** ([creations-sdk](https://github.com/rabbit-hmi-oss/creations-sdk)).
- R1 patterns from `ShayneP/rabbit-r1-livekit-skill` and `DavidBuchanan314`'s R1 notes.

Full acknowledgements: [CREDITS.md](CREDITS.md).
