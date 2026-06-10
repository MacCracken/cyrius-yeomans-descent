# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.5.0** — M4 close, 2026-06-09. The Combat Tick has a job. Mobs
(`src/mob.cyr`) and items/corpses (`src/item.cyr`) load from CYML; combat
(`src/combat.cyr`) resolves a hidden-roll round per 2.5 s tick inside
`advance_tick`. A player `kill`s a mob, both trade `d20`-vs-AC attacks
each tick, mobs die into lootable corpses (`get all from corpse`), and
players respawn at the Hub. The full loop — explore, fight, loot, carry,
die, respawn — is playable end to end. Load-proven: 32 players × 64 mobs
tick at p99 ≈ 62 µs, well inside the 50 ms budget. The world (0.4.0),
parser (0.3.0), wire (0.2.0), and tick scheduler (0.1.0) underneath are
intact. Classes (M5) turn the player's flat default stats into mechanics.

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
  session.cyr    Session struct (224 B), login (M1-E) + world entry,
                 M2/M3/M4 dispatch (movement, render w/ mobs+objs, examine,
                 social, kill/flee→combat, get/drop/inv→items), ANSI SGR,
                 combat stats (SS_HP/AC/TARGET/dice) + SS_INV, g_epfd
  item.cyr       M4-E/F objects: templates (CYML kind=obj) + instances,
                 corpses + loot, get/drop/inventory, room object render
  combat.cyr     M4 combat: xorshift RNG, d20 hit + NdM damage, kill/flee,
                 per-tick round (combat_round), mob death + player respawn
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler,
                 epoll dispatch, idle sweep (M1-F), observability (M1-H),
                 zone+mob+obj load at boot, room broadcast / presence / who
                 (M3-C/F, non-dropping), combat_tick_all from advance_tick
  test.cyr       top-level test entrypoint (per cyrius.cyml [build].test)

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

Binary at `build/cyrius-yeomans-descent` (~209 KB with `CYRIUS_DCE=1`).

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test tests/cyrius-yeomans-descent.tcyr` — 203 unit assertions:

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
  synthesis + loot population
- **idle** — the `session_is_idle` threshold predicate

Fuzz: `cyrius fuzz` → `fuzz/parser_fuzz.fcyr`, 100k random inputs +
directed adversarial cases, all invariants hold (token/buffer bounds,
index ranges, no `resolve_all` overrun), no crash / hang / leak.

End-to-end smokes validated locally on Linux x86_64 at the 0.5.0 cut:

- combat loop: engage a scavver, watch per-tick rounds (hit/miss + damage
  both ways, HP condition line); kill → corpse appears, `get all from
  corpse` loots it, `inventory` / `drop` move items; the boss Sentinel
  kills the player → death prose + respawn at the gate with full HP
- mobs / objects render in rooms (red mobs, yellow objects); `examine`
  resolves a mob to its description
- 0.4.0 two-player walk + social smokes still hold (M4 is additive)

Benchmark: `cyrius bench` →
- `bench_telnet` — telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte (pure
  data), 16 M iterations, stable since 0.2.0
- `bench_combat` (M4-H) — 32 players × 64 mobs through 120 real ticks;
  **p99 ≈ 62 µs, max ≈ 70 µs** against the 50 ms drift budget (≈ 800×
  headroom). Combat is O(engaged combatants) per tick, off the accept path.
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

**No active cycle.** M4 closed at 0.5.0. Pick up the next slot per the
boot guide below.

---

## Next-agent boot guide

You are picking up at **M5-A — class selection** ([roadmap.md M5 sub-bites](roadmap.md#m5--classes--abilities-v060)). M5 turns the four classes (Pikeman / Splicer / Courier / Chaplain) from text-table flavor into playable mechanics: class pick at character creation, per-class attribute scaling, three abilities each, and tick-composed cooldowns ([ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md) negative consequence — abilities *compose* with the 2.5 s tick, they don't replace it). Ships at v0.6.0.

### What's already built (0.5.0)

- **Combat (M4)** — `src/combat.cyr`. `combat_round(s)` resolves one tick
  for an engaged session; `advance_tick` → `combat_tick_all()` runs it for
  everyone. Hit = `d20 + hit + AC >= 20` (`combat_try_hit`), damage =
  `roll(ndice, dsize, dmod)`. **Player stats are flat defaults** in the
  `PlayerStat` enum (session.cyr: HP 30, AC 8, hit +1, 1d6+1) — **M5-B
  replaces these with per-class attribute scaling.**
- **Combat state** lives in SS_ slots (`SS_HP`/`SS_MAXHP`/`SS_AC`/
  `SS_TARGET`/`SS_HIT`/`SS_NDICE`/`SS_DSIZE`/`SS_DMOD`/`SS_INV`). The
  `SS_PLAYER` slot (offset 80, reserved since M1-B) still awaits the M6
  persistence handle; the session is the actor for now. **M5 adds a class
  id + attribute (STR/DEX/CON/TEC) slots here.**
- **Mobs (M4)** — `src/mob.cyr`: templates (`world_load_mobs`) + instances
  (`mob_spawn`, `mob_in_room_by_kw`, `mob_remove`), room-occupant list.
- **Items (M4)** — `src/item.cyr`: object templates + instances, corpses +
  loot, `get`/`drop`/`inventory`. Abilities that consume/grant items (e.g.
  a Chaplain's stims) hook here.
- **Login flow** — `login_on_name` (session.cyr) captures the name then
  calls `session_enter_world`. **M5-A inserts class selection between the
  name prompt and world entry** (a new login phase, or a sub-prompt).
- **Tick** — `advance_tick` (server.cyr) is the one place per-tick work
  runs. **Ability cooldowns (M5-G) decrement here**, composed with combat.

### What M5 needs

1. **Class data (M5-B).** A `data/classes.cyml` (single-entry or one entry
   per class) with per-class STR/DEX/CON/TEC start values + growth, and the
   derived HP/AC/hit/damage that replace the flat `PlayerStat` defaults.
   This is the same CYML format ([ADR 0005](../adr/0005-zone-file-format.md) precedent).
2. **Class selection (M5-A).** A login sub-phase after the name prompt.
3. **Abilities (M5-C..F).** Three per class, as new verbs that act inside /
   alongside combat; **tick-composed cooldowns (M5-G)** decremented in
   `advance_tick`.
4. **Solo-playable verification (M5-H).** Each class clears the Hub solo,
   killing the Foundry Sentinel boss (`foundry.overseer`) without dying
   twice. Tune class stats against the existing bestiary.

### Reference

- Class table (roles, core commands, attribute focus): [`../architecture/overview.md` §3](../architecture/overview.md).
- Attributes → combat math: [`../architecture/overview.md` §2.2-2.3](../architecture/overview.md).
- Cooldowns compose with the tick: [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md) (negative consequence).
- Combat hooks: `src/combat.cyr` (`combat_round`, `roll`, `combat_try_hit`).

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test tests/cyrius-yeomans-descent.tcyr   # 203 assertions
cyrius fuzz                                      # parser fuzz, 100k inputs
cyrius bench                                     # telnet baseline + combat load test
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — log in, `n`, `kill scavver`, wait a tick, loot the corpse
```

### Open ADRs

ADR 0005 (zone-file format) was resolved at M3-A. Two remain ahead of
their consumers — see [roadmap.md § Open ADRs](roadmap.md#open-adrs):
**0004** (identity/auth, gates M6) and **0006** (T.Ron persistence shape,
M6). Neither blocks M4.
