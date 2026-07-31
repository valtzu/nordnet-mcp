---
name: nordnet-portfolio
description: >
  Connects an agent to a user's Nordnet brokerage account (Sweden, Norway, Denmark, or
  Finland) for read-only portfolio data — accounts, positions, trades, balances,
  orders, and instrument lookup — by registering the dockerized nordnet-mcp MCP
  server, no Python/uv install required, only Docker. Use this skill whenever the user
  asks to check their Nordnet holdings, positions, trades, balance, buying power, or
  portfolio value, wants to look up or search for an instrument/stock via Nordnet, or
  asks to "connect", "log in", or "set up" access to their Nordnet account — even if
  they don't mention MCP, Docker, or this skill by name. Also use it if a Nordnet tool
  call comes back with a 401/session-expired error, since re-running the login step
  fixes that.
compatibility: Requires Docker (running daemon, image pulled from ghcr.io). Works with
  any MCP-capable agent/host, not just Claude — this is a standard stdio MCP server.
  Registration mechanics differ by host; see "Step 2" for the common ones and a
  generic fallback for anything else.
---

# Nordnet portfolio access

This skill gets an agent talking to a real Nordnet account with zero local install
beyond Docker — the whole server (Python runtime, dependencies, everything) lives in
the `ghcr.io/hpasic/nordnet-mcp` image. You never `pip install` or `uv sync` anything
here; you only ever `docker run` it.

Read-only by design: it can list accounts, positions, trades, balances, orders, and
look up instruments, but it cannot place trades or move money.

## When to use this

Trigger this skill for anything Nordnet-portfolio-shaped: "what's in my Nordnet
account", "how did my portfolio do this week", "look up ISIN SE0000108656 on
Nordnet", "connect my Nordnet account", or a Nordnet tool call failing with a 401.
Don't trigger it for general investing questions unrelated to the user's own Nordnet
account — this skill is about *connecting to and reading* their account, not general
advice (it also cannot give personalized financial advice; if asked, say so).

## Step 1 — Check whether the server is already registered

If `nordnet` (or similarly named) tools already appear in your available tools, skip
straight to Step 3. Otherwise continue.

If you're running in Claude Code and this repo was installed as a **plugin** (via
`/plugin marketplace add hpasic/nordnet-mcp` then `/plugin install
nordnet-mcp@nordnet-mcp-marketplace`), the MCP server is already registered
automatically through the plugin's bundled `.mcp.json` — the user picked the market
host during install, so there's nothing to do here either; skip to Step 3. The manual
registration in Step 2 is only for hosts/setups that don't go through that plugin
mechanism.

## Step 2 — Register the MCP server via Docker

First confirm Docker is available:

```bash
docker --version
```

If that fails, tell the user this skill needs Docker Desktop (or the Docker Engine)
installed and running, and stop here — do not fall back to a local Python install,
that defeats the point of this skill.

Ask the user which Nordnet market their account is on, if not already obvious from
context (e.g. their locale, language, or how they refer to their account). Map it to
a host:

| Market   | `NORDNET_HOST`      |
|----------|---------------------|
| Sweden   | `public.nordnet.se` |
| Norway   | `public.nordnet.no` |
| Denmark  | `public.nordnet.dk` |
| Finland  | `public.nordnet.fi` |

This must match the market of the Nordnet **mobile app** they'll use to approve
login — an app registered in the wrong market will silently ignore the QR/login
request later.

The server itself is nothing more than this one command — everything below is just
how to hand that command to whatever agent/host you're running in:

```bash
docker run --rm -i -e NORDNET_HOST=public.nordnet.se ghcr.io/hpasic/nordnet-mcp:latest
```

Figure out which of these you're operating as, and use the matching method. If none
apply, use the generic fallback at the end.

### Hosts with an MCP-add CLI command (e.g. Claude Code)

```bash
claude mcp add nordnet --scope project -- docker run --rm -i -e NORDNET_HOST=public.nordnet.se ghcr.io/hpasic/nordnet-mcp:latest
```

(`--scope user` instead registers it globally for that user rather than just this
project.) Other CLI-driven agents that expose an equivalent "add MCP server" command
should be given the same underlying `docker run ...` line as the command to register.

### Hosts configured via an MCP JSON config file (Claude Desktop, Cursor, Windsurf, etc.)

Merge this into whichever MCP config file that host reads (e.g.
`claude_desktop_config.json`, `.cursor/mcp.json`, `~/.codeium/windsurf/mcp_config.json`
— the key may be `mcpServers` or `mcp.servers` depending on the host, so check that
host's own docs for the exact key/location):

```json
{
  "mcpServers": {
    "nordnet": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "NORDNET_HOST=public.nordnet.se",
        "ghcr.io/hpasic/nordnet-mcp:latest"
      ]
    }
  }
}
```

The user will need to restart/reload that host app after saving it.

### Generic fallback (any agent that can run a subprocess and speak MCP/JSON-RPC)

If your host has neither of the above, you can drive the server directly: run the
`docker run` command as a long-lived subprocess and speak the MCP stdio protocol
(JSON-RPC messages over stdin/stdout) to it yourself — `initialize`, then
`tools/list`, then `tools/call` as needed. This is exactly what a proper MCP client
integration does under the hood; do this only if your host truly has no built-in MCP
client support.

## Step 3 — Log in

No token setup is required up front. Call the `nordnet_auth` tool (or just call any
Nordnet data tool — a 401 will prompt you to call it). It returns a QR code; tell the
user to scan it with their Nordnet mobile app (the one matching the market chosen in
Step 2) and approve the login there.

- If your host renders MCP Apps, the QR shows as a live image that auto-refreshes;
  once approved, it resolves on its own or you may need to call
  `nordnet_login_poll` (see the tool's own description for host-specific behavior).
- If it only renders as ASCII text (e.g. plain Claude Code), wait for the user to
  say they've scanned and approved it, then call `nordnet_login_poll` yourself to
  finish.
- The session is kept in the server's memory only — it is never written to disk by
  this flow. If the container restarts, the user logs in again; that's expected and
  not a bug.

Once logged in, proceed to whatever Nordnet data the user actually asked for.

## Troubleshooting

- **`NEXT_INVALID_SESSION` errors**: add `-e NORDNET_CLIENT_ID=NEXT` to the `docker
  run` args (or config `args`/`env` block) and re-register/restart the server.
- **401 after working previously**: Nordnet sessions expire after a couple of idle
  hours. Just call `nordnet_auth` again — it's a normal re-login, not a failure to
  report as broken.
- **QR scanned but nothing happens**: the Nordnet app's market almost certainly
  doesn't match `NORDNET_HOST`. Re-confirm the market with the user and re-register
  with the corrected host.
