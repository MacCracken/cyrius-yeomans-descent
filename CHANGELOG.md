# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.4.0] — 2026-06-09

M3 — the world becomes physical. The server loads CYML zone files at boot
into an in-memory room tree, places players in it at login, and gives them
movement, ANSI-rendered rooms, inspection, and room-scoped social verbs.
Two players can walk the authored 21-room starter zone (the Hub) and see
each other's arrivals, departures, and speech in real time. Items, mobs,
and combat are still ahead (M4-M5); the world they move through is here.

### Added

- **ADR 0005 — Zone file format.** Decided **CYML** (`lib/cyml.cyr`): a
  TOML header + markdown prose body per entry maps onto a DikuMUD room
  (structured fields + description blob) using an already-fuzzed
  first-party parser. One file per zone per entity kind
  (`<zone>.rooms/.mobs/.objs.cyml`), mirroring `.wld`/`.mob`/`.obj`, each
  ≤ 32 entries (the parser's per-file ceiling).
- **M3-B — Zone loader + world tree** (`src/world.cyr`). Parses a rooms
  file at boot, interns ids, keeps prose zero-copy into the persistent
  CYML buffer, resolves every `exit_<dir>` to a room index, and **rejects
  dangling exits at boot** (a bad graph fails to start, not mid-walk). An
  optional `start` header field names the spawn room. Loading is once at
  startup, never in the tick (ADR 0003).
- **M3-C — Movement.** `n`/`s`/`e`/`w`/`u`/`d` traverse exits; auto-look on
  arrival; "you can't go that way" for closed directions. Departure and
  arrival lines broadcast to onlookers in the source / destination rooms
  (a published `g_epfd` lets the session layer flush them immediately).
- **M3-D — ANSI room rendering.** Bold-yellow title, default-weight prose,
  cyan exits, bold-green player names — raw SGR emitted inline rather than
  pulling the client-side `darshana` lib (kept the zero-external-deps
  stance; `\x1b` is a one-byte ESC in Cyrius strings).
- **M3-E — Inspection.** `look` / `exits` render the current room;
  `examine` inspects self or a player present in the room (the M2
  resolver's first live scope); `inventory` is empty until items land.
- **M3-F — Social presence.** `say` / `emote` broadcast to the room (the
  actor sees their own line); `tell` is a directed cross-room message;
  `who` lists every connected player and their room.
- **M3-G — The Hub.** A 21-room starter zone
  (`data/zones/hub.rooms.cyml`): the Rusted Flagon tavern hub plus three
  loops — the Cinder Market, the Foundry, and the drowned Undercroft.
  Fully connected, every exit bidirectional, walkable end to end. Doubles
  as the v1.0 demo content.
- Unit suite grown 154 → 174 assertions (zone loader: interning, exit
  resolution both directions, `start`, dangling / wrong-kind / missing-file
  rejection, `verb_to_dir`). Self-contained fixtures under `tests/fixtures/`.

### Changed

- `cmd_dispatch` (`src/session.cyr`) replaces every M3-pending placeholder
  with real handlers: movement, room display, examine, and the social
  verbs now act on the world. The M2-era placeholders remain only as the
  graceful no-zone-loaded fallback.
- New `[deps]` stdlib: `cyml`, `toml` (zone-file parsing). Still no
  external (non-stdlib) deps — T.Ron (M6) and Joshua (M8) are the first.
- The session struct gains `SS_ROOM` (current room index, -1 until login);
  `cmd_serve` loads the Hub at startup (a load failure is non-fatal — the
  server runs roomless with the placeholder verbs).

## [0.3.0] — 2026-06-09

M2 — the verb-noun parser. Lines typed at the command prompt are now
tokenized, resolved to a canonical verb, and decomposed into direct
object / preposition / indirect object with `all.X` / `N.X` qualifiers.
The echo stub behind the login gate is gone; `cmd_on_line` routes through
the parser. The world the verbs act on still lands at M3 — until then the
handlers acknowledge the *parse* rather than fake world state. Pure and
fuzz-clean: 100k random inputs, no crash / hang / unbounded growth.

### Added

- **M2-A — Tokenizer** (`src/parser.cyr`). Whitespace-split (space / tab)
  with double-quote grouping for multi-word objects and lowercase
  normalization. Tokens are length-counted copies in a norm buffer —
  never NUL-terminated — so an embedded NUL is content, not a terminator.
  One shared `Parser` (lazily allocated) serves every session; parsing is
  synchronous and never spans calls.
- **M2-B — Verb table + aliases.** The canonical v1.0 verb set (movement,
  inspection, item manipulation, combat, social, session) resolves the
  first token to a `Verb` id; aliases fold in (`n`→north, `l`→look,
  `i`/`inv`→inventory). `verb_name` / `verb_is_movement` keep the taxonomy
  in one place.
- **M2-C — Direct-object resolution.** DikuMUD-style keyword prefix
  matching against an abstract scope (array of keyword strings). A unique
  match returns its index; zero → `RES_NOTFOUND`; many → `RES_AMBIGUOUS`.
  The live scope (room + inventory + equipment) is wired at M3 — the
  matcher is the deliverable, exercised here with synthetic scopes.
- **M2-D — Preposition / indirect-object.** Preposition table
  (`in`/`on`/`to`/`from`/`at`/`with`); the first preposition after the
  verb splits the line into direct- and indirect-object phrases, each
  resolved on its head noun (`give monoblade to kiran`,
  `put rations in pack`, `get all from corpse`).
- **M2-E — Qualifiers.** `all.X` (every match), `N.X` (the Nth match in
  deterministic scan order), and bare `all` (everything in scope).
  `qual_parse` splits the qualifier off the noun; `resolve_all` /
  `resolve_nth` collect against the scope under a caller-supplied cap.
- **M2-F — Fuzz harness** (`fuzz/parser_fuzz.fcyr`, run by `cyrius fuzz`).
  Deterministic xorshift PRNG, 100k iterations of parser-significant
  random bytes plus directed adversarial cases. Every iteration asserts:
  token count ≤ cap, norm buffer ≤ cap, each token inside the buffer,
  every parse-result index in range, `resolve_all` never overruns. One
  reused parser proves no per-line leak.
- Unit suite grown 52 → 154 assertions (tokenizer, verb table, resolution,
  preposition split, qualifiers).

### Changed

- `cmd_on_line` (`src/session.cyr`) replaces the M1-E echo stub with full
  verb dispatch. Social verbs echo the case-preserved message; object
  verbs reflect the parsed structure; movement / look / inventory return
  M3-pending placeholders; unknown verbs prompt `help`.
- **`quit` now disconnects.** A new `SS_QUIT` session flag, set by the
  verb and checked in `dispatch_session` after the goodbye flushes, tears
  the session down cleanly.
- The login welcome no longer advertises the echo stub — it points new
  players at `help`.

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
