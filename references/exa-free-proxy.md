# ExaFree proxy (exa.chengtx.vip) — endpoint notes

This workspace uses an Exa-compatible proxy ("ExaFree") hosted at:

- Base: `https://exa.chengtx.vip`

Verified endpoints (from `/openapi.json`):

- `POST /search`
- `POST /answer`
- `POST /contents`
- `POST /findSimilar`
- `GET /research/v1`
- `POST /research/v1`

Auth headers (both accepted by the proxy):

- `Authorization: Bearer <key>`
- `x-api-key: <key>`

Notes

- Some endpoints may be flaky under Cloudflare (occasional `SSLEOFError`), so clients should retry with backoff.
- MCP at `/mcp/` is currently blocked by Cloudflare with HTTP 421 "Invalid Host header" (as of 2026-03-16).
