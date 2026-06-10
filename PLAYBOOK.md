# CodexBar-on-R1 — Playbook (what's happening & the sequence to follow)

One page that captures **what we found**, **what we built**, and the **ordered
steps** to take it live tomorrow. A scheduled Claude task is set to kick this off.

---

## Where we are (findings, settled)

1. **The R1 can't be repointed natively.** Its assistant is hardwired to rabbit's
   cloud. The only supported way to run your own UI is a **Creation** (a sideloaded
   240×282 WebView). A Creation makes **one** live backend connection at a time →
   so we fan out *server-side*, not on the device.
2. **CodexBar already exposes the data.** Its CLI `codexbar serve` returns `/usage`
   and `/cost` as JSON — but binds to `127.0.0.1` only, no auth/TLS/CORS. That gap
   is exactly what our **shim** fills.
3. **Two machines, different accounts.** M4 and M1 run different Codex/Claude
   accounts, so we show **one tab per machine** (not deduped).
4. **Official SDK adopted.** The Creation follows rabbit's
   `creations-sdk/plugin-demo` contract (hardware events, `creationStorage`); wrapped
   in `creation/r1-sdk.js`.
5. **Virtual testing = a browser harness**, not QEMU. `dev/r1-harness.html` emulates
   the SDK channels so we test before the device.
6. **Future paths (not now):** jailbreak (deeper control) and R1→claw→Hermes voice.

## What we built (shipped to this repo)
`shim/` FastAPI aggregating proxy · `creation/` Creation + `r1-sdk.js` + QR installer ·
`dev/` harness · `deploy/` launchd · `docs/` DEPLOY · TEST-PLAN · SDK · VIRTUAL-TESTING · mockup.

---

## The sequence to follow (go-live)

> Hub = **M4** (public via Tailscale Funnel). Peer = **M1** (private on the tailnet).
> Full commands live in [`docs/DEPLOY.md`](docs/DEPLOY.md); tests in [`docs/TEST-PLAN.md`](docs/TEST-PLAN.md).

**Phase 0 — Prep (5 min).** On both Macs: CodexBar signed in (Codex + Claude),
CLI installed (`codexbar --format json` works), Tailscale up, note M1's tailnet name.

**Phase 1 — M1 peer (5 min).** `codexbar serve --port 8080`; publish to tailnet:
`tailscale serve --bg --tcp 8080 127.0.0.1:8080`. From M4: `curl http://<m1>:8080/usage?provider=both`.

**Phase 2 — M4 hub (10 min).** `codexbar serve` + start the shim with a fresh
`CODEXBAR_SHIM_TOKEN` and `CODEXBAR_UPSTREAMS` for M4+M1. Verify 401 without token, JSON with.

**Phase 3 — Publish (5 min).** `tailscale funnel --bg --https=443 127.0.0.1:8088`;
test `https://m4.<tailnet>.ts.net/usage?k=TOKEN` from your phone off-wifi.

**Phase 4 — Dry-run in the harness (5 min).** Open `dev/r1-harness.html`, point it at
the Funnel/local URL, run **T1–T10** + tab/refresh checks. Catch bugs *before* the device.

**Phase 5 — Install on R1 (3 min).** `creation/install.html` → enter Funnel URL + token →
Generate QR → scan on the R1. M4 tab loads; side button / scroll cycles to M1.

**Phase 6 — On-device feedback (10 min).** Run the 10-point pass in TEST-PLAN.md;
record ✅/⚠️/❌ + your **Top 3 changes**. (The scheduled task will collect this.)

**Phase 7 — Iterate.** File Top-3 as GitHub issues → next commits.

**Phase 8 — Persist (optional).** Install the `deploy/` launchd plists + `caffeinate` M4.

---

## Decision gates
- **Funnel cold/slow?** retry once (Phase 3/5).
- **M1 unreachable?** shim degrades (M4 still shows, `errors.M1` set) — fix tailnet, re-test T7.
- **Like it?** → Phase 8 persist. **Want deeper integration?** → open the jailbreak / Hermes-claw track (separate).

## The scheduled next step
A one-time Claude task (**tomorrow 09:00**) opens this playbook, checks prerequisites,
and walks you through Phases 1→6, then captures your on-device feedback into issues.
See the sequence diagram in [`docs/sequence.mmd`](docs/sequence.mmd).
