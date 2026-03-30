#!/usr/bin/env python3
"""ExaFree proxy client (for https://exa.chengtx.vip)

Purpose
- Provide a small, explicit CLI to call ExaFree proxy endpoints:
  /search /answer /contents /findSimilar /research/v1
- Designed for testing + integration glue around search-layer.

Auth
- Provide API key via one of:
  - --api-key
  - env EXA_API_KEY
  - env EXA_FREE_API_KEY

Base URL
- --base-url (default: env EXA_BASE_URL / EXA_FREE_BASE_URL / https://exa.chengtx.vip)

Notes
- We try Authorization: Bearer first; if 401/403, retry with x-api-key.
- We keep output as raw JSON (pretty-printed) for inspectability.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print(
        json.dumps(
            {
                "error": "python dependency missing: requests",
                "fix": "Create a venv and install requests, e.g. python3 -m venv .venv && . .venv/bin/activate && pip install requests",
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    raise SystemExit(1)


def _pick_base_url(cli: str | None) -> str:
    if cli:
        return cli.rstrip("/")
    return (
        os.environ.get("EXA_BASE_URL")
        or os.environ.get("EXA_FREE_BASE_URL")
        or "https://exa.chengtx.vip"
    ).rstrip("/")


def _pick_key(cli: str | None) -> str | None:
    return cli or os.environ.get("EXA_API_KEY") or os.environ.get("EXA_FREE_API_KEY")


def _post_json(url: str, api_key: str | None, payload: dict, timeout: int = 30, retries: int = 2):
    """POST JSON with auth fallback + small retries (for flaky proxy)."""
    headers_bearer = {"Content-Type": "application/json"}
    headers_xkey = {"Content-Type": "application/json"}
    if api_key:
        headers_bearer["Authorization"] = f"Bearer {api_key}"
        headers_xkey["x-api-key"] = api_key

    last_exc = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=headers_bearer, json=payload, timeout=timeout)
            if r.status_code in (401, 403) and api_key:
                r = requests.post(url, headers=headers_xkey, json=payload, timeout=timeout)
            return r
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(0.6 * (2**attempt))
                continue
            raise


def _get(url: str, api_key: str | None, timeout: int = 30):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return requests.get(url, headers=headers, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--api-key", default=None)

    sub = ap.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--num", type=int, default=5)
    p_search.add_argument("--type", default="auto")

    p_answer = sub.add_parser("answer")
    p_answer.add_argument("query")
    p_answer.add_argument("--num", type=int, default=5)

    p_contents = sub.add_parser("contents")
    p_contents.add_argument("--ids", nargs="+", required=True)
    p_contents.add_argument("--text", action="store_true")

    p_sim = sub.add_parser("findSimilar")
    p_sim.add_argument("url")
    p_sim.add_argument("--num", type=int, default=5)

    p_rlist = sub.add_parser("research_list")
    p_rcreate = sub.add_parser("research_create")
    p_rcreate.add_argument("query")

    args = ap.parse_args()

    base = _pick_base_url(args.base_url)
    key = _pick_key(args.api_key)

    if args.cmd == "search":
        r = _post_json(
            f"{base}/search",
            key,
            {"query": args.query, "num_results": args.num, "type": args.type},
        )
    elif args.cmd == "answer":
        r = _post_json(
            f"{base}/answer",
            key,
            {"query": args.query, "num_results": args.num},
        )
    elif args.cmd == "contents":
        r = _post_json(
            f"{base}/contents",
            key,
            {"ids": args.ids, "text": bool(args.text)},
        )
    elif args.cmd == "findSimilar":
        r = _post_json(
            f"{base}/findSimilar",
            key,
            {"url": args.url, "num_results": args.num},
        )
    elif args.cmd == "research_list":
        r = _get(f"{base}/research/v1", key)
    elif args.cmd == "research_create":
        r = _post_json(
            f"{base}/research/v1",
            key,
            {"query": args.query},
            timeout=60,
        )
    else:
        ap.error("unknown cmd")

    out = {
        "ok": bool(r.status_code and int(r.status_code) < 400),
        "status": r.status_code,
        "url": getattr(r, "url", None),
        "contentType": r.headers.get("content-type"),
        "text": None,
        "json": None,
    }

    text = r.text or ""
    out["text"] = text[:2000] if text else ""
    if (r.headers.get("content-type") or "").startswith("application/json"):
        try:
            out["json"] = r.json()
        except Exception:
            pass

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
