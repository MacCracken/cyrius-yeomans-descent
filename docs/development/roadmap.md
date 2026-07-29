# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-07-29 (v1.6.12 — sweep shipped; the line closes on a clean re-run)
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

**Shipped: 0.1.0 → 1.6.12.** Thirty-eight releases — M0–M7 to the 1.0 server,
the 0.8.x polish and 0.9.x hardening, M10–M13 across the 1.x line, and the
1.6.0–1.6.12 audit sweep. Per-tag detail is in
[`../../CHANGELOG.md`](../../CHANGELOG.md); the sweep's shape is
[below](#the-16x-audit-sweep); one-line milestone summaries are in
[Closed milestones](#closed-milestones).

### 2.0 line — planned

The 1.x line is **maintenance and foundations**: everything that touches no
ADR-0007-frozen surface. 2.0 is where the surface opens and the game becomes a
MUD rather than a well-built room-crawler.

| Tag | Theme | Status |
|---|---|---|
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

**No active cycle.** The tree builds, `cyrius audit` exits 0, and 706 assertions
+ 5 benches pass. Live state — versions, surface area, dep gaps — is in
[`state.md`](state.md); per-release history is in
[`../../CHANGELOG.md`](../../CHANGELOG.md). This section is only ever "what is
being worked on now", and the running commentary that used to accumulate here
has been removed: two of the stale-doc findings in 1.6.9 and 1.6.11 came from
exactly this kind of duplication.

**Next is another re-run sweep** — the gate. Everything both re-runs produced is
closed; what remains is a pass that comes back with no critical or high findings.
See [The gate](#the-gate--still-open).

**Then 2.0.0**, starting with **M14 — ADR 0008 + save schema v2**, which
everything else in the 2.0 line routes through. Read the
[critical path](#critical-path) first: saves are signed with a key derived from
the player's passphrase, which the server never holds, so **migration is
lazy-at-login and additive only**.

The public surface stays frozen until then
([ADR 0007](../adr/0007-frozen-1.0-surface.md)): command verbs, the
`@`-namespace, save schema v1, Telnet/wire behaviour, the zone-file format, and
the `YD_*` knob set.

---

## The 1.6.x audit sweep

**Status: shipped 1.6.0–1.6.12. The line is not closed — see *The gate* below.**

Per-release detail is in [`../../CHANGELOG.md`](../../CHANGELOG.md); this is the
shape of it, because the shape is the part worth remembering.

The 1.6.0 audit produced 56 findings, 44 verified, closed across 1.6.0–1.6.9 in
batches grouped by *kind of work* rather than severity, so each release had one
coherent theme and one coherent test story:

| | | |
|---|---|---|
| **1.6.6** A | state integrity | double login, template-id round trip, audit-chain resume |
| **1.6.7** B | content + parser | the `N.X` qualifier, `put`/`give`, signed `toml_int` |
| **1.6.8** C | resource + timing | broadcast coalescing, metered autosave, the tick schedule |
| **1.6.9** D | coverage, then re-run | `bench_persist`, `bench_loaders`, a soak, a docs sweep |
| **1.6.10** E | the re-run's critical + highs | `SS_QUIT` on the tick path, the drain budget, creation caps |
| **1.6.11** — | the re-run's tail | `render_who`, key wipes, loader unpublish, `put` round-trip |
| **1.6.12** — | the re-run's *second* critical | the event batch, both loops, `passwd` |

**Two re-runs, two sets of serious defects the previous pass missed.** 1.6.9's
re-run found a remote crash on a first-class command verb (`examine`
dereferencing `room_at(-1)`) that the original sweep never saw. 1.6.12's re-run
found an unbounded event batch — 4.12 s per batch — plus an unmetered `passwd`.

**The lesson, twice over: fixing an instance is not fixing the class.** 1.6.12's
critical was the fourth appearance of one defect — *a per-item cap is not a bound
on a loop that walks many items* — after three releases each capped a neighbour
of the open hole. Both questions that would have found it were one command away:
`grep -n ident_derive src/` enumerates every expensive-line path, and "every loop
that dispatches lines" enumerates every place a cap must be aggregate. When a
finding looks familiar, enumerate the class before writing the patch.

### The gate — still open

**The 1.x line closes when a re-run sweep comes back with no critical or high
findings.** That has not happened. Everything both re-runs produced is fixed and
`cyrius audit` is green, but each pass so far has found real defects, so the bar
stays where it is.

Everything currently known to be wrong is listed, worst first, in
[Open issues — needs repair](#open-issues--needs-repair). Nothing there is
critical or high; the two that can affect a running server are an inventory that
grows until saves stop, and an upstream libro allocation.

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

## Open issues — needs repair

Everything currently known to be wrong, worst first. Each entry says **what
breaks**, **whether it can happen to a running server today**, **whose code it
is**, and **how big the fix is** — in that order, because that is the order you
need to decide whether to care.

Verified against source at 1.6.12. Anything that turned out to be already fixed
has been deleted, not left here with a note.

---

### 1. A player who fills their inventory can never save again

**What breaks.** The save record is built into a fixed 4096-byte buffer
(`SAVE_CAP`). Inventory is written as a comma-joined list of item ids and
**nothing caps how many items a player may carry**. Once the list pushes the
record past the buffer, `_build_record` returns -1 and `player_save` reports
failure — and it does so on *every* subsequent save, forever, because the
inventory never shrinks on its own. The player keeps playing; nothing they do
after that point is persisted.

**Can it happen today?** **Yes.** No attacker needed — a player who hoards.
Roughly 190+ items on the shipped Hub id lengths. The failure is loud in the
audit log (`save.fail.sweep`) and silent to the player.

**Whose.** Ours — `src/persist.cyr`, the inventory loop in `_build_record`.

**Fix size.** Small: cap carried items (a `MAX_INV` checked in `cmd_get` /
`cmd_give`), or drop the overflow with a message rather than failing the whole
record. The cap is the honest fix; refusing the save is the current behaviour and
it is the wrong one.

---

### 2. Repeated failed logins burn memory that is never given back

**What breaks.** Every audit event costs ~1.6 kB from the bump allocator, which
has no `free`. 1.6.12 cut this to one event per connection instead of five, but
the per-event cost itself is inside libro's `filestore_append`, which rebuilds a
string builder on every append.

**Can it happen today?** **Yes, slowly.** Bounded per connection, unbounded
across reconnects. It needs sustained CPU saturation to matter, and the server is
already unusable from CPU at that point — so the distinctive harm is that memory
does not come back when the attack stops. A restart clears it.

**Whose.** **Upstream — libro.** `CLAUDE.md` forbids touching `lib/`. Descent's
own contribution is already zero.

**Fix size.** Needs a **libro 2.8.5** release, same shape as the 1.6.1 chain fix.
Not ours to land.

---

### 3. Character stats from `classes.cyml` aren't range-checked on creation

**What breaks.** 1.6.7 taught the config reader to accept negative numbers, and
1.6.11 clamped `hp` and `energy` on the creation path — but `str`, `dex`, `con`
and `tec` were missed, and the damage-dice profile (`ndice`/`dsize`) is unbounded
on both the class and mob paths. The *load* path clamps all of them; the
*creation* path does not, so the same field is checked when a saved character is
read and unchecked when a new one is made.

**Can it happen today?** **Only via an authored file.** `data/classes.cyml` and
the zone files are operator content, not player input — so this is a typo away,
not an attack. An unbounded `ndice` also feeds a `roll()` loop.

**Whose.** Ours — `src/classes.cyr` (`apply_class`), `src/mob.cyr`.

**Fix size.** Small — four `_clamp` calls and a dice bound, mirroring what
`player_auth_load` already does.

---

### 4. Class IDs are not zero-terminated

**What breaks.** A class id is copied into a 32-byte slot using all 32 bytes,
leaving no terminator. The two fields beside it (name, role) copy at most 31 for
exactly that reason.

**Can it happen today?** **No — dormant.** Every reader uses the stored length,
so nothing treats an id as a terminated string. It is a trap for the first piece
of code that does.

**Whose.** Ours — `src/classes.cyr:131`.

**Fix size.** One character: `CL_ID_CAP` → `CL_ID_CAP - 1`.

---

### 5. An ARM build would read session pointers from the wrong offset

**What breaks.** The event loop hardcodes the x86 layout of the kernel's
`epoll_event` struct — 12 bytes, pointer at offset 4. On aarch64 Linux the struct
is unpacked: 16 bytes, pointer at offset 8. The server would read a session
pointer out of the wrong bytes and dereference garbage.

**Can it happen today?** **No — dormant.** Descent builds x86_64 and agnos only.
It fires the first time anyone runs `--aarch64`.

**Whose.** Ours, and avoidably so: **the Cyrius stdlib already handles this**. It
ships a per-architecture `epoll_event_new` (x86_64 writes data at +4, aarch64 at
+8, with a comment explaining the split). Descent *uses* that helper to **write**
events and then hardcodes its own constants to **read** them back. The write path
is portable; only the read path is not.

**Fix size.** Small: derive the size and data offset per target the way the
stdlib does, instead of the local `EPOLL_EVENT_SIZE = 12`.

---

### 6. `epoll_event_new` allocates 16 bytes per accepted connection

**What breaks.** Every accept and every EPOLLOUT arm/disarm allocates a fresh
16-byte event struct from the non-reclaiming bump allocator.

**Can it happen today?** **Yes, but trivially** — 16 bytes per connection.
Listed for completeness, not because it needs doing.

**Whose.** Shared: the allocation is in the stdlib helper; the call frequency is
ours.

**Fix size.** Small — reuse one scratch event struct.

---

### Deferred by design, not forgotten

Two config-validation gaps are deliberately left open because fixing them would
reject zone files that load today, and ADR 0007 §5 freezes the zone format for
all of 1.x. Both are folded into **M14-D**, where a format version gives them
something to hang off:

- **Unparseable config values silently take the default** instead of erroring, so
  a typo'd field reads as "absent".
- **`parse_uint` has no overflow check** (`v * 10 + d`), so an absurd literal
  wraps to an arbitrary in-range value rather than being rejected. The
  `reset_secs` clamp makes that *harmless*, not *correct*.

## Milestones — 1.x (all shipped)

M0–M9 delivered the 1.0 server; M10–M13 delivered the 1.x line. One-liners for
each are in [Closed milestones](#closed-milestones) below, and the per-tag
chronology is in [`../../CHANGELOG.md`](../../CHANGELOG.md). **M8 (Joshua) was
moved to the backlog** — see that section for why, and note that the operator
work worth doing is **M18** and does not depend on it.

The detailed per-sub-item breakdowns that used to live here have been removed:
every one of them shipped, and keeping two copies of a finished plan is how the
stale-docs findings in 1.6.9 and 1.6.11 happened in the first place.

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

### M10–M13 — the 1.x line ✅ shipped

Wire-safe prose (M10, v1.3.0), the migration-gate repair (M11, v1.3.0), instance
lifecycle (M12, v1.4.0) and the actor tick (M13, v1.5.0). Detail in the
CHANGELOG; the constraint M11 established is restated in the critical path above,
because M14 depends on it.

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
- **M14-C — Signed-integer support.** ✅ **Pulled forward into 1.6.7** (batch B). `toml_int` accepts a leading `-`; the writer already emitted one. Additive and behaviour-preserving for every value that parsed before, so it did not need to wait for the contract change. M16/M17 can assume signed fields read back.
- **M14-D — Zone format stamp, strict field parsing, and integer-overflow rejection.** A `format` key in the zone header plus a `WL_ERR_FORMAT`, so zone authors get a real error instead of a misparse when the format moves again. **This is also where `toml_int` gets to be strict** — carried forward from 1.6.7 batch B, which fixed the signed gap but deliberately left the lenient fallback in place: a typo'd field still reads as "absent" and silently takes the default. Rejecting it would reject zone files that load today, and ADR 0007 §5 freezes the zone format for all of 1.x, so strictness has nothing to hang off until the format carries a version. Once it does: an unparseable value under `format >= 2` is a load error, and under an absent/`1` stamp it keeps the 1.x fallback. **Also carried here from 1.6.8 batch C:** `parse_uint` accumulates `v * 10 + d` with no overflow check, so an absurd authored literal wraps to an arbitrary value rather than being rejected. Every `toml_int` caller is affected — class stats, save fields, zone fields — which is why it did not land in a patch release.
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

## v1.0 criteria — met at 1.0.0

All ten criteria were met at the 1.0.0 tag (M0–M7 + the 0.8.x polish + 0.9.x
hardening; clean build/test/bench; concurrent sessions; fuzz-clean parser; tick
drift inside budget; zone-reset semantics; crash-safe signed persistence; the
0.9.0 security sweep; the ADR 0007 surface freeze; a complete CHANGELOG). The
checklist itself is retired — see [v2.0 criteria](#v20-criteria) for the live one.

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

## Out of scope

- **Windows client support.** Telnet clients exist on every platform; not our problem.
- **Native web client.** Telnet-over-WebSocket bridges (existing OSS) cover this without us shipping browser code.
- **TLS on the wire.** Operators wrap the listener in `stunnel` or an SSH tunnel for non-LAN deployments — see [`SECURITY.md`](../../SECURITY.md) and [ADR 0002](../adr/0002-raw-tcp-telnet-protocol.md).
- **PvP arenas.** Later, if demand emerges.
- **Player housing.**
- **Voice / audio.**
- **Native graphics.**
- **MUD-specific protocol extensions** (MCCP, MSP, MXP, GMCP). Additive — they don't break the base Telnet contract, but they are not on the path to 2.0 either.
- **Federated identity / cross-server character portability.**
- **Mod / plugin loader.** The whole game is one binary; in-tree content additions land via PR, not runtime load. (Runtime *zone* loading is a different thing and is M15.)

---

## Cross-references

- [`state.md`](state.md) — live state snapshot (current version, in-flight slot, **next-agent boot guide**).
- [`../architecture/overview.md`](../architecture/overview.md) — system design.
- [`../adr/`](../adr/) — architecture decision records.
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — per-tag chronology.
- [`../../CLAUDE.md`](../../CLAUDE.md) — durable agent-session rules.
