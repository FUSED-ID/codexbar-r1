# Virtual testing — no R1 in hand

## TL;DR
You don't need QEMU. A Creation is a 240×282 web app with a few native JS
bridges, so the fastest "virtual device" is a **browser harness**:
[`dev/r1-harness.html`](../dev/r1-harness.html) — exact viewport, stubbed
bridges, clickable hardware buttons. Run it against the local shim and you can
reproduce on-device behaviour (incl. tab cycling) before touching the R1.

## The landscape

| Approach | What it is | Good for | Effort |
|----------|------------|----------|--------|
| **Browser harness** (this repo) | 240×282 iframe + stubbed `PluginMessageHandler` / `CreationStorageHandler` / side-button & scroll events | Testing *your Creation* (layout, fetch, bridges, tab logic) | trivial |
| **`creations-sdk/plugin-demo`** | rabbit's official browser-runnable demo of every bridge | Reference for the real bridge API | low |
| **Android AVD "r1 emulator"** | Android Virtual Device (QEMU-backed) configured to R1 specs, via [`awesome-rabbit-r1`](https://github.com/sayhiben/awesome-rabbit-r1) | Emulating the *whole device/launcher* (jailbreak-adjacent) | high |
| **`rabbitude-backend` + launcher** | Go reimplementation of the R1 cloud API + a native launcher | Running the full stack off-device | high |

No one is QEMU-emulating the R1 *to test Creations* — because Creations are web,
the device layer is irrelevant. QEMU/AVD only matters if you're hacking rabbitOS
itself.

## Using the harness
```bash
# 1. start the shim (real data)
cd shim && CODEXBAR_SHIM_TOKEN=dev CODEXBAR_UPSTREAMS='{"M4":"http://127.0.0.1:8080"}' python3 codexbar_shim.py
# 2. open dev/r1-harness.html, set URL to  http://127.0.0.1:8088/?k=dev , Load
# 3. click "Side button" to cycle machine tabs; "Long-press" to force refresh
```
Same-origin note: the bridge stubs and dispatched events only reach the iframe
when it's same-origin (use the localhost shim, or serve the folder with
`python3 -m http.server`). A cross-origin `file://` iframe will render but can't
receive synthetic hardware events — the harness logs this.

## What it catches (and what it can't)
- ✅ Layout/clipping at exactly 240×282, fetch/auth, tab logic, bridge calls,
  hardware-event handlers, refresh cadence.
- ❌ Real mic/camera/accelerometer, Flutter-WebView quirks (Canvas-2D-only, touch
  `preventDefault`), and true network/Funnel latency — those still need the
  device pass in [TEST-PLAN.md](TEST-PLAN.md).
