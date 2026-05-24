# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-05-24

## Version

**0.1.0** — first tag, 2026-05-24. Greenfield scaffold + three load-bearing
ADRs (0001 / 0002 / 0003) + the first slice of M1 — event loop (M1-A)
and per-connection sessions (M1-B). Echo stub on the wire; Telnet parser
(M1-C) and verb dispatch (M2) are the next slots.

## Toolchain

- **Cyrius pin**: `6.0.1` (in `cyrius.cyml [package].cyrius`)

## Source

- `src/main.cyr` — argv dispatch (`serve [port]` / `version` / `help`)
- `src/server.cyr` — event loop, listener bring-up, signalfd shutdown,
  tick scheduler, per-session epoll dispatch
- `src/session.cyr` — per-connection Session struct; rx accumulator,
  tx queue, drain helpers, M1-B echo stub for complete CRLF lines
- `src/test.cyr` — top-level test entrypoint
- Binary at `build/cyrius-yeomans-descent` (~83 KB with `CYRIUS_DCE=1`)

Next-up module surface (per [roadmap M1-C](roadmap.md#m1--tcp--telnet-listener-v020)):
`src/telnet.cyr` — RFC 854 IAC state machine, RFC 1143 Q-method option
negotiation, naive-refuse first-cut.

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

- `tests/cyrius-yeomans-descent.tcyr` — primary suite (smoke; passes on `cyrius test`)
- `tests/cyrius-yeomans-descent.bcyr` — benchmark stub (no-op)
- `tests/cyrius-yeomans-descent.fcyr` — fuzz stub

End-to-end smokes validated locally on Linux x86_64 at 0.1.0 cut:

- single-client banner + echo round-trip
- 32-way concurrent fanout (banner delivered + per-client echo correct)
- 100-line single-session round-trip (1490 B in / 1490 B out, byte-exact)
- 5× rapid connect/close cycles (no leak, no crash)
- SIGINT → clean shutdown, exit 0

## Dependencies

Direct (declared in `cyrius.cyml`):

- stdlib — string, fmt, alloc, io, vec, str, syscalls, assert, bench,
  args, net, chrono, result, tagged, fnptr, freelist

No external (non-stdlib) deps yet. T.Ron and Joshua integrations land later — see [roadmap M6](roadmap.md#m6--persistence-via-tron-v070) and [M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

Nothing in flight. Next slot is **M1-C — Telnet IAC parser**
([roadmap.md](roadmap.md#m1--tcp--telnet-listener-v020)) — RFC 854
state machine (DATA / IAC / OPT / SB / SB_IAC), pure / side-effect-free,
fed by `session_on_readable` one byte at a time. M1-D follows with
RFC 1143 Q-method option negotiation.
