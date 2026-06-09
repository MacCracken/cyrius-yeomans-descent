# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.0] — 2026-06-09

M1 close — the binary now opens a port, walks the Telnet protocol,
negotiates options, runs a real login flow, reaps idle clients, and
surfaces loop observability, all over the single-thread epoll loop and
2.5 s tick from 0.1.0. Combat / world / verbs remain empty; the wire and
the heartbeat are complete.

### Added

- **M1-C — Telnet IAC parser** (`src/telnet.cyr`). Pure, side-effect-free
  RFC 854 §11.2 state machine (DATA / IAC / OPT / SB / SB_IAC). `telnet_feed`
  consumes one wire byte and emits EV_NONE / EV_DATA / EV_SB; escaped
  `IAC IAC` → literal `0xFF`; malformed subnegotiation recovers to DATA so
  hostile input can't pin the parser. One `TelnetState` per session in the
  reserved `SS_TS` slot. Decoded data bytes flow into a per-session line
  accumulator (`session_on_line`).
- **M1-D — Option negotiation** (RFC 1143 Q-method). Opening salvo
  `IAC WILL ECHO` + `IAC WILL SUPPRESS_GO_AHEAD` on connect, ahead of the
  banner. Per-option us/him Q-state; tracked options (ECHO, SGA) negotiate
  to agreement, everything else naive-refuses (WILL → DONT, DO → WONT). No
  renegotiation loops.
- **M1-E — Login flow scaffold.** MOTD → name prompt → MOTD-2 → command
  prompt. Names are captured (not authenticated — real auth at M6) and
  validated: 2–16 alphanumerics, must start with a letter, reserved handles
  (`system`, `admin`, leading `_`) refused with a re-prompt.
- **M1-F — Idle timeout & graceful disconnect.** Slowloris defense: a
  per-tick sweep reaps sessions silent past 5 minutes (intrusive
  active-session list threaded through `SS_NEXT` / `SS_PREV`). Threshold
  overridable via the `YD_IDLE_MS` env var for testing / ops. EOF / RST /
  write-error teardown drains in-flight tx best-effort.
- **M1-G — Benchmark harness** (`benches/bench_telnet.bcyr`). IAC-parser
  hot path; M1-close baseline ≈ 6 ns/byte mixed traffic, ≈ 5 ns/byte pure
  data. Re-run at every minor through 1.0 (roadmap M9-C).
- **M1-H — Observability.** `@stats` admin verb surfaces live connections,
  sessions logged in, ticks since boot, and tick-drift p99 (ms, over a
  512-sample ring). Becomes a Joshua input at M8.
- Test suite grown to 52 unit assertions across the parser, Q-method
  negotiation, name validation, and the idle predicate
  (`tests/cyrius-yeomans-descent.tcyr`).

### Changed

- Toolchain pin bumped `6.0.1` → `6.1.17` (`cyrius.cyml [package].cyrius`).
- The M1-B CRLF echo stub is now the `PHASE_CMD` placeholder behind the
  login gate, retained as a regression baseline until the M2 verb parser
  replaces it.

## [0.1.0] — 2026-05-24

First tag. Greenfield scaffold + the three load-bearing design ADRs +
the first slice of M1 (event-loop listener through per-connection
sessions, M1-A and M1-B). Echo stub on the wire; Telnet parser and
verb dispatch land at M1-C / M2.

### Added

- Project scaffold via `cyrius init` — `cyrius.cyml` manifest, `src/main.cyr`,
  `src/test.cyr`, `tests/cyrius-yeomans-descent.{tcyr,bcyr,fcyr}`,
  full first-party doc tree (`docs/adr/`, `docs/architecture/`,
  `docs/development/`, `docs/guides/`, `docs/examples/`).
- ADR 0001 — tick-based combat over real-time cooldowns. 2.5 s server-wide
  Combat Tick; hidden 1d20 + DEX-modifier vs AC rolls per tick.
- ADR 0002 — raw TCP / Telnet as the transport. Browser clients ride
  external Telnet-over-WebSocket bridges; we don't speak WebSocket natively.
- ADR 0003 — single-thread event loop for connection concurrency.
  Rules out fork-per-accept (cannot express shared world state) and
  thread-per-accept (mutex audit surface across every world-state mutation).
- `docs/architecture/overview.md` — system design: classes, parser shape,
  zones, transport.
- `docs/development/roadmap.md` — milestone plan M0 → M9, sub-bites under
  each milestone, v1.0 criteria, open-ADR queue.
- `docs/development/state.md` — live-state snapshot template; refreshed
  every release.
- M1-A — event-loop skeleton (`src/server.cyr`). Non-blocking listener
  via `lib/net.cyr`; `epoll`-shape multiplex; absolute-time tick scheduling
  with drift-resistant catch-up; SIGINT / SIGTERM shutdown via `signalfd`
  in the same epoll set. No-op `advance_tick()` placeholder for M4.
- M1-B — per-connection session struct (`src/session.cyr`). Heap-alloc
  via `lib/freelist.cyr` at accept, freed at disconnect per ADR 0003.
  Holds: fd, login phase, rx line buffer (4 KB), tx queue (4 KB),
  last-activity timestamp, and stub slots for the Telnet parser state
  (M1-C) and player id (M6). EPOLLOUT armed on demand when a write
  would block; disarmed when the tx queue drains. Echo stub processes
  complete CRLF lines as a sanity check pending the M1-C parser.
- CLI: `serve [port]` opens the listener (default 4000); `version` prints
  the version string; `help` shows usage.

### Notes

- Validated locally on Linux x86_64: 32-client concurrent fanout green
  (banner delivered + per-client echo round-trip); 100-line round-trip on
  a single session byte-exact; SIGINT shutdown clean (exit 0). Iron
  validation deferred until M1 closes.
- Binary: ~83 KB (`CYRIUS_DCE=1 cyrius build`).
