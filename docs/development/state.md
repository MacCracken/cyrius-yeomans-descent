# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.3.0** — M2 close, 2026-06-09. The command prompt now drives a real
verb-noun parser (`src/parser.cyr`): tokenizer (M2-A), canonical verb
table + aliases (M2-B), keyword-prefix direct-object resolution (M2-C),
preposition / indirect-object split (M2-D), and `all.X` / `N.X`
qualifiers (M2-E), fuzz-hardened against 100k random inputs (M2-F).
`cmd_on_line` routes through the parser instead of echoing; `quit`
disconnects. The verbs' *world* — rooms, items, mobs — lands at M3, so
the handlers acknowledge the parse rather than fake state, and the
resolution matchers run against synthetic scopes until M3 supplies live
contents. The wire (0.2.0) and heartbeat (0.1.0) underneath are intact.

## Toolchain

- **Cyrius pin**: `6.1.17` (`cyrius.cyml [package].cyrius`)

## Source layout

```
src/
  main.cyr       argv dispatch (`serve [port]` / `version` / `help`);
                 include order telnet → parser → session → server
  telnet.cyr     RFC 854 IAC parser + RFC 1143 Q-method negotiation
                 (M1-C/M1-D); pure, no I/O; one TelnetState per session
  parser.cyr     M2 verb-noun parser: tokenizer, verb table + aliases,
                 keyword-prefix object resolution, preposition split,
                 all.X / N.X qualifiers; pure, no session I/O
  session.cyr    Session struct (144 B), rx scratch, decoded-line
                 accumulator, tx queue, login flow + name validation
                 (M1-E), idle predicate (M1-F), M2 command dispatch
                 (cmd_on_line → parser → cmd_dispatch), SS_QUIT teardown
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler,
                 epoll dispatch, active-session list + idle sweep (M1-F),
                 observability counters + render_stats (M1-H), SS_QUIT drop
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

tests/
  cyrius-yeomans-descent.tcyr   unit suite (154 assertions)
  cyrius-yeomans-descent.bcyr   scaffold-family placeholder (real benches
                                live in benches/ — see below)
  cyrius-yeomans-descent.fcyr   scaffold-family stub; real fuzz harness in
                                fuzz/ (the toolchain runs fuzz/*.fcyr)

fuzz/
  parser_fuzz.fcyr             M2-F parser fuzz harness (100k inputs);
                               `cyrius fuzz` auto-discovers fuzz/

benches/
  bench_telnet.bcyr             IAC-parser hot-path baseline (M1-G);
                                `cyrius bench` auto-discovers benches/
```

Binary at `build/cyrius-yeomans-descent` (~131 KB with `CYRIUS_DCE=1`).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test tests/cyrius-yeomans-descent.tcyr` — 154 unit assertions:

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
- **idle** — the `session_is_idle` threshold predicate

Fuzz: `cyrius fuzz` → `fuzz/parser_fuzz.fcyr`, 100k random inputs +
directed adversarial cases, all invariants hold (token/buffer bounds,
index ranges, no `resolve_all` overrun), no crash / hang / leak.

End-to-end smokes validated locally on Linux x86_64 at the 0.3.0 cut:

- full login → command loop: `look`, `get all.rations from corpse`,
  `give monoblade to kiran`, `n`, `xyzzy`, `say …`, `emote …`, `help`,
  `@stats`, `quit` — each routes to the right handler; the dobj/prep/iobj
  decomposition is visible in the object-verb echo; `quit` disconnects
- social verbs echo the case-preserved message text (parser tokens are
  lowercased, but the social path reads the original line)
- 0.2.0 wire/idle/concurrency smokes still hold (parser is additive)

Benchmark: `cyrius bench` → telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte
(pure data), 16 M iterations, stable (unchanged — parser not yet benched;
M9-C locks a parser-p99 baseline).

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

**No active cycle.** M2 closed at 0.3.0. Pick up the next slot per the
boot guide below.

---

## Next-agent boot guide

You are picking up at **M3-A — zone file format** ([roadmap.md M3 sub-bites](roadmap.md#m3--world-rooms-movement-v040)). M3 makes the world physical: a zone-file format, a loader, movement, ANSI room rendering, the inspection + social verbs, and an authored starter zone, shipping at v0.4.0. **M3-A opens with ADR 0005** (zone-file serialization: `lib/cyml.cyr` vs `lib/toml.cyr` vs a bespoke DikuMUD `.wld`/`.mob`/`.obj`/`.zon` dialect) — decide it before any M3 code.

### What's already built (0.3.0)

- **Telnet wire (0.2.0)** — `telnet_feed` is a pure RFC 854 parser;
  `session_consume_rx` routes decoded bytes into the line accumulator,
  which dispatches complete lines to `session_on_line` (branches on phase).
- **Verb-noun parser (M2)** — `src/parser.cyr`, pure, one shared
  `g_parser` (lazily alloc'd). `parser_parse(pa, buf, len)` tokenizes +
  decomposes into `PA_VERB` / `PA_PREP` / `PA_DOBJ_I` / `PA_IOBJ_I`
  (accessors: `parsed_verb`, `parsed_prep`, `parsed_dobj`, `parsed_iobj`).
  Verb ids in the `Verb` enum; `verb_lookup` folds aliases.
- **Object resolution matchers (M2-C/E)** — `resolve_noun` (single,
  ambiguity-checked), `resolve_nth`, `resolve_all`, and the
  `kw_matches` keyword-prefix primitive. **These take a *scope* —
  `names` = array of `n` NUL-terminated keyword-string pointers in
  deterministic scan order.** Today only the test/fuzz harnesses build
  that array; **M3 is where the world supplies it** (inventory →
  room contents → worn/wielded, in that scan order, per M2-C's contract).
- **Command dispatch (M2)** — `cmd_on_line` → `parser_parse` →
  `cmd_dispatch`. Object/movement/look verbs currently emit M3-pending
  placeholders; `cmd_object` already renders the parsed dobj/prep/iobj.
  This is the seam M3 fills with real handlers.
- **`quit` teardown** — `SS_QUIT` flag set by the verb, checked in
  `dispatch_session` after the goodbye flush → `drop_session`.
- **Idle sweep + observability** — unchanged from 0.2.0 (`sweep_idle`,
  `@stats` / `render_stats`, the drift ring).

### What M3-A should do

1. **File ADR 0005** (zone-file format) — see [roadmap.md § Open ADRs](roadmap.md#open-adrs).
2. Define the format: zone metadata, rooms (id / title / prose / exits /
   mob spawns / object spawns), mob templates, object templates.
3. Then M3-B (loader: parse at boot, validate the exit graph, build the
   in-memory world tree) and M3-C (movement) follow.

When the world tree exists, the M2 resolution matchers bind to it:
build the `names` scope array from a room's contents + the actor's
inventory and call `resolve_noun` / `resolve_nth` / `resolve_all`. The
`SS_PLAYER` slot (offset 80, reserved since M1-B) gets the actor handle
at M6; until then the actor is the session.

### Reference

- Resolution scope contract: `src/parser.cyr` M2-C header comment.
- Room rendering uses `lib/darshana` for SGR escapes (M3-D).
- World / room / zone semantics: [roadmap.md M3](roadmap.md#m3--world-rooms-movement-v040)
  and [`../architecture/overview.md`](../architecture/overview.md).

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test tests/cyrius-yeomans-descent.tcyr   # 154 assertions
cyrius fuzz                                      # parser fuzz, 100k inputs
cyrius bench                                     # IAC parser baseline
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — log in, type `help`, try `get all.x from y`, `quit`
```

### Open ADRs

Three decisions are queued ahead of their consumer milestones — see
[roadmap.md § Open ADRs](roadmap.md#open-adrs). **ADR 0005 (zone-file
format) is now due — it gates M3-A.**
