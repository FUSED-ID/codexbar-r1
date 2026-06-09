# Deployment runbook — tomorrow

Goal: CodexBar usage for **Codex + Claude** across **M4** and **M1** live on the
Rabbit R1, one tab per machine. ~30–40 min end to end.

Hub = **M4** (public via Tailscale Funnel). Peer = **M1** (private on the tailnet).

---

## 0. Prerequisites (both machines)
- CodexBar installed, providers signed in (Codex + Claude), menu bar shows real numbers.
- CodexBar CLI installed: CodexBar → Settings → Advanced → **Install CLI**. Verify:
  ```bash
  codexbar --format json --pretty | head
  which codexbar          # note the path for the launchd plist
  ```
- Tailscale up on both; `tailscale status` shows the other machine. Note M1's tailnet name.
- Python 3.11+ on M4 (`python3 -V`).

## 1. M1 (peer) — expose codexbar serve on the tailnet
```bash
codexbar serve --port 8080 --refresh-interval 60      # leave running (or use the launchd plist)
# Publish to the tailnet ONLY (not Funnel):
tailscale serve --bg --tcp 8080 127.0.0.1:8080         # M4 will reach http://<m1>:8080
```
Quick check from M4: `curl -s http://<m1-tailnet-name>:8080/usage?provider=both | head -c 200`

## 2. M4 (hub) — codexbar serve + shim
```bash
codexbar serve --port 8080 --refresh-interval 60       # hub's own data (or launchd plist)

cd <repo>/shim
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export CODEXBAR_SHIM_TOKEN=$(openssl rand -hex 16); echo "TOKEN=$CODEXBAR_SHIM_TOKEN"
export CODEXBAR_UPSTREAMS='{"M4":"http://127.0.0.1:8080","M1":"http://<m1-tailnet-name>:8080"}'
python3 codexbar_shim.py
```
Local check (new terminal):
```bash
curl -s "http://127.0.0.1:8088/usage?k=$CODEXBAR_SHIM_TOKEN" | python3 -m json.tool | head -40
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8088/usage    # expect 401 (no token)
```

## 3. Publish the hub via Tailscale Funnel
```bash
tailscale funnel --bg --https=443 127.0.0.1:8088
tailscale funnel status        # note the public URL: https://m4.<tailnet>.ts.net
```
Check from your phone (off wifi): `https://m4.<tailnet>.ts.net/usage?k=TOKEN` → JSON.

## 4. Install the Creation on the R1
1. Open `creation/install.html` in any browser.
2. Enter the Funnel URL + token → **Generate QR**.
3. On the R1, open the creation install flow and scan the QR.
4. The R1 loads the Creation; M4 tab shows first, side button cycles to M1.

## 5. Make it survive reboots (optional, after it works)
- `deploy/com.fused.codexbar-serve.plist` on both machines.
- `deploy/com.fused.codexbar-shim.plist` on M4 (fill REPO_PATH + token).
- `cp` to `~/Library/LaunchAgents/`, `launchctl load -w …`.
- Keep M4 awake during the day: `caffeinate -dimsu` or Amphetamine.

## Rollback / kill
```bash
tailscale funnel --https=443 off
launchctl unload ~/Library/LaunchAgents/com.fused.codexbar-shim.plist
# Ctrl-C the serve/shim processes if run by hand.
```

## Security notes
- **Never** expose `codexbar serve` directly — it has no auth. Only the token-gated
  shim is public; CodexBar stays on loopback / tailnet.
- The token lives in the R1's URL → low-trust. Rotate (regen token, re-issue QR) if leaked.
- Funnel is the public internet; the token gates everything. Leak risk = usage stats, not creds.
