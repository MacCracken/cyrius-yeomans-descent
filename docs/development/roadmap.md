# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-07-28 (v1.6.2 — pre-auth DoS fixed; the 1.x line is closed)
>
> Milestone plan through v1.0 (shipped) and on to v2.0. State lives in [`state.md`](state.md);
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
| **0.9.1** | Surface freeze — public surface locked ([ADR 0007](../adr/0007-frozen-1.0-surface.md)) + save `schema` stamp + `@`-admin gated | ✅ 2026-06-10 |
| **1.0.0** | Clean release — final hardening + playtest sign-off | ✅ 2026-06-10 |
| **1.1.x** | AGNOS build target, telnet echo fix, dep-sidecar migration | ✅ 2026-07-02 |
| **1.2.0** | Toolchain 6.4.83 + libro 2.8.2; first clean `cyrius audit` | ✅ 2026-07-28 |

### 2.0 line — planned

The 1.x line is **maintenance and foundations**: everything that touches no
ADR-0007-frozen surface. 2.0 is where the surface opens and the game becomes a
MUD rather than a well-built room-crawler.

| Tag | Theme | Status |
|---|---|---|
| **1.3.0** | M10 — wire-safe prose · M11 — migration-gate repair | ✅ 2026-07-28 |
| **1.4.0** | M12 — instance lifecycle: free the leaks, decay the corpses | ✅ 2026-07-28 |
| **1.5.0** | M13 — the actor tick: mobs get agency | ✅ 2026-07-28 |
| **1.6.0** | Hardening sweep — toolchain 6.4.86 + libro 2.8.3; UAF, inventory leak, hp clamp | ✅ 2026-07-28 |
| **1.6.1** | Audit-chain bound via upstream libro 2.8.4 (`chain_new_streaming`) | ✅ 2026-07-28 |
| **1.6.2** | Pre-auth CPU exhaustion — dispatch cap, bare-CR guard, passlen hoist, attempt cap | ✅ 2026-07-28 |
| **2.0.0** | M14 — ADR 0008 + save schema v2 · M15 — zone registry + entry cap · M16 — XP, levels, death cost | planned |
| **2.1.0** | M17 — equipment slots + item modifiers · M18 — operator identity + control channel | planned |
| **2.2.0** | M19 — threat, aggression, resistance · M20 — currency and shops | planned |
| **2.3.0** | M21 — titles, channels, ignore · M22 — offline state (mail / boards / guilds) | planned |
| **2.4.0** | M23 — parties and group play | planned |

**The minimum credible 2.0 is M14 + M15 + M16** — the contract, the content
ceiling, and progression. Everything from M17 on can slip to 2.x without
embarrassing the release.

---

## In progress

**No active cycle.** 1.2.0 closed — a toolchain (6.3.32 → 6.4.83) and dependency (libro 2.7.10 → 2.8.2) upgrade plus the first clean `cyrius audit` run. It repaired a `main` that no longer compiled, a bench that no longer compiled, a `version` verb two releases behind, and three latent symbol-collision hazards; see [CHANGELOG 1.2.0](../../CHANGELOG.md). The public surface remains frozen ([ADR 0007](../adr/0007-frozen-1.0-surface.md)): command verbs + `@`-namespace, save-record schema v1 (stamped + version-gated), Telnet/wire behaviour, zone-file format, env knobs. The `@`-admin namespace is gated behind `YD_ADMIN` (default off).

**1.3.0 shipped** — M10 (wire-safe prose) and M11 (migration-gate repair), 333 assertions (was 298). M10 fixed a live cross-player defect: a bare Telnet IAC in a `say` reached every listener's protocol stream unescaped, verified end-to-end with two real clients before and after. M11 repaired the four latent defects in the save migration gate that would otherwise have shipped *with* the 2.0 schema bump they protect.

**1.4.0 shipped** — M12 (instance lifecycle), 346 assertions. The milestone under-stated the problem: `alloc()` has no `free()` at all, so instances had to *move* to the freelist rather than simply gain a reclaim path. Corpses now decay after 120 ticks (~5 min), taking un-looted contents with them. The use-after-free trap was real and landed first: every session reference to a dying mob is cleared, not just the killer's. `bench_combat` p99 1422 µs, unmoved by the new per-tick sweep.

**1.5.0 shipped** — M13 (the actor tick), 373 assertions. Mobs wander, assist and flee; wander is leashed to within one room of home after the first live run walked the boss into the newbie start room. The zone reset now counts by `MI_HOME`, which it had to before wander could ship. p99 1338 µs — the actor tick is not measurable at Hub scale.

**1.6.0 shipped — the 1.x line is closed.** Toolchain 6.4.86, libro 2.8.3, and an eight-lens hardening sweep with every finding adversarially refuted. Three fixes landed, all mutation-verified: a use-after-free that 1.5.0's actor tick had activated (a mob dereferencing a disconnected player's freed Session), a remotely-driven unbounded inventory leak at disconnect, and `hp` never being clamped against `maxhp` on load. 385 assertions.

**Next is 2.0.0**, starting with **M14 — ADR 0008 + save schema v2**, the gate everything else routes through. Read the critical path above first: saves are signed with a key derived from the player's passphrase, which the server never holds, so **migration is lazy-at-login and additive only**. Pickup pointer in [`state.md`](state.md).

---

## Backlog — Joshua operator interface (was M8)

**Unscheduled. Blocked on an upstream port, and the spec no longer matches its
dependency.** M8 was written against a "Joshua" that is an AGNOS game-*management*
CLI — `joshua mud players`, `joshua mud kick <name>`, `joshua mud broadcast`.
[MacCracken/joshua](https://github.com/MacCracken/joshua) is something else: a
v0.1.0 **Rust** "AI-native game manager and simulation runtime" — NPC perception
and memory, deterministic replay, scene format, engine/physics bridges, mood and
pathfinding integrations. Its own README says it is not a game engine; it is an
NPC brain. It is also **not yet ported to Cyrius**, so `[deps.joshua]` cannot
resolve at all today.

Two independent prerequisites, in order:

1. **Joshua ports to Cyrius** (`cyrius port`, the Rust → Cyrius migration path).
   Upstream work, not descent's.
2. **The M8 spec is rewritten against what Joshua actually is** — or descent's
   operator control channel is designed to stand alone, and Joshua integration
   becomes a separate, later concern. Kick/ban/broadcast/reload do not need an
   AI simulation runtime; they need a control channel and operator auth.

Nothing here blocks the 2.0 line. Operator auth — replacing the `YD_ADMIN` env
gate, which is the part with real security value — is tracked in the 2.0
milestones below and deliberately does **not** depend on Joshua.

**Held sub-bites, verbatim from the old M8:**

- **M8-A — Joshua dep landing.** Pull Joshua into `cyrius.cyml [deps]`. *(Blocked: not ported.)*
- **M8-B — Live player list.** `joshua mud players` → name / class / level / location / idle-time / connection-time. *(Note: "level" does not exist yet — see M16.)*
- **M8-C — Kick & ban.** `joshua mud kick <name>` (terminate session); `joshua mud ban <name> [--for <duration>]` (refuse reconnect).
- **M8-D — Broadcast.** `joshua mud broadcast <message>` → server-wide announcement rendered to every live session.
- **M8-E — Zone reload.** `joshua mud reload <zone>` → re-parse the zone file, replace the in-memory zone tree, evict mobs that no longer exist, relocate players whose room was deleted.
- **M8-F — Operator audit log.** Every operator action appends to `docs/audit/operator.log` with operator identity + timestamp + target.

The groundwork that already exists stays valid whichever way this resolves:
`@stats` / `@who` / `@reset` (`render_*` in `server.cyr`, gated by `YD_ADMIN`),
`g_session_head` for session enumeration, `g_zone_last_reset_ms = 0` to force a
reset, and the libro audit chain as the operator-action log.

---

## Post-1.0 backlog — known bugs

Surfaced playing the AGNOS build (1.1.x) over telnet. The 1.0 Telnet/wire surface is
frozen ([ADR 0007](../adr/0007-frozen-1.0-surface.md)) — these are wire-behaviour
**fixes**, not surface changes, so they don't need a major bump.

### B1 — Telnet line discipline in character mode (1.1.x)

A conformant telnet client that honours the connect-time **WILL SGA** switches to
character-at-a-time mode and stops cooking the line locally — but the server only does
full server-side line editing for the passphrase (`session_push_line_byte`'s `is_pass`
path). For normal input (name, class selection, commands) the discipline is incomplete:

- **Return displays `^M`.** The raw CR (0x0D) isn't consumed/cooked; the client renders
  it literally — e.g. `Enter a number or name: teacher^M`.
- **Enter doesn't advance.** The line isn't dispatched cleanly (CR-in-stream / char-mode
  handling), so e.g. class selection doesn't move forward.
- **Backspace doesn't delete — shows `^?`.** DEL (0x7F) / BS (0x08) aren't handled for
  normal input; the client renders the raw control char instead of erasing.

**Root cause:** character-at-a-time mode (induced by WILL SGA) requires the server to own
the full line discipline — echo, CR→CRLF + dispatch, backspace erase, strip CR from the
buffer — for *all* input, not just the passphrase. The 1.1.1 echo change (dropped WILL
ECHO, kept WILL SGA) made the raw control chars visible.

**Fix options (pick one):**
1. **Full server-side line editing for all phases** — extend the `is_pass` handling in
   `session_push_line_byte` to every phase: echo each char, draw CR/LF on Enter, erase on
   backspace, never buffer the CR (`*` mask stays passphrase-only). Server owns the line.
2. **Drop WILL SGA from `telnet_announce`** — keep the client in pure line-mode (it cooks
   backspace + CR locally and sends a clean line); raise WILL ECHO only around the
   passphrase (already done via `session_echo_off`). Simpler; the conventional MUD model. *(Recommended.)*

**Status:** Option 2 shipped at **1.1.2** — the connect-time option salvo is dropped, so
cooked-mode clients (`telnet` / `nc` / Mudlet) now get working backspace, clean Enter, and no
`^M` / `^?`, with the passphrase still masked. **Remaining (review later):** Option 1 — full
server-side line editing for character-at-a-time clients — only matters if descent later
re-adopts WILL SGA / char-mode for advanced client features. Parked until then.

Verify against `telnet`, `nc`, and Mudlet; QEMU-repro via `agnosticos/docker/descent-sweep/`
(`./run.sh serve` → telnet in).

### B2 — `world_load_classes` leaves a live half-table on a mid-file error (1.2.0)

`world_load_classes` (`src/classes.cyr`) sets `g_class_count = n` **before** its parse
loop, then can `return WL_ERR_NOID` / `WL_ERR_KIND` from inside it. The caller
(`src/server.cyr`, `var cc = world_load_classes(DP_CLASSES)`) only prints a message on
a negative return and never zeroes the count — so a malformed entry partway through
`data/classes.cyml` leaves a live table whose trailing records are zeroed, and
`apply_class` will stamp `hp = 0` / `maxhp = 0` / `ac = 0` / `energy = 0` onto a player
who picks one. The failure is silent: it presents as a 0-HP character, not as
"no classes loaded". Fix: set `g_class_count` only on success, or zero it on every
error path. Authored content, so not player-reachable — a robustness bug, not a
security one.

### B3 — `CL_ID` is copied at `CAP`, not `CAP - 1` (1.2.0)

`src/classes.cyr` does `copy_str_capped(c + CL_ID, CL_ID_CAP, id)` while the adjacent
name/role copies use `CL_NAME_CAP - 1` / `CL_ROLE_CAP - 1`. A full 32-byte id therefore
fills the buffer with no NUL and abuts `CL_ID_LEN` at offset 32. Safe **today** only
because `cl_id_eq` and `class_id_prefix` iterate by `CL_ID_LEN` and never treat
`CL_ID` as a cstr — a latent trap for the first caller that does. Fix: use
`CL_ID_CAP - 1` for consistency with every other inline-string field.

### B4 — `epoll_event` layout is hardcoded to the x86 packed struct

`src/server.cyr` — `EPOLL_EVENT_SIZE = 12` with `load32(events_buf + ev_off)` and
`load64(events_buf + ev_off + 4)`. That is the x86_64 **packed** layout. aarch64 Linux
uses the unpacked 16-byte struct with `data` at offset 8. Not hit today (descent builds
and runs x86_64 + agnos), but the first `--aarch64` build that runs will read a
corrupt session pointer out of every epoll event. Fix: `#ifdef CYRIUS_ARCH_AARCH64`
the size and the data offset together.

### B5 — Instances are never freed; corpses are never removed

`mob_spawn` (`src/mob.cyr`) takes each instance from `alloc(MI_SIZE)`; `mob_remove`
only unlinks it from the room occupant list. `item_new` and `corpse_new`
(`src/item.cyr`) likewise use `alloc(OI_SIZE)`, and **no corpse is ever removed
from a room** — there is no decay path at all. Every kill and every zone reset
leaks, and rooms accumulate corpses for the process lifetime, which is exactly
descent's deployment shape. Mobs and objects use `alloc`, not the per-session
`fl_alloc` arena, so disconnect does not reclaim them either.

Scheduled as **M12**, not a drive-by fix: `mob_died` clears only the *killing*
session's `SS_TARGET`, so a second attacker still holds the pointer across ticks.
That is inert today precisely *because* nothing is reclaimed — the first free
turns it into a use-after-free onto a recycled instance.

### B6 — The save-record writer is unbounded

`_ac` / `_ap` / `_ai` / `_fstr` / `_fint` (`src/persist.cyr`) append into the
4096-byte `g_persist_save` with **no** bounds check against `SAVE_CAP`; the only
guard in `_build_record` is inside the inventory loop. Safe today only because
`name` is capped at 16 and room ids are short — but it is a write-side overflow
that no amount of load-side clamping prevents, and every variable-length 2.0
field would land on it. Fix: make the appenders fail closed and check once at the
end of `_build_record`. Scheduled as **M11-D**, ahead of any new save field.

### B7 — Signed integers do not round-trip through a save

`toml_int` (`src/mob.cyr`) routes through `parse_uint` and returns the caller's
default on a negative parse, while the writer `_ai` uses `fmt_int_buf`, which
*does* emit a sign. So the record writer can produce a value the reader silently
discards and replaces with a default. **Latent, not confirmed live** — no v1
schema field appears to reach a negative value in practice, and the obvious
candidate (`hp` going negative in combat) is reset by `player_died` within the
same tick. But the first genuinely signed field — an item `ac` modifier, a class
whose AC improves with level — would fail silently. Fix: a signed reader
(**M14-C**) before M16/M17 need one.

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

- **M3-A — Zone file format.** Pick a serialization — likely `lib/cyml.cyr` or `lib/toml.cyr`. Decision recorded as **ADR 0005** ([see ADRs](#adrs)). Format covers zone metadata, rooms (id / title / prose / exits / mob spawns / object spawns), mob templates, object templates.
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

### M6 — Persistence via libro + sigil (v0.7.0) ✅

Players survive server restart. Crash-safe writes. Queued — disk I/O cannot block the loop ([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md) negative consequence). **Shipped at 0.7.0.** (Originally framed "via T.Ron"; the t-ron repo is an MCP security monitor and is not used — the crash-safe primitive is **libro**, with **sigil** for identity. See [ADR 0006](../adr/0006-persistence-shape.md).)

**Sub-bites (as shipped):**

- **M6-A — dep landing.** `[deps.libro]` 2.7.1, pulling sigil/sakshi/patra/agnosys transitively; the required opt-in stdlib listed in `cyrius.cyml`.
- **M6-B — Identity model.** [ADR 0004](../adr/0004-identity-and-authentication.md): **Ed25519 keypair derived from `SHA-256(salt‖passphrase)`** (sigil) — server stores only salt + pubkey.
- **M6-C — Player save shape.** Attrs (STR / DEX / CON / TEC + class), inventory (template ids), location (room id), HP / energy / combat profile, identity (salt + pubkey), creation / last-login timestamps. (No level/XP — not implemented.)
- **M6-D — Save triggers.** On `quit`, on `save`, on character creation, and on a debounced ~5-minute tick sweep — **queued, never inline** in the loop.
- **M6-E — Load on login.** Look up by name; restore full state into a session struct; place into the recorded room (or starter Hub if the room no longer exists).
- **M6-F — Crash-safe writes.** Atomic file replacement (write to `.tmp` + rename). Each record is Ed25519-signed; partial writes are discarded on next start.

**Gate met:** `kill -9` mid-tick during active combat → restart → no player data loss; the player respawns at their last room with full attrs / inventory.

### M7 — Zone resets (v0.8.0) ✅

Mobs and loot respawn. Players don't get respawn-stomped. **Shipped at 0.8.0.**

**Sub-bites (as shipped):**

- **M7-A — Per-zone reset timer.** Configurable per zone via the `reset_secs` header field (the Hub uses 15 min); `YD_RESET_SECS` overrides. Tracked from last reset, not last server start.
- **M7-B — Player-presence gate.** Reset checks every room in the zone; if any room contains a connected player, defer the reset to the next tick. (Empty-zone check is single-writer per [ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md) — no race.)
- **M7-C — Mob respawn.** From zone-file mob spawns; full HP; tops each room up to its authored mob multiset (living mobs not duplicated).
- **M7-D — Loot respawn.** Object spawns reapplied; existing objects in the room left in place (no double-up, matched by template id).
- **M7-E — Reset event log.** Each reset writes a single line: `[ts] zone=X reset (rooms=N, mobs=M, objs=O)` — for the operator interface (post-1.0) to read.

**Gate met:** empty zone resets within its window; a zone with a player in any room does not reset; reset event log matches observed state.

### M8 — Joshua management interface — **moved to backlog**

No longer a scheduled milestone. It was blocked on an upstream Cyrius port and
specced against a dependency that turned out to be a different product. The full
sub-bite list and the reasoning are held in
[Backlog — Joshua operator interface](#backlog--joshua-operator-interface-was-m8)
above. The operator work with real value — replacing the `YD_ADMIN` env gate with
operator authentication — is **M18**, and deliberately does not depend on Joshua.

### M9 — Hardening → 1.0 (executed across 0.9.0 / 0.9.1 / 1.0.0)

The closeout. Rather than one milestone, this shipped as the 0.9.x line: the
security sweep at **0.9.0**, the surface freeze at **0.9.1** ([ADR 0007](../adr/0007-frozen-1.0-surface.md)),
and the clean release at **1.0.0**.

**Sub-bites:**

- **M9-A — Security audit (✅ 0.9.0).** Full sweep over every input path (Telnet bytes, command lines, zone files, save files), buffers, and syscall consumers. Found + fixed two heap overflows (one pre-auth), an OOB read, and a DoS; documented in the CHANGELOG 0.9.0 entry. (No Joshua RPC surface — M8 deferred.)
- **M9-B — CVE sweep (✅ 0.9.0).** Cross-checked against current CVE classes — telnet pre-auth option-negotiation overflows (CVE-2026-32746), Ed25519 malleability (CVE-2020-36843), MUD-family buffer/injection bugs. Applicability judged and documented.
- **M9-C — Benchmark baselines.** Combat-tick bench in `benches/`; parser/world p99 baselines remain a post-1.0 nicety (not a 1.0 gate).
- **M9-D — Public surface freeze (✅ 0.9.1).** [ADR 0007](../adr/0007-frozen-1.0-surface.md): command verbs + `@`-namespace, the save-record schema (now `schema`-stamped), Telnet/wire behaviour, the zone-file format, and the env knobs are locked for 1.x. Post-1.0 changes need a major bump or a `schema` migration.
- **M9-E — Closeout pass (1.0.0).** Full test suite (298 assertions), dead-code/DCE build, doc sync (README, guides, CHANGELOG, state.md), version verification (`VERSION` / `cyrius.cyml` / `VERSION_STRING` in lockstep).
- **M9-F — Internal playtest (1.0.0).** Multi-player session with the AGNOS internal cohort: crash-bug-free; no player-data corruption.

**Gate:** all v1.0 criteria (below) green.

---

## Milestones — the 2.0 line

### Critical path

Three things gate everything, and two ship in 1.x.

**M11** repairs the save migration hook *before* it becomes load-bearing.
`player_auth_load` reads `toml_int(pairs, "schema", SCHEMA_VERSION)`
(`src/persist.cyr:407`) — the default for a record with no `schema` key is the
*current* version, not the literal 1. Harmless while `SCHEMA_VERSION == 1`;
the instant it becomes 2, every pre-0.9.1 record claims to be v2 and skips the
v1 path. The bug ships **with** the bump unless it is fixed first.

**M12** gives instances a free path. `mob_spawn` (`src/mob.cyr`), `item_new` and
`corpse_new` (`src/item.cyr`) all take memory from `alloc`; `mob_remove` only
unlinks, and **no corpse is ever removed from a room**. Every milestone after
this one mints more instances, so the reclaim path must exist before they do.

**M14** is the 2.0 contract, and one discovery inside it binds every other
milestone: `_build_record` signs with the secret key re-derived from the typed
passphrase ([ADR 0004](../adr/0004-identity-and-authentication.md)), which the
server never holds. **There is therefore no offline save migration and there
cannot be one.** Every 2.0 save field must be additive, defaulted, and migrated
lazily at login. That is also why schema 2 should be the *last* schema bump of
the 2.x line: fields added inside schema 2 are read-with-default and
ignored-if-unknown, so equipment and currency do not each earn a bump.

    M11 ──> M14 ──> M15 ──> M16 ──> M17, M20, M23
    M12 ──> M13, M15, M17, M20
    M10 ──> M21, M22        (persisted player prose)
    M13 ──> M19             (threat needs a mob that can act)
    M14 ──> everything touching a frozen surface

**Honest sizing.** M10–M13 is on the order of six to eight months of solo
evenings; the 2.0 gate (M14–M16) another five or six; the full set through 2.4
is comfortably past two years. Plan the 2.0 gate, not the tail.

### M10 — Wire-safe prose (v1.3.0) ✅

**Line:** 1.x · **Status:** shipped

Player-authored bytes reach every other player's socket by raw `memcpy`.
`telnet_feed` *decodes* `IAC IAC` into a literal 0xFF data byte — that is correct
RFC 854 behaviour and the suite asserts it — but `session_push_line_byte` then
drops only `b < 32`, so 0xFF survives into the line buffer, and `cmd_say` hands
`buf + rs, len - rs` straight to `session_appendtx` and `room_say_broadcast`. A
player can put a bare IAC into a `say` and a conformant client on the other end
reads it as the start of a Telnet command. The comment at that filter —
"telnet IAC is already stripped upstream" — is wrong: IAC is stripped as
*framing*, and the escaped literal is deliberately preserved as data. Re-emitting
it unescaped is the bug. Touches no frozen surface, and it is the precondition
for 2.0 ever persisting player prose.

**Sub-bites:**

- **M10-A — `session_appendtx_prose`.** An escaping appender beside `session_appendtx`: double 0xFF to `IAC IAC`, drop C0/C1. It must be a **bounded writer** against `TX_CAP - SS_TX_LEN`, not a pure `(buf,len)` transform — `LINE_CAP` and `TX_CAP` are both 4096, so a 4096-byte all-0xFF `say` escapes to 8192, and `session_appendtx`'s silent truncation could cut *between* the two bytes of a pair and re-emit the very lone 0xFF this fixes.
- **M10-B — Route player bytes through it.** `cmd_say`, `cmd_emote`, both halves of `cmd_tell`, and the `body` parameters of `room_say_broadcast`. The `lead`/`tail` cstr parameters stay as they are — those are server literals. Authored room prose (`room_prose_ptr`, zero-copy into the CYML buffer) must **not** be sanitized, or zone authors lose formatting.
- **M10-C — Names too.** `room_broadcast`, `room_append_present`, `cmd_who`, `render_who`, `cmd_examine`'s player branch. `login_name_ok` already constrains names to leading-alpha alnum, so this is defence in depth — but it is the identical path M21's persisted `title` will use.
- **M10-D — Fuzz the sanitizer.** Every byte value at every position; no lone 0xFF survives; no partial escape pair at the buffer boundary. Test the C0/C1 branch by calling the sanitizer directly — ESC cannot reach it through `say` today, since the input filter drops everything `< 32`.

**Gate:** a session sending `IAC IAC` inside `say`/`emote`/`tell` produces no lone 0xFF in any other session's tx buffer, including at the truncation boundary; the sanitizer fuzzes clean across all 256 byte values.

### M11 — Migration-gate repair (v1.3.0) ✅

**Line:** 1.x · **Blocks:** M14 and every milestone that adds a save field
**Status:** shipped — all five sub-bites landed, 319 assertions (was 298),
`cyrius audit` exits 0 on both host and `--agnos`. One thing learned in the
doing: **M11-A cannot be proven while `SCHEMA_VERSION == 1`** — the old and new
defaults agree, so its regression test is a pin that only discriminates once M14
moves the constant. The test says so in place. M11-C and M11-D likewise guard
surfaces v1 cannot reach; both are unit-tested directly rather than end-to-end,
because an end-to-end test passes against the unfixed code and proves nothing.

Three defects in the migration hook, all latent at `SCHEMA_VERSION == 1` and all
load-bearing the moment it moves. The schema default (above). The same gate
returns the *same* error code as a failed `ed25519_verify`, so an operator who
rolls a deploy back tells every returning player their record "has been tampered
with". And `_find_sig_offset` ends the signed prefix at the first line beginning
`sig ` — harmless while no field can carry a newline, fatal the first time a 2.0
field carries free text. Nothing observable changes when this lands, which is
exactly why it must not be folded into the bump it protects.

**Sub-bites:**

- **M11-A — Default the stamp to a literal.** Add `SCHEMA_V1 = 1` to `enum PersistConst`; the gate reads `toml_int(pairs, "schema", SCHEMA_V1)`. Identical today, correct after the bump. Also introduce the test seam the regression floor needs — `SCHEMA_VERSION` is a compile-time enum member and the suite compiles the same `persist.cyr`, so make the ceiling a settable `var` or an `#ifdef`, and name the mechanism here.
- **M11-B — Separate "too new" from "tampered".** A distinct `PL_ERR_SCHEMA` and a third branch: *"Your record was written by a newer server than this one."* No `SEV_SECURITY` audit entry. Still refuses the session — a downgraded server must not half-load a v2 record.
- **M11-C — Refuse signed-prefix splitting.** Reject any record whose `name` / `room` / `inv` value contains a byte `< 0x20`, before those values are trusted.
- **M11-D — Bound the record writer.** `_ac` / `_ap` / `_ai` / `_fstr` / `_fint` do **no** bounds check against `SAVE_CAP`; the only guard is inside the inventory loop. Safe today only because `name ≤ 16` and room ids are short — but every variable-length 2.0 field would write unguarded into a 4096-byte buffer. Make the appenders fail closed and check once at the end of `_build_record`. This is the sub-bite that makes every later additive field safe by construction.
- **M11-E — Regression floor.** Extend `test_freeze`: a stampless record loading as v1 under a schema-2 ceiling; `schema = 0`; a non-integer `schema`; the planted-newline record; the negative-integer round-trip from B7.

**Gate:** a record with no `schema` key loads through the v1 path under a schema-2 ceiling; a `schema = 3` record disconnects with the "newer server" message and writes no tamper audit entry; an over-long record fails the write instead of overflowing.

### M12 — Instance lifecycle (v1.4.0) ✅

**Line:** 1.x · **Blocks:** M13, M15, M17, M20 · **Status:** shipped

The milestone under-stated the problem: `alloc()` has no `free()` at all, so this
was not "add a reclaim path" but "move instances onto the freelist", the only
reclaiming allocator available. `fl_alloc` reuses blocks **without zeroing**,
which the old bump-allocated code silently depended on — `mob_spawn` now memsets.

Nothing the world creates is ever reclaimed. Mob instances come from
`alloc(MI_SIZE)` and `mob_remove` only unlinks them; object and corpse instances
come from `alloc(OI_SIZE)` and corpses are never removed from a room at all. On a
long-lived server — descent's entire deployment shape — every kill and every zone
reset leaks, and rooms silently fill with corpses. This is both the memory fix and
the gameplay fix, and it must precede anything that mints instances faster.

**Sub-bites:**

- **M12-A — Corpse decay.** A tick-driven sweep retiring corpses after N ticks, and the room-render change that follows. This is the one site in 1.x where an instance genuinely leaves the object graph, so it is also the only place a free is unambiguously safe.
- **M12-B — Free rule.** State it as *"free only where an instance leaves the object graph entirely."* Not "free at `ilist_remove`" — that is the **move** primitive (`cmd_get` does `ilist_remove` then `ilist_push`), and freeing there would destroy every `get`.
- **M12-C — The dangling-target hazard.** `mob_died` clears only the *killing* session's `SS_TARGET`. A second session that also engaged still holds that pointer across ticks. Today that is inert because nothing is ever reclaimed and `combat_round`'s `mi_hp(m) <= 0` guard catches it. **The moment M12 frees anything, that becomes a use-after-free onto a recycled instance.** Deferring the free to end-of-tick does not fix it. Every reference must be cleared — sweep sessions on death, or carry a generation counter.
- **M12-D — Live counters.** `lib/freelist.cyr` exposes no occupancy accessor and CLAUDE.md forbids modifying `lib/`, so the gate needs descent-side `g_mob_live` / `g_obj_live`, incremented on create and decremented on free.

**Gate:** a soak of N zone resets with combat returns `g_mob_live` / `g_obj_live` to a bounded steady state; no room accumulates corpses without bound; the suite gains a use-after-free regression for the two-attacker case.

### M13 — The actor tick: mobs get agency (v1.5.0) ✅

**Line:** 1.x · **Depends on:** M12 · **Blocks:** M19 · **Status:** shipped

One thing the milestone did not anticipate: **wander needs a leash.** The first
live run walked the Foundry Sentinel out of `foundry.overseer` and into the
newbie start room. Mobs are now bounded to within one room of `MI_HOME`. The
proper per-template "does not roam" flag is frozen surface and stays M19's.
Also load-bearing: the zone reset had to start counting by home rather than by
current room, or every reset would have duplicated each wandered mob.

Mobs stand still until hit. Give them a turn: wander, assist, flee at low health.
This is the last big 1.x item because it needs no new zone field — thresholds are
hardcoded constants here, and authored `morale` / aggression keys are M19's
business, since a `kind = "mob"` key is frozen surface. Note the interaction with
`maybe_zone_reset`'s presence gate: wandering mobs change what "the zone is empty"
means. Everything here is paid out of the 50 ms p99 tick budget, and the bench
must be re-run per sub-bite.

**Sub-bites:**

- **M13-A — Mob turn in `advance_tick`.** O(living mobs), not O(rooms). Budget it.
- **M13-B — Wander.** Movement between rooms with onlooker broadcasts, respecting the reset presence gate.
- **M13-C — Assist and flee.** Room-mates join a fight; a mob below a hardcoded `MORALE_FLEE_PCT` disengages and moves.
- **M13-D — Bench.** `bench_combat` re-baselined with the actor tick live; the drift budget re-verified with mobs moving, not just swinging.

**Gate:** mobs wander, assist, and flee; an occupied zone still defers its reset correctly; `bench_combat` p99 stays inside 50 ms with the actor tick active.

### M14 — ADR 0008 and save schema v2 (v2.0.0)

**Line:** 2.0 · **Depends on:** M11 · **Blocks:** everything below

The contract change. [ADR 0007](../adr/0007-frozen-1.0-surface.md) says plainly
that "a 2.0 may supersede it"; this milestone is that supersession, and it should
be a new ADR 0008 rather than an edit — the 1.x contract stays readable for anyone
maintaining a 1.x deployment. The binding constraint is the one named in the
critical path: saves are signed with a key derived from the player's passphrase,
which the server never has, so **migration is lazy-at-login and additive only.**

**Sub-bites:**

- **M14-A — ADR 0008.** Supersede 0007. Enumerate the new frozen-for-2.x surface: verb table, `@`-namespace, schema 2 field set, wire behaviour, zone format (with its own `format` stamp), env knobs. Record the no-offline-migration constraint as the reason schema 2 is designed to be the last bump of the line.
- **M14-B — Schema 2.** Bump `SCHEMA_VERSION`; `v >= 2` reads the v2 path, else v1. Every v2 field is read-with-default so a v1 record upgrades silently on the next successful login. Unknown keys are ignored, never fatal.
- **M14-C — Signed-integer support.** `toml_int` routes through `parse_uint` and returns the default on a negative, while the writer `_ai` uses `fmt_int_buf`, which emits a sign. Nothing v1 appears to go negative today, so this is latent — but the first signed field (an item `ac` modifier, a class whose AC improves with level) would silently read back its default. Add a signed reader before M16/M17 need it.
- **M14-D — Zone format stamp.** A `format` key in the zone header plus a `WL_ERR_FORMAT`, so zone authors get a real error instead of a misparse when the format moves again.
- **M14-E — `validate` argv verb.** Offline zone/save validation, outside the command surface. Also the natural home for an authored-prose 0xFF check (M10's gate covers player bytes, not authored files).

**Gate:** a 1.2.0 save loads, upgrades to schema 2 on login, and round-trips; a schema-3 record is refused with the "newer server" message; ADR 0008 is Accepted and 0007 marked Superseded.

### M15 — Zone registry and the entry cap (v2.0.0)

**Line:** 2.0 · **Depends on:** M12, M14

The content ceiling, and the reason it is 2.0 rather than 1.x: ADR 0007 §5 freezes
the zone-file format, and a zone *manifest* introduces a new file kind and new
header keys. That is a strictly larger §5 change than the entry cap — the plan
cannot hold one integer to 2.0 and ship a new file type in a minor. Today
`MAX_ENTRIES = 32` and there is exactly one room table (`g_rooms`,
`g_room_count`, `g_zone_id`, `g_zone_reset_secs` — all single globals), so the
world is capped at 32 entries and 21 rooms of it are spent.

**Sub-bites:**

- **M15-A — Raise the cap.** `MAX_ENTRIES` to **255**, not 256: `bayan_cyml_parse` stops scanning at 256 entries, and descent's check is `n > MAX_ENTRIES`, so 256 would admit exactly the silently-truncated case. Four call sites share the constant.
- **M15-B — Zone registry.** Replace the `g_zone_*` singletons with a table; per-zone reset timers; `world_load_rooms` becomes a per-zone load. This is the architectural core of the milestone and it is a rewrite of `world.cyr`'s ownership model, not an addition.
- **M15-C — Room-id namespacing.** Saves already record location by **string room id**, not index — so location survives multi-zone for free, *provided ids stay unique across zones*. Make a cross-zone duplicate a boot error. Do not rewrite authored ids to a dotted scheme; that breaks every existing zone file.
- **M15-D — Cross-zone exits.** Exit resolution across the registry, with dangling-reference rejection preserved.
- **M15-E — Boot fallback.** A 1.x data directory holding only `hub.*.cyml` must still boot — try the manifest, fall back to the three `DP_*` paths as a synthetic single-zone registry, and make the fallback a tested path.

**Gate:** two zones load and link; a player walks between them and a reconnect restores them to the right room in the right zone; a duplicate room id across zones fails the boot loudly; a 1.2.0-shaped data directory still boots.

### M16 — XP, levels, and a death cost (v2.0.0)

**Line:** 2.0 · **Depends on:** M14, M15

The thing a MUD is. Players have fixed class stats and never advance;
`MT_LEVEL` exists on every mob template and **nothing reads it**. `mob_died`
already holds both the killing session and the mob, so the XP hook has its
arguments in scope. `player_died` currently restores full HP and moves you to the
start room with no cost at all.

**Sub-bites:**

- **M16-A — XP and the curve.** Award in `mob_died`, valued off `mt_level` — the field goes live. `xp` and `level` become schema-2 fields.
- **M16-B — Level-up.** HP/energy/stat progression on top of the class profile, so `apply_class` becomes the level-1 case of a curve rather than the whole story.
- **M16-C — Ability gating.** The 12 existing class abilities gate by level instead of all arriving at creation.
- **M16-D — Death cost.** Replace the free respawn. XP loss, a corpse run, or a resurrection cost — pick one and write it down; the point is that death means something.
- **M16-E — Surface.** `examine me` and `who` show level. Note `who`'s output shape is frozen surface, which is why this is 2.0.

**Gate:** a fresh character levels from 1 to the cap through authored content; a v1 save upgrades to level 1 with its existing stats intact; death imposes its cost and is recoverable.

### M17–M23 — the 2.x tail

Sketched, not specified. Each earns a full entry when the milestone before it
lands and the design is real rather than aspirational.

- **M17 — Equipment slots + item modifiers (2.1.0).** Real slots feeding `player_eff_ac` / `player_eff_hit` / `player_dmg_bonus`, which already exist as the hook. Item stat modifiers need M14-C's signed reader.
- **M18 — Operator identity + control channel (2.1.0).** Replace the `YD_ADMIN` env gate with real operator auth and an out-of-band channel. **Deliberately independent of Joshua** — see the backlog above.
- **M19 — Threat, aggression, resistance (2.2.0).** Needs M13's actor tick to have a turn to spend. Authored `morale` / aggression keys land here.
- **M20 — Currency and shops (2.2.0).** Shopkeeper mobs, a `scrip` currency folded into the session rather than carried as instances — which needs an inventory migration for records that already hold one.
- **M21 — Titles, channels, ignore (2.3.0).** The first persisted *player-authored* prose; hard-depends on M10.
- **M22 — Offline state: mail, boards, guilds (2.3.0).** Consider libro rather than player saves — it is already a dep and is an append-only signed chain, which is a better fit for boards and mail than a per-player record.
- **M23 — Parties and group play (2.4.0).** Shared XP and group targeting; price it against the tick budget before committing.

---

## v2.0 criteria

A release qualifies for 2.0 when:

1. **M14, M15 and M16 have shipped** — the contract, the world, and progression. M17+ are not 2.0 gates.
2. **ADR 0008 is Accepted and ADR 0007 is marked Superseded**, with the 2.x surface enumerated as precisely as 0007 enumerated 1.x.
3. **Every 1.2.0 save loads and upgrades** to schema 2 on first login, with no data loss and no operator intervention.
4. **Every 1.x-authored zone file still loads**, or fails with a named error that says what to change.
5. **The world spans at least two linked zones**, and reconnect restores a player to the correct room in the correct zone.
6. **A character can level from 1 to the cap through authored content**, and death imposes a real, recoverable cost.
7. **Build, test, bench, fuzz and `cyrius audit` all pass** — the 1.2.0 gate, held.
8. **`bench_combat` p99 stays inside the 50 ms drift budget** with the actor tick and progression live.
9. **No instance leak** — mob, object and corpse counts return to a bounded steady state under soak.
10. **CHANGELOG, README, `state.md` and this file current.**

## Deferred to 2.x and beyond

- **Joshua integration** — blocked on an upstream Cyrius port and a spec rewrite. See the backlog above. Operator control (M18) deliberately does not wait for it.
- **PvP** — needs threat, equipment and levels to be meaningful first. Post-2.0.
- **Crafting** — needs currency, shops and item modifiers underneath it.
- **Quests** — needs a state machine per player, which is a schema conversation, and a lot of authored content.
- **Skills separate from levels** — a second progression axis; not worth it until the first one is proven.
- **aarch64** — B4 must be fixed before any ARM target runs, but no target is planned.
- Everything in the v1.0 **Out of scope** list below still stands, except that PvP and MUD protocol extensions move from "not our problem" to "post-2.0, on merit".

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
- **M4 (0.5.0)** — the combat tick. Mobs (`src/mob.cyr`) and items/corpses (`src/item.cyr`) load from `<zone>.mobs/.objs.cyml`; combat (`src/combat.cyr`) resolves a hidden-roll round per tick inside `advance_tick` (M4-A/B/C/D), with `kill`/`flee`, death → corpse + loot, and player respawn (M4-E/F). The Hub gains a bestiary (scavver → Foundry Sentinel boss) and loot tables. Gate met: `benches/bench_combat.bcyr` ticks 32 players × 64 mobs inside the 50 ms budget; 203-assertion suite. (The p99 ≈ 62 µs figure recorded here at 0.5.0 is **stale** — the bench stopped compiling at some point before 1.2.0 and was only repaired there. Measured at the 1.2.0 cut: **p99 ≈ 1.4–1.7 ms**, still far inside budget, but the two numbers are not comparable — the current compilation unit includes `persist.cyr` and a newer codegen.)
- **M5 (0.6.0)** — the four classes (`src/classes.cyr`, `data/classes.cyml`). Class selection at login (M5-A), per-class attributes + combat profile (M5-B), and twelve abilities (M5-C..F) on an energy + tick-cooldown + status framework (M5-G) that composes with the auto-attack. Gate met: each class clears the Hub solo and kills the Foundry Sentinel without dying (M5-H); 232-assertion suite.
- **M6 (0.7.0)** — player persistence via **libro + sigil** (`src/persist.cyr`). Ed25519 identity derived from a passphrase ([ADR 0004](../adr/0004-identity-and-authentication.md)); crash-safe signed per-player CYML saves with `.tmp`+rename writes ([ADR 0006](../adr/0006-persistence-shape.md)); load+auth on login; libro audit chain. Gate met: `kill -9` mid-tick → restart → no data loss.
- **M7 (0.8.0)** — zone resets (`src/server.cyr` `maybe_zone_reset`, `mob.cyr`/`item.cyr` respawn). Per-zone `reset_secs` timer, player-presence gate (defer while occupied), mob/loot top-up without duplication, reset event log. Gate met: empty zone resets in window; occupied zone defers.
- **0.8.1–0.8.3** — polish: password echo suppression + `passwd` verb + last-seen greeting (0.8.1); lived-in Hub room objects (0.8.2); `@who` / `@reset` operator verbs (0.8.3).
- **0.9.0** — security sweep: CVE-class audit + two heap-overflow / OOB / DoS fixes (save-load validation; "a signature proves authorship, not field validity").
- **0.9.1** — surface freeze ([ADR 0007](../adr/0007-frozen-1.0-surface.md)): save `schema` stamp; `@`-admin gated behind `YD_ADMIN`.

---

## v1.0 criteria

A release qualifies for 1.0 when:

1. **M0–M7 + the 0.8.x polish + 0.9.x hardening have all shipped.** (M8 — the Joshua operator interface — is deferred post-1.0 and is **not** a 1.0 gate.)
2. **Build + test + bench pass from a clean build.**
3. **TCP / Telnet server accepts concurrent player sessions reliably** — connect → log in → walk a zone → engage combat → die / loot / quit, across N simultaneous sessions without state corruption.
4. **Verb-noun parser handles the full v1.0 verb table without ambiguity** — fuzz harness clean against 100k random inputs.
5. **Combat tick (2.5s) runs deterministically under load** — drift < 50 ms p99 with all four classes engaged across N players × M mobs.
6. **Zone reset semantics enforced** — no respawn while players present; respawn within the reset window once empty.
7. **libro + sigil-backed persistence** — players survive `kill -9` mid-tick; no data loss; Ed25519-signed, validated-on-load records.
8. **Security sweep passed** — memory-safety + CVE-class audit complete, all findings fixed (0.9.0); save-load validation in force.
9. **Public surface frozen** — [ADR 0007](../adr/0007-frozen-1.0-surface.md); save records `schema`-stamped; `@`-admin gated behind `YD_ADMIN`.
10. **CHANGELOG complete** from v0.1.0 onward; README + guides current.

---

## ADRs

All ADRs are filed and **Accepted** — none open at 1.0. Index in [`../adr/README.md`](../adr/README.md):

- [0001](../adr/0001-tick-based-combat-over-cooldowns.md) tick-based combat · [0002](../adr/0002-raw-tcp-telnet-protocol.md) raw TCP/Telnet · [0003](../adr/0003-single-thread-event-loop-concurrency.md) single-thread event loop
- [0004](../adr/0004-identity-and-authentication.md) Ed25519 identity from a passphrase (resolved at M6) · [0005](../adr/0005-zone-file-format.md) CYML zone format (M3) · [0006](../adr/0006-persistence-shape.md) per-player signed saves + libro audit (M6)
- [0007](../adr/0007-frozen-1.0-surface.md) frozen 1.0 surface (0.9.1)

Two land in the 2.0 line: **ADR 0008** supersedes 0007 with the 2.x surface
contract (M14), and the operator control channel (M18) earns its own if it adds a
new wire/auth surface — which it will, since it replaces the `YD_ADMIN` gate.

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
