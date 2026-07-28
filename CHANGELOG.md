# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.6.3] — 2026-07-28

**The accept path, and the `save` verb.** Two more findings from the 1.6.0 sweep.

### Fixed

- **Fd exhaustion pinned a core and leaked 2.3 MB/s.** `handle_accept` treated
  every non-`Ok` `sock_accept` as "backlog drained", so `EMFILE`/`ENFILE` were
  indistinguishable from `EAGAIN`. The listener is level-triggered — nothing here
  sets `EPOLLET` — so a pending-but-unacceptable connection made `epoll_wait`
  return instantly, forever. And where the `EAGAIN` path hands back a shared
  singleton (`lib/net.cyr`, added at 6.4.61 precisely to avoid this), a real
  error boxes a **fresh `Err`** every pass from the allocator that never frees.

  Measured at an fd limit of 48 with 60 idle sockets over 15 s:

  | | before | after |
  |---|---|---|
  | CPU | **99.9% of one core** | **0.0%** |
  | RSS drift | **+33,876 kB** | **+596 kB** |

  Three changes: `handle_accept` now compares `err_code_of` against
  `_NET_EAGAIN`; a real error **disarms the listener** in epoll and the tick
  re-arms it after `ACCEPT_BACKOFF_TICKS`; and `MAX_SESSIONS` (256) caps
  concurrent sessions, closing over-cap connections rather than leaving them
  pending. `g_session_count` had been incremented, decremented and printed by
  `@stats` since M1-H, but never **compared** to anything.

  **Suppressing the accept alone was not enough** — that fixed the leak and left
  the core at 99.9%, because a level-triggered listener stays readable whether or
  not you accept it. Taking the interest off epoll is what stops the spin.
- **The `save` verb had no rate limit.** `player_save` is ~1.2 ms, nearly all
  `ed25519_sign`, plus a file write, a rename and an audit append — and
  `SS_AUTHED` was the only gate, so 4 KB of `save\r` was 819 signed writes.
  Now gated on `SS_LAST_SAVE_MS`, which `persist.cyr` has always written and
  nothing ever read. Deliberately **not** on `SS_SAVE_DIRTY`: `cmd_on_line`
  re-sets that flag *after* `cmd_dispatch` returns, so every line in a burst sees
  it set and a dirty-gate would be a no-op against exactly this pattern.

### Notes

- Suite **399 → 410**. Mutation-verified: neutering the save gate fails 1,
  stopping `listener_disarm` clearing its flag fails 2.
- The rate-limit rule is a named predicate (`save_rate_limited`) rather than
  inline in `cmd_dispatch`. The first version of its test drove `cmd_dispatch`
  on a bare test session and **segfaulted** — it needs a full session, parser and
  world. A test that cannot run proves nothing; the predicate is testable on its
  own.
- 1.6.2's dispatch cap already meters the *rate* of both attacks; 1.6.3 caps the
  *work* each one can demand. They are complementary, not redundant.

## [1.6.2] — 2026-07-28

**Pre-auth CPU exhaustion.** One 4 KB write from an unauthenticated connection
froze the entire single-threaded loop (ADR 0003) for seconds — every other player
stalled with it. Measured against a bystander's time-to-first-byte:

| 4 KB burst | before | after |
|---|---|---|
| `wrong\r` × 682 (a name with a save record) | **5,232 ms** | **13 ms** |
| bare `\r` × 4096 | **27,145 ms** | **0.4 ms** |

### Fixed

Four changes, one defect chain. None touches an ADR 0007 frozen surface.

- **`session_consume_rx` had no dispatch cap.** It fed every byte of a 4 KB read
  and dispatched every complete line, then zeroed `SS_RX_LEN` regardless. Now it
  stops after `RX_MAX_LINES` (8) completed lines and **retains** the rest.
  The resume point is a **byte** index, not a line index: `telnet_feed` is a
  byte-at-a-time state machine and an IAC sequence can straddle the cut, so
  resuming anywhere else would resurrect the split-IAC case that machine exists
  to handle.
- **Retained bytes are drained on the tick** (`drain_pending_rx`). epoll is
  level-triggered on *socket* data — nothing here sets `EPOLLET` — so once bytes
  are off the socket and into `rx` it will not fire again for them. Without this
  a capped remainder would sit unprocessed until the client happened to send
  more. Metering per tick is the point: a burst is spread across ticks at 8 lines
  each and the loop stays responsive throughout.
- **A bare CR dispatched an empty line.** The LF branch has always guarded
  `len == 0`; CR never did, so 4096 bare CRs cost 4096 full login attempts. This
  is why the CR burst was 5× worse than the wrong-passphrase one.
- **The passphrase length bounds ran *after* the expensive work** — after
  `file_read_all`, `toml_parse` **and** `ed25519_verify` (~7 ms). Hoisted above
  the record read. Same semantics: 0, a re-promptable wrong passphrase.
- **`login_on_pass` re-prompted forever.** Now capped at `MAX_LOGIN_FAILS` (5)
  *consecutive* failures, then the session closes; a success resets the count.
  Hardcoded — ADR 0007 §6 freezes the `YD_*` knob set for 1.x.

### Changed

- `SS_PLAYER` → **`SS_FAILS`**. That slot was declared at M1-B and never read by
  anything in the tree; reused for the attempt counter rather than growing the
  Session struct.
- `session_push_line_byte` now returns 1 when it completed and dispatched a
  line — the signal the cap meters on.

### Notes

- Suite **390 → 399**. All three guards mutation-verified: removing the dispatch
  cap fails 3, the bare-CR guard fails 1, the passlen hoist fails 4.
- **A measurement correction worth recording.** The first before/after run
  reported 65 s → 60 s and looked like the fix had barely helped. The instrument
  was wrong: it timed a full socket *drain*, which waits out its own timeout
  after the banner arrives, so both readings were pinned at the timeout. Switched
  to time-to-first-byte and rebuilt a pre-fix binary for a like-for-like
  comparison — the table above. The corrected "before" figures (5.2 s / 27.1 s)
  match the audit sweep's independent estimates (5.2 s / 28 s).
- The existing 0.9.0 assertion `over-long salt hex rejected before decode` used a
  1-byte passphrase, which the hoist now short-circuits — it would have kept
  passing while silently no longer reaching the salt-length check. Given an
  in-range passphrase so it still exercises that path, and the short-circuit
  itself got its own assertions.

## [1.6.1] — 2026-07-28

**Bounds the audit chain, via an upstream libro fix.** `[deps.libro]` `2.8.3` →
**`2.8.4`**.

### Fixed

- **The in-memory audit chain no longer grows without bound.** `audit_event`
  appended on every login / save / security event, and `g_audit_chain` is
  **never read** — nothing in this tree calls `chain_verify` / `chain_len` /
  `chain_by_*` on it; durability is `filestore_append`. It was also not fixable
  from here: `chain_new()` leaves `max_capacity` at 0 so `_chain_auto_rotate`
  never fires, there was no capacity constructor, `chain_apply_retention`
  redistributes into fresh vecs while archived entries stay referenced, and
  libro had one `fl_free` in ~4,400 lines, none of it on the entry path.

  libro **2.8.4** adds `chain_new_streaming()` — a chain that links every entry
  exactly as before (each records its predecessor's hash, so the durable chain
  in `data/audit.libro` verifies identically) but retains none of them, keeping
  only the head hash in the `prev_hash` carry-over slot `_chain_prev_link`
  already falls back to. descent now uses it, and `entry_free`s each entry once
  the store has it.

### Notes — measured honestly

- **RSS does not move, and is the wrong instrument.** A 260 s / 42-login soak
  reads +624 kB against a +636 kB baseline. Two reasons, both structural: the
  `Str`s each entry carries (timestamp, hash, algorithm, plus descent's own
  source / action / details) come from the **bump allocator**, which has no
  `free` at this layer; and freelist memory is never returned to the OS. What
  1.6.1 removes is the **unbounded term** — one vec slot and one 88-byte entry
  struct per event, forever. A smaller per-event `Str` residue remains and needs
  an allocator-level fix, recorded in libro 2.8.4's CHANGELOG.
- `chain_len` is the honest instrument, and the new assertions use it: 50 audit
  events must retain nothing.
- **`entry_free` is gated on `chain_streaming`.** Freeing is correct only
  because the chain retains nothing; on a retaining chain the entries vec still
  references the entry and the next `_chain_prev_link` reads freed memory —
  verified, it segfaults (exit 139). Rather than trust two lines to stay in
  step, the free is conditional. Mutation-reverting the constructor now fails
  three assertions cleanly instead of crashing.

### Changed

- Hardening fixes retagged **M14-A/B/C → H1/H2/H3**. `M14` already belongs to
  the 2.0 contract (ADR 0008 + save schema v2) in the roadmap, and
  `roadmap.md:225` already referenced an **M14-C** for the signed reader — two
  different M14-Cs existed in one tree. Caught by the 1.6.0 sweep.

Suite **385 → 388**.

## [1.6.0] — 2026-07-28

**Hardening sweep, closing the 1.x line.** Toolchain `6.4.83` → **`6.4.86`**,
libro `2.8.2` → **`2.8.3`** (a pure toolchain refresh upstream — zero `src`
changes). Then an eight-lens audit of the whole tree with every finding put
through an independent refuter.

### Fixed

- **Use-after-free: a mob kept pointing at a disconnected player — a regression
  1.5.0 introduced.** `drop_session` frees a Session on quit / idle-reap /
  socket close and never walked the mob lists, so a mob the player had engaged
  (`cmd_kill` → `mi_set_target(m, s)`) held `MI_TARGET` into freed memory.
  That was **inert until 1.5.0**: `MI_TARGET` had only ever been *compared*
  (`combat_disengage`), never followed. M13's `_mob_assist` reads it and then
  dereferences — `var s = mi_target(other); … load64(s + SS_ROOM)` — so the actor
  tick turned a dormant dangling pointer into a live use-after-free. Worse,
  `fl_free` returns the block to the size class the next `session_new` draws
  from, so the read can land on a **live, different player** and hand that
  session to a second mob as its target.
  New `mobs_forget_session` — the exact mirror of 1.4.0's `sessions_forget_mob`,
  the same hazard pointing the other way — called from `drop_session` before the
  free.
- **A disconnecting player's inventory was never reclaimed.** `session_free`
  frees the rx / tx / line / name buffers and the ident block, and has never
  touched `SS_INV`, so every carried object leaked. Remotely driven and
  unbounded: connect, `get all`, `quit`, repeat. 1.4.0 gave objects a free path
  but only wired it to corpse decay; `session_drop_inv` is the other end of that
  job. Safe because the save record stores inventory by **template id**, not by
  instance — the player gets them back from a fresh `item_new` on next login.
- **`hp` was clamped to an absolute range but never against `maxhp`.** The two
  were validated independently, and nothing downstream ever pulls an over-max
  value back down: `classes_upkeep` regenerates only while `hp < max`,
  `ability_heal` caps on the way up, `player_died` assigns `hp = maxhp`. A
  re-signed record carrying `hp = 1000000, maxhp = 30` produced a permanently
  million-HP character. A player owns their signing key (ADR 0004), so this is
  the 0.9.0 rule again — a signature proves **authorship**, not field validity —
  extended to *relational* invariants, not just per-field ranges. Load-side
  only; no schema change.

### Notes

- Suite **373 → 385**. All three fixes mutation-verified: neutering
  `mobs_forget_session` fails 2, stopping `session_drop_inv` freeing fails 2,
  removing the `hp`/`maxhp` clamp fails 1.
- **RSS is the wrong instrument for the inventory leak** and deliberately is not
  quoted as evidence: `fl_free` returns blocks to the freelist but never
  `munmap`s, so reclaiming cannot shrink RSS. A 260 s / 41-login soak measures
  +636 kB both before and after. The fix is proven by `g_obj_live` returning to
  baseline, which the mutation test confirms.
- `bench_combat` p99 **1299 µs** against the 50 ms budget; `--agnos`
  warning-free; `cyrius audit` exits 0.

### Known — needs upstream libro

**The in-memory audit chain grows without bound.** `audit_event` appends on every
login / save / security event and `g_audit_chain` is **never read** — durability
comes from `filestore_append`. libro offers no way to bound it that actually
releases memory: `chain_new()` sets capacity `0` so `_chain_auto_rotate` returns
immediately and rotation never fires (there is no capacity constructor);
`chain_apply_retention` redistributes into two *new* vecs while archived entries
stay referenced; and libro contains exactly one `fl_free` in ~4,400 lines,
nowhere near the entry path. This is the residual growth in the soak above.
Fixing it needs a libro mode that frees, or descent dropping the in-memory chain
entirely — neither is a 1.x change.

## [1.5.0] — 2026-07-28

**M13 — the actor tick.** Mobs were furniture: they stood in their authored room
forever and did nothing until a player typed `kill`. They now take a turn each
server tick — pace around, join a room-mate's fight, or break off when badly
hurt. The world moves whether or not you are looking at it.

### Added

- **`mob_tick_all`**, run once per tick from `advance_tick`. O(rooms + living
  mobs), no inner scan. Returns the number of mobs that **took a turn**, not the
  number that visibly did something — wander and assist are 1-in-N rolls, so an
  "acted" count is probabilistic and cannot be asserted on.
- **Wander** — an idle mob paces to an adjacent room (`WANDER_CHANCE` 1-in-20 per
  tick, roughly one move per 50 s), with departure and arrival lines to whoever
  is watching.
- **Assist** — an idle mob joins a room-mate's fight against a player who is
  actually present. A target who has walked out is stale and is not joined.
- **Flee** — below `MORALE_FLEE_PCT` (20%) of max HP a mob drops its target and
  bolts. Cornered, it fights on.

All three thresholds are hardcoded constants, **not** authored template fields:
`kind = "mob"` keys are frozen by [ADR 0007](docs/adr/0007-frozen-1.0-surface.md)
§5 for all of 1.x, so authored `morale` / aggression belongs to M19.

### Fixed

- **Wander was leashed after it broke the game.** The first live run had the
  Foundry Sentinel — the endgame boss, authored into `foundry.overseer` — walk
  the length of the zone and turn up in `hub.gate`, the newbie start room. A
  roaming population diffuses evenly across the map and erases the authored
  difficulty curve entirely. Mobs now stay within one room of `MI_HOME`. The
  proper fix is a per-template "does not roam" flag, which is frozen surface and
  therefore M19's; a home leash needs no authored field because it is a spatial
  rule. Flee respects the leash too — a boss that could flee anywhere would end
  up exactly where wander must not put it.
- **The zone reset would have duplicated every wandered mob.** Respawn topped
  each room up by counting mobs *standing in it*; a mob that walked away left a
  deficit behind, so every reset spawned a replacement and the population would
  climb by one per reset forever. `_mob_alive_count` now counts by **`MI_HOME`**
  across the world — home is the authored fact, `MI_ROOM` is just where it
  happens to be standing.
- **`mob_unlink` split out from `mob_remove`.** Wander relinks an instance into
  a different room: the same unlink, but the instance lives on. Conflating them
  would double-free on every move — verified, and it does not merely fail a test,
  it corrupts the freelist into an infinite loop.

### Notes

- **Re-entry guard.** `MI_ACTED` stamps the tick a mob last took a turn. The
  sweep captures `next` *before* the mob acts (a wander unlinks it from the list
  being walked), and the stamp stops a mob that wandered *forward* into a
  not-yet-visited room from taking a second turn in the same tick.
- `mob_tick_all` takes the tick as a **parameter** rather than reading
  `g_tick_count`: that global lives in `server.cyr`, which is included *after*
  `mob.cyr`, and leaning on forward global resolution is the kind of
  silent-wrong the guard exists to prevent.
- **Tick budget:** p99 **1338 µs** against a 50 ms budget — the actor tick is not
  measurable at Hub scale. Re-measure when the world grows.
- Suite **346 → 373**. Mutation-verified: unleashing wander fails the soak,
  removing the re-entry guard fails the turn count, ignoring the morale
  threshold fails 2, assisting an absent target fails 1, and letting `MI_HOME`
  follow a move fails 2. An earlier draft of the re-entry test passed against the
  unguarded code — it asserted on a 1-in-20 wander — and was rewritten to assert
  on turns taken instead.

## [1.4.0] — 2026-07-28

**M12 — instance lifecycle.** Nothing the world created was ever reclaimed. Mob,
object and corpse instances all came from `alloc()`, and **`alloc()` has no
`free()`** — it is a bump allocator, so every kill and every zone reset leaked
for the process lifetime. Corpses compounded it: they were never removed from a
room at all, so rooms filled with the dead and their loot stayed live forever.
On a long-lived server — descent's entire deployment shape — that is unbounded.

The fix is not "add a free call": it is moving instances off the bump allocator
onto the freelist, which is the only reclaiming allocator available
(`fl_alloc`/`fl_free`).

### Fixed

- **Mob, object and corpse instances now come from `fl_alloc`** and are returned
  with `fl_free`. `fl_alloc` **reuses freed blocks without zeroing**, unlike the
  fresh pages the bump allocator handed out, so `mob_spawn` now `memset`s — the
  old code leaned on that zeroing without saying so.
- **Corpse decay** — a per-tick sweep ages corpses and reclaims them, along with
  whatever loot is still inside. `CORPSE_TICKS = 120` is 5 minutes at the
  standard 2.5 s cadence: long enough to walk back and loot, well inside the
  15-minute zone reset. Hardcoded deliberately — [ADR 0007](docs/adr/0007-frozen-1.0-surface.md)
  §6 freezes the `YD_*` knob names for all of 1.x, so a `YD_CORPSE_TICKS` would
  be a frozen-surface change and belongs to 2.0.
- **Every session reference to a dying mob is now cleared**, not just the
  killer's. `mob_died` cleared only the killing session's `SS_TARGET`, so a
  second attacker kept a pointer across ticks. That was inert *precisely
  because* nothing was reclaimed — `combat_round`'s `mi_hp(m) <= 0` guard read
  the dead instance and disengaged. The first free turns it into a
  use-after-free, and `fl_free` returns the block to a size class the very next
  `mob_spawn` re-issues, so the stale pointer would resolve to a **live,
  different mob** rather than obviously-dead memory. This had to land before any
  free, and did.

**Behaviour change:** corpses now disappear after ~5 minutes, taking un-looted
contents with them. Not a frozen-surface item (ADR 0007 enumerates no corpse
lifetime), and the alternative is a server that grows without bound.

### Added

- **`g_mob_live` / `g_obj_live`** — live-instance counters, incremented at each
  mint site and decremented at each free. `lib/freelist.cyr` exposes no
  occupancy accessor and CLAUDE.md forbids modifying `lib/`, so there was no
  other way to assert the invariant. `@stats` is the natural place to surface
  them once the operator channel lands.
- **`lifecycle` test group** — 13 assertions (333 → 346), including a
  spawn/kill/decay soak that requires both counters to return to baseline.
  Mutation-verified: restoring the mob leak fails 2, stopping `obj_free` from
  recursing into contents fails 2, and reverting the reference sweep fails 2.
  One of those asserts the rule explicitly — `ilist_remove` is the **move**
  primitive (`cmd_get` is remove-then-push), so freeing there would destroy
  every `get`.

**Tick budget:** `bench_combat` p99 **1422 µs**, against 1427 µs before the
sweep and a 50 ms budget — the per-tick cost is not measurable at Hub scale.
Re-measure if the world grows past a few hundred objects.

## [1.3.0] — 2026-07-28

### Fixed — M10, wire-safe prose (1.3.0)

**A player could inject a bare Telnet IAC into another player's protocol
stream.** `telnet_feed` decodes `IAC IAC` into a literal 0xFF data byte — correct
RFC 854 behaviour, and the suite asserts it — but `session_push_line_byte` drops
only `b < 32`, so 0xFF survived into the line buffer, and `cmd_say` handed that
buffer straight to every listener's socket. RFC 854 requires a data-stream 0xFF
be re-sent as `IAC IAC`; sending it bare means a conformant client reads the
start of a Telnet command. The comment on that input filter — *"telnet IAC is
already stripped upstream"* — was wrong, and is corrected: IAC is stripped as
**framing**, while the escaped literal is deliberately preserved as **data**.

Verified end-to-end against a running server with two real clients. Before:
the listener receives `AA\xffBB`. After: `AA\xff\xffBB`.

- **New `session_appendtx_prose`** — the appender for anything a player typed.
  Doubles 0xFF; drops C0 and DEL (ESC among them, so player text cannot forge
  the SGR runs `ansi_title()` / `ansi_actor()` emit). It writes into the tx queue
  directly rather than delegating, because `session_appendtx` truncates silently
  at `TX_CAP`: `LINE_CAP` and `TX_CAP` are both 4096, so a full line of 0xFF
  escapes to 8192, and a truncation landing *between* the two bytes of a pair
  would emit the exact lone IAC this fixes. Escape pairs are written whole or
  not at all.
- **Routed every player-authored byte through it** — `cmd_say`, `cmd_emote`,
  both halves of `cmd_tell`, and `room_say_broadcast`'s body. Server literals
  (the `lead`/`tail` parameters) and authored zone prose are deliberately left
  on the raw appender: sanitizing `room_prose_ptr` would strip zone authors'
  formatting to fix a byte no authored file contains.
- **Player names too** — 10 emission sites across `session.cyr` / `server.cyr`
  (`room_broadcast`, `room_append_present`, `cmd_who`, `render_who`,
  `cmd_examine`, the `tell` headers). `login_name_ok` already constrains names
  to leading-alpha alnum, so this is defence in depth — but it is the same path
  M21's persisted `title` will use.

**Deviation from the milestone sketch:** it specified dropping "C0/C1". C1
(0x80–0x9F) is **kept** — as raw bytes those are UTF-8 continuation bytes, the
tokenizer explicitly passes UTF-8 through, and dropping them would corrupt every
non-ASCII name and message to fix nothing a Telnet client reacts to.

### Fixed — M11, the save-record migration gate (1.3.0)

Four defects in the persistence layer, all latent while `SCHEMA_VERSION == 1` and
all load-bearing the moment it moves. This is the hard prerequisite for the 2.0
schema bump: each one would otherwise have shipped *with* the bump it protects.

- **A stamp-less record no longer re-labels itself.** `player_auth_load` read
  `toml_int(pairs, "schema", SCHEMA_VERSION)` — the default for a *missing* key
  was the current version. 0.7.0–0.9.0 records carry no stamp and **are** v1, so
  the instant `SCHEMA_VERSION` became 2 every one of them would have claimed to
  be v2 and skipped the v1 read path. Now pinned to a literal `SCHEMA_V1` via a
  new `_record_schema`, which also clamps a nonsense `schema = 0` up to 1 so
  callers can branch on `>= 2` without a third case.
- **"Written by a newer server" is no longer reported as tampering.** The schema
  gate returned the same code as a failed `ed25519_verify`, so an operator
  rolling a deploy back told every returning player their record had been
  attacked — and wrote a `SEV_SECURITY` audit entry for what is a versioning
  event. New `PL_ERR_SCHEMA` with its own message; still refuses the session,
  since a downgraded server must not half-load a record it doesn't understand.
- **The save-record writer is bounded.** `_ac` / `_ap` / `_ai` / `_fstr` /
  `_fint` appended into the 4096-byte `g_persist_save` with no check; the only
  guard was inside `_build_record`'s inventory loop. Appends now fail closed and
  propagate a poisoned offset, checked once before signing — so no partially
  built record can ever be signed or written. **Not a live overflow today** (the
  unguarded fields are all short-capped), but every variable-length 2.0 field
  would have landed straight on it.
- **Control bytes in string fields are refused.** `_find_sig_offset` ends the
  signed prefix at the first line beginning `sig `, so a newline inside a value
  could move that boundary. Unreachable in v1 — the CYML parser ends a value at
  the newline first — but the guard has to exist before 2.0 adds free text.

**Behaviour change:** a record from a newer server now produces *"Your record was
written by a newer server than this one."* instead of the tamper message. Not a
frozen-surface item ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md) does not
enumerate login error text), and the old text was simply wrong.

### Added

- **`migration` test group** — 21 new assertions (298 → 319). Verified by
  mutation: reverting the writer bound fails 4, neutering the control-byte guard
  fails 2, dropping the schema clamp fails 1. The missing-stamp assertion is
  documented in-place as a **pin rather than a proof** — while `SCHEMA_VERSION`
  is 1 the old and new defaults agree, so it cannot discriminate until M14 moves
  the constant.
- **`g_schema_max`** — the load ceiling as a settable `var` seeded from
  `SCHEMA_VERSION`, so the suite can drive a schema-2 world against a schema-1
  build. `SCHEMA_VERSION` is a compile-time enum member and the suite compiles
  the same source, so there was no other seam.
- **`wire-hygiene` test group** — 14 assertions including a 256-value fuzz sweep
  over every byte at every position: no lone IAC survives, no control byte
  reaches the wire, output never exceeds 2× input, and an escape pair is never
  split at the buffer boundary. Mutation-verified — removing the escaping fails
  5 assertions, allowing a split pair fails 1, dropping the control filter
  fails 2.

Suite: **298 → 333 assertions.** `cyrius audit` exits 0; host and `--agnos`
both build warning-free.

## [1.2.0] — 2026-07-28

**Toolchain 6.3.32 → 6.4.83, libro 2.7.10 → 2.8.2, and a full `cyrius audit` sweep.**
A maintenance release with no observable game-surface change — the frozen 1.0 surface
([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)) holds. `main` did not build at the
1.1.5 tag; it does now, and every audit gate is green for the first time.

### Fixed

- **CI never ran the tests.** The `Test` step was `cyrius test src/test.cyr`, and
  `src/test.cyr` is a deliberate no-op stub (`fn main() { return 0; }`) that exists
  only to satisfy `[build].test`. CI compiled the stub, exited 0, and printed no
  assertions — **the 298-assertion suite has never executed in CI.** Every green run
  before this one said nothing about the tests. The workaround it grew from was real
  but long stale (at cyrius 6.0.1 the released toolchain couldn't discover
  `tests/*.tcyr`); 6.4.72's corpus walker recurses `tests/`, and bare `cyrius test`
  at the pinned 6.4.83 runs both the `.tcyr` corpus and `[build].test`. CI now runs
  bare `cyrius test`, plus a new `cyrius audit` step.
- **`player_exists()` was wrong on agnos** — `sys_stat` is one of the few stdlib
  calls whose *arity* differs by target: agnos takes `(path, pathlen, statbuf)`
  (counted paths, per its VFS), Linux/macOS take `(path, buf)`. descent used the
  2-arg form unconditionally, so on agnos the statbuf pointer landed in the
  `pathlen` slot and `statbuf` was garbage — and this is the branch that decides
  whether a connecting name is a **returning player** (passphrase prompt) or a
  **new** one (character creation). `cyrius build --agnos` had been warning
  (`'sys_stat' expects 3 arguments, got 2`); the host build could not see it.
  Now `#ifdef`-gated, and `--agnos` builds warning-free.
- **`main` did not compile** — `error: refusing to emit binary with 1 reachable
  undefined function(s): 'thread_local_alloc'`. cyrius 6.4.65 replaced hardcoded
  thread-local slot indices with an allocator (`thread_local_alloc`), and the sibling
  sigil checkout (3.12.1, reached through `path = "../libro"`) calls it — but the
  committed `lib/thread_local.cyr` was still the 6.3.32 vintage that predates it.
  Re-vendoring the stdlib at the new pin resolves it. Note this was a *hard error*,
  not the old warn-and-emit-`ud2` behaviour: 6.4.x refuses to emit rather than
  shipping a binary that SIGILLs on first call.
- **`benches/bench_combat.bcyr` had stopped compiling** (`undefined variable
  'DP_ROOMS'`). It includes `src/server.cyr`, whose boot path reads the data-path
  globals that live in `src/persist.cyr`, but never included persist or the M6
  crypto prelude. `cyrius bench` reported 2 passed / 1 failed. Now 3 passed, and the
  M4-H gate is measured again: **p99 1427 µs** against the 50 ms drift budget.
- **`version` reported the wrong version.** `VERSION_STRING` in `src/main.cyr` was
  still `1.1.3` — it missed both the 1.1.4 and 1.1.5 bumps, so a released binary
  identified itself as two releases old. The release checklist in `CLAUDE.md` now
  names that line explicitly, next to `VERSION` and `cyrius.cyml`.
- **Stale comment in `src/server.cyr`** claimed the `@`-admin namespace was
  "unguarded for now". It has been gated behind `YD_ADMIN` (default off) since
  0.9.1. Corrected, and both admin-gate comments now cross-reference roadmap M8.

### Changed

- **Dropped the monolithic `lib/sigil.cyr` include** (`src/main.cyr`,
  `tests/cyrius-yeomans-descent.tcyr`). libro 2.8.0 thinned its sigil surface to
  capability sub-bundles, so `[deps.libro]` now resolves `sigil-mldsa` (Ed25519) +
  `sigil_sha256` + `sigil_sha_ni` + `sigil_hex` into `lib/` and cyrius auto-includes
  them. Including the 1 MB monolith *on top* defined all of it a second time and
  dragged in the x509/RSA bignum tables descent never touches. All six symbols the
  server actually calls — `ed25519_{keypair,sign,verify}`, `sha256`,
  `hex_{encode,decode_into}` — live in the thin bundles.
  **Static data 13,405,408 B → 83,336 B (.bss); duplicate-symbol warnings 267 → 40**
  (the remaining 40 were the `cyml`/`toml` carve-out below, which took it to 0).
- **`cyml` / `toml` are no longer stdlib leaves** — 6.4.83 carved them into **bayan**
  (the same carve that took `json`/`bigint` at 6.1.25) and ships no `cyml.cyr` /
  `toml.cyr` at all. Listing them in `[deps] stdlib` only ever resolved because the
  committed `lib/` still held pre-carve copies, which then redefined every
  `cyml_*`/`toml_*` symbol on top of bayan's (40 more duplicate-symbol warnings) —
  and "last definition wins" meant the zone and class loaders ran on whichever copy
  the include order happened to pick.
  `bayan` is now a direct `[deps] stdlib` entry (descent's own `world.cyr` and
  `classes.cyr` call `cyml_*`, so it is a first-party need, not a libro side effect).
- **Renamed the parser's `MAX_TOKENS` → `PA_MAX_TOKENS`.** The bare name collided
  with patra's `enum TokLim { MAX_TOKENS = 128; }` (patra arrives transitively via
  `[deps.libro]`); Cyrius resolves enum constants into one flat namespace, so the two
  raced under "last definition wins". Same value (64), unambiguous symbol.
- **Pruned 12 dead leaves from the committed `lib/`** — `cyml`, `toml`, `json`,
  `bigint`, `base64`, `csv`, `u128`, `linalg`, `matrix`, `agnosys` (all carved out of
  the 6.4.83 stdlib), plus `niyama` and `yantra` (never referenced by descent, and
  stale at 1.0.5/1.0.0 against the pinned 1.0.6/1.0.1). Verified `cyrius deps` +
  `build` + `test` are unaffected and every leaf descent and libro's sidecar require
  is present in the pinned toolchain lib.
- `[package].cyrius` `6.3.32` → **`6.4.83`**; `[deps.libro]` `2.7.10` → **`2.8.2`**
  (pulls sigil **3.12.1**, patra **1.12.12**, sakshi, bayan transitively).
  `cyrius lib sync --full` re-vendored the stdlib snapshot at the new pin.

- **`programs/*.cyr` and the `.tcyr` suite carried the same include debt.** Both
  smoke harnesses pulled the monolithic `lib/sigil.cyr` (13.4 MB static each), and
  both they and the test suite included `session.cyr` without `server.cyr`, so every
  run printed 12 `undefined function` warnings — noise that would bury a real one.
  All three are now warning-free.

### Added

- **Doc comments on all 111 previously undocumented public functions** across
  `src/` and `programs/` — the `docs` gate of `cyrius audit`.
- **`signal_ignore(SIGPIPE)` at server startup** (hardening). `session_drain`
  writes with a raw flagsless `sys_write`, and the default SIGPIPE disposition is
  *terminate the process*, so a write landing on a peer that already sent RST would
  take the whole server down with every connected player. `dispatch_session` calls
  `flush_session` **before** its `EPOLLHUP`/`EPOLLERR` check, so that ordering is
  genuinely reachable on paper. `signal_ignore` arrived in the stdlib at 6.4.51 and
  is a no-op on agnos/Windows, so the call needs no target gate; with `SIG_IGN` the
  write returns `-EPIPE`, which `session_drain` already routes down its existing
  "real error → disconnect" path.
  **Honest scope:** the window was *not* reproducible — 200 abrupt RST disconnects,
  and 60 stalled peers RST while holding unsent tx, both left the server serving
  (the epoll HUP path appears to reap sessions first in practice). This is defence
  in depth against a latent hazard, not a fix for a demonstrated DoS.

### Quality

`cyrius audit` (the project sweep — fmt / lint / docs / tests / bench) now **exits 0**.
Previously it failed four of five gates. Full gate at the 1.2.0 cut:

| gate | result |
|---|---|
| `cyrius deps --verify` | 102 verified, 0 failed |
| `cyrius build` (host) | OK, 0 warnings |
| `cyrius build --agnos` | OK, 0 warnings |
| `cyrius test` (bare, as CI now runs it) | 298 passed, 0 failed (+ 1) |
| `cyrius bench` | 3 passed, 0 failed |
| `cyrius fuzz` | 1 passed, 0 failed |
| `cyrius audit` | exit 0 |

- **fmt** — `#ifdef`/`#else`/`#endif` inside function bodies now indent to block
  level in `session.cyr` / `server.cyr`; one hanging comment in `persist.cyr`
  restructured; two continuation lines rewrapped.
- **lint** — 14 over-length lines and 3 untracked deferrals cleared. Note the gate
  counts **bytes**: the `# ─────` section rules were 209 B each (`─` is 3 bytes), not
  the 69 columns they look like.
- **tests** — 298 assertions pass; `cyrius test src/test.cyr` exits 0.
- **bench** — 3 passed, 0 failed (was 2/1).

### Known / upstream

- `cyrius build` still warns that `./lib/` shadows the pinned toolchain lib for
  **sakshi 2.4.3 (pinned: 2.4.6)**. sigil 3.12.1 pins sakshi 2.4.3 in its own
  manifest, so `cyrius deps` writes 2.4.3 over the synced 2.4.6. Not resolvable from
  descent — it needs a sigil-side bump. No functional impact observed.
- Two toolchain quirks worked around rather than fixed here: `cyrius fmt -w` does not
  write (capture `cyrius fmt <file>` stdout instead), and `cyrius lib sync --full`
  reports a full 99-file snapshot while skipping `niyama.cyr` / `yantra.cyr`.

## [1.1.5] — 2026-07-02

**agnos server startup fixed — freelist agnos mmap (cyrius 6.3.32) + libro 2.7.10.** Re-synced the
vendored stdlib to cyrius 6.3.32, which carries the official fix for the freelist allocator's agnos
mmap ABI — retiring the local hand-patch. Before it, agnos `fl_alloc` (libro's audit chain, reached
via `persist_init` → `chain_new`) issued the Linux 6-arg `mmap` with the length in **arg2**, but
agnos `mmap#27` reads it from **arg1** → `mmap(0)` → 0 → the first store SIGSEGV'd. descent crashed
in `persist_init` immediately after world-load whenever it ran on agnos / under mirshi.

### Fixed
- **agnos server startup** — descent now boots its persistence (`persist: player saves + audit chain
  ready`), binds, and serves on agnos. Verified end-to-end under mirshi (`--root <rootfs> --net`):
  the world loads (21 rooms), it listens on `:4000`, and a telnet client reaches the login banner.

### Changed
- `cyrius lib sync` → **6.3.32** vendored stdlib (official `freelist.cyr` with the `_fl_mmap`
  target-dispatch helper; the local hand-patch is retired). `[deps.libro]` tag `2.7.7` → **`2.7.10`**.
  Root cause fixed upstream in cyrius 6.3.31 (issue `2026-07-02-freelist-agnos-mmap-abi`).

### Fixed
- **CI dep resolution** (`cyrius deps` failed *"dep libro requires 'bayan' / dep patra requires
  'sync' … not in the cyrius stdlib"*). The dep leaves resolve from descent's **committed vendored
  `lib/`** (the release tarball is a minimal stdlib — it doesn't even ship `cyml`/`toml`, so `lib/`
  must stay committed), and that snapshot was **missing `bayan.cyr` + `sync.cyr`** — newly required
  by `[deps.libro]` (→ bayan) and its transitive patra (→ sync). Completed `lib/` with
  `cyrius lib sync --full` so every required leaf is present.
- **CI installer** — switched `ci.yml` + `release.yml` from the hand-rolled `curl … tar … cp -r
  lib/*` step to the upstream **`scripts/install.sh`** (`CYRIUS_VERSION=<pin> sh`), matching
  patra's / sigil's CI.

**Migrate off the 29-element hand-ordered stdlib list onto libro's dependency
sidecar.** The M6 persistence chain's crypto/store leaves (ct/keccak/random/thread/
thread_local for sigil; fs/process/hashmap/slice + bayan for libro — json/bigint were
carved into bayan @6.1.25) are no longer hand-listed in `[deps].stdlib`. As of cyrius
6.2.46–.48 + libro 2.7.8, the libro fold ships a `dist/libro.deps` sidecar declaring
exactly those leaves; `cyrius deps` auto-resolves them transitively (topological order,
fail-loud on a missing one) when `[deps.libro]` resolves. `[deps].stdlib` now lists
only descent's OWN direct M1 surface (18 leaves). **This ends the omit-one→runtime-SIGILL
trap** the hand-ordered list existed to paper over. Toolchain pin 6.2.36 → **6.2.48**;
libro pin → **2.7.8**. Verified: `cyrius build` compiles clean (no undefined-fn warnings).

## [1.1.3] — 2026-06-22

Bug-fix release: the world loads + is interactable on AGNOS, character creation no
longer crashes, and Telnet stays in clean line mode. Frozen 1.0 surface
([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)) holds — these are wire/build/content
fixes, not surface changes.

### Fixed

- **Character creation crashed (`SIGILL`) — missing `thread_local` includes.** sigil 3.7
  banks the SHA-256 message schedule per-thread (`cbank()` → `thread_local_get`), but
  `lib/thread.cyr` / `lib/thread_local.cyr` were never included (the `[deps]`-stdlib
  auto-prepend pulls `ct`/`keccak`/`random` but **not** `thread`/`thread_local`), so those
  calls compiled to `ud2`/SIGILL trap stubs. `sha256` — and therefore `ident_derive` —
  trapped the instant a player chose a passphrase, dropping the connection and failing the
  `persist` test suite. Added the two explicit includes to `src/main.cyr` and the test
  harness. The whole 298-assertion suite is green again. (Regression rode in with the 1.1.0
  agnos re-vendor of sigil; pre-1.1 sigil didn't bank per-thread.)
- **AGNOS ran "roomless" — relative data paths.** The world / class loaders and the persist
  store used relative paths (`data/zones/...`), but AGNOS's VFS requires **absolute** paths
  (a path not leading with `/` returns `FS_NONE`), so every load silently failed and the
  server served an empty world. Centralised the data paths in one `#ifdef
  CYRIUS_TARGET_AGNOS` block — `/data/...` on AGNOS, `data/...` on Linux (unchanged). The
  Hub (21 rooms, mobs, objects, classes) now loads on the sovereign kernel.
- **`examine`/`look` couldn't see room objects.** `cmd_examine` resolved the noun against
  players and mobs but never the room's objects or the player's inventory — so a visible
  object (the Hub's work-notice) reported "You see no … here." Examine now resolves room
  objects + carried items and renders the object's description, so examining a readable
  (the work-notice, postings) reads it.
- **Telnet: server no longer agrees to echo normal input.** 1.1.2 dropped the connect-time
  option salvo but left `ECHO` *preferred*, so a client's unsolicited `DO ECHO` still drew
  `WILL ECHO` and the server would echo normal input (double-echo). `ECHO` is now
  tracked-but-unpreferred: an unsolicited `DO ECHO` is refused (`WONT ECHO`, line mode
  preserved), while the passphrase prompt raises a tracked `WILL ECHO` so its `*` masking
  still works. `session_echo_off`/`on` guard `SS_TS` for bare test sessions.

## [1.1.2] — 2026-06-21

**Telnet cooked-line-mode fix — backspace, Enter, and no stray `^M` / `^?`.** 1.1.1's
echo fix dropped WILL ECHO but kept WILL SGA, which pushes conformant clients into
character-at-a-time mode: the client stops cooking the line, so backspace was inert
(rendered `^?`), carriage return showed as `^M`, and Enter could mishandle the line.
This drops the connect-time option salvo entirely, leaving the client in its default
**cooked line mode** — it local-echoes, edits with backspace, and submits a clean line
on Enter. The passphrase prompts still raise WILL ECHO themselves for the masked `*`
echo. Telnet-wire only; frozen 1.0 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md))
untouched; applies to both the Linux and AGNOS builds.

### Fixed
- **`src/telnet.cyr` `telnet_announce` — no connect-time WILL ECHO / WILL SGA salvo.**
  Conformant clients (`telnet`, `nc`, Mudlet) stay in cooked line mode: backspace
  deletes, CR submits, no raw `^M` / `^?` on screen, and Enter advances. The passphrase
  masking is unchanged — it raises WILL ECHO around its own prompt and the server draws
  `*` per char.

## [1.1.1] — 2026-06-21

**Telnet echo fix — visible input + masked passphrase.** The login flow announced
`WILL ECHO` at connect, which makes a conformant client stop local-echoing — but
the server never echoed input, so names and commands were typed **blind**. Now the
client line-echoes normal input (visible), and the server takes over echo only at
the passphrase prompts, masking each character with `*`. Telnet-wire behaviour only;
the frozen 1.0 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)) is
untouched, and the fix applies to both the Linux and AGNOS builds.

### Fixed
- **`src/telnet.cyr` — dropped `WILL ECHO` from `telnet_announce`** (kept `WILL SGA`).
  A conformant client now line-echoes the name + commands, so the player sees what
  they type instead of typing blind.
- **`src/session.cyr` `session_push_line_byte` — `*`-masked passphrase echo.** During
  the passphrase phases (`PHASE_PASS`/`NEWPASS`/`CONFIRMPASS`/`CHPASS_*`, which raise
  `WILL ECHO` via `session_echo_off`), the server now draws a `*` per character,
  erases on backspace, and emits CR/LF — the passphrase shows as `****` rather than
  being invisible. Normal input stays client-echoed (no double echo); `nc` and other
  clients that ignore `WILL ECHO` now also show typed input.

## [1.1.0] — 2026-06-21

**AGNOS compatibility — Yeoman's Descent runs as a sovereign ring-3 network service on the AGNOS kernel.** `cyrius build --agnos` now produces a static agnos ELF that agnsh execs from disk, serving the telnet MUD over the AGNOS kernel's TCP stack. End-to-end QEMU-validated (`agnosticos/docker/descent-sweep/`): boot agnos → agnsh `run /bin/descent serve 4000` → a host client connects over SLIRP, receives the login banner, and the session responds to input (name → passphrase prompt). The frozen 1.0 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)) holds — no new verbs, save fields, zone fields, or env knobs; AGNOS support is purely additive platform code behind `#ifdef CYRIUS_TARGET_AGNOS`, and **Linux behavior is byte-identical**.

### Added
- **AGNOS build target (`CYRIUS_TARGET_AGNOS`).** The event loop is platform-split: AGNOS `epoll` watches only signalfd/timerfd (never sockets) and is 3-arg (no timeout), so the Linux epoll socket-multiplexer becomes a **`sleep_ms`#41-paced poll loop** — non-blocking `sock_accept`#57 drain → non-blocking `sock_recv`#49 sweep over the active-session list → the absolute 2.5 s combat-tick schedule. The Linux epoll loop is untouched.
- `session_on_readable` AGNOS branch using non-blocking `sock_recv`#49 (correct WOULD_BLOCK/EOF sense — inverted from Linux; `sys_read` on an agnos socket fd is the *blocking* adapter and would park the single-threaded loop).
- AGNOS gates: `set_nonblock` no-op (sockets inherently non-blocking), `install_signal_fd`/epoll-ctl helpers compiled out, `EPOLLIN`/`EPOLLOUT` compat constants, in-band/process-kill shutdown.

### Changed
- Toolchain pinned to cyrius **6.2.36**; the M6 persistence chain rides patra **1.12.3** + libro **2.7.7** (the AGNOS syscall-ABI fixes: WAL time / entropy / clock / `lseek` / flock).
- `cyrius.cyml` `version` now resolves from the `VERSION` file (`${file:VERSION}`) — single source of truth.

## [1.0.1] — 2026-06-10

**Gateway-verified maintenance release.** Nothing observable changed from 1.0.0 — the frozen 1.0 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)) holds: no new verbs, save fields, zone fields, or env knobs, and no source change. This bump records Yeoman's Descent as the verified target of the **agora Descent link** (agora 1.4.0, its [ADR 0017](https://github.com/MacCracken/agora/blob/main/docs/adr/0017-descent-link-gateway.md)): a logged-in agora citizen can now step through a portal and reach this MUD over the shared telnet substrate.

- **How the gateway works (no MUD change required).** agora dials this server as a *transparent TCP byte-proxy* and shuttles bytes both ways. Because the proxy is byte-transparent, the MUD's own RFC 1143 telnet negotiation, passphrase echo suppression, and Ed25519-from-passphrase login (ADR 0004 / 0006) flow through to the agora client unchanged — **the MUD authenticates the player itself**, exactly as for a direct connection. The two projects stay decoupled: the wire is the only contract, and each keeps its own release cycle.
- **Identity hand-off is deferred.** Carrying agora's sigil identity across the link (single-sign-on) would require an external-identity / pre-authenticated-session path that the frozen 1.0 surface deliberately does not expose. That is a future, two-repo bite (agora ADR 0017 § Decision); for now a citizen logs into the MUD on arrival.
- **Verification.** Exercised end-to-end by agora's `docs/examples/20-descent.sh` smoke — agora builds and starts this server, a logged-in citizen runs `descent`, and the MUD's own login banner ("By what name are you known?") proxies back through the gateway.
- Toolchain pin unchanged (cyrius 6.1.23). Test suite unchanged and green.

## [1.0.0] — 2026-06-10

**Yeoman's Descent 1.0 — feature-complete.** The clean cut: a stabilisation-only
release against the frozen 0.9.1 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).
No new verbs, save fields, zone fields, or env knobs — nothing observable
changed from 0.9.1. The full game loop is implemented, secured, and documented.

### The 1.0 game

- **Wire** — raw TCP / Telnet, RFC 854 IAC + RFC 1143 negotiation, per-session
  line handling, passphrase echo suppression.
- **Parser** — verb-noun with direct/indirect objects, prepositions, and
  `all.X` / `N.X` qualifiers; fuzz-clean.
- **World** — a hand-authored 21-room Hub across four districts, with ambient
  loot that restocks on reset.
- **Combat** — a 2.5 s server-wide tick, hidden `1d20`+mods vs AC, corpses + loot.
- **Classes** — Pikeman / Splicer / Courier / Chaplain, each with three abilities
  on an energy + cooldown + status framework; each clears the Hub solo.
- **Persistence** — Ed25519 identity derived from a passphrase (sigil); crash-safe,
  signed, schema-stamped per-player saves; a libro audit chain. Reconnect
  restores attrs / room / inventory; survives `kill -9`.
- **Zone resets** — presence-gated mob/loot respawn on a per-zone timer.
- **Security** — memory-safety + CVE-class swept (0.9.0); every loaded save field
  validated; the `@`-admin namespace gated behind `YD_ADMIN`.

### Documentation

- README rewritten for 1.0 (status, libro+sigil backend, real usage).
- New player/operator guides: `docs/guides/playing.md`, `commands.md`,
  `running.md`; `getting-started.md` refreshed.
- Stale-data sweep across all docs: corrected the legacy "backed by T.Ron" /
  "managed via Joshua" framing (persistence is libro+sigil; Joshua/M8 is
  deferred post-1.0), refreshed the architecture overview, roadmap, and state
  snapshot, and updated test counts (298).

### Deferred (post-1.0)

- **M8 — Joshua operator interface.** The `@`-admin verbs are groundwork; full
  operator authentication and the Joshua control channel come after 1.0.

## [0.9.1] — 2026-06-10

**Surface freeze.** The public surface is enumerated and locked for 1.0 so the
final release is stabilisation-only ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).
Two behaviour-affecting changes land here; 1.0.0 changes nothing observable.

### Added

- **Save-record schema version** ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md) §3).
  Every record now stamps `schema = 1` (in the signed prefix); the loader
  rejects any record stamped newer than it understands. Records from
  0.7.0–0.9.0 carry no `schema` field and load as v1 (back-compatible). This is
  the migration hook for post-1.0 field changes.
- **ADR 0007 — frozen 1.0 surface.** Documents the locked surface: command
  verbs + aliases + `@`-namespace, save schema v1 fields, Telnet/wire
  behaviour, zone-file format, env knobs.

### Changed

- **The `@`-admin namespace is gated behind `YD_ADMIN` (default off).**
  `@stats`/`@who`/`@reset` only work when the server is started with
  `YD_ADMIN=1`; otherwise they read as unknown commands and are hidden from
  `help`. Closes the last unguarded surface in the default build; full operator
  authentication remains deferred to M8 (post-1.0). **Behaviour change:**
  `@stats`, always-on since M1-H, now requires `YD_ADMIN=1`.

## [0.9.0] — 2026-06-10

**Security sweep & audit.** A focused pass over the network-input and
save-file attack surface, informed by current CVE classes (telnet pre-auth
overflows à la CVE-2026-32746, Ed25519 malleability à la CVE-2020-36843).
Four memory-safety / DoS issues found and fixed; all reachable from a raw TCP
connection or a planted save file. New `security` test group (9 assertions);
the remote pre-auth vector is live-verified to no longer crash the server.

### Security

- **[Critical] Two heap buffer overflows in the auth path, both bounded now.**
  (1) `ident_derive` copied the passphrase into a 256-byte scratch using the
  raw line length (up to `LINE_CAP` = 4096) — reachable **pre-auth** at the
  returning-login passphrase prompt. (2) `player_auth_load` hex-decoded the
  record's `salt`/`pubkey`/`sig` into 16/32/64-byte slots with no length check
  **before** signature verification, so an over-long hex field in a planted
  record overflowed the heap. Fixes: `ident_derive` hard-clamps the passphrase
  to `PASS_MAX`; every derive call site bounds its length; the loader requires
  exact hex lengths before decoding.
- **[High] OOB read from an unvalidated `class` index.** A loaded `class` fed
  `class_name_ptr(cls) = g_classes + cls*CL_SIZE` with no bound — a player owns
  their Ed25519 key and can re-sign their own record with `class = <huge>`,
  leaking heap memory to the wire on the next `examine`/`help`. Now clamped to
  `[0, g_class_count)` (out-of-range → classless).
- **[Medium] Server-wide DoS from an unvalidated `ndice`.** A re-signed save
  with `ndice = 2e9` spun the `roll()` loop for billions of iterations inside
  the single-thread combat tick. Every numeric save field is now clamped to a
  sane range on load.
- **Hardening principle.** A save's Ed25519 signature proves its **author**,
  not its field **values** — so every field loaded from a player-owned record
  is now validated/clamped, not trusted on the strength of the signature.

### Notes

- **Ed25519 signature malleability** (CVE-2020-36843 / CVE-2026-33895 class:
  missing `S < L` check) was researched and judged **non-applicable**: the
  record signature is used for integrity, not signature uniqueness or
  replay-prevention, so a malleable variant cannot tamper a record; and the
  verifier lives in vendored `sigil`. No code change.
- Toolchain pin → **6.1.23**.

## [0.8.3] — 2026-06-10

Operator read-only verbs — groundwork for the M8 Joshua interface, surfacing
live server state from inside the world.

### Added

- **`@who`** — lists every in-world session (name + the room it's standing in)
  and the in-world count.
- **`@reset`** — forces an immediate zone reset, bypassing the presence gate.
  The top-up is idempotent (only dead mobs / missing objects respawn), re-arms
  the reset timer, and writes the standard reset log line. Reports
  `mobs +N, objs +M`.

### Notes

- The `@`-verb namespace (`@stats`, `@who`, `@reset`) is currently unguarded;
  M8 lands operator authentication in front of it.

## [0.8.2] — 2026-06-10

A content patch — the Hub gets lived-in. The M7-D object-respawn mechanism
finally has something to act on: ambient loot and flavor now populate the
world and restock on each zone reset.

### Added

- **Six flavor/loot object templates** (`data/zones/hub.objs.cyml`): a work
  notice, a dented tankard, a foil ration, a slag ingot, a clouded optic, and
  a shrine-token — alongside the existing scrip / cell / shard / core.
- **`objects =` spawns across 11 Hub rooms** (13 objects total), thematically
  placed: a notice at the gate and market arch, a tankard in the Flagon, a
  ration in the bunks, scrap on the stalls and through the foundry, scrip at
  the exchange, offerings at the Drowned Shrine. They render on `look` and, via
  M7-D, respawn when the zone resets — so the world restocks itself.

## [0.8.1] — 2026-06-10

A login & identity polish patch — no new milestone. Passphrases stay off the
screen, returning players get a greeting, and you can change your passphrase
from inside the world.

### Added

- **`passwd` verb.** Re-key your character from the command prompt: a fresh
  random salt + the new passphrase derive a new Ed25519 identity, the record
  is re-signed and saved ([ADR 0004](docs/adr/0004-identity-and-authentication.md)).
  Two-step (new + confirm), echo-suppressed, audited as `passwd.change`. The
  old passphrase stops working immediately.
- **Last-seen greeting.** A returning player is welcomed with `Last seen N
  <units> ago`, computed from the record's prior `last_login`.

### Changed

- **Passphrases no longer echo.** The server now sends `IAC WILL ECHO` before
  every passphrase prompt (login, new-character, and `passwd`) and `IAC WONT
  ECHO` once it's entered, so conformant Telnet clients hide the keystrokes —
  the deferred ADR-0004 item. Clients that ignore ECHO behave as before.
- `cmd_on_line` re-prompts with `> ` only when still at the command phase, so a
  verb that switches phase (like `passwd`) doesn't double-prompt.
- Toolchain pin → **6.1.22**.

## [0.8.0] — 2026-06-10

**M7 — zone resets.** The world heals itself: mobs and loot respawn to the
authored layout on a timer, but never while a player is standing in the zone.
Gate met: an empty zone resets within its window; a zone with a player in any
room defers until it empties.

### Added

- **M7-A — per-zone reset timer.** The zone header's `reset_secs` (Hub: 900)
  is read into `g_zone_reset_secs`; the clock tracks time since the last reset
  (armed at boot), not since server start. `YD_RESET_SECS` overrides it for
  testing/ops, alongside `YD_TICK_MS` / `YD_IDLE_MS`.
- **M7-B — player-presence gate.** `maybe_zone_reset` (in `advance_tick`)
  defers a due reset while any in-world session occupies the zone, retrying
  each tick until it empties — single-writer, so the snapshot can't race
  ([ADR 0003](docs/adr/0003-single-thread-event-loop-concurrency.md)).
- **M7-C — mob respawn.** `zone_reset_mobs` tops each room up to its authored
  mob multiset: for a template authored *k* times, it spawns *k − alive* fresh
  full-HP instances, so living mobs are never duplicated and a `scavver
  scavver` room refills only what died.
- **M7-D — object respawn.** `zone_reset_objs` reapplies each room's `objects`
  spawn list without duplicating objects already present (matched by the new
  `OI_TPL_ID`); corpses/dropped loot never match or block. Also wired at boot,
  so authored room objects now spawn (no Hub room declares any yet — mechanism
  is in place for future zones).
- **M7-E — reset event log.** Each reset emits one line for Joshua (M8):
  `[<epoch>] zone=<id> reset (rooms=N, mobs=M, objs=O)`.

### Changed

- Boot now reports `… mobs, … objs spawned` and arms the zone-reset timer.

### Fixed

- Removed a duplicate room-id lookup: M6's `world_room_by_id` re-implemented
  the existing `room_index_by_id` (M3-B); `persist.cyr` now calls the latter.

## [0.7.0] — 2026-06-09

**M6 — player persistence.** Players now survive a server restart. The gate
holds: `kill -9` the server mid-session → restart → the player reconnects at
their last room with full attributes and inventory. Identity is real
cryptography ([ADR 0004](docs/adr/0004-identity-and-authentication.md)); saves
are crash-safe and tamper-evident ([ADR 0006](docs/adr/0006-persistence-shape.md)).

### Added

- **M6-A — persistence dep chain.** First external (non-stdlib) dependency:
  **libro 2.7.1** (append-only SHA-256 hash-chain store), pulling **sigil
  3.6.0** (Ed25519), sakshi, patra, and agnosys transitively via
  `[deps.libro]`. The opt-in stdlib it needs (`ct`/`keccak`/`thread`/
  `thread_local`/`random`/`fs`/`process`/…) is declared in `cyrius.cyml`.
- **M6-B — Ed25519 identity (ADR 0004).** A player's identity is a sigil
  Ed25519 keypair whose seed is `SHA-256(salt‖passphrase)`. The login flow
  gained passphrase phases: a new name forges an identity (choose + confirm a
  passphrase); a known name must present it. Only salt + public key are stored
  — the secret key is re-derived from the typed passphrase and never written.
- **M6-C — player save shape.** `data/players/<name>.cyml` (one `[player]`
  TOML section): identity, class, room (by stable id), attrs, vitals, combat
  profile, inventory (template ids), and timestamps. Inventory persists via a
  new `OI_TPL_ID` on item instances and re-instantiates from templates on load.
- **M6-D — save triggers.** On `save`, on disconnect (`quit` / idle reap /
  dropped socket), at character creation, and a debounced ~5-min tick sweep of
  dirty sessions — all out of the command hot path ([ADR 0003](docs/adr/0003-single-thread-event-loop-concurrency.md)).
- **M6-E — load on login.** A returning player's record is verified and
  restored, dropping them back into their recorded room (or the start room if
  it has since been removed).
- **M6-F — crash-safe writes.** Serialize → write `<name>.cyml.tmp` →
  atomic `rename(2)`. A crash leaves the complete old or new record, never a
  torn file. Each record is Ed25519-signed over its prefix; load rejects a
  corrupt or tampered record rather than loading bad state.
- **libro audit chain.** Login / save / character-creation / auth-failure /
  tamper-rejection events append to a hash-linked `data/audit.libro`.
- **Validation.** `programs/crypto_smoke.cyr` (crypto + chain) and
  `programs/persist_smoke.cyr` (on-disk save→reload round-trip + auth + tamper)
  build and run to exit 0; 16 new `persist` unit assertions (256 total, all
  pass); a live-server `kill -9` → restart → restore exercise passes.

### Fixed

- **Corrected the M6 "blocked on a sigil bug" misdiagnosis.** The crypto
  SIGILL (exit 132) was never a sigil defect — cyrius stdlib is **opt-in,
  never auto-resolved**, so `dist/sigil.cyr` was consumed without listing
  the stdlib modules its crypto calls (`ct`/`keccak`/`thread`/
  `thread_local`/`random`). cyrius 6.1.x only *warns* on the undefined
  symbols and compiles each to a `ud2` trap, so the build passed then
  crashed the moment a crypto path ran. Fix: those modules are now opted
  in via `cyrius.cyml [deps] stdlib`, ahead of the sigil include
  (single-pass forward-resolution). Diagnosed in sigil 3.7.8's CHANGELOG.

## [0.6.1] — 2026-06-09

A polish patch that completes the lived-in feel of combat — no new
milestone, no new dependencies. Fights are now visible to bystanders, mob
health reads at a glance, and every class recovers between fights.

### Added

- **Onlooker combat visibility.** Other players in a room now see a fight
  in third person — `alice strikes a rust-drone.`, `a rust-drone hits
  alice!`, `… collapses, destroyed.` — instead of nothing. Auto-attacks,
  misses, ability strikes, and kills all broadcast (`room_combat_line`,
  non-dropping). The combatant still gets the detailed first-person line.
- **Mob health condition.** `mob_condition` reports qualitative health
  (unhurt / lightly wounded / wounded / badly wounded / near death) from
  the HP fraction; shown in the room's mob list (when hurt) and in
  `examine`. Hidden numbers stay hidden.
- **Out-of-combat recovery.** A player regenerates HP each tick while not
  engaged, scaled by CON (`+1 + CON/5`), so every class — not just the
  Chaplain — heals between fights. No regen mid-combat (abilities only).

### Changed

- `classes_upkeep` now also runs out-of-combat HP recovery.
- 8 new unit assertions (240 total): `mob_condition` thresholds, CON-scaled
  regen, no-regen-while-engaged, regen HP cap.

## [0.6.0] — 2026-06-09

M5 — the four classes go from text-table flavor to playable mechanics.
Character creation now asks your calling; each class brings its own
attributes, combat profile, and three abilities that compose with the
2.5 s tick rather than replacing it ([ADR 0001](docs/adr/0001-tick-based-combat-over-cooldowns.md)).
All four can clear the Hub solo and kill the Foundry Sentinel boss
without dying — each through its own identity (the Pikeman tanks, the
Splicer bursts, the Courier strikes from the dark, the Chaplain sustains).

### Added

- **Classes** (`src/classes.cyr`, `data/classes.cyml`). Pikeman / Splicer /
  Courier / Chaplain, each with STR/DEX/CON/TEC, a derived combat profile
  (HP/AC/hit/damage), and an energy pool. `world_load_classes` parses the
  CYML; `apply_class` stamps the chosen class onto the session, replacing
  the M4 flat defaults.
- **M5-A — Class selection.** A login sub-phase (`PHASE_CLASS`) between the
  name prompt and world entry: a numbered menu; pick by number or name
  (prefix-matched); invalid picks re-prompt.
- **M5-G — Ability framework.** Per-session energy (regenerates each tick),
  three tick-counted cooldown slots, class-gating, and status effects —
  mob stun, an AC buff (brace/bypass), a damage+hit buff (stim), and
  stealth (backstab priming) — all folded into `combat_round`. Abilities
  resolve the instant they're typed, composing with the auto-attack.
- **M5-C/D/E/F — twelve abilities.** Pikeman `bash` (stun) / `brace` /
  `cleave`; Splicer `hack` / `overload` / `emp` (TEC-scaled, stun);
  Courier `sneak` / `backstab` (triple damage from stealth) / `bypass`;
  Chaplain `patch` / `stim` / `rally` (heal + buff). Cooldown / energy
  state is legible in the per-round condition line.
- **M5-H — solo verification.** A fresh-server-per-class harness confirms
  each class kills the Sentinel without dying twice.
- **`examine me`** is now a character sheet (class, HP/energy, attributes,
  AC); in-game `help` lists the player's class abilities.
- **`YD_TICK_MS`** env override for the combat-tick interval (mirrors
  `YD_IDLE_MS`) — fast ticks make combat verification quick.
- Unit suite grown 203 → 232 assertions (class load + fields, `class_by_input`
  number/prefix/trim/invalid, `apply_class`, `classes_upkeep` regen/decay,
  effective-stat buff helpers).

### Changed

- The login flow gained the class step: `login_on_name` now advances to
  `PHASE_CLASS` (not straight to the world); `login_on_class` applies the
  class and enters the world.
- `combat_round` reads buffed effective stats (`player_eff_ac` /
  `player_eff_hit` / `player_dmg_bonus`) and skips a stunned mob's turn;
  `combat_tick_all` runs `classes_upkeep` for every logged-in session.
- The combat load bench (`bench_combat.bcyr`) now includes `classes.cyr`
  and exercises per-tick upkeep alongside combat (p99 ≈ 57 µs).

## [0.5.0] — 2026-06-09

M4 — the tick gets a job. The placeholder 2.5 s Combat Tick from M1 now
resolves combat: a player engages a mob with `kill`, and each tick both
trade hidden-roll attacks until one dies. Mobs leave lootable corpses;
players respawn at the Hub. The full gameplay loop — explore, fight, loot,
carry, die, respawn — is playable end to end. Verified under load: 32
players × 64 mobs tick at a p99 of ~62 µs, ~800× inside the 50 ms budget.

### Added

- **Mobs** (`src/mob.cyr`). Templates load from `<zone>.mobs.cyml`
  (ADR 0005, `kind = "mob"`): id, display name, keywords, level, HP, AC,
  to-hit, and an `NdM+K` damage profile. Live instances spawn into rooms
  from each room's `mobs = "..."` list, on an intrusive room-occupant
  list; `mob_in_room_by_kw` resolves a typed noun against them.
- **Items + corpses** (`src/item.cyr`). Object templates from
  `<zone>.objs.cyml` (`kind = "obj"`); instances live in rooms,
  inventories, or containers on one shared list. A mob death synthesizes
  "the corpse of <mob>" holding the mob's `loot`, and `get all from
  corpse` (the M2 parser feature) empties it. `get` / `drop` /
  `inventory` wired to the live lists.
- **Combat** (`src/combat.cyr`). M4-A registry (per-session HP/AC/target +
  per-mob target). M4-B/C hit (`d20 + hit + AC >= 20`, nat-20 hits /
  nat-1 misses) and damage (`NdM+K`), hidden, prose-rendered. M4-D
  aggression: `kill` engages and the mob fights back; `flee` breaks off
  down a random exit; death disengages. The round runs inside
  `advance_tick`, flushed per session (the tick never frees a session —
  drops are left to the epoll path — so broadcasts are non-dropping).
- **M4-E** death + respawn. Mob → corpse + loot; player → drop inventory,
  respawn at the Hub start with full HP.
- **M4-G/H** drift + load test. The M1-H drift hook now wraps the combat
  tick; `benches/bench_combat.bcyr` drives 32 engaged sessions × 64 mobs
  through 120 real ticks and asserts p99 < 50 ms (measured ~62 µs).
- **Hub bestiary + loot** — `data/zones/hub.mobs.cyml` (scavver, rust-
  drone, wire-gang enforcer, the Foundry Sentinel boss) and
  `data/zones/hub.objs.cyml` (scrip, cells, plating, the Sentinel's core),
  spawned across the zone with per-mob loot tables.
- Unit suite grown 174 → 203 assertions (dice parse, RNG bounds, hit
  distribution, mob/obj template loading, spawn/find/remove, corpse + loot).

### Changed

- `cmd_dispatch` wires `kill`/`flee`/`get`/`drop`/`inventory`/`examine`
  to combat + items; the room render lists objects and mobs; `examine`
  resolves mobs (the M2 resolver's keyword scope is now live mob/item
  keywords). The session struct gains combat stats (`SS_HP`/`AC`/`TARGET`/
  weapon dice) and `SS_INV`.
- `g_epfd` moved to `session.cyr` (ahead of `combat.cyr`); room broadcasts
  and combat flushes are now non-dropping, so the combat tick can flush
  mid-walk without freeing a session.
- `cmd_serve` loads the Hub's objects + mobs and seeds the combat RNG at
  startup.

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
