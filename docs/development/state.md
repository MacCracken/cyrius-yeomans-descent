# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-05-24

## Version

**0.1.0** — first tag, 2026-05-24. Greenfield scaffold + three load-bearing
ADRs (0001 combat tick / 0002 raw TCP+Telnet / 0003 single-thread event loop)
+ the first slice of M1: M1-A event loop + M1-B per-connection sessions.
Echo stub on the wire pending the M1-C Telnet parser.

## Toolchain

- **Cyrius pin**: `6.0.1` (`cyrius.cyml [package].cyrius`)

## Source layout

```
src/
  main.cyr       argv dispatch (`serve [port]` / `version` / `help`)
  server.cyr     event loop, listener bring-up, signalfd shutdown,
                 tick scheduler, per-session epoll dispatch
  session.cyr    Session struct (~88 B), rx accumulator, tx queue,
                 drain helpers, M1-B CRLF-line echo stub
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

tests/
  cyrius-yeomans-descent.tcyr   smoke suite
  cyrius-yeomans-descent.bcyr   benchmark stub (no-op until M1-G)
  cyrius-yeomans-descent.fcyr   fuzz stub (no-op until M2-F)
```

Binary at `build/cyrius-yeomans-descent` (~90 KB with `CYRIUS_DCE=1`).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

End-to-end smokes validated locally on Linux x86_64 at 0.1.0 cut:

- single-client banner + echo round-trip
- 32-way concurrent fanout (banner delivered + per-client echo correct)
- 100-line single-session round-trip (1490 B in / 1490 B out, byte-exact)
- 5× rapid connect/close cycles (no leak, no crash)
- SIGINT → clean shutdown, exit 0

`cyrius test src/test.cyr` exits 0. CI uses the explicit form (cyrius 6.0.1
released binary doesn't honor bare `cyrius test` auto-discovery — see
`.github/workflows/ci.yml` comment).

## Dependencies

Direct (declared in `cyrius.cyml`):

- **stdlib** — string, fmt, alloc, io, vec, str, syscalls, assert, bench, args, net, chrono, result, tagged, fnptr, freelist

No external (non-stdlib) deps yet. T.Ron lands at M6, Joshua at M8 — see
[roadmap M6](roadmap.md#m6--persistence-via-tron-v070) and [M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

**No active cycle.** Pickup the next slot per the boot guide below.

---

## Next-agent boot guide

You are picking up at **M1-C — Telnet IAC parser** ([roadmap.md M1 sub-bites](roadmap.md#m1--tcp--telnet-listener-v020-in-progress)). The path to closing M1 at v0.2.0 is M1-C → M1-D → M1-E → M1-F → M1-G → M1-H.

### What's already built (0.1.0)

- **Event loop** — `src/server.cyr` `cmd_serve(port)` opens a non-blocking listener, runs an epoll multiplex over `lib/net.cyr`, ticks every 2.5 s via absolute-time scheduling. SIGINT/SIGTERM via signalfd in the same epoll set.
- **Per-conn sessions** — `src/session.cyr` `Session` struct (88 B) is heap-alloc'd via `lib/freelist.cyr` at accept, freed at disconnect. Rx 4 KB + tx 4 KB buffers. `session_on_readable(s, now)` pulls bytes; `session_consume_rx(s)` walks them line-by-line; `session_drain(s)` writes the tx queue with EAGAIN-aware partial-write handling; `flush_session(epfd, s)` arms/disarms EPOLLOUT to match.
- **Reserved slots** waiting for M1-C through M6:
  - `SS_TS` (offset 72 in `src/session.cyr`) — Telnet parser state pointer; **M1-C owns it**.
  - `SS_LAST_MS` — last-activity timestamp; M1-F idle timeout consumes it.
  - `SS_PLAYER` — player id slot; M6 fills it.
- **Observability primitives already wired** — `g_session_count` (server.cyr) and `g_tick_count`. M1-H just needs to surface them via an admin verb.

### What M1-C should do

Create `src/telnet.cyr` with a pure (no-I/O) RFC 854 §11.2 state machine: DATA → IAC → OPT → SB → SB_IAC. The byte-feed function signature should be something like `telnet_feed(ts, b)` returning an event tag (data byte ready / no-op / subneg complete). Caller is `session_on_readable` (or a new helper between it and `session_consume_rx`), which routes data bytes into the existing rx buffer and discards no-op bytes (IAC command escapes).

`session_new` should allocate a `TelnetState` and store the pointer in `SS_TS`. `session_free` should `fl_free` it.

The M1-B echo stub stays useful as a regression baseline — once M1-C lands, lines from the rx buffer still get echoed, but with IAC sequences correctly consumed mid-stream. Test with `telnet 127.0.0.1 4000` directly — real clients send IAC negotiation salvos on connect.

### Reference

- **agora's `src/telnet.cyr`** (`/home/macro/Repos/agora/src/telnet.cyr`, ~718 lines) is the closest existing template. Same `TelCmd` / `TelOpt` / `TelState` / `TelEvent` shape; same `TS` struct field layout. Pattern is sound; **don't copy verbatim** — adapt to fit our Session struct and our single-thread-shared model (agora forks per-conn, we don't).
- RFC 854: https://datatracker.ietf.org/doc/html/rfc854
- RFC 1143 (Q-method, lands at M1-D): https://datatracker.ietf.org/doc/html/rfc1143

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
./build/cyrius-yeomans-descent serve 4000
# in another terminal: nc / telnet / python — connect, type, see echo, ^C
```

### Open ADRs

Three decisions are queued ahead of their consumer milestones — see [roadmap.md § Open ADRs](roadmap.md#open-adrs). None block M1-C.
