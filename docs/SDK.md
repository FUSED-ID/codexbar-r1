# R1 Creations SDK — what we use

This Creation follows rabbit's **official** SDK contract, documented in
[`rabbit-hmi-oss/creations-sdk` → `plugin-demo/reference/creation-triggers.md`](https://github.com/rabbit-hmi-oss/creations-sdk/blob/main/plugin-demo/reference/creation-triggers.md).
That `plugin-demo` is rabbit's own browser-runnable reference (Hardware / Data /
Speak pages) — the canonical way to learn the channels. We wrap the bits we need
in [`creation/r1-sdk.js`](../creation/r1-sdk.js) so the same code runs on-device,
in the harness, and in a plain browser (every call degrades gracefully).

## The official channels (verbatim contract)

| Channel | Official API | We use it for |
|---|---|---|
| **Hardware events** | `window.addEventListener("sideClick" \| "longPressStart" \| "longPressEnd" \| "scrollUp" \| "scrollDown", fn)` | side button + scroll wheel cycle machine tabs; long-press refreshes |
| **Storage** | `window.creationStorage.plain` / `.secure` — async `getItem/setItem/removeItem/clear`, **values Base64-encoded** | persist the active machine tab |
| **LLM** | `PluginMessageHandler.postMessage(JSON.stringify({message, useLLM, wantsR1Response, wantsJournalEntry}))`, reply via `window.onPluginMessage(data)` with `data.data` = JSON string | not used yet (data comes from the shim); wired in `r1-sdk.js` for later |
| **Accelerometer** | `window.creationSensors.accelerometer.{isAvailable, start(cb,{frequency}), stop}` | available via `r1-sdk.js`; unused in this Creation |
| **Close** | `closeWebView.postMessage("")` | — |
| **Touch** | `TouchEventHandler.postMessage(JSON.stringify({type,x,y}))` | — |

## `r1-sdk.js` mapping (our thin wrapper)
```js
R1.storage.get(key[,secure]) / R1.storage.set(key,val[,secure])   // Base64 handled for you
R1.hardware.onSideClick(fn) / onScrollUp / onScrollDown / onLongPressStart / onLongPressEnd
R1.llm(message, {wantsR1Response, wantsJournalEntry})  // → Promise<{message,data}>
R1.accelerometer.isAvailable() / start(cb,opts) / stop()
R1.close()
R1.available.{storage,sensors,llm}()                   // feature-detect
```

## Design rules we follow (from the SDK docs)
- Everything fits **240×282 px**, portrait.
- Hardware is weak: prefer `transform`/`opacity`, CSS transitions over JS animation,
  minimal DOM churn, **Canvas-2D only** (no WebGL).
- Storage values must be **Base64**; storage is isolated per plugin id.

## Harness
[`dev/r1-harness.html`](../dev/r1-harness.html) emulates every channel above so you
can exercise the real code paths (storage, hardware events, `onPluginMessage`,
accelerometer) without a device. See [VIRTUAL-TESTING.md](VIRTUAL-TESTING.md).

> Credit: the SDK and `plugin-demo` reference are rabbit's
> ([rabbit-hmi-oss](https://github.com/rabbit-hmi-oss/creations-sdk)). This project
> is unofficial and not affiliated. See [CREDITS](../CREDITS.md).
