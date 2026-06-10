# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-06-09

## Version

**0.8.0** — M7 close, 2026-06-10. Zones heal themselves. The zone header's
`reset_secs` (Hub: 900) drives a reset that respawns mobs and loot to the
authored layout — but `maybe_zone_reset` (in `advance_tick`) defers while any
in-world player occupies the zone, retrying each tick until it empties. Mob
respawn tops each room up to its authored multiset (`zone_reset_mobs`: spawn
`authored − alive`, never duplicating); object respawn reapplies room `objects`
spawns without double-up (`zone_reset_objs`, matched by the new `OI_TPL_ID`).
Each reset logs `[<epoch>] zone=<id> reset (rooms=N, mobs=M, objs=O)` for
Joshua (M8). `YD_RESET_SECS` overrides the cadence for testing. **Gate met**:
empty zone resets in window, occupied zone defers, log matches state. 272
tests pass; live presence-gate verified. Also bumped the toolchain pin to
**6.1.21** and removed a duplicate room-id lookup (`world_room_by_id` →
`room_index_by_id`).

**0.7.0** — M6 close, 2026-06-09. Players persist across restart. Identity is
a sigil Ed25519 keypair derived from the player's passphrase ([ADR 0004](../adr/0004-identity-and-authentication.md)):
a new name forges + confirms a passphrase, a known name presents it; only
salt+pubkey are stored, the secret key is re-derived and never written. State
saves to a signed per-player `data/players/<name>.cyml` via atomic `.tmp`+rename
([ADR 0006](../adr/0006-persistence-shape.md)), triggered on `save` / disconnect
/ creation / a debounced 5-min tick sweep; load verifies the signature, restores
attrs + room (by id) + inventory, and drops the player back where they logged
off. A libro hash chain (`data/audit.libro`) logs every login/save/security
event. **Gate met**: `kill -9` mid-session → restart → no data loss. New module
`src/persist.cyr`; 256 tests pass. Combat (0.5.0) and earlier intact.

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

- **Cyrius pin**: `6.1.21` (`cyrius.cyml [package].cyrius`)

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
                 dangling-ref rejection, verb→dir; pure, no session I/O;
                 M7 zone-reset cadence (g_zone_reset_secs/_id, last-reset)
  mob.cyr        M4 mobs: templates (CYML kind=mob) + live instances,
                 room-occupant list, keyword lookup, dice parse, spawn;
                 M7 mob respawn (zone_reset_mobs — top-up to authored)
  session.cyr    Session struct (328 B), login (M1-E) + class select (M5-A)
                 + world entry, dispatch (movement, render, examine sheet,
                 social, kill/flee, abilities, get/drop/inv), ANSI SGR,
                 combat + class + ability state (SS_HP..SS_STEALTH), g_epfd
  item.cyr       M4-E/F objects: templates (CYML kind=obj) + instances,
                 corpses + loot, get/drop/inventory, room object render;
                 OI_TPL_ID (M6 persist); M7 object respawn (zone_reset_objs)
  combat.cyr     M4 combat: xorshift RNG, d20 hit + NdM damage, kill/flee,
                 per-tick round (combat_round), mob death + player respawn,
                 M5 effective-stat buffs (guard/stim) + condition line
  classes.cyr    M5 classes: load data/classes.cyml, selection login phase,
                 apply_class, ability framework (energy/cooldown/status),
                 the 12 class abilities (cmd_ability), classes_upkeep
  persist.cyr    M6 persistence: Ed25519 identity derived from passphrase
                 (ADR 0004), per-player signed cyml save shape, crash-safe
                 .tmp+rename writes, load+auth, login phase handlers, libro
                 audit chain. Included after the enum-defining src files +
                 lib/sakshi/sigil/libro.
  server.cyr     event loop, listener, signalfd shutdown, tick scheduler
                 (YD_TICK_MS override), epoll dispatch, idle sweep (M1-F),
                 observability (M1-H), zone+mob+obj+class load at boot,
                 room broadcast / presence / who (M3-C/F), combat_tick_all,
                 persist_init + debounced save sweep + save-on-disconnect (M6),
                 M7 zone reset (maybe_zone_reset/presence gate/log) + YD_RESET_SECS
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

- **stdlib** — string, fmt, alloc, io, vec, str, slice, syscalls, assert, bench, args, net, chrono, result, tagged, fnptr, freelist, cyml, toml, **fs, process, hashmap, json, bigint, ct, keccak, thread, thread_local, random** (M6 chain — see below)
- **libro** `2.7.1` (git, `path = "../libro"`) — append-only SHA-256 hash-chain store (the crash-safe primitive behind "T.Ron" persistence). Pulls **sigil 3.6.0** (Ed25519, ADR 0004 identity) + **sakshi 2.2.4** + **patra 1.10.3** + **agnosys 1.3.2** transitively. Resolved by `cyrius deps` into `lib/` (+ `cyrius.lock`).

**M6 complete (0.7.0, 2026-06-09).** Full persistence shipped — see the Version
section above and `src/persist.cyr`. The dep-landing (M6-A) lesson is preserved
below because it shaped the whole milestone: the earlier "blocked on a sigil
bug" note was a **misdiagnosis**: cyrius stdlib is **opt-in, never
auto-resolved**, so
including `dist/sigil.cyr` without listing the modules its crypto calls
(`ct`/`keccak`/`thread`/`thread_local`/`random`) left those symbols
undefined — cyrius 6.1.x only *warns* and emits a `ud2`, so it built then
SIGILL'd (exit 132) the instant `sha256`/`ed25519` ran. Sigil 3.7.8's
CHANGELOG diagnosed it against this repo; the fix is the opt-in list now in
`cyrius.cyml [deps] stdlib`. Joshua still lands at M8 — see
[roadmap M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

**No active cycle.** M7 closed at 0.8.0. Next slot is **M8 — Joshua operator
interface** (v0.9.0). Pick up per the boot guide below.

---

## Next-agent boot guide

You are picking up at **M8 — Joshua management interface** ([roadmap.md M8](roadmap.md#m8--joshua-management-interface-v090)): an out-of-band operator surface to inspect and steer a running server — list/boot players, reload a zone, force a reset, read the observability counters and event logs. The hooks it consumes already exist; M8 is mostly wiring them to a control channel.

### What M7 left in place (zone resets done)

- **Reset engine** — `maybe_zone_reset` / `zone_has_player` / `zone_reset_log`
  (server.cyr), `zone_reset_mobs` (mob.cyr), `zone_reset_objs` (item.cyr). The
  timer is `g_zone_reset_secs` (from the zone header) + `g_zone_last_reset_ms`;
  `YD_RESET_SECS` overrides. **Joshua's "force reset now" is a one-liner** —
  set `g_zone_last_reset_ms = 0` (or call the reset directly).
- **Observability counters** (M1-H, server.cyr) — live connections, sessions,
  ticks, tick-drift p99 — already surfaced by the `@stats` admin verb. Joshua
  reads the same.
- **Event logs Joshua tails** — the reset line (`zone=<id> reset (…)`) and the
  libro audit chain (`data/audit.libro`: logins/saves/security).
- **`g_zone_id` / `g_zone_name`** are read from the zone header; the world is
  still single-zone (one `g_rooms` block) — multi-zone is a pre-req if M8 wants
  per-zone control, otherwise it operates on the one loaded zone.

### What M8 needs (sketch)

1. **Control channel** — decide the surface: a privileged Telnet verb set
   (`@who`/`@reload`/`@reset`/`@boot <name>`), a separate admin socket, or a
   signal/file trigger. ADR-worthy if it adds a new wire/auth surface.
2. **Operations** — list/boot sessions (walk `g_session_head`), reload a zone
   (re-run `world_load_*` + respawn), force a reset, dump counters/logs.
3. **Auth** — operator authentication (reuse the sigil/ADR-0004 machinery, or
   a separate operator credential). Telnet-no-TLS caveat applies.

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test                                      # 272 assertions, all pass
./build/cyrius-yeomans-descent serve 4000
# telnet 127.0.0.1 4000 — new name → passphrase → class → play; `save`/`quit`,
# reconnect → restored. kill -9 after a save → restart → reconnect → no loss.
# zone resets: YD_TICK_MS=200 YD_RESET_SECS=5 ./build/...; kill a mob, leave the
# zone empty, watch the server log for `zone=hub reset (... mobs=N ...)`.
```

### Open ADRs

None outstanding. 0001–0003 (combat / wire / concurrency), 0004 (identity),
0005 (zone format), 0006 (persistence shape) are all Accepted. M8 likely earns
a new ADR if the operator channel adds a new wire/auth surface.
