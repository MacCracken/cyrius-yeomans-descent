# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-11-02 (v1.8.1)
>
> **Future-facing only.** It covers what is left on the 1.x line, the 2.0.0
> milestones, and a backlog for after 2.0. Shipped work is in
> [`CHANGELOG.md`](../../CHANGELOG.md).
>
> The gate-sweep write-ups (re-runs #2–#5, items A–BT, per-release detail
> through 1.8.0) were removed from this file at 1.8.1. They are kept in git:
> `git show a9e7dc1:docs/development/roadmap.md`. Live tree state is in
> [`state.md`](state.md), design in
> [`../architecture/overview.md`](../architecture/overview.md), and decisions in
> [`../adr/`](../adr/).

---

## What is left

In the order it should happen.

| # | Next | What | Blocks |
|---|---|---|---|
| **1** | [Re-measure BU at 6.7.18](#1-bu--nobody-can-log-in-on-a-real-agnos-kernel) | One QEMU run. The code BU faults in changed in this bump, and nobody has looked since | the 1.x gate |
| **2** | [BU · BJ · AA](#the-agnos-lib-conversation--bu-bj-aa) | One upstream conversation about what vendored `lib/` owes the AGNOS target. These are decisions, not patches | the 1.x gate |
| **3** | [1.8.x in-repo work](#18x--in-repo-work) | The instruments gate re-run #6 needs, plus small fixes (AB, H, CI `--locked`, binary size) | re-run #6 |
| **4** | [Gate re-run #6](#gate-re-run-6) | After 1–3. Must come back with no critical or high finding | the 1.x gate |
| **5** | [2.0.0](#milestones--the-20-line) | M14 contract + schema v2 · M15 zone registry · M16 progression · broadcast fan-out (K) · donation bin (Q) · loot ceiling (BT) | — |
| — | [Backlog](#backlog--after-200) | M17–M23, Joshua, deferred and unclaimed features | reorganised when 2.0.0 ships |

**The minimum credible 2.0 is M14 + M15 + M16**: the contract, the content
ceiling, and progression. Everything after that can slip without embarrassing
the release.

---

## 1.x — closing the line

### The gate

**The 1.x line closes when a gate re-run comes back with no critical or high
finding.** Gate re-run #5 (2026-07-31, against v1.7.20) returned **0 critical /
3 high / 5 medium / 4 low**. All three highs were on the AGNOS build. On x86_64
it came back with **zero highs**, the first time in seven sweeps. 1.7.21 closed
ten of #5's twelve findings. The QEMU harness built in that same release then
found **BU**, which is worse than any of them.

**So the gate is blocked by one target, through code this repo does not own.**

**There is a policy option, and it should be taken deliberately or not at all:**
scope AGNOS out of the 1.x gate. The case against it: item T (1.7.8) was an
AGNOS-only defect rated high and closed as high, and
[`running.md`](../guides/running.md) has advertised AGNOS as a supported
deployment since 1.1.0. If the call is made, it belongs in ADR 0007 as a contract
change, not in a sweep verdict.

### The AGNOS lib/ conversation — BU, BJ, AA

All three land in vendored `lib/` (off-limits here) plus the agnos kernel. Take
them upstream together.

#### 1. BU — nobody can log in on a real AGNOS kernel

*(high — found by the 1.7.21 QEMU harness)*

- **What breaks.** A player connects, is greeted, gives a name and is prompted
  for a passphrase. The server **dies the moment the passphrase is submitted**:
  `run: exit 142`, the kernel's ring-3 page-fault kill. Character creation and
  login have never worked on that target since `--agnos` shipped in 1.1.0.
  Everything before that point works: zone load, `sock_listen`, `sock_accept`,
  the MOTD, the Telnet salvo and name entry.
- **Where.** Bisected to `ident_derive`. The fault is in sigil's per-thread
  crypto scratch: the first call self-installs a TLS block
  (`crypto_tls_main_init` → `thread_local_get`). That is vendored `lib/` plus the
  kernel's TLS support. `src/main.cyr` already includes `lib/thread.cyr` and
  `lib/thread_local.cyr` explicitly, so the gap is deeper than an include.
- ⚠ **Do first: re-measure at 6.7.18.** 1.7.22 could say BU "did not move" because
  `lib/thread_local.cyr` was byte-identical across that bump. It is not
  identical across 1.8.1's: `lib/thread_local.cyr` changed by 245 lines and
  `lib/syscalls_x86_64_agnos.cyr` by 213, and sigil 3.13.15 restructured
  `cbank()`. The TLS self-install is still on the path (`cbank` →
  `_crypto_slot_get` → `crypto_tls_main_init`). Run `scripts/agnos-qemu-smoke.sh`
  (see [`running.md`](../guides/running.md); it needs `../agnos/build/agnos` built
  with `BENCH_CONNECT_SELFTEST=1`). If BU is gone, the gate's picture changes. If
  it stands, take the fresh trace upstream.

#### 2. BJ — one stalled client freezes the whole AGNOS server

*(high — a decision, not a patch)*

- `session_drain` treats only `-11` (Linux `EAGAIN`) as would-block. On AGNOS,
  `sys_write` on a socket is the blocking `sock_send` (#48), which has no EAGAIN.
  So a full send window parks the single-threaded loop. Measured under emulation:
  a bystander's `look` went from 0.000 s to **15.7 s**.
- The read half already has its AGNOS branch (`session_on_readable_max`); the
  write half never got one.
- **Why it waits.** agnos exposes **no non-blocking send primitive**. Any fix here
  would be written against an API nobody has agreed to. It also only matters once
  BU is fixed, since until then nobody can log in to stall.

#### 3. AA — every accepted connection costs 16 bytes, forever

*(medium — a decision, not a patch)*

- `sock_accept` returns `Ok(cfd)`, and the payload is boxed with a bump
  `alloc(16)` in `lib/net.cyr`, on both arms. With no free, that is ~5.7 MB/hour
  at 100 connections/s, reachable before a single byte is read.
- **Descent's lever is the count:** either a non-allocating accept upstream, or an
  accept-*rate* bound here. `MAX_SESSIONS` and `ACCEPT_BACKOFF_TICKS` bound
  concurrency and accept errors, not the cumulative count.
- **Decide alongside it:** 256 silent sockets refuse legitimate connections (13 of
  14 probes in re-run #4) and refill as the 30 s reaper collects them. That is the
  same missing rate limit.

### 1.8.x — in-repo work

Everything here is fixable in this repo today, listed worst first. The first four
are the instruments re-run #6 needs.

- **The conservation invariant.** Assert `world + offline == authored` per object
  id as a test and as part of `cyrius audit`. Re-runs #4 and #5 both called it the
  highest-value instrument to build, and it would have caught AM, AZ, BC, BL and
  BT. Today nothing reads `g_obj_offline` directly, so every census measurement is
  a threshold oracle that cannot tell a phantom count of 1 from 5.
- **A CYML loader fuzz target.** `cyrius fuzz` covers the parser and the save
  record, but not the five CYML loaders. 31 hand-authored mutations held in re-run
  #4, which is a sample, not coverage. It matters more now: bayan 1.7 / 1.8
  changed how CYML marker lines are read, and a CRLF zone file that used to load
  as empty now loads.
- **Land the forged-signature harness.** It was built twice as a ~150-line
  throwaway in re-run #5 and produced BQ. It is the only way to test ADR 0004's
  stated threat model: the player owns the key their record is signed with.
- **Audit-chain self-hash verification.** #5 checked linkage only. Also decide how
  descent's own resume treats a **torn final record**. From 2.11.3, libro's
  verifiers reject one; descent's boot path does not call them.
- **AB — refuse each untracked Telnet option once per session.**
  `telnet_respond_refuse` answers every `IAC DO <x>` for an untracked option, so N
  repeats buy N replies. 1.7.9 made the reply atomic and the queue bounds it, so
  this is wasted work, not corruption. The fix is half-built: `TS_OPT_US` /
  `TS_OPT_HIM` have spare states. It changes RFC 1143 behaviour on a path with no
  test coverage, so test that path first. *(low)*
- **H — finish mutation-checking the pre-1.6.7 guards.** About 17 guards landed in
  1.6.0–1.6.6. Six were mutation-tested, and the two that came back uncovered (F, G)
  got tests in 1.7.3. **About 11 have never been checked.** *(low, test debt)*
- **CI: `cyrius deps --locked`.** CI's resolve step is a plain `cyrius deps`.
  `--locked` (cyrius 6.7.6+) resolves the tags, writes nothing, and fails naming
  each file that differs. That would make CI catch the lib/ divergence that 1.7.22
  and 1.7.24 each found by hand. It passes on the committed tree at 1.8.1.
- **Binary size.** 1.8.1 grew 41.6% (1.85 MB), and 57% even under `CYRIUS_DCE=1`
  (795 KB). Decide whether release builds use DCE. Attribute the growth between
  bayan 1.11 and the 6.7.18 compiler; that A/B needs moving the pin, because
  `cyrius build` re-vendors declared stdlib leaves.
- **`EPOLL_EVENT_SIZE` is declared twice.** `src/server.cyr`'s enum member shadows
  the stdlib `const` added in 6.7.12. Neither target warns and the values agree
  where it matters; use the stdlib's or rename it. *(hygiene)*

### Gate re-run #6

Run it after the AGNOS conversation and the instruments above. Use the same
protocol as #4 and #5: finders in isolated worktrees, required to build and run,
each attacked by an independent skeptic told to default to REFUTED. Aim it at
what #5 could not reach:

- **A real AGNOS kernel**, using the harness that has existed since 1.7.21. Cover
  every `YD_*` knob, zone reset, `save_sweep`, audit rotation, `passwd`, and the
  40-cell phase × tick matrix. On `--agnos` that matrix runs on the **second
  driver**, its own poll-loop `advance_tick`.
- **The conservation invariant under load**, and the CYML loader fuzz target.
- **A multi-hour soak in one run.** The best so far is 22.8 minutes. Kill by port
  or PID, never by name: a sibling agent's `pkill -f descent` ended #5's soak.
- **Audit rotation on `--agnos`**, and self-hash verification.
- **The heal state**, a `PHASE_CLASS` session with `SS_ROOM >= 0`. The PHASE_CMD
  gates in `room_say_broadcast`, `room_append_present`, `cmd_who` and
  `find_player_global` skip it, but `zone_has_player` counts it.

**Settled, so #6 does not re-derive them:**

- Two players under one tick: every contended ordering serialised and conserved
  (#4). The census defects were in accounting, not interleaving.
- `parse_uint` overflow is exact at both bounds (BE).
- `classes_upkeep` un-gated costs ≤0.4% of the drift allowance at `MAX_SESSIONS`.
- The rotation collision guard refused every same-name rotation. Marker coalescing
  cannot bite at shipped settings. `AUDIT_SEG_MAX` takes ~5,000 years to exhaust.
- Per-operation arena allocation is **0 bytes** across 14 verbs, every lifecycle,
  corpse decay, zone resets and all of `advance_tick` (1.7 M operations).
- The forged-record scalar-clamp battery held everywhere: extreme, zero, negative
  and malformed values, duplicate keys, key prefixes, `[player]` inside a value.
- `save_sweep` gating on `SS_AUTHED`: the differing cell is unreachable (refuted in
  #4).
- `drain_pending_rx`'s `SS_QUIT` arm overshoots by one signature per pass, by
  design (Z).

**Process rule that came out of #4:** when a fix changes a predicate, grep every
call site of it and every caller of the function it lives in, and record that
list in the fix's own comment. Three of #4's nine findings would have died to one
grep.

---

## Milestones — the 2.0 line

### Critical path

    M14 ──> M15 ──> M16
    M14 ──> everything touching a frozen surface (ADR 0007)

M10–M13 shipped in 1.3.0–1.5.0, so the save migration hook works and instances
have a free path. **One constraint binds every 2.0 milestone:** `_build_record`
signs with a key re-derived from the typed passphrase
([ADR 0004](../adr/0004-identity-and-authentication.md)), which the server never
holds. **There is no offline save migration, and there cannot be one.** Every 2.0
save field is additive, defaulted, and migrated lazily at login. That is also why
schema 2 should be the *last* schema bump of the 2.x line: fields added inside it
are read-with-default and ignored-if-unknown.

**Sizing.** The 2.0 gate (M14–M16) is on the order of five or six months of solo
evenings. Plan the gate, not the tail.

### M14 — ADR 0008 and save schema v2

**Depends on:** nothing open · **Blocks:** everything below

The contract change. [ADR 0007](../adr/0007-frozen-1.0-surface.md) says a 2.0 may
supersede it. This milestone is that supersession, written as a new ADR 0008
rather than an edit, so the 1.x contract stays readable for 1.x deployments.

- **M14-A — ADR 0008.** Supersedes 0007. Enumerate the frozen-for-2.x surface:
  verb table, `@`-namespace, schema 2 field set, wire behaviour, zone format (with
  its own `format` stamp) and env knobs. Record the no-offline-migration
  constraint as the reason schema 2 is the last bump.
- **M14-B — Schema 2.** Bump `SCHEMA_VERSION`. `v >= 2` reads the v2 path, else v1.
  Every v2 field is read-with-default, so a v1 record upgrades on its next login.
  Unknown keys are ignored, never fatal.
- **M14-D — Zone format stamp and strict field parsing.** Add a `format` key in the
  zone header and a `WL_ERR_FORMAT`. Under `format >= 2`, an unparseable value
  becomes a load error. Under an absent or `1` stamp, the 1.x fallback stays (a
  typo'd value reads as absent and takes its default). ADR 0007 §5 freezes the
  zone format for 1.x, so strictness has nothing to hang off until the format
  carries a version. *(The `parse_uint` overflow half closed as BE in 1.7.18; do
  not re-add a domain bound inside the shared reader.)*
- **M14-E — `validate` argv verb.** Offline zone and save validation, outside the
  command surface. It is also the natural home for an authored-prose 0xFF check;
  M10's gate covers player bytes, not authored files.

**Gate:** a 1.2.0 save loads, upgrades to schema 2 on login, and round-trips; a
schema-3 record is refused with the "newer server" message; ADR 0008 is Accepted
and 0007 is marked Superseded.

### M15 — Zone registry and the entry cap

**Depends on:** M14

The content ceiling. ADR 0007 §5 freezes the zone-file format, and a zone
*manifest* is a new file kind, which is why this is 2.0. Today
`MAX_ENTRIES = 32` and there is exactly one room table (`g_rooms`,
`g_room_count`, `g_zone_id`, `g_zone_reset_secs`, all single globals). The
world is capped at 32 entries, and 21 rooms of that are already used.

- **M15-A — Raise the cap.** The old plan said 255, because bayan's CYML scan
  stopped at 256 entries. **bayan 1.5.1 removed that truncation**, so re-derive
  the number from descent's own limits (load time, `bench_loaders`). Six files
  share the constant.
- **M15-B — Zone registry.** Replace the `g_zone_*` singletons with a table, give
  each zone its own reset timer, and make `world_load_rooms` a per-zone load. This
  is a rewrite of `world.cyr`'s ownership model, not an addition.
- **M15-C — Room-id namespacing.** Saves record location by **string room id**, so
  location survives multi-zone as long as ids stay unique across zones. Make a
  cross-zone duplicate a boot error. Do not rewrite authored ids into a dotted
  scheme; that breaks every existing zone file.
- **M15-D — Cross-zone exits.** Resolve exits across the registry, keeping
  dangling-reference rejection.
- **M15-E — Boot fallback.** A 1.x data directory holding only `hub.*.cyml` must
  still boot: try the manifest, fall back to the three `DP_*` paths as a synthetic
  single-zone registry, and make the fallback a tested path.
- **BT — mob loot is minted outside the object ceiling.** *(low, found by #5)*
  `corpse_of` mints loot with a bare `item_new` and no max-exist check, while
  `zone_reset_room_objs` consults `_obj_id_present`. Loot ids overlap authored
  ids, so a looted copy carried or saved pushes the count past the ceiling, and
  the authored copies never come back. The world ends up permanently
  **under**-stocked. This is the object-ownership question M15's registry owns.

**Gate:** two zones load and link; a player walks between them, and a reconnect
restores them to the right room in the right zone; a duplicate room id across
zones fails the boot loudly; a 1.2.0-shaped data directory still boots.

### M16 — XP, levels, and a death cost

**Depends on:** M14, M15

The thing a MUD is. Players have fixed class stats and never advance. `MT_LEVEL`
exists on every mob template and **nothing reads it**. `mob_died` already holds
both the killing session and the mob. `player_died` restores full HP and moves
the player to the start room at no cost.

- **M16-A — XP and the curve.** Award XP in `mob_died`, valued off `mt_level`.
  `xp` and `level` become schema-2 fields.
- **M16-B — Level-up.** HP, energy and stat progression on top of the class
  profile, so `apply_class` becomes the level-1 case of a curve.
- **M16-C — Ability gating.** The 12 class abilities unlock by level instead of
  all arriving at creation.
- **M16-D — Death cost.** Replace the free respawn with XP loss, a corpse run, or
  a resurrection cost. Pick one and write it down.
- **M16-E — Surface.** `examine me` and `who` show level. `who`'s output shape is
  frozen surface, which is why this is 2.0.

**Gate:** a fresh character levels from 1 to the cap through authored content; a
v1 save upgrades to level 1 with its stats intact; death imposes its cost and is
recoverable.

### Also in 2.0.0

**K — bound the broadcast fan-out.** *(needs a new `@stats` field, frozen until
M14)*

- Combat tick-body **p99 = 0.432 µs × N²** for N co-located, mutually engaged
  players. The 50 ms drift budget breaches at **N ≈ 345** (bracketed 336–352).
  `MAX_SESSIONS` is 256, so **the breach is 1.35× the population the server
  accepts.** At 256 the real cost is 26–28 ms.
- **The limiting term is measured:** with 256 sessions engaged and only the room
  split varying, `cost(k) = A/k + B`, where **A = 26.4 ms (96.7%) is the
  per-recipient prose append**. It is not the room walk. **Bounding fan-out means
  bounding the append.** Volume is 110 × N² bytes per tick, validated over real
  TCP at 250 players.
- Closing it means bounding fan-out at **every** broadcast site, and adding a
  tick-body occupancy counter to measure the result. Related unbudgeted walks:
  `room_say_broadcast`, `cmd_who`, `render_who`, `room_append_present`,
  `find_player_global`, `room_find_player`, `sessions_forget_mob`.
- **Do not subtract tick-body cost from the drift allowance.** That was proposed
  during 1.7.0 and is refuted in
  [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md).
- **The highest-leverage change is a sigil release:** `ed25519_verify` costs ~4.7×
  its own sign. Descent's own job is to avoid calling verify when the answer
  cannot matter, which 1.7.0 did.

**Q — the donation bin.** *(needs a zone field and a cap, both frozen by ADR
0007)*

Authored zone furniture never ground-decays, and `cmd_put` does not arm what
goes into it. So items put in a town barrel stay forever, uncapped and unwalked by
`look`. That is a feature people will want (a donation bin, a guild chest), but
today it exists by accident. A real bin needs to be **authored** (a zone field
marking a container persistent), **capped**, and **persistent across restarts**,
because floors are not saved today and a stash that a restart empties is a trap.
The interim behaviour is deliberate and documented at `cmd_put` in
`src/item.cyr`.

### v2.0 criteria

A release qualifies for 2.0 when:

1. **M14, M15 and M16 have shipped.** M17+ are not 2.0 gates.
2. **ADR 0008 is Accepted and ADR 0007 is marked Superseded**, with the 2.x
   surface enumerated as precisely as 0007 enumerated 1.x.
3. **Every 1.2.0 save loads and upgrades** to schema 2 on first login, with no
   data loss and no operator intervention.
4. **Every 1.x-authored zone file still loads**, or fails with a named error that
   says what to change.
5. **The world spans at least two linked zones**, and reconnect restores a player
   to the correct room in the correct zone.
6. **A character can level from 1 to the cap through authored content**, and death
   imposes a real, recoverable cost.
7. **Build, test, bench, fuzz and `cyrius audit` all pass.**
8. **`bench_combat` p99 stays inside the 50 ms drift budget** with the actor tick
   and progression live.
9. **No instance leak:** mob, object and corpse counts return to a bounded steady
   state under soak.
10. **CHANGELOG, README, `state.md` and this file are current.**

ADR 0008 is reserved for M14. The ADRs filed so far are 0001–0007 and 0009 (audit-log
rotation), indexed in [`../adr/README.md`](../adr/README.md).

---

## Backlog — after 2.0.0

> **Not scheduled.** When 2.0.0 ships, reorganise this section into 2.x releases
> and give each milestone a full entry once the one before it lands.

### M17–M23 — the 2.x tail

Sketched, not specified.

- **M17 — Equipment slots and item modifiers.** Real slots feeding
  `player_eff_ac` / `player_eff_hit` / `player_dmg_bonus`, which already exist
  as the hook. Item stat modifiers rely on the signed integer reader (shipped
  1.6.7).
- **M18 — Operator identity and a control channel.** Replace the `YD_ADMIN` env
  gate with real operator auth and an out-of-band channel. It probably earns its
  own ADR, since it adds a wire/auth surface. **It does not depend on Joshua.**
- **M19 — Threat, aggression, resistance.** Uses M13's actor tick. Authored
  `morale` and aggression keys land here.
- **M20 — Currency and shops.** Shopkeeper mobs, and a `scrip` currency held on the
  session rather than carried as instances. That needs an inventory migration for
  records that already hold one.
- **M21 — Titles, channels, ignore.** The first persisted *player-authored* prose;
  it depends on M10's wire-safe prose.
- **M22 — Offline state: mail, boards, guilds.** Consider libro rather than player
  saves; an append-only signed chain fits boards and mail better than a
  per-player record.
- **M23 — Parties and group play.** Shared XP and group targeting. Price it
  against the tick budget (K) before committing.

### Joshua operator interface (was M8)

Blocked upstream, and the old spec no longer matches its dependency. M8 assumed
"Joshua" was an AGNOS game-management CLI (`joshua mud players`, `kick`,
`broadcast`). [MacCracken/joshua](https://github.com/MacCracken/joshua) is
actually a Rust NPC-brain and simulation runtime, and it is **not yet ported to
Cyrius**, so `[deps.joshua]` cannot resolve. It has two prerequisites:

1. **Joshua is ported to Cyrius.** That is upstream work.
2. **The spec is rewritten against what Joshua is**, or the operator channel stands
   alone (M18) and Joshua integration becomes a separate concern.

The held sub-items from the old M8 are:

- **M8-A** dep landing *(blocked)*
- **M8-B** live player list *(needs M16's level)*
- **M8-C** kick and ban
- **M8-D** broadcast
- **M8-E** zone reload *(needs M15)*
- **M8-F** operator audit log

The existing groundwork stays valid either way: `@stats` / `@who` / `@reset`,
`g_session_head`, `g_zone_last_reset_ms = 0` to force a reset, and the libro
audit chain.

### Deferred — wanted, blocked on something

- **PvP.** Needs threat, equipment and levels to mean anything.
- **Crafting.** Needs currency, shops and item modifiers underneath it.
- **Quests.** Needs a per-player state machine (a schema conversation) and a lot of
  authored content.
- **Skills separate from levels.** A second progression axis; not worth it until
  the first is proven.
- **aarch64 in CI.** No longer blocked (1.6.14 fixed the epoll layout), but CI
  builds only native and `--agnos`. No ARM target is planned. Add the step before
  relying on the arm.

### Unclaimed — available on demand

Nothing has been decided against these, and nothing blocks them. They are only
waiting for a reason to want them.

- **Telnet NAWS, TERMINAL-TYPE and LINEMODE.** Refusing them is correct RFC 1143
  behaviour today, not a stub. Each would need a preference entry in
  `opt_pref_us` / `opt_pref_him` (`src/telnet.cyr`) plus subnegotiation handling;
  the SB state machine already collects the payload.
  - **NAWS** (window size) is small, and is the one to add first if output ever
    needs to wrap to width.
  - **TERMINAL-TYPE** is small, and would make ANSI colour conditional.
  - **LINEMODE** is the largest, and only matters for character-at-a-time mode.

  [ADR 0002](../adr/0002-raw-tcp-telnet-protocol.md) lists terminal-type discovery
  as in scope.

### Out of scope — decided against

Reversing one of these needs a new argument. Something merely unwanted for now
belongs in *Unclaimed*.

- **Windows client support.** Telnet clients exist on every platform.
- **Native web client.** Existing Telnet-over-WebSocket bridges cover it.
- **TLS on the wire.** Operators wrap the listener in `stunnel` or an SSH tunnel;
  see [`SECURITY.md`](../../SECURITY.md) and ADR 0002.
- **PvP arenas**, **player housing**, **voice / audio**, **native graphics**.
- **MUD protocol extensions** (MCCP, MSP, MXP, GMCP). They are additive, but not on
  the path to 2.0; reconsider on merit after it.
- **Federated identity / cross-server character portability.**
- **A mod / plugin loader.** The game is one binary, and content lands by PR.
  Runtime *zone* loading is a different thing, and is M15.

---

## Cross-references

- [`state.md`](state.md) — the live state snapshot and the next-agent boot guide.
- [`../architecture/overview.md`](../architecture/overview.md) — system design.
- [`../adr/`](../adr/) — architecture decision records.
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — per-tag chronology, including
  everything this file used to carry.
- [`../../CLAUDE.md`](../../CLAUDE.md) — durable agent-session rules.
