# Test plan + R1 feedback loop

Run top-to-bottom during tomorrow's deploy. Each layer is verified before the
next so failures localise. Then a structured on-device pass with LGV's R1.

## Layer tests (gate each before moving on)

| # | Layer | Command / action | Pass criteria |
|---|-------|------------------|---------------|
| T1 | CodexBar CLI (M4) | `codexbar --format json --pretty` | JSON with codex + claude, real %s |
| T2 | CodexBar CLI (M1) | same on M1 | JSON, M1's accounts |
| T3 | serve (M4) | `curl 127.0.0.1:8080/usage?provider=both` | 200 JSON |
| T4 | serve (M1) via tailnet | `curl http://<m1>:8080/usage?provider=both` (from M4) | 200 JSON |
| T5 | shim auth | `curl 127.0.0.1:8088/usage` (no token) | **401** |
| T6 | shim aggregate | `curl 127.0.0.1:8088/usage?k=TOKEN` | `machines.M4` + `machines.M1`, `errors` empty |
| T7 | shim degraded | stop M1 serve, repeat T6 | M4 still returns; `errors.M1` set; no 500 |
| T8 | Funnel | `https://m4.<tailnet>.ts.net/usage?k=TOKEN` from phone off-wifi | 200 JSON |
| T9 | Funnel auth | same without `?k` | 401 |
| T10 | Creation loads | scan QR on R1 | tabs render, bars draw, no blank screen |

## On-device feedback pass (LGV + R1)

For each, LGV records: ✅ / ⚠️ / ❌ + a one-line note. Capture an R1 photo for any ⚠️/❌.

1. **First paint** — does the Creation open within ~3s and show M4's Codex + Claude bars?
2. **Numbers match** — do R1 bars/percentages match the CodexBar menu bar on M4 right now?
3. **Tab switch** — side button cycles M4 → M1 → M4; only one machine shows at a time (no stacking).
4. **M1 accuracy** — M1 tab shows M1's accounts (Codex Plus / Claude Pro), not M4's.
5. **Reset countdowns** — do "Session/Weekly · resets" values look right vs the menu bar?
6. **Refresh** — long-press forces refresh; the `updated HH:MM` stamp changes.
7. **Legibility** — readable at arm's length? colour (green/amber/red) reads correctly?
8. **Stability** — leave it 10 min; auto-refresh (60s) keeps working, no freeze/blank.
9. **Edge** — put a provider near/over limit; does it flip amber→red as expected?
10. **Wishlist** — what's missing at a glance? (cost line? sonnet? bigger reset?)

### Feedback capture template (paste back to me)
```
T-results: T1..T10 = [pass/fail + notes]
On-device:
 1 first-paint:   ✅/⚠️/❌  —
 2 numbers-match: ✅/⚠️/❌  —
 3 tab-switch:    ✅/⚠️/❌  —
 4 m1-accuracy:   ✅/⚠️/❌  —
 5 countdowns:    ✅/⚠️/❌  —
 6 refresh:       ✅/⚠️/❌  —
 7 legibility:    ✅/⚠️/❌  —
 8 stability:     ✅/⚠️/❌  —
 9 edge-color:    ✅/⚠️/❌  —
10 wishlist:      —
Top 3 changes I want: 1) … 2) … 3) …
```

## Known sharp edges to watch
- **Account-level windows:** Codex/Claude limit windows are per-account; if M4 and M1
  share an account a tab looks "duplicated". (Confirmed different accounts → fine.)
- **CodexBar `both` shape:** may be an array or `{providers:[…]}`; the Creation handles both.
- **Hub sleep:** if M4 sleeps, data goes stale — `caffeinate` for the test window.
- **Funnel cold start:** first request after idle can be slow; retry once.

## After feedback → iterate
LGV's "Top 3 changes" drive the next commit (layout tweaks, add cost line, etc.).
File them as GitHub issues so the loop is auditable.
