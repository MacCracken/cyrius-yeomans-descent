# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-06-09
>
> Milestone plan through v1.0. State lives in [`state.md`](state.md);
> this file is the sequencing — what ships, in what order, against
> what dependency gates. Design reference: [`../architecture/overview.md`](../architecture/overview.md).
>
> Per-tag chronology lives in [`../../CHANGELOG.md`](../../CHANGELOG.md);
> current-cycle status in [`state.md`](state.md). ADRs cross-referenced
> at [`../adr/`](../adr/).

---

## Release plan

| Tag | Theme | Status |
|---|---|---|
| **0.1.0** | M0 scaffold + ADRs 0001 / 0002 / 0003 + M1-A event loop + M1-B sessions | ✅ 2026-05-24 |
| **0.2.0** | M1 close — Telnet parser (M1-C) + option negotiation (M1-D) + login scaffold (M1-E) + idle timeout (M1-F) + bench harness (M1-G) + observability (M1-H) | ✅ 2026-06-09 |
| **0.3.0** | M2 — verb-noun parser + fuzz harness | ✅ 2026-06-09 |
| **0.4.0** | M3 — world / rooms / movement + starter zone | ✅ 2026-06-09 |
| **0.5.0** | M4 — combat tick + hit/damage math + corpses | ✅ 2026-06-09 |
| **0.6.0** | M5 — four classes playable solo through the starter zone | ✅ 2026-06-09 |
| **0.7.0** | M6 — libro+sigil player persistence (Ed25519 identity) + crash-safe writes | ✅ 2026-06-09 |
| **0.8.0** | M7 — zone resets with player-presence gating | ✅ 2026-06-10 |
| **0.8.1** | Login/identity polish — password echo, last-seen, `passwd` | ✅ 2026-06-10 |
| **0.8.2** | Lived-in Hub content — room objects (exercises M7-D) | ✅ 2026-06-10 |
| **0.8.3** | Operator read-only verbs — `@who` / `@reset` | ✅ 2026-06-10 |
| **0.9.0** | Security sweep & audit — CVE-class review + memory-safety fixes | ✅ 2026-06-10 |
| **0.9.1** | Surface freeze — lock the public command / save / wire surface | |
| **1.0.0** | Clean release — final hardening + playtest sign-off | |
| _future_ | M8 — Joshua operator interface (deferred post-1.0) | |

---

## In progress

**No active cycle.** 0.9.0 closed — security sweep done: a CVE-informed audit of the network-input + save-file surface found and fixed two heap overflows (one pre-auth), an OOB-read, and a DoS, all rooting in "a signature proves authorship, not field validity." Next slot is **0.9.1 — surface freeze**: stop adding to the public surface (commands, save-record fields, wire/Telnet behaviour, the `@`-admin namespace) and lock it so 1.0.0 is a stabilisation-only release. **M8 (Joshua) is deferred to post-1.0** at the user's direction. Pickup pointer in [`state.md`](state.md).

---

## Milestones

### M2 — Verb-noun parser (v0.3.0)

Turns lines from the command prompt into structured actions. The MUD-defining parser: not just a verb table, but direct-object / preposition / indirect-object resolution, qualifiers, and aliases.

**Sub-bites:**

- **M2-A — Tokenizer.** Whitespace-split with quote handling for multi-word direct objects. Lowercase normalization.
- **M2-B — Verb table.** Canonical v1.0 verb list: movement (`n`/`s`/`e`/`w`/`u`/`d`, `north`/...), inspection (`look`, `examine`, `exits`, `inventory`, `who`), item manipulation (`get`, `drop`, `put`, `give`, `wear`, `remove`, `wield`), combat (`kill`, `flee`), social (`say`, `tell`, `emote`), session (`quit`, `save`, `help`). Aliases (`n` → `north`, `inv`/`i` → `inventory`, `l` → `look`).
- **M2-C — Direct-object resolution.** Resolve the noun against the actor's inventory + the current room's contents + the actor's worn/wielded slots. Ambiguity returns a "which X did you mean?" prompt.
- **M2-D — Preposition / indirect-object resolution.** `put rations in pack`, `give monoblade to kiran`, `get all from corpse`. Preposition table: `in`, `on`, `to`, `from`, `at`, `with`.
- **M2-E — Qualifiers.** `all.X` (every X in scope), `X.N` (the Nth X in deterministic scan order). `get all.rations`, `kill 2.drone`.
- **M2-F — Fuzz harness.** `tests/cyrius-yeomans-descent.fcyr` driven against the parser: 100k random byte sequences, every UTF-8 length, every embedded NUL position. No crashes, no hangs, no unbounded memory growth.

**Gate:** fuzz harness clean against 100k random inputs; verb table covered by `tests/cyrius-yeomans-descent.tcyr`.

### M3 — World, rooms, movement (v0.4.0)

The world becomes physical. Players have a location; rooms have prose, exits, contents; movement updates state and notifies onlookers.

**Sub-bites:**

- **M3-A — Zone file format.** Pick a serialization — likely `lib/cyml.cyr` or `lib/toml.cyr`. Decision recorded as **ADR 0005** ([see open ADRs](#open-adrs)). Format covers zone metadata, rooms (id / title / prose / exits / mob spawns / object spawns), mob templates, object templates.
- **M3-B — Zone loader.** Parse zone files at boot; validate exit graph (no dangling refs); build in-memory world tree. Reload via an admin verb (becomes Joshua-driven at M8).
- **M3-C — Movement.** Cardinal navigation (`n`/`s`/`e`/`w`/`u`/`d`); auto-look on arrival; departure / arrival messages to onlookers in the source / destination rooms; "you can't go that way" for closed exits.
- **M3-D — Room rendering (ANSI).** Title (bold/colored), prose (default), exits line (cyan-ish), present entities (one per line, distinct color per kind: players / mobs / objects). Uses `lib/darshana` for SGR escapes.
- **M3-E — `look`, `examine`, `exits`, `inventory`.** Inspection verbs against rooms / objects / mobs / self.
- **M3-F — `say`, `emote`, `who`.** Social essentials for testing multi-player presence end-to-end.
- **M3-G — Starter zone authored.** "The Hub" — a ~20-room zone in the Under-Grid surface tier. Tavern hub, three exits to mini-loops, ~30 hand-authored rooms total. Doubles as the v1.0 demo content.

**Gate:** the starter zone is walkable end-to-end by two players, each seeing the other's arrivals / departures / says in real time.

### M4 — Combat tick (v0.5.0)

The placeholder tick from M1 gets a job. Engaged combatants resolve a round every 2.5s, in lockstep, per [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md).

**Sub-bites:**

- **M4-A — Combat state registry.** Per-actor engagement record (target, last-attacked, aggro list). Lives on the actor (player or mob), referenced from the tick.
- **M4-B — Hit resolution.** `1d20 + DEX-modifier + weapon-accuracy` vs target AC; THAC0 lookup table. Hidden roll, prose-rendered outcome.
- **M4-C — Damage roll.** Weapon dice + STR or TEC modifier (per weapon class). Damage applied to target HP; death at HP ≤ 0.
- **M4-D — Aggression model.** `kill <target>` engages; auto-attack continues each tick; target switches via `kill <other>` (single target at a time); death disengages.
- **M4-E — Death & corpses.** On death: mob → corpse object in the room holding the mob's loot; player → death prose, drop inventory in current room, respawn at the starter Hub (full v1.0 death penalty is M5+ class flavor).
- **M4-F — `get all from corpse`** (parser already supports it at M2; combat creates the consumers).
- **M4-G — Tick drift instrumentation.** Continuous p99-drift measurement; logged via the M1-H observability hook.
- **M4-H — Load test.** `tests/cyrius-yeomans-descent.bcyr` — N players × M mobs × 5-minute run; assert p99 drift < 50 ms.

**Gate:** load test passes — 32 simulated players × 64 mobs ticking without drift breach.

### M5 — Classes & abilities (v0.6.0)

Four classes go from text-table flavor to playable mechanics.

**Sub-bites:**

- **M5-A — Class selection** during character creation (between name prompt and MOTD-2 at first login).
- **M5-B — Attribute scaling.** Per-class STR / DEX / CON / TEC starting values + growth curve. Lookup tables checked into the zone-file family (or a sibling `data/classes.cyml`).
- **M5-C — Pikeman.** `bash`, `brace`, `cleave`. STR / CON focus. Melee tank role.
- **M5-D — Splicer.** `hack`, `overload`, `emp`. TEC focus. Caster / hacker role.
- **M5-E — Courier.** `sneak`, `backstab`, `bypass`. DEX focus. Rogue / stealth role.
- **M5-F — Chaplain.** `patch`, `stim`, `rally`. TEC / CON focus. Healer / support role.
- **M5-G — Tick-composed cooldowns.** Abilities cost stamina / energy and have a tick-counted recharge — they compose with the 2.5s tick, they don't replace it ([ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md) negative consequence).
- **M5-H — Solo-playable verification.** Each class can complete the starter zone solo — kill the boss-tier mob at the Hub-3 endpoint without dying twice.

**Gate:** each class fully playable solo through the starter zone; ability-cooldown text legible inside the tick prose stream.

### M6 — Persistence via T.Ron (v0.7.0)

Players survive server restart. Crash-safe writes. Asynchronous (or queued) — disk I/O cannot block the loop ([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md) negative consequence).

**Sub-bites:**

- **M6-A — T.Ron dep landing.** Pull T.Ron into `cyrius.cyml [deps]`. If T.Ron isn't ready, this milestone moves; the dep gap is tracked in `state.md`.
- **M6-B — Identity model ADR.** **ADR 0004 ([open](#open-adrs))** — name+password (era-correct) vs sigil Ed25519 (AGNOS-ecosystem aligned). Decided before any M6 code.
- **M6-C — Player save shape.** Attrs (STR / DEX / CON / TEC + class + level + XP), inventory (object ids + counts + worn/wielded slot bindings), location (zone + room id), HP / stamina, identity (name + hashed password OR fingerprint), creation / last-login timestamps.
- **M6-D — Save triggers.** On `quit`, on `save`, on every level-up, and on a debounced timer (every 5 minutes per player) — but **queued, never inline** in the loop.
- **M6-E — Load on login.** Look up by name; restore full state into a session struct; place into the recorded room (or starter Hub if the room no longer exists).
- **M6-F — Crash-safe writes.** Atomic file replacement (write to `.tmp` + rename), per T.Ron's transactional semantics. Partial writes recovered on next start.

**Gate:** `kill -9` the server mid-tick during active combat → restart → no player data loss; the player respawns at their last room with full attrs / inventory.

### M7 — Zone resets (v0.8.0)

Mobs and loot respawn. Players don't get respawn-stomped.

**Sub-bites:**

- **M7-A — Per-zone reset timer.** Configurable interval per zone (default 15-30 min); tracked from last reset, not last server start.
- **M7-B — Player-presence gate.** Reset checks every room in the zone; if any room contains a connected player, defer the reset to the next tick. (Empty-zone check is single-writer per [ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md) — no race.)
- **M7-C — Mob respawn.** From zone-file mob spawns; full HP / inventory; original position. Existing-but-dead mob slot reused.
- **M7-D — Loot respawn.** Object spawns reapplied; existing objects in the room left in place (no double-up).
- **M7-E — Reset event log.** Each reset writes a single line: `[ts] zone=X reset (rooms=N, mobs=M, objs=O)`. Joshua reads this at M8.

**Gate:** empty zone resets within its window; a zone with a player in any room does not reset; reset event log matches observed state.

### M8 — Joshua management interface (v0.9.0)

The operator surface. Joshua is the AGNOS game-management tool; this milestone wires the MUD's admin verbs into it.

**Sub-bites:**

- **M8-A — Joshua dep landing.** Pull Joshua into `cyrius.cyml [deps]`. Same dep-gap caveat as M6.
- **M8-B — Live player list.** `joshua mud players` → name / class / level / location / idle-time / connection-time.
- **M8-C — Kick & ban.** `joshua mud kick <name>` (terminate session); `joshua mud ban <name> [--for <duration>]` (refuse reconnect).
- **M8-D — Broadcast.** `joshua mud broadcast <message>` → server-wide MOTD-style announcement (rendered to every live session).
- **M8-E — Zone reload.** `joshua mud reload <zone>` → re-parse the zone file, replace the in-memory zone tree, evict any mobs that no longer exist (players gracefully relocated if their room was deleted).
- **M8-F — Audit log.** Every operator action (kick / ban / broadcast / reload) appends to `docs/audit/operator.log` with operator identity + timestamp + target.

**Gate:** the v1.0 live-ops procedures (kick a misbehaving player, ban a repeat offender, broadcast a server-restart warning, reload a zone after a content fix) are all runnable from Joshua alone, no MUD-server shell access required.

### M9 — Hardening + v1.0 (v1.0.0)

The closeout.

**Sub-bites:**

- **M9-A — Security audit.** Full sweep per [CLAUDE.md § Process](../../CLAUDE.md) and [first-party-standards § Security Hardening](https://github.com/MacCracken/agnosticos/blob/main/docs/development/applications/first-party-standards.md#security-hardening-required-before-every-release). Every input path (Telnet bytes, command lines, zone files, save files, Joshua RPC), every buffer, every syscall consumer. Findings filed at `docs/audit/YYYY-MM-DD-audit.md`. Severity-graded (CRITICAL / HIGH / MEDIUM / LOW). All CRITICAL / HIGH close before 1.0; MEDIUM / LOW may carry forward with a written deferral rationale.
- **M9-B — CVE sweep.** Cross-check the codebase against the historical MUD-server CVE record (CircleMUD / tinymud / SMAUG / DikuMUD-family disclosures) — buffer overflows in IAC handling, parser stack-smash via long input lines, save-file path traversal, command-shell injection via player names.
- **M9-C — Benchmark baselines locked.** `docs/benchmarks.md` snapshot: IAC parser ns/byte, verb-parser p99 µs, tick-drift p99 ms at N players, accept-loop sessions/sec. Re-runs at every future minor compare against the 1.0 baseline.
- **M9-D — Public API freeze.** Anything outside `src/` that another tool would script against (Joshua RPC surface, zone-file schema, save-file schema) gets a written ABI/format contract. Future changes need an ADR + migration path.
- **M9-E — Closeout pass.** Per [CLAUDE.md § Process](../../CLAUDE.md): full test suite, benchmark baseline re-run, dead-code audit, refactor pass on the minor's accretion, doc sync (CHANGELOG, state.md, doc-health.md), version verification (`VERSION` / `cyrius.cyml` / git tag in lockstep), clean DCE build.
- **M9-F — Internal playtest.** Summer-of-Games slate. Two-week multi-player session with the AGNOS internal cohort. Crash-bug-free; no player-data corruption; no operator-required intervention more than once per day. Sign-off in `docs/audit/YYYY-MM-DD-playtest.md`.

**Gate:** all v1.0 criteria green; sign-off captured.

---

## Closed milestones

Brief one-liners; per-tag chronology in [`../../CHANGELOG.md`](../../CHANGELOG.md). Detail folded back into the active body when relevant.

- **M0 (0.1.0)** — `cyrius init` scaffold; doc tree per first-party-documentation; design captured in `docs/architecture/overview.md`. Three load-bearing ADRs filed: combat tick model ([0001](../adr/0001-tick-based-combat-over-cooldowns.md)), raw TCP / Telnet transport ([0002](../adr/0002-raw-tcp-telnet-protocol.md)), single-thread event-loop concurrency ([0003](../adr/0003-single-thread-event-loop-concurrency.md)).
- **M1-A (0.1.0)** — event-loop skeleton in `src/server.cyr`. Non-blocking listener; `epoll`-shape multiplex; absolute-time tick scheduling (`next_tick += 2500ms`, drift-resistant catch-up); SIGINT / SIGTERM shutdown via `signalfd` in the same epoll set; no-op `advance_tick()` placeholder for M4.
- **M1-B (0.1.0)** — per-connection session struct in `src/session.cyr`. Heap-alloc via `lib/freelist.cyr` at accept, freed at disconnect ([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md)). Rx 4 KB + tx 4 KB buffers with on-demand EPOLLOUT arming; CRLF-line echo stub pending the M1-C parser. Smokes: single-client round-trip, 32-way concurrent fanout, 100-line single-session byte-exact, SIGINT exit 0.
- **M1 (0.2.0)** — milestone closed. The wire and the loop are complete.
  - **M1-C** — RFC 854 IAC parser (`src/telnet.cyr`); pure DATA/IAC/OPT/SB/SB_IAC state machine, escaped-IAC + malformed-SB recovery, one `TelnetState` per session feeding a decoded-line accumulator.
  - **M1-D** — RFC 1143 Q-method negotiation; WILL ECHO + WILL SGA announce salvo on connect, naive-refuse for untracked options, no renegotiation loops.
  - **M1-E** — login flow (MOTD → name → MOTD-2 → command prompt); name captured + validated (2–16 alnum, leading letter, reserved handles refused), unauthenticated pending M6.
  - **M1-F** — 5-minute idle sweep over an intrusive session list (`SS_NEXT`/`SS_PREV`), `YD_IDLE_MS` override; best-effort tx drain on teardown.
  - **M1-G** — `benches/bench_telnet.bcyr` IAC-parser baseline (≈ 6 ns/byte mixed, ≈ 5 ns/byte data).
  - **M1-H** — `@stats` admin verb (connections, logged-in, ticks, tick-drift p99). Gate met: 32 concurrent connect→login→disconnect, sessions reclaimed, tick p99 drift < 10 ms.
- **M2 (0.3.0)** — the verb-noun parser (`src/parser.cyr`), pure and fuzz-clean. Tokenizer (M2-A) → verb table + aliases (M2-B) → keyword-prefix direct-object resolution (M2-C) → preposition / indirect-object split (M2-D) → `all.X` / `N.X` qualifiers (M2-E) → 100k-input fuzz harness (M2-F, `fuzz/parser_fuzz.fcyr`). `cmd_on_line` routes through the parser; `quit` disconnects via the new `SS_QUIT` flag. Object/world binding deferred to M3 — the resolution matchers run against synthetic scopes for now. Gate met: fuzz clean against 100k random inputs; verb table covered by the 154-assertion suite.
- **M3 (0.4.0)** — the world becomes physical. [ADR 0005](../adr/0005-zone-file-format.md) picks CYML for zone files; the loader (`src/world.cyr`, M3-B) builds an in-memory room tree at boot and rejects dangling exits. Movement (M3-C) with onlooker broadcasts, ANSI room rendering (M3-D), inspection verbs (M3-E, `examine` resolving the M2 parser against live room presence), room-scoped `say`/`emote` + cross-room `tell` + `who` (M3-F), and the authored 21-room Hub starter zone (M3-G, `data/zones/hub.rooms.cyml`). Gate met: two players walk the Hub end-to-end seeing each other's arrivals / departures / says; 174-assertion suite.
- **M4 (0.5.0)** — the combat tick. Mobs (`src/mob.cyr`) and items/corpses (`src/item.cyr`) load from `<zone>.mobs/.objs.cyml`; combat (`src/combat.cyr`) resolves a hidden-roll round per tick inside `advance_tick` (M4-A/B/C/D), with `kill`/`flee`, death → corpse + loot, and player respawn (M4-E/F). The Hub gains a bestiary (scavver → Foundry Sentinel boss) and loot tables. Gate met: `benches/bench_combat.bcyr` ticks 32 players × 64 mobs at p99 ≈ 62 µs (50 ms budget); 203-assertion suite.
- **M5 (0.6.0)** — the four classes (`src/classes.cyr`, `data/classes.cyml`). Class selection at login (M5-A), per-class attributes + combat profile (M5-B), and twelve abilities (M5-C..F) on an energy + tick-cooldown + status framework (M5-G) that composes with the auto-attack. Gate met: each class clears the Hub solo and kills the Foundry Sentinel without dying (M5-H); 232-assertion suite.

---

## v1.0 criteria

A release qualifies for 1.0 when:

1. **M0–M8 + hardening have all shipped at least once.**
2. **`cyrius audit` passes from a clean build** (lint / test / bench / doc).
3. **TCP / Telnet server accepts concurrent player sessions reliably** — connect → log in → walk a zone → engage combat → die / loot / quit, across N simultaneous sessions without state corruption.
4. **Verb-noun parser handles the full v1.0 verb table without ambiguity** — fuzz harness clean against 100k random inputs.
5. **Combat tick (2.5s) runs deterministically under load** — drift < 50 ms p99 with all four classes engaged across N players × M mobs.
6. **Zone reset semantics enforced** — no respawn while players present; respawn within the reset window once empty.
7. **T.Ron-backed persistence** — players survive `kill -9` mid-tick; no data loss.
8. **Joshua game management interface online for live ops** — operator can list / kick / ban / broadcast / reload zones.
9. **Security audit pass logged** in `docs/audit/YYYY-MM-DD-audit.md`.
10. **Benchmarks captured** in `docs/benchmarks.md` (tick throughput, parser p99, connection capacity).
11. **CHANGELOG complete** from v0.1.0 onward.

---

## Open ADRs

The decisions queued ahead of their consumer milestones:

- **ADR 0004 — Identity & authentication model.** Name+password (DikuMUD/CircleMUD tradition, era-correct, no key-management UX cost) vs sigil Ed25519 (AGNOS-ecosystem aligned, agora-precedented, no password-on-wire — but Telnet has no TLS so plaintext passwords are the same problem). Resolved before **M6-B**.
- ~~**ADR 0005 — Zone file format.**~~ **Resolved 2026-06-09** → [ADR 0005](../adr/0005-zone-file-format.md): **CYML** (`lib/cyml.cyr`), one file per zone per entity kind (`<zone>.rooms/.mobs/.objs.cyml`), ≤ 32 entries/file. Header fields + markdown prose body per entry.
- **ADR 0006 — Persistence shape with T.Ron.** Per-player file vs single-store transactional log vs hybrid. Depends on T.Ron's transactional API surface as of M6 landing. Resolved at **M6-A**.

Filed when their first consumer lands; numbered in flight, not pre-allocated.

---

## Out of scope (for v1.0)

- **Windows client support.** Telnet clients exist on every platform; not our problem.
- **Native web client.** Telnet-over-WebSocket bridges (existing OSS) cover this without us shipping browser code.
- **TLS on the wire.** Operators wrap the listener in `stunnel` or an SSH tunnel for non-LAN deployments — see [`SECURITY.md`](../../SECURITY.md) and [ADR 0002](../adr/0002-raw-tcp-telnet-protocol.md).
- **PvP arenas.** Post-v1.0 if demand emerges.
- **Player housing.**
- **Voice / audio.**
- **Native graphics.**
- **MUD-specific protocol extensions** (MCCP, MSP, MXP, GMCP). Additive — they don't break the base Telnet contract, but they aren't on the v1.0 path.
- **Federated identity / cross-server character portability.**
- **Mod / plugin loader.** The whole game is one binary in v1.0; in-tree content additions land via PR, not runtime load.

---

## Cross-references

- [`state.md`](state.md) — live state snapshot (current version, in-flight slot, **next-agent boot guide**).
- [`../architecture/overview.md`](../architecture/overview.md) — system design.
- [`../adr/`](../adr/) — architecture decision records.
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — per-tag chronology.
- [`../../CLAUDE.md`](../../CLAUDE.md) — durable agent-session rules.
