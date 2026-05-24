# 0002 — Raw TCP / Telnet as the transport

**Status**: Accepted
**Date**: 2026-05-24

## Context

A network multi-user game has to pick a transport. The realistic options:

1. **Raw TCP with Telnet line discipline** — the historical MUD protocol. Works with Mudlet, CMUD, tintin++, and every Telnet client ever shipped. Connects through a browser via WebSocket-to-Telnet bridges.
2. **WebSockets natively** — pleasant for browser clients; locks out every existing MUD client and forces us to ship our own.
3. **HTTP long-poll / SSE** — request/response is fundamentally the wrong shape for a multiplayer real-time text channel.
4. **Custom binary protocol** — buys us nothing the text channel doesn't already provide.

The design doc commits to "accurately reflecting the DikuMUD and LPMud era," which biases hard toward (1). The ecosystem of MUD clients is rich, mature, and free.

## Decision

The server speaks **raw TCP with Telnet line discipline** as its primary transport. Browser clients are supported via an external Telnet-over-WebSocket wrapper — we do not ship a web client of our own, and we do not natively speak WebSocket.

In scope: line-oriented Telnet (CR/LF), basic option negotiation (echo on/off for passwords, terminal-type discovery), ANSI color sequences inline in the text stream.

Out of scope: MUD-specific protocol extensions (MCCP, MSP, MXP, GMCP) for v1.0. May be added post-v1.0 once the base game is stable.

## Consequences

**Positive**

- Every existing MUD client works on day one. The community already knows how to connect.
- No browser-client engineering burden — we own the server, the community owns the clients.
- Telnet is dead simple to implement, debug, and test. `telnet host port` is a working repro tool.
- Aligns with [`first-party-standards § Own the Stack`](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-standards.md#own-the-stack) — Cyrius stdlib speaks raw sockets natively; no external lib.

**Negative**

- Telnet's security story is "there isn't one" — credentials cross the wire in plaintext. We rely on the operator wrapping the listener in TLS (`stunnel`, reverse proxy) for any non-LAN deployment. **This is a load-bearing operational invariant; see [`SECURITY.md`](../../SECURITY.md).**
- We inherit Telnet's quirks: NVT semantics, option-negotiation edge cases, clients that send malformed sequences. Every input path needs bounds checking. ([`first-party-standards § Security Hardening`](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-standards.md#security-hardening-required-before-every-release).)
- Browser players have an extra hop (Telnet-over-WebSocket bridge) to set up.

**Neutral**

- Future protocol extensions (MCCP for compression, GMCP for client-side automation) are additive — they don't break the base Telnet contract.

## Alternatives considered

- **Native WebSockets only** — rejected: breaks compatibility with the entire existing MUD client ecosystem, which is the explicit aesthetic target.
- **Both Telnet and WebSocket natively** — deferred. The bridge pattern covers browser users without doubling the protocol surface; we can revisit if the bridge proves operationally painful.
- **Custom protocol** — rejected: zero ecosystem, no debugging tools, no benefit over the text channel we already have.
