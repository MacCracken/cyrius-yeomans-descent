# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.2.0** — M1 close, 2026-06-09. The listener now walks the Telnet
protocol (M1-C), negotiates options via the RFC 1143 Q-method (M1-D),
runs a real login flow (M1-E), reaps idle clients (M1-F), is benchmarked
(M1-G), and surfaces loop observability via the `@stats` verb (M1-H) —
all over the single-thread epoll loop + 2.5 s tick from 0.1.0. Combat,
world, and the verb parser are still empty; the wire and the heartbeat
are complete.

## Toolchain

- **Cyrius pin**: `6.1.17` (`cyrius.cyml [package].cyrius`)

## Source layout

```
src/
  main.cyr       argv dispatch (`serve [port]` / `version` / `help`);
                 include order telnet → session → server
  telnet.cyr     RFC 854 IAC parser + RFC 1143 Q-method negotiation
                 (M1-C/M1-D); pure, no I/O; one TelnetState per session
  session.cyr    Session struct (136 B), rx scratch, decoded-line
                 accumulator, tx queue, login flow + name validation
                 (M1-E), idle predicate (M1-F), @stats int formatting
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler,
                 epoll dispatch, active-session list + idle sweep (M1-F),
                 observability counters + render_stats (M1-H)
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

tests/
  cyrius-yeomans-descent.tcyr   unit suite (52 assertions)
  cyrius-yeomans-descent.bcyr   scaffold-family placeholder (real benches
                                live in benches/ — see below)
  cyrius-yeomans-descent.fcyr   fuzz stub (no-op until M2-F)

benches/
  bench_telnet.bcyr             IAC-parser hot-path baseline (M1-G);
                                `cyrius bench` auto-discovers benches/
```

Binary at `build/cyrius-yeomans-descent` (~112 KB with `CYRIUS_DCE=1`).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test tests/cyrius-yeomans-descent.tcyr` — 52 unit assertions:

- **telnet** — data passthrough, escaped `IAC IAC`, naive-refuse,
  single-byte commands, subnegotiation collection, escaped-IAC-in-SB,
  malformed-SB recovery, mixed data/negotiation streams
- **negotiation** — announce salvo shape, DO/DONT confirmation of the
  announce, untracked-option refuse, cold DO SGA acceptance
- **login** — name length bounds, leading-letter rule, alphanumeric
  rule, reserved-handle refusal (case-insensitive)
- **idle** — the `session_is_idle` threshold predicate

End-to-end smokes validated locally on Linux x86_64 at the 0.2.0 cut:

- opening salvo (IAC WILL ECHO / WILL SGA) precedes the banner; client
  DO-confirmation draws no renegotiation loop
- full login: reserved/underscore names refused + re-prompted, valid
  name → welcome + command prompt; `@stats` renders the status block
- `YD_IDLE_MS=1000` → idle client gets the goodbye line and is
  disconnected on the next tick (~1.9 s)
- 32-way concurrent connect → negotiate → log in → command → disconnect;
  sessions fully reclaimed afterward (no leak); tick p99 drift < 10 ms

Benchmark: `cyrius bench` → telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte
(pure data), 16 M iterations, stable.

`cyrius test src/test.cyr` exits 0 (CI uses this explicit form — see
`.github/workflows/ci.yml`; the pin reads from `cyrius.cyml`).

## Dependencies

Direct (declared in `cyrius.cyml`):

- **stdlib** — string, fmt, alloc, io, vec, str, syscalls, assert, bench, args, net, chrono, result, tagged, fnptr, freelist

No external (non-stdlib) deps yet. T.Ron lands at M6, Joshua at M8 — see
[roadmap M6](roadmap.md#m6--persistence-via-tron-v070) and [M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

**No active cycle.** M1 closed at 0.2.0. Pick up the next slot per the
boot guide below.

---

## Next-agent boot guide

You are picking up at **M2-A — tokenizer** ([roadmap.md M2 sub-bites](roadmap.md#m2--verb-noun-parser-v030)). M2 is the verb-noun parser: tokenizer → verb table → direct-object resolution → preposition/indirect-object → qualifiers → fuzz harness, shipping at v0.3.0.

### What's already built (0.2.0)

- **Telnet wire** — `src/telnet.cyr` `telnet_feed(ts, b)` is a pure
  RFC 854 parser emitting EV_NONE / EV_DATA / EV_SB; negotiation replies
  queue in the state's tx buffer (Q-method, ECHO + SGA preferred). One
  `TelnetState` per session in `SS_TS`, alloc'd/freed with the session.
- **Decoded-line plumbing** — `session_consume_rx` feeds raw rx bytes
  through the parser, copies negotiation replies into the session tx
  queue, and routes EV_DATA bytes into the per-session line accumulator.
  Complete lines (CR / CRLF / lone-LF) dispatch to `session_on_line`,
  which branches on phase.
- **Login flow** — `PHASE_NAME` → `PHASE_CMD`. `login_on_name` validates
  and captures the name into `SS_NAME_BUF`; `cmd_on_line` is where M2
  plugs the verb parser in (it currently echoes + handles `@stats`).
- **Idle sweep** — active sessions are on an intrusive list
  (`SS_NEXT`/`SS_PREV`, head `g_session_head`); `sweep_idle` reaps them
  each tick past `g_idle_timeout_ms` (default 300000, `YD_IDLE_MS` env
  override).
- **Observability** — `g_session_count`, `g_tick_count`, the drift ring,
  `count_logged_in()`, and `render_stats()` back the `@stats` verb.

### What M2-A should do

Create `src/parser.cyr` (or similar): a tokenizer that splits a command
line on whitespace with quote handling for multi-word direct objects and
lowercase normalization. Its input is the `buf`/`len` handed to
`cmd_on_line`; its output is a token vector the M2-B verb table consumes.
Keep it pure (no session I/O) so it fuzzes cleanly at M2-F. Reserve the
`SS_PLAYER` slot for M6; the parser operates on the line, not the session.

### Reference

- **agora's command path** (`/home/macro/Repos/agora/src/main.cyr`
  around the `session_execute` / tokenizer region) is the closest
  template — adapt to our single-thread-shared model.
- Verb table + resolution semantics: [roadmap.md M2](roadmap.md#m2--verb-noun-parser-v030).

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test tests/cyrius-yeomans-descent.tcyr   # 52 assertions
cyrius bench                                     # IAC parser baseline
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — log in, type @stats, ^C
```

### Open ADRs

Three decisions are queued ahead of their consumer milestones — see
[roadmap.md § Open ADRs](roadmap.md#open-adrs). None block M2.
