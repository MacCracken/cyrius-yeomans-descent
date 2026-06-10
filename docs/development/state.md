# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.4.0** — M3 close, 2026-06-09. The world is physical. A CYML zone
loader ([ADR 0005](../adr/0005-zone-file-format.md), `src/world.cyr`)
builds an in-memory room tree at boot and rejects dangling exits; players
spawn into it at login and have a location. Movement (`n`/`s`/…) traverses
exits with auto-look and onlooker broadcasts; rooms render in ANSI;
`look`/`examine`/`exits`/`inventory` inspect; `say`/`emote` carry to the
room, `tell` across rooms, `who` lists everyone online. The authored
21-room Hub (`data/zones/hub.rooms.cyml`) is walkable end-to-end by two
players who see each other in real time. Items, mobs, and combat are M4-M5;
the parser (0.3.0), wire (0.2.0), and tick (0.1.0) underneath are intact.

## Toolchain

- **Cyrius pin**: `6.1.17` (`cyrius.cyml [package].cyrius`)

## Source layout

```
src/
  main.cyr       argv dispatch (`serve [port]` / `version` / `help`);
                 include order telnet → parser → world → session → server
  telnet.cyr     RFC 854 IAC parser + RFC 1143 Q-method negotiation
                 (M1-C/M1-D); pure, no I/O; one TelnetState per session
  parser.cyr     M2 verb-noun parser: tokenizer, verb table + aliases,
                 keyword-prefix object resolution, preposition split,
                 all.X / N.X qualifiers; pure, no session I/O
  world.cyr      M3 world tree: CYML zone loader, Room struct (208 B),
                 exit resolution + dangling-ref rejection, verb→dir,
                 room/exit accessors; pure, no session I/O
  session.cyr    Session struct (152 B), rx scratch, decoded-line
                 accumulator, tx queue, login (M1-E) + world entry,
                 M2/M3 dispatch (movement, room render, examine, social),
                 ANSI SGR helpers, SS_QUIT teardown, SS_ROOM location
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler,
                 epoll dispatch, active-session list + idle sweep (M1-F),
                 observability + render_stats (M1-H), zone load at boot,
                 g_epfd + room broadcast / presence / who (M3-C/F)
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

data/zones/
  hub.rooms.cyml                the authored 21-room Hub starter zone (M3-G)
  example.rooms.cyml            3-room schema example (ADR 0005)

tests/
  cyrius-yeomans-descent.tcyr   unit suite (174 assertions)
  cyrius-yeomans-descent.bcyr   scaffold-family placeholder (real benches
                                live in benches/ — see below)
  cyrius-yeomans-descent.fcyr   scaffold-family stub; real fuzz harness in
                                fuzz/ (the toolchain runs fuzz/*.fcyr)
  fixtures/                     zone-loader test fixtures (loop / dangling /
                                wrongkind)

fuzz/
  parser_fuzz.fcyr             M2-F parser fuzz harness (100k inputs);
                               `cyrius fuzz` auto-discovers fuzz/

benches/
  bench_telnet.bcyr             IAC-parser hot-path baseline (M1-G);
                                `cyrius bench` auto-discovers benches/
```

Binary at `build/cyrius-yeomans-descent` (~182 KB with `CYRIUS_DCE=1`;
the cyml / toml parsers add the weight over 0.3.0's 131 KB).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test tests/cyrius-yeomans-descent.tcyr` — 174 unit assertions:

- **telnet** — data passthrough, escaped `IAC IAC`, naive-refuse,
  single-byte commands, subnegotiation collection, escaped-IAC-in-SB,
  malformed-SB recovery, mixed data/negotiation streams
- **negotiation** — announce salvo shape, DO/DONT confirmation of the
  announce, untracked-option refuse, cold DO SGA acceptance
- **login** — name length bounds, leading-letter rule, alphanumeric
  rule, reserved-handle refusal (case-insensitive)
- **tokenize** (M2-A) — split, lowercase, whitespace collapse, tabs,
  quoted multi-word tokens, empty/unterminated quotes, OOB guards
- **verbs** (M2-B) — canonical words, aliases (`l`/`i`/`inv`/directions),
  case-insensitivity, unknown/empty, taxonomy + name round-trip
- **resolve** (M2-C) — unique/prefix match, ambiguity, not-found,
  case-insensitive, `kw_matches` / `resolve_count` primitives
- **prep** (M2-D) — verb/dobj/prep/iobj split, empty-dobj, bare-verb,
  head-noun rule, multi-preposition, empty line
- **qual** (M2-E) — `all.X` / bare `all` / `N.X` / plain parse,
  `parse_uint` / `is_word_all`, `resolve_nth` / `resolve_all` + cap
- **world** (M3-B) — zone load, id interning + lookup, `start` field,
  bidirectional exit resolution, title/prose capture, `verb_to_dir`,
  dangling / wrong-kind / missing-file rejection (fixtures in `tests/fixtures/`)
- **idle** — the `session_is_idle` threshold predicate

Fuzz: `cyrius fuzz` → `fuzz/parser_fuzz.fcyr`, 100k random inputs +
directed adversarial cases, all invariants hold (token/buffer bounds,
index ranges, no `resolve_all` overrun), no crash / hang / leak.

End-to-end smokes validated locally on Linux x86_64 at the 0.4.0 cut:

- the Hub loads (21 rooms); graph check: 0 asymmetric exits, 21/21
  reachable from the `hub.gate` start — walkable end-to-end
- two-player walk: A and B spawn at the gate; A moves and B sees
  `alice heads north`, A sees `bob arrives`; presence (`Also here:`),
  ANSI title/exits, and `look`/`exits` render the live room
- social: `say` / `emote` reach the room (not other rooms), `tell`
  crosses rooms, `who` lists both with room titles, `examine` resolves
  self and a present player
- 0.2.0/0.3.0 wire / parser / idle smokes still hold (M3 is additive)

Benchmark: `cyrius bench` → telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte
(pure data), 16 M iterations, stable (unchanged — parser / world not yet
benched; M9-C locks the wider baseline). Zone load is one-shot at boot,
off the tick path, so it has no steady-state cost.

`cyrius test src/test.cyr` exits 0 (CI uses this explicit form — see
`.github/workflows/ci.yml`; the pin reads from `cyrius.cyml`).

## Dependencies

Direct (declared in `cyrius.cyml`):

- **stdlib** — string, fmt, alloc, io, vec, str, syscalls, assert, bench, args, net, chrono, result, tagged, fnptr, freelist, **cyml, toml** (zone-file parsing, added M3)

No external (non-stdlib) deps yet. T.Ron lands at M6, Joshua at M8 — see
[roadmap M6](roadmap.md#m6--persistence-via-tron-v070) and [M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

**No active cycle.** M3 closed at 0.4.0. Pick up the next slot per the
boot guide below.

---

## Next-agent boot guide

You are picking up at **M4-A — combat state registry** ([roadmap.md M4 sub-bites](roadmap.md#m4--combat-tick-v050)). M4 gives the placeholder 2.5 s tick a job: engaged combatants resolve a round every tick in lockstep ([ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md)) — hit/damage math (THAC0-style hidden rolls), aggression, death + corpses, drift instrumentation, and a load test. Ships at v0.5.0. M4 needs mobs and items, which **do not exist yet** — see "What M4 needs first" below.

### What's already built (0.4.0)

- **Tick loop (M1-A)** — `cmd_serve`'s epoll loop fires `advance_tick()`
  every 2.5 s on an absolute schedule with drift-resistant catch-up;
  `record_tick_drift` feeds the p99 ring. `advance_tick` is still a no-op
  counter bump — **M4-A/B hang the combat round off it.**
- **World tree (M3)** — `src/world.cyr`. `world_load_rooms(path)` builds
  rooms; `room_at(i)`, `room_exit(r, dir)`, `room_id/title/prose_*`
  accessors. Rooms currently hold only static fields — **no contents
  list yet** (mob/object instances in a room are M4's to add).
- **Players in the world** — each session has `SS_ROOM` (current room).
  `room_broadcast(room, except, mover, a, b, c)` and `room_say_broadcast`
  (server.cyr) push lines to everyone in a room + flush them; combat prose
  reuses these. `room_find_player` resolves a name in a room.
- **Verb-noun parser (M2)** — `cmd_dispatch` (session.cyr) routes verbs.
  `kill` / `flee` currently fall through to `cmd_object` placeholders —
  **M4-D wires them.** The resolver (`resolve_noun` / `resolve_nth` /
  `resolve_all`, `kw_matches`) takes a *scope* = array of NUL-terminated
  keyword strings; **M4 builds that scope from a room's mob/object
  contents** (the `keywords` field in mob/obj CYML entries, ADR 0005).
- **Zone format (ADR 0005)** — mob / object templates are CYML entries
  with `kind = "mob"` / `"obj"` in their own files
  (`<zone>.mobs.cyml` / `<zone>.objs.cyml`), ≤ 32 entries each. `world.cyr`
  loads rooms only so far; **M4/M5 add `world_load_mobs` / `_objs`** and a
  per-room contents list.

### What M4 needs first

M4 is combat, but there is nothing to fight yet. Expect to build, in order:

1. **Mob templates + instances.** Extend `world.cyr` with a `world_load_mobs`
   (kind="mob") and a per-room contents/occupants list so a room can hold
   live mobs. Author a few mobs into `data/zones/hub.mobs.cyml` + room
   `mobs = [...]` spawn lists (the room field is already in the schema).
2. **Combat state registry (M4-A).** Per-actor engagement record (target,
   aggro) on the player (session) and the mob instance.
3. Then hit/damage (M4-B/C) off `advance_tick`, aggression (M4-D, wiring
   `kill` / `flee`), death + corpses (M4-E/F), drift + load test (M4-G/H).

The `SS_PLAYER` slot (session offset 80, reserved since M1-B) gets a real
actor/combatant handle when persistence lands (M6); until then the
session *is* the player-actor — combat state can live in new SS_ slots.

### Reference

- Combat math (1d20 + DEX vs AC, THAC0; weapon dice + STR/TEC): [`../architecture/overview.md` §2.3](../architecture/overview.md) and [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md).
- Resolution scope contract: `src/parser.cyr` M2-C header comment.
- Mob/obj entry schema: [ADR 0005](../adr/0005-zone-file-format.md).

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test tests/cyrius-yeomans-descent.tcyr   # 174 assertions
cyrius fuzz                                      # parser fuzz, 100k inputs
cyrius bench                                     # IAC parser baseline
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — log in, `look`, walk n/s/e/w, `who`, `say hi`, `quit`
```

### Open ADRs

ADR 0005 (zone-file format) was resolved at M3-A. Two remain ahead of
their consumers — see [roadmap.md § Open ADRs](roadmap.md#open-adrs):
**0004** (identity/auth, gates M6) and **0006** (T.Ron persistence shape,
M6). Neither blocks M4.
