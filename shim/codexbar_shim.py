#!/usr/bin/env python3
"""
CodexBar R1 Shim
================
A token-gated, HTTPS-friendly aggregating proxy that puts your CodexBar usage
on a Rabbit R1.

CodexBar ships a bundled CLI with a local JSON server (`codexbar serve`) that
exposes /usage and /cost. That server (v1) binds to 127.0.0.1 only, with no
auth, no TLS, no CORS, and it rejects non-loopback Host headers. A Rabbit R1
Creation is a WebView on the public internet (fronted by Tailscale Funnel), so
it cannot talk to that directly.

This shim sits next to CodexBar on the HUB machine and adds the missing pieces:
  • remote reach (publish via Tailscale Funnel)
  • a bearer token (the only secret, carried in the install QR URL)
  • CORS headers (the WebView fetch needs them)
  • Host-header rewrite (so codexbar serve accepts the forwarded request)
  • fan-out: it also queries OTHER machines' codexbar serve over the tailnet
    and merges everything into one response tagged by machine.

  R1 Creation
    -> Tailscale Funnel (https :443)
      -> this shim (127.0.0.1:8088)
        -> codexbar serve on the hub        (127.0.0.1:8080, loopback)
        -> codexbar serve on each peer       (http://<peer-tailnet>:8080)

Configure with environment variables (see .env.example):
  CODEXBAR_SHIM_TOKEN   required   shared secret
  CODEXBAR_UPSTREAMS    json       {"M4":"http://127.0.0.1:8080","M1":"http://m1:8080"}
  CODEXBAR_PROVIDER     default    "both"  (codex + claude)
  CODEXBAR_SHIM_HOST    default    127.0.0.1
  CODEXBAR_SHIM_PORT    default    8088

Credits:
  • CodexBar + its `serve` CLI — Peter Steinberger (@steipete)  https://github.com/steipete/CodexBar
  • Rabbit R1 / creations stack — rabbit  https://github.com/rabbit-hmi-oss/creations-sdk
This project is unofficial and not affiliated with or endorsed by either.
"""
from __future__ import annotations

import json
import os
import pathlib
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse

# ----------------------------------------------------------------------------
TOKEN = os.environ.get("CODEXBAR_SHIM_TOKEN", "")
UPSTREAMS = json.loads(os.environ.get("CODEXBAR_UPSTREAMS", '{"M4":"http://127.0.0.1:8080"}'))
DEFAULT_PROVIDER = os.environ.get("CODEXBAR_PROVIDER", "both")
BIND_HOST = os.environ.get("CODEXBAR_SHIM_HOST", "127.0.0.1")
BIND_PORT = int(os.environ.get("CODEXBAR_SHIM_PORT", "8088"))
CREATION_DIR = pathlib.Path(__file__).resolve().parent.parent / "creation"

if not TOKEN:
    raise SystemExit("Set CODEXBAR_SHIM_TOKEN (e.g. `openssl rand -hex 16`).")

app = FastAPI(title="CodexBar R1 Shim", docs_url=None, redoc_url=None)

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, content-type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
}


def _token_ok(request: Request) -> bool:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer ") and auth[7:] == TOKEN:
        return True
    return request.query_params.get("k", "") == TOKEN


def _host_of(url: str) -> str:
    # codexbar serve rejects non-loopback Host headers; forward a Host it accepts.
    return url.split("://", 1)[-1].rstrip("/")


async def _fetch(client: httpx.AsyncClient, base: str, path: str, provider: str):
    r = await client.get(
        f"{base.rstrip('/')}{path}",
        params={"provider": provider},
        headers={"Host": _host_of(base), "Accept": "application/json"},
    )
    r.raise_for_status()
    return r.json()


async def _aggregate(path: str, provider: str) -> dict:
    machines, errors = {}, {}
    async with httpx.AsyncClient(timeout=20) as client:
        for name, base in UPSTREAMS.items():
            try:
                machines[name] = await _fetch(client, base, path, provider)
            except Exception as e:  # noqa: BLE001 — report, don't crash the whole view
                errors[name] = str(e)
    return {
        "machines": machines,
        "errors": errors,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


@app.options("/{_:path}")
async def preflight(_: str):
    return Response(status_code=204, headers=CORS)


@app.get("/health")
async def health():
    return JSONResponse({"ok": True, "machines": list(UPSTREAMS)}, headers=CORS)


@app.get("/usage")
async def usage(request: Request):
    if not _token_ok(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=CORS)
    provider = request.query_params.get("provider", DEFAULT_PROVIDER)
    return JSONResponse(await _aggregate("/usage", provider), headers=CORS)


@app.get("/cost")
async def cost(request: Request):
    if not _token_ok(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=CORS)
    provider = request.query_params.get("provider", DEFAULT_PROVIDER)
    return JSONResponse(await _aggregate("/cost", provider), headers=CORS)


@app.get("/r1-sdk.js")
async def sdk():
    # Official-contract SDK wrappers. No secrets → ungated (same-dir for the Creation).
    f = CREATION_DIR / "r1-sdk.js"
    return FileResponse(f, media_type="application/javascript") if f.exists() \
        else PlainTextResponse("r1-sdk.js missing", 404)


@app.get("/")
async def root(request: Request):
    if not _token_ok(request):
        return PlainTextResponse("unauthorized", status_code=401)
    index = CREATION_DIR / "index.html"
    return FileResponse(index) if index.exists() else PlainTextResponse("creation/index.html missing", 404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=BIND_HOST, port=BIND_PORT, log_level="info")
