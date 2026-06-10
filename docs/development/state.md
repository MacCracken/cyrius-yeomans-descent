# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.6.1** — polish patch, 2026-06-09. Combat reads as lived-in: onlookers
see fights in third person (`room_combat_line`), mobs show qualitative
health (`mob_condition`, in `look` / `examine`), and every class recovers
HP out of combat (CON-scaled, in `classes_upkeep`). No new milestone, no
new deps. Details below are the 0.6.0 (M5) baseline this builds on.

**0.6.0** — M5 close, 2026-06-09. The four classes are playable. Character
creation asks your calling (Pikeman / Splicer / Courier / Chaplain,
`src/classes.cyr` + `data/classes.cyml`); each brings its own attributes,
combat profile, and three abilities on an energy + tick-cooldown + status
framework that composes with the 2.5 s auto-attack. Every class clears the
Hub solo and kills the Foundry Sentinel without dying — the Pikeman tanks,
the Splicer bursts, the Courier strikes from stealth, the Chaplain
sustains. Combat (0.5.0), world (0.4.0), parser (0.3.0), wire (0.2.0), and
tick (0.1.0) underneath are intact. **Players still vanish on restart —
persistence (M6) is next.**

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
  world.cyr      M3 world tree: CYML zone loader, Room struct (240 B,
                 +mob/obj list heads + spawn lists), exit resolution +
                 dangling-ref rejection, verb→dir; pure, no session I/O
  mob.cyr        M4 mobs: templates (CYML kind=mob) + live instances,
                 room-occupant list, keyword lookup, dice parse, spawn
  session.cyr    Session struct (328 B), login (M1-E) + class select (M5-A)
                 + world entry, dispatch (movement, render, examine sheet,
                 social, kill/flee, abilities, get/drop/inv), ANSI SGR,
                 combat + class + ability state (SS_HP..SS_STEALTH), g_epfd
  item.cyr       M4-E/F objects: templates (CYML kind=obj) + instances,
                 corpses + loot, get/drop/inventory, room object render
  combat.cyr     M4 combat: xorshift RNG, d20 hit + NdM damage, kill/flee,
                 per-tick round (combat_round), mob death + player respawn,
                 M5 effective-stat buffs (guard/stim) + condition line
  classes.cyr    M5 classes: load data/classes.cyml, selection login phase,
                 apply_class, ability framework (energy/cooldown/status),
                 the 12 class abilities (cmd_ability), classes_upkeep
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler
                 (YD_TICK_MS override), epoll dispatch, idle sweep (M1-F),
                 observability (M1-H), zone+mob+obj+class load at boot,
                 room broadcast / presence / who (M3-C/F), combat_tick_all
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

data/
  classes.cyml                  the 4 player classes (M5-B)
data/zones/
  hub.rooms.cyml                the authored 21-room Hub starter zone (M3-G)
  hub.mobs.cyml                 Hub bestiary: scavver → Sentinel boss (M4)
  hub.objs.cyml                 Hub loot objects (M4)
  example.rooms.cyml            3-room schema example (ADR 0005)

tests/
  cyrius-yeomans-descent.tcyr   unit suite (203 assertions)
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
  bench_telnet.bcyr             IAC-parser hot-path baseline (M1-G)
  bench_combat.bcyr            M4-H combat load test (32 players × 64 mobs,
                               p99 < 50 ms); `cyrius bench` runs benches/
```

Binary at `build/cyrius-yeomans-descent` (~229 KB with `CYRIUS_DCE=1`).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test tests/cyrius-yeomans-descent.tcyr` — 240 unit assertions:

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
- **combat** (M4) — `parse_dice` (`NdM+K` + malformed default), `die`/
  `roll` bounds, `combat_try_hit` hit/miss distribution, mob + object
  template loading + field values, spawn / keyword-find / remove, corpse
  synthesis + loot population, `mob_condition` thresholds (0.6.1)
- **classes** (M5) — class load + field values, `cl_id_eq`,
  `class_by_input` (number / prefix / trim / invalid / out-of-range),
  `apply_class`, `classes_upkeep` (energy regen cap, cooldown + buff
  decay, 0.6.1 out-of-combat HP regen), effective-stat buff helpers
- **idle** — the `session_is_idle` threshold predicate

Fuzz: `cyrius fuzz` → `fuzz/parser_fuzz.fcyr`, 100k random inputs +
directed adversarial cases, all invariants hold (token/buffer bounds,
index ranges, no `resolve_all` overrun), no crash / hang / leak.

End-to-end smokes validated locally on Linux x86_64 at the 0.6.0 cut:

- class selection: name → numbered class menu; pick by number or name
  prefix; invalid re-prompts; `examine me` shows the class character sheet
- abilities: class-gating ("you don't know how to hack"), energy spend,
  tick cooldowns, `bash` stun, `brace`/`stim` buffs in the condition line
- **solo verification (M5-H)**: a fresh server per class — Pikeman /
  Splicer / Courier / Chaplain each engage and kill the Foundry Sentinel
  with zero deaths (run at `YD_TICK_MS=200`)
- 0.5.0 combat / loot + 0.4.0 walk / social smokes still hold (M5 additive)

Benchmark: `cyrius bench` →
- `bench_telnet` — telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte (pure
  data), 16 M iterations, stable since 0.2.0
- `bench_combat` (M4-H) — 32 players × 64 mobs through 120 real ticks,
  now including per-tick `classes_upkeep`; **p99 ≈ 57 µs** against the
  50 ms drift budget. Combat is O(engaged combatants) per tick.
- (parser / world p99 baselines land at M9-C.)

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

**No active cycle.** M5 closed at 0.6.0. Pick up the next slot per the
boot guide below.

---

## Next-agent boot guide

You are picking up at **M6 — persistence via T.Ron** ([roadmap.md M6 sub-bites](roadmap.md#m6--persistence-via-tron-v070)). Players survive a server restart; writes are crash-safe and **queued, never inline** in the loop ([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md) negative consequence — disk I/O can't block the single-thread tick). Ships at v0.7.0. **M6 opens with two decisions before any code:** ADR 0004 (identity / auth — name+password vs sigil Ed25519) and ADR 0006 (persistence shape with T.Ron). M6-A also lands the **first external (non-stdlib) dependency**, T.Ron.

### What's already built (0.6.0)

- **The full character is in `SS_` slots** (session.cyr) and is exactly
  what M6 must persist: name (`SS_NAME_BUF`/`LEN`), class (`SS_CLASS`),
  attributes (`SS_STR`/`DEX`/`CON`/`TEC`), vitals (`SS_HP`/`SS_MAXHP`/
  `SS_ENERGY`/`SS_MAXENERGY`), combat profile (`SS_AC`/`SS_HIT`/`SS_NDICE`/
  `SS_DSIZE`/`SS_DMOD`), location (`SS_ROOM`), and inventory (`SS_INV` → an
  `item.cyr` object-instance list). **The save shape (M6-C) is this set.**
- **`SS_PLAYER` slot** (offset 80, reserved since M1-B) is still 0 — it is
  the natural home for a persistent player/account handle (M6-E load).
- **Classes load from CYML** (`world_load_classes`, `classes.cyr`) — the
  same load-at-boot pattern T.Ron data will follow; `apply_class` is how a
  fresh character is built, and a loaded save will set the same `SS_` slots.
- **Login flow** — `login_on_name` → `PHASE_CLASS` → `login_on_class` →
  world. **M6-E inserts a load step**: look up the name; if a save exists,
  restore it (skipping class selection); else fall through to class pick.
- **Item instances** (`item.cyr`) are heap objects with name/keywords/desc
  copied inline + a template-less corpse variant — serializable by
  template id + a small amount of state.
- **Tick** — `advance_tick` (server.cyr) is where the M6-D debounced
  save-timer would enqueue (never write inline). `YD_TICK_MS` overrides
  the interval for testing.

### What M6 needs (in order)

1. **ADR 0004** (identity/auth) + **ADR 0006** (persistence shape) — decide
   before code. Note [ADR 0002](../adr/0002-raw-tcp-telnet-protocol.md): Telnet has no TLS, so a
   plaintext password on the wire is the same exposure as a sigil — weigh
   that in 0004.
2. **M6-A** — land T.Ron in `cyrius.cyml [deps]` (first external dep; if
   T.Ron isn't ready, the milestone moves — track the gap here).
3. **M6-C/D/E/F** — save shape, queued save triggers (quit / save / level /
   debounced timer), load-on-login, crash-safe atomic writes (`.tmp` +
   rename). Gate: `kill -9` mid-combat → restart → no data loss.

### Reference

- Save shape + triggers + crash-safety: [roadmap.md M6](roadmap.md#m6--persistence-via-tron-v070).
- Identity options: [roadmap.md § Open ADRs](roadmap.md#open-adrs) (ADR 0004).
- Character state to persist: the `SS_` enum in `src/session.cyr`.

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test tests/cyrius-yeomans-descent.tcyr   # 232 assertions
cyrius fuzz                                      # parser fuzz, 100k inputs
cyrius bench                                     # telnet baseline + combat load test
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — log in, pick a class, `n`, `kill scavver`, `bash`, loot
# fast combat: YD_TICK_MS=200 ./build/cyrius-yeomans-descent serve 4000
```

### Open ADRs

ADR 0005 (zone-file format) was resolved at M3-A. Two remain — both now
**due, gating M6** — see [roadmap.md § Open ADRs](roadmap.md#open-adrs):
**0004** (identity / auth) and **0006** (T.Ron persistence shape).
