# Credits & Acknowledgements

This project stands entirely on other people's work. It is **unofficial** and
**not affiliated with or endorsed by** any of the projects below.

## CodexBar — Peter Steinberger ([@steipete](https://github.com/steipete))
The usage data, and the only reason this is clean to build, comes from
**CodexBar** and its bundled `codexbar serve` CLI, which exposes `/usage` and
`/cost` as JSON. All the hard work — polling 40+ providers, parsing local Codex
and Claude logs, modelling session/weekly windows — happens there.
- App & docs: https://github.com/steipete/CodexBar
- Site: https://codexbar.app
Thank you, Peter. This shim is just a thin proxy in front of your CLI.

## Rabbit R1 stack — rabbit ([@rabbit-hmi-oss](https://github.com/rabbit-hmi-oss))
The on-device app is a **Creation** — a sideloaded WebView app — built on
rabbit's R1 / creations stack and its hardware bridges (scroll wheel, side
button, storage).
- Creations SDK: https://github.com/rabbit-hmi-oss/creations-sdk
- rabbit: https://www.rabbit.tech

## Reference R1 creations
Patterns (240×282 WebView constraints, QR sideload, native bridges) learned from:
- `ShayneP/rabbit-r1-livekit-skill` — bring-your-own-model voice agent for the R1.
- `DavidBuchanan314` — unofficial R1 API notes.

## This project
The shim, the CodexBar Creation, and the deploy/test tooling are by
Leon-Gerard Vandenberg / FUSED-ID, MIT-licensed.
