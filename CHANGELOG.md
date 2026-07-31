# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Gate re-run #3 — DO-NOT-CLOSE (2026-07-31)

Run against a clean tree at `84c9a3a`. **0 critical, 4 high, 5 medium, 7 low** —
16 distinct defects from 19 candidates, one refuted. Recorded as roadmap items
**AJ-AY**; no code changed in this entry.

**This run could BUILD AND RUN.** Re-run #2 executed nothing and named that as its
own worst limit. Every finder here got an isolated git worktree and was told to
measure rather than estimate, and three of the four highs were demonstrated
against a **live server over TCP**: `passwd` mid-fight leaves a player permanently
immune (0 combat lines in 40 s while engaged); an unauthenticated peer burns
**200 account slots in 0.46 s** with zero records written; and one **one-character**
typo in `hub.objs.cyml` silently and irreversibly empties the inventory of every
player who connects during the outage.

**Three of the four highs are a rule applied at one site and not its sibling, and
two are siblings of fixes this release line shipped.** A rejected class table is
fatal at boot (1.7.11); a rejected objects table **35 lines above in the same
function** carries on. The 1.7.11 classless heal loses the player's room.
1.7.11's `session_persistable` gate made the account-cap phantom permanent.

**Two of the six benches in the audit gate cannot fail** — `bench_telnet` has no
budget constant and returns 0 unconditionally, and `tests/*.bcyr` is an explicit
no-op. `cyrius audit` has reported 6/6 throughout while 2 of the 6 were
decoration.


### Gate re-run #2 — DO-NOT-CLOSE (2026-07-31)

Run against 1.7.10. Five independent finders over distinct surfaces; every
candidate faced three skeptics with separate lenses (correctness / reachability /
novelty) and had to survive a majority; the judge reproduced each survivor against
the shipped tree. **Nothing was dropped.** Ten reports collapsed to **eight
distinct defects** — roadmap items **AC-AI**.

**Critical 0 · high 2 · medium 3 · low 3.** No code changed in this entry; the
findings are recorded in [`roadmap.md`](docs/development/roadmap.md) and scheduled
across 1.7.11-1.7.14.

Both highs are operator-facing data loss and neither needs an attacker:

- **A clean shutdown saves nobody.** `cmd_serve`'s exit never walks
  `g_session_head`, so SIGINT/SIGTERM loses up to five minutes of progress for
  every connected player, on every restart — while `docs/guides/running.md`
  promises the opposite.
- **A character can be persisted with no class, permanently.** `SS_AUTHED` is set
  before class selection and `PHASE_CLASS` is stored in exactly one place in the
  tree, so there is no route back to the menu. Worse: a failed `classes.cyml` load
  is non-fatal, the load path clamps every character to `class = -1`, and the next
  disconnect writes that demotion to disk. One operator typo plus a restart is
  playerbase-wide and irreversible, because records are signed with a key derived
  from the player's passphrase.

**For the fourth consecutive sweep, most findings are a rule applied at some sites
and not the others.** The unmetered epoll teardown is *verbatim* the 1.7.0 finding
— fixed in `drain_pending_rx`, never carried to the batch loop, in the release
whose own comment says "ONE constant for BOTH dispatch sites, on purpose".

**The sweep executed nothing** — no build, no suite, no bench, no running server —
so every figure in it is derived from source. That is not incidental: item AF
survived because `bench_tick_budget.bcyr` memsets its fixture, leaving
`SS_AUTHED = 0` so the arm it would measure cannot fire. **Gate re-run #3 must be
allowed to run the suite and the benches.**


## [1.7.17] — 2026-07-31

**Mechanics and instruments.** 1387 assertions (was 1362); `cyrius audit` exits 0;
6/6 benches; **2/2 fuzz targets**; both targets build; **9/9 mutations killed**.

The tail of gate re-run #3 — items **AP** and **AQ** plus **AR–AY**. With this,
**every finding from that run is closed.**

### Fixed

- **A mob could not kill an unengaged player (AP).** `classes_upkeep` treated
  `SS_TARGET == 0` as "out of combat", but combat is two-sided and the sides are
  recorded separately: `SS_TARGET` is what the PLAYER attacked, `MI_TARGET` is
  what the MOB attacked, and `_mob_assist` and the leash set only the latter. A
  player who never typed `kill` therefore regenerated every tick while being hit.
  Measured: **70 incoming swings in 60 s, 24 of them hits, HP never below 36/40.**
  `session_in_combat` now asks the question the comment always meant.

- **`parse_uint` wrapped silently (AR).** `v * 10 + d` overflows i64 with no
  check, so a 20-digit ordinal landed on some small positive number and `N.X`
  resolved to a **real object**. Refused at a documented domain bound instead —
  an ordinal above a million is not a number that lost precision, it is not an
  ordinal.

- **Death did not mark the record dirty (AT).** `player_died` drops the whole
  inventory to the floor and moves the body, and nothing flagged the record —
  `cmd_on_line` only flags the session that typed a command, and dying is
  something the tick does to you. A player who died and then sat still was skipped
  by the debounced sweep, so a `kill -9` restored them holding everything they had
  just dropped.

- **The hidden-roll RNG was seeded from uptime (AU).** `combat_seed(clock_now_ms())`
  — and `clock_now_ms` is milliseconds since **boot**, a distinction this project
  already learned the hard way in 1.6.8. A server started at a repeatable point in
  an init sequence replayed every combat roll identically, and ADR 0001 makes
  those rolls the game's only uncertainty. Now seeded from `random_bytes`, with
  the clock and epoch mixed in so a degraded entropy source cannot silently take
  the seed to a constant.

### Changed — the instruments

- **The M2-F fuzz gate was a no-op on half its iterations, and has been fixed and
  made self-checking (AQ).** `rng_next` returns a signed i64, so `r % 320` was
  negative on **49,585 of 100,000 iterations** — those fed a negative length and
  parsed nothing. The longest input it ever produced was **319 bytes against a
  4096-byte norm buffer**, so `pa_emit_byte`'s cap branch — the guard F3 (1.6.11)
  exists for — **had never once executed** while the gate reported PASS.

  Fixing the sign was not enough: uniform random bytes produce a delimiter every
  few bytes, so the *token* cap trips first and `PA_NORM_LEN` still peaked at 747.
  A quarter of iterations now generate long delimiter-free runs. **Result:
  `NORM_CAP` reached 7,988 times per run**, and the parser survives it.

  The harness now **asserts its own coverage** and fails if the inputs stop
  reaching the guards — the only way a fuzz gate can notice it has been defanged.

- **A second fuzz target: the pre-auth record scanner (AX).** `cyrius fuzz`
  covered exactly one project file while this project's docs name two untrusted
  inputs. `fuzz/record_fuzz.fcyr` fuzzes 1.7.8's `_scan_kv` — reachable by anyone
  who can open a socket and name a character that exists. 100k iterations,
  measured at 12,383 matches and 87,617 rejections, so both paths run. **The CYML
  zone loaders remain uncovered and are recorded as such**, rather than implied by
  a target that does not cover them.

- **Two of the six benches in the audit gate could not fail (AW).**
  `bench_telnet` had no budget constant and returned 0 unconditionally;
  `tests/*.bcyr` is an explicit scaffold no-op. `cyrius audit` has reported "6
  passed" throughout for a five-bench gate. `bench_telnet` now gates at 30 ns/byte
  against a measured 5–6 ns — 5× headroom deliberately, because what it must catch
  is a regression in KIND (a syscall, an allocation, an accidental O(n²)) and this
  repo has been burned twice by nondeterministic gates. **Verified to exit 1 when
  breached.** The placeholder now announces itself so the count is not misread.

- **Two guards that had no test now have one (AV, AY).** The `sig` hex-length
  bound and the `MAX_SESSIONS` accept cap. `MAX_SESSIONS` was also verified live:
  **256 connections accepted, 44 refused.**

### Notes

- **The `sig` guard's observable is memory, not a return code.** Removing it still
  yields `-2`, because the signature then fails to verify anyway — which is
  exactly why it had no test and why the first version of this assertion could not
  kill the mutation. What it prevents is `hex_decode_into` writing 2500 bytes
  through a 256-byte buffer into the globals after it, so the assertion is now on
  a sentinel past `g_persist_dec`.

- **AS is a content constraint, not a parser bug, and is documented as one.** A
  noun spelled like a preposition can never be a direct object. Every candidate
  fix changed the meaning of inputs that *do* occur — treating a trailing
  preposition as a noun turns `put a in` from "put a into what?" into "put in" —
  so [ADR 0005](docs/adr/0005-zone-file-format.md) now states the authoring rule
  and the suite pins the behaviour so it cannot drift silently.

## [1.7.16] — 2026-07-31

**The peer-reachable highs.** 1362 assertions (was 1340); `cyrius audit` exits 0;
6/6 benches; fuzz clean; both targets build; **10/10 mutations killed**.

The three remaining highs from gate re-run #3 (**AK**, **AM**, **AL**), all
reachable by an ordinary peer with no admin and no malice.

### Fixed

- **Typing `passwd` mid-fight made you permanently immune (AK).**
  `combat_tick_all` gates the whole round on `SS_PHASE == PHASE_CMD`, and
  `mob_tick_all` skipped its own swing whenever the player was targeting that mob
  — deferring to a round that, outside `PHASE_CMD`, never runs. **Neither side
  swung.** Measured by the sweep at the authored 2.5 s tick: 0 combat lines in
  40 s while engaged, then combat resuming on the same engagement once the re-key
  finished. At 1 HP that is unbounded invulnerability from two shipped verbs, and
  the idle reaper cannot collect it either because every re-prompt refreshes
  `SS_LAST_MS`.

  The deferral now asks the question its own comment already stated — *will
  `combat_round` actually swing this?* — rather than approximating it with
  `SS_TARGET == m`. The consequence is deliberate: a player who opens the
  passphrase prompt mid-fight keeps taking damage and stops dealing it.

- **An object was duplicated on every logout/reset cycle (AM).**
  `_obj_id_world_count` summed room contents plus **online** sessions, and
  `maybe_zone_reset` defers while any player is in-world — so the session term is
  provably always zero on that path and the ceiling really meant "how many are
  lying in rooms". Everything carried offline was invisible, the reset minted a
  replacement, and the owner brought theirs back. Measured: six
  get/quit/reset/relog cycles turned one `notice` into **seven**, and produced
  **five copies of `relic`, which is authored exactly once**. Re-verified live
  after the fix: six cycles, still one.

  There is now an **offline census** — per-template counts of what saved records
  hold — seeded once at boot and moved by the two events that change it:
  `_restore_inv` takes a holding online at login, `session_drop_inv` returns it
  offline at disconnect, immediately after `drop_session`'s save.

- **The account cap counted sealed identities, not records (AL).**
  `g_account_count` was incremented the moment an identity was sealed, and
  **nothing anywhere decrements** — so a peer that hung up at the class menu burned
  a slot for a character that never existed. Measured: **200 slots in 0.46 s
  (436/s)** from one reused name and a 27-byte payload, unauthenticated, with
  **zero records on disk**, after which a genuine player is refused. The increment
  now happens where the record is actually written.

  **1.7.11 widened this without noticing**: `session_persistable` correctly
  stopped `drop_session` writing a classless record on abandon, and thereby
  removed the record that used to make the count true.

### Notes

- **The census design was wrong twice before it was right, and both were caught by
  measurement rather than review.** The first cut rebuilt it from disk at the top
  of every reset pass — correct, but `dir_list` and `str_from` allocate on an
  arena with no free, **measured at ~70 kB permanently lost per rebuild** on a
  path that runs every fifteen minutes. That is 1.7.1's item-C shape reappearing
  *inside the fix for a different unbounded-growth bug*. The second cut seeded it
  from `persist_init` — before the ready flag, so the builder's own
  `persist_init()` call recursed forever. A test now pins both the wiring and the
  ordering, because only the ordering makes it terminate.

- **`cyrius audit` failed where `cyrius test` passed, and the difference was real.**
  The reset now consults offline holdings, which makes anything driving
  `zone_reset_room_objs` depend on what is in `data/players` when the process
  starts — so a pre-existing assertion passed from a clean tree and failed after a
  prior test run had left records. The test now zeroes the census for the id it
  exercises and restores it. **A test whose outcome depends on disk state left by
  an earlier run is a landmine**, and this release added the coupling that armed it.

- **Two of this release's own test bugs.** `session_free` was called on a
  `_mk_sess` session, which leaves `SS_TS = 0` — `telnet_state_free` dereferenced
  it and the run died with SIGSEGV after printing its own group header, which is
  the "a test that dies silently reads exactly like a test that passed" lesson,
  live. And a fixture hardcoded template 0, which is authored exactly once and was
  already held by a leftover record, so the ceiling was permanently met and the
  restock assertion could never run; the template is now chosen at runtime for
  headroom.

## [1.7.15] — 2026-07-31

**The operator-edit blast radius.** 1340 assertions (was 1310); `cyrius audit`
exits 0; 6/6 benches; both targets build; **9/9 mutations killed**.

The first three findings of gate re-run #3 (**AJ**, **AN**, **AO**). One trigger
between them: an operator edits a data file, and the server runs on with a
half-published table or a positional reference that has moved.

### Fixed

- **One typo in a zone objects file silently and irreversibly emptied every
  player's inventory (AJ, high).** `world_load_objs` unpublishes the whole table
  on any failure, and `cmd_serve` printed a diagnostic and **carried on**. With
  the table empty every saved inventory id failed to resolve, `_restore_inv`
  dropped the lot in silence, and `drop_session` wrote the emptied inventory back.
  Irreversible — records are signed with a key derived from the player's
  passphrase, which the server never holds (ADR 0004).

  Measured by the sweep against a live server and re-verified here: a
  **one-character** edit (`kind = "obj"` → `"objj"`), and a player who connects
  once and is RST-closed **while typing nothing** loses everything. The server now
  refuses to start, **exit code 1**.

  **1.7.11 made exactly this fatal for `data/classes.cyml` thirty-five lines
  below, in the same function**, under a comment explaining precisely why carrying
  on is catastrophic. The class table got the guard; the object table did not.

  Keyed on the loader's **return code**, not on `g_obj_tpl_count == 0` the way the
  class check is: a zone that authors no objects is legitimate and loads
  successfully with a count of zero, so the two tests are not interchangeable.

- **The silent half of AJ, which the boot guard does not cover.** An operator who
  legitimately removes one authored object still costs every holder that item at
  their next login. That is arguably correct — it no longer exists — but it must
  not be invisible. `_restore_inv` now returns the number of ids it could not
  resolve; the player is told, and an audit entry records it.

- **`class` was persisted as a positional index into `data/classes.cyml`
  (AN, medium).** Adding or removing a class silently re-assigned every existing
  character — a Chaplain logs in as a Courier. `room` is stored as a stable id
  string **one line away**, and ADR 0006 states the rule in the same sentence that
  lists `class`. Now written by id, with the read path accepting **both** forms so
  existing records migrate the first time they save. No schema bump — which
  matters, because ADR 0004 means there is no offline migration and cannot be.

- **1.7.11's classless-record heal threw away the player's room (AO, medium).**
  The heal correctly sent the player back to the class menu; the menu's exit path
  then called `session_enter_world`, which **overwrites `SS_ROOM` with the start
  room**. Silent, permanent relocation. A defect inside this line's own fix, and
  the shape this project keeps finding: 1.7.11 did not ask what the menu's exit
  would do to the state it had just restored.

### Notes

- **`AK_NKEYS` was bumped with the new audit key, on the second attempt.** The
  first cut added `AK_LOAD_INV_DROP = 21` against `AK_NKEYS = 20`. The guard in
  `audit_keyed` catches an out-of-range key and falls through to a verbatim
  `audit_event` — so nothing crashes, and every occurrence quietly costs **1944
  permanent bytes**, which is the 1.7.1 defect reintroduced one key at a time. The
  comment at that guard predicted this exact mistake; a comment saying so is not
  the same as a check, and this one was caught by reading rather than by a test.

- **Three of this release's own test bugs, each of a named kind.** `cl_at` returns
  a **pointer into** the class table, so holding it across a swap compared an entry
  with itself and would have passed no matter what. A hand-built "legacy" record
  omitted `salt` and `pubkey` and so returned -2 long before reaching the `class`
  field it existed to test. And `room_broadcast` **excludes the arriving session**,
  so the arrival-prose assertion was watching the one observer that can never see
  it — the fix needed a second session standing in the room.

- **A guard that survives deletion is not a guard.** Mutation testing showed the
  audit entry, the exact-match requirement in the id lookup, and the new/returning
  distinction each survived being removed. The first two had no assertion at all;
  the third is behaviourally identical except for the arrival prose, because
  `session_resume_world` falls back to the start room when `SS_ROOM` is -1 — so
  only an onlooker can tell the paths apart, and now one does.

## [1.7.14] — 2026-07-31

**Hygiene — the last two items from gate re-run #2.** 1310 assertions (was 1295);
`cyrius audit` exits 0; 6/6 benches; both targets build; **9/9 mutations killed**.
Both were graded low, and both are the kind of thing that only ever gets fixed in
a release that has nothing more urgent in it.

**Every finding from gate re-run #2 is now closed** (AC–AI).

### Fixed

- **Key material outlived the operation that made it (AH).** `ident_derive`
  copied the player's **plaintext passphrase** to `g_ident_scratch + 16` and the
  **Ed25519 seed** — the private key in its most compact form — to `+200`, and
  wiped neither. That block is `alloc`ed and the bump allocator has no free, so
  both sat in the process image for its whole life. Worse than "the last one
  stays": each derive overwrites only a **prefix**, so the tail of the longest
  passphrase ever seen persisted indefinitely.

  `login_on_confirm` separately left a full 64-byte secret key at
  `g_persist_dec + 160`, in scratch that every session shares. Its wipe is placed
  **before** the match/mismatch branch on purpose — the mismatch path is the early
  return an attacker can drive repeatedly. `chpass` needed no equivalent: it
  derives into the per-session candidate block, which `sess_cand_clear` has wiped
  since 1.7.3.

  There is no wire-reachable disclosure primitive in this tree today, which is why
  the gate graded it low — but that is a statement about this month's code, and a
  core dump, a debugger or a future OOB read is not bound by it. The rule was
  already in force at `sess_cand_clear` and `session_free`; these were simply the
  third and fourth holders of key material and nobody had looked.

- **`sweep_idle` charged unauthenticated reaps against a signature budget (AI).**
  `IDLE_REAP_MAX`'s entire derivation is *"every reap is a signature"*, and that
  was never true for the pre-auth reaps `PREAUTH_TIMEOUT_MS` (1.6.13) exists to
  serve. `drop_session` saves only what `session_persistable` admits, so an
  unauthed reap is a `close` and a list unlink — none of the 1.30 ms this cap
  exists to ration. Charging it one anyway meant **a burst of slowloris
  connections could exhaust the tick's reap budget and delay eviction of exactly
  the sessions the timeout is for.**

  The predicate is sampled **before** the teardown, because `drop_session` calls
  `session_free` and reading `SS_AUTHED` afterwards is a use-after-free — the
  H1 / M12-C shape.

### Notes

- **Honest scope on AI:** this does not close slot exhaustion. A peer sending one
  byte every 29 seconds keeps a session non-idle and holds its slot regardless of
  how the reap budget is spent. What this fixes is the reap budget being consumed
  by work that costs nothing.

- **A test that pinned the cap with the wrong population.** The existing
  idle-reap assertion built its fixtures with bare `_freeable_sess()` — i.e.
  `SS_AUTHED = 0` — so after AI they cost nothing and are no longer rationed, and
  the assertion failed. It was not wrong to fail: it had been pinning
  `IDLE_REAP_MAX` with exactly the sessions the cap was never about. It now
  asserts both halves — the cap holds for reaps that cost a signature, and
  unauthenticated ones are reaped uncapped.

- **A third guard that only the source can hold.** Sampling `session_persistable`
  after the teardown is a use-after-free that **no test can see**: the freelist
  hands blocks back without zeroing, so the stale bytes read the same and the
  mutation passes every behavioural assertion. The ORDER is pinned from the
  source, as 1.7.11 and 1.7.12 pin their call sites. Three releases running have
  needed that technique, which is itself worth noticing.

## [1.7.13] — 2026-07-31

**The reserve is per-command; the queue is per-read.** 1295 assertions (was
1270); `cyrius audit` exits 0; 6/6 benches; both targets build; **7/7 mutations
killed**.

One accounting error at two altitudes — which is why the roadmap insisted this be
a single edit. Fixing either alone leaves the mechanism intact.

### Fixed

- **Altitude 1 — `examine` rendered authored bodies unbounded.** Room prose, mob
  descriptions and object descriptions are all raw `(ptr, len)` borrowed straight
  from the parsed CYML buffer, with no `copy_str_capped` anywhere on the path, so
  their length is whatever an operator authored — and `item_new` propagates the
  object pointer verbatim into every instance of that object. **Measured: a
  6000-byte mob body ran the queue dry at 4096 and the prompt never arrived.**

  1.7.9 fixed exactly this for the room header and clamped it **inline**, which is
  why the two `examine` arms were missed. The clamp is now a function —
  `session_append_bounded` — and the room header uses it too, so there is one
  implementation rather than a fourth hand-written copy waiting to be forgotten.

- **Altitude 2 — output accumulated across a whole read.** Nothing flushes between
  the lines of one read (1.6.8 coalesced writes to one per session per tick, and
  that is worth keeping), so up to `RX_MAX_LINES = 8` commands share one 4 kB
  queue while `room_line_fits` re-measures its 512-byte reserve against the
  **whole buffer** each time. Every guarded section stopped correctly; what
  accumulated was the ~260 bytes of header, exits and prompt that no check
  covered. **Measured: eight `look`s in a busy room ran the queue dry at 4096,
  the last reply cut mid-number inside its own "...and 120 more items" tail.**

  The room display and the exits line now decline **whole** rather than emit a
  fragment, so the reserve they leave untouched is what carries the prompt.

  | | before | after |
  |---|---|---|
  | `examine`, 6000 B authored body | 4096 — run dry, **no prompt** | 3606, prompt |
  | 8 × `look` in a busy room | 4096 — run dry, reply cut mid-number | 3646, prompt |

### Notes

- **Fixed on the OUTPUT side only, which is 1.7.9's lesson restated.** The obvious
  alternative — flush between dispatched lines, or stop dispatching when the queue
  is full — was rejected twice over: flushing per line undoes 1.6.8's coalescing
  (the change that took the 256-player broadcast from 81 ms to 27 ms), and
  refusing to dispatch while the queue is full couples input to output and
  deadlocks in precisely the way 1.7.9's first draft did. Bounding what is written
  has neither problem.

- **The loader cap was considered and deliberately not taken.** The roadmap
  suggested capping `MT_DESC` / `OT_DESC` at load. The descriptions are
  *zero-copy borrows* into a buffer that is already resident, so a loader cap
  saves no memory and only adds a second place for the length to be wrong — while
  silently discarding authored text that a future paginated reader could use.
  Clamping at render is necessary and sufficient, and matches what 1.7.9 chose for
  room prose.

- **A guard with two callers, tested through one, is a guard tested through none.**
  The exits-line guard survived its first mutation because `session_show_room`
  returns before reaching it — but the `exits` VERB calls
  `session_append_exits` directly, with no header check in front of it. That
  second path is where the guard earns its place, and it had no test.

- **A fixture that cannot distinguish the guard from its absence proves nothing.**
  The first attempt at that assertion filled the queue to one byte past the
  reserve line, where the exits line still fits — so it passed with the guard
  deleted. It now fills to within 24 bytes of the cap, which is the state
  accumulation across one read actually produces.

## [1.7.12] — 2026-07-31

**Persistence integrity, and the bench that could not see the defect it was
written to watch.** 1270 assertions (was 1259); `cyrius audit` exits 0; 6/6
benches; both targets build; **5/5 mutations killed**.

### Fixed

- **A refused duplicate login reverted the real session's state (AE).**
  `player_auth_load` sets `SS_AUTHED = 1` — the passphrase really did check out —
  and the double-login refusal then set `SS_QUIT` and **left `SS_AUTHED` set**. So
  the refused duplicate still owned the record, and `drop_session` wrote its
  load-time snapshot over everything the live session had done since.

  **The window is not one batch, which is why this looked harmless.** On the epoll
  path the teardown does follow immediately. On the retained-line path it does
  not: once `EVENT_LINES_MAX` is spent, `session_consume_rx_max` retains the
  passphrase line and `drain_pending_rx` dispatches it in its *else* arm, which
  sets `SS_QUIT` and does **not** drop. That consume also empties `SS_RX_LEN`, so
  `g_rx_backlog` is not incremented and the loop parks in `epoll_wait` for a full
  tick — the stale snapshot is held **up to 2500 ms**, spanning a later batch. A
  victim's `passwd` or `save` inside that window was silently reverted.

  One line: clear `SS_AUTHED` in the refusal arm. Item duplication was chased here
  too and is **not** a risk — `session_drop_inv` frees the copies `_restore_inv`
  minted rather than dropping them to the room.

- **The epoll batch and the AGNOS sweep tore sessions down unmetered (AF).**
  `drop_session`'s first act is an unconditional `player_save`, one
  `ed25519_sign` — `CHG_SIGN = 10` against a `PASS_CHARGE_MAX` of 20. Neither
  batch loop consulted the meter, so a full batch of `MAX_EPOLL_EVENTS = 64`
  condemned sessions spent **640 charge units inside a 20-unit window** while
  every other path in the pass believed it was metered.

  **This is verbatim the 1.7.0 finding** — fixed there for `drain_pending_rx`,
  never carried to the two batch loops, in the release whose own comment reads
  *"ONE constant for BOTH dispatch sites, on purpose."* Both loops now use that
  same shape: the teardown happens (it cannot be deferred — the fd is a real
  resource, and deferring the save would hold a pointer `fl_free` is about to
  reissue), the meter sees it, and the rest of the batch waits. epoll is
  level-triggered, so every event not read is reported again next pass.

- **`cmd_give` did not mark the recipient dirty.** `cmd_on_line` flags only the
  session that typed the command, and this is the one verb in the tree that
  mutates another session's persistent state. Swept rather than assumed: nothing
  else writes `SS_INV` / `SS_HP` / `SS_CLASS` on a session other than the actor,
  and `ability_heal` is self-only. Without it the debounced sweep could skip a
  recipient who then did nothing, so a gift lived on the giver's record and not
  the receiver's until their next command or disconnect.

### Changed

- **`bench_tick_budget` gained the arm it was missing, and it is a real gate.**
  Every fixture in that bench was `memset` to zero and therefore had
  `SS_AUTHED = 0`, so `drop_session`'s save arm could not fire and the teardown
  measured as **nothing**. That is why AF survived a gate sweep *in code this
  bench exists to watch.* A new `tb_condemned` fixture drives the real arm at the
  real bound (`MAX_EPOLL_EVENTS`, not the smaller `TB_ATTACKERS`), and the numbers
  are measured both ways:

  | | teardown | torn down | gated pre-tick total |
  |---|---|---|---|
  | **with the fix** | 2 ms | 3 of 64 | 6 ms — 12% of the drift allowance, PASS |
  | **without** | 55 ms | 64 of 64 | **59 ms — 118%, FAIL** |

  So AF was a real breach of the ADR 0001 drift allowance, not a theoretical one.

### Notes

- **`drop_session` still does not consult `SS_SAVE_DIRTY`, deliberately.** The
  gate re-run asked whether it should. The answer is no while the flag has holes
  like the `cmd_give` one this release just fixed — an unconditional save on the
  way out is what has been covering for them. Gating on a flag we have evidence is
  wrong would convert a latent inconsistency into real data loss.

- **A line that looked like a guard and was not.** The refusal arm first got a
  belt-and-braces `SS_SAVE_DIRTY = 0` alongside the `SS_AUTHED` clear. Mutation
  testing showed nothing could tell whether it was there — with `SS_AUTHED` clear
  the flag is never consulted again — so it was removed rather than shipped as
  untestable ballast.

- **A presence check is not a wiring check.** The first source-level assertion for
  AF only proved the drop arms were no longer one-liners, and passed with either
  batch loop's meter deleted — *the exact state that shipped for eleven releases*.
  It now counts: the meter must be consulted at **all three** drop sites, and each
  must re-arm the loop.

- **The test that failed for the right reason.** AE's end-to-end assertion first
  came back `got 8, expected 99`, because the fixture raised `hp` above its
  `maxhp` and the H3 invariant clamped it straight back on load — the assertion
  was measuring the clamp, not the defect. This project has a standing lesson
  about exactly that, and it cost one debugging round to re-learn.

## [1.7.11] — 2026-07-31

**The two highs from gate re-run #2.** 1259 assertions (was 1229); `cyrius audit`
exits 0; 6/6 benches; both targets build; **10/10 mutations killed**. Both are
operator-facing data loss and neither needs an attacker.

### Fixed

- **A clean shutdown saved nobody (AC).** `cmd_serve`'s exit was `println` →
  `audit_flush_all` → `sock_close` → `return`. It never walked `g_session_head`,
  and `handle_signal` only sets `stop = 1`. Every `player_save` call site in the
  tree — creation, the `save` verb, `save_sweep`, `drop_session`, chpass — is on
  some other path, so **SIGINT/SIGTERM lost up to `SAVE_SWEEP_MIN_MS` (five
  minutes) of progress for every connected player, on every restart.**

  Verified against a live server, not only in the suite: a player picks up an item
  and holds the socket open, the server takes SIGTERM, and it now logs
  `server: saved 1 session(s) on shutdown` with `inv = "notice"` on disk. Before
  the fix that item was simply gone.

  The walk is deliberately **not** `drop_session` (the process is exiting; closing
  fds and freeing memory buys nothing, and `drop_session` unlinks mid-walk) and
  deliberately **unbudgeted** (every other save path is metered because it competes
  with the tick; this one has no next tick to protect).

- **A character could be persisted with no class, permanently (AD).** `SS_AUTHED`
  is set in `login_on_confirm` *before* the class menu, and `drop_session` gated on
  `SS_AUTHED` alone — so closing the window at the menu wrote a `class = -1`
  record. It was **permanent**, because `PHASE_CLASS` is stored in exactly one
  place in this tree (the creation path), so nothing ever returned a player to the
  menu; and an operator cannot repair the file, because records are signed with a
  key derived from the player's passphrase, which the server never holds
  ([ADR 0004](docs/adr/0004-identity-and-authentication.md)).

  **The worse trigger was the operator's.** A failed `data/classes.cyml` load left
  the table empty and `cmd_serve` carried on — *"no classes loaded — players spawn
  classless"*. With the table empty, the load path's `cls >= g_class_count` clamp
  demoted **every** character to `-1`, and the next disconnect wrote that demotion
  to disk. **One typo plus a restart was playerbase-wide, irreversible loss.**

  Closed at all three points, because any one alone leaves a hole:
  - `session_persistable` replaces the bare `SS_AUTHED` test at the disconnect and
    shutdown paths, so no new classless record is written.
  - **The login path HEALS one.** A loaded record with `class < 0` is sent back to
    the class menu instead of resumed into the world. This is the half that
    matters for records already on disk — a save-side guard alone would leave
    those players stuck forever, with no one able to fix it.
  - **An empty class table is now a FATAL boot error**, exit code 1. A server that
    cannot make a character was never a working configuration; the affordance was
    buying nothing and costing everything.

### Notes

- **Two guards that no runtime instrument in this suite can see.** The suite
  cannot run `cmd_serve` — it parks in `epoll_wait` — so "the function is correct
  but nothing calls it" is invisible, and *that is precisely what AC was*: every
  save path existed and none was on the shutdown path. Mutation testing said so
  out loud: removing the `shutdown_save_all()` call and removing the fatal boot
  check each broke **no test**. Both are now asserted from the source, the same
  way 1.7.8 guards the raw-syscall class — the call must exist, must sit inside
  the shutdown epilogue, and must run before `audit_flush_all` so a save failure
  still reaches the log.

- **A landmine in this release's own test, caught by its own mutation run.** The
  group asserts the ABSENCE of records, so the mutation passes — which
  deliberately run with the guards removed — left `ShutThree` and `MenuQuit` on
  disk and poisoned every subsequent run. The group now unlinks its fixtures
  first. *"A test that is not idempotent is a landmine"* has been in this
  project's lessons since 1.6.x, and a group whose assertions are about absence is
  the easiest place to repeat it.

- **The docs promised the opposite of what the code did.**
  `docs/guides/running.md` said *"Shut down cleanly with SIGINT/SIGTERM; a
  `kill -9` is safe too"*, which reads as "clean shutdown is at least as safe" —
  and [ADR 0006](docs/adr/0006-persistence-shape.md)'s save-trigger list did not
  include a signalled shutdown at all. Both corrected.

## [1.7.10] — 2026-07-30

**Toolchain 6.4.86 → 6.5.4, and the dependency snapshot with it.** A release of
its own, per the 1.2.0 precedent: that upgrade repaired a `main` and a bench that
had both silently stopped compiling, which is not something to discover folded
into a feature change. 1229 assertions; `cyrius audit` exits 0; 6/6 benches; both
targets build. **No source change was required.**

### Changed

- **`cyrius.cyml` pins `6.5.4`** (was `6.4.86`). The installed toolchain had been
  ahead for three releases and `cyrius audit` emitted a drift warning on every
  run; that warning is now gone.

- **`cyrius lib sync --full` refreshed the vendored snapshot** — 9 files moved:
  `bayan`, `sigil`, `sigil-mldsa`, `sakshi`, `sandhi`, `yukti`, `io`, `regex`,
  `vec`. `cyrius deps` re-resolved and rewrote `cyrius.lock`.

- **The sakshi shadow gap is CLOSED.** `sakshi 2.4.3 → 2.4.7`. This had been
  carried in `state.md` as a known upstream gap since 1.2.0 — sigil pinned 2.4.3
  in its own manifest while the toolchain bundled a newer one, so `cyrius deps`
  wrote the older copy over the synced one on every resolve. It resolves cleanly
  at 6.5.4 and needs no sigil-side change after all.

### Verified rather than assumed

The two things a dependency bump could plausibly have broken here, both checked
explicitly because the code that depends on them shipped in the last two releases:

- **`lib/io.cyr` still carries the AGNOS branches.** `file_rename` and `xunlink`
  both keep their `#ifdef CYRIUS_TARGET_AGNOS` forms with the length-carrying
  arities 1.7.8's persistence fix routes through. `io.cyr` was one of the nine
  files the sync moved, so this was a real risk, not a formality.
- **`lib/bayan.cyr` moved (1.2.1 → 1.3.0) and the TOML behaviour 1.7.8 reasons
  about still holds.** The parser-differential guard depends on bayan taking the
  FIRST match on a duplicate key and accepting shapes the strict scanner skips;
  the `preauth-alloc` group asserts both through crafted, validly-signed records,
  and it passes unchanged.

### Notes

- **Measurably faster, for free.** `bench_combat` p99 fell **530 µs → 444 µs**
  (32 players × 64 mobs) and the gated pre-tick total **4 ms → 3 ms**. Recorded
  because the numbers in `state.md` are quoted elsewhere and would otherwise
  drift; nothing in this tree changed to earn them.

- **Two shadow warnings remain, and they are the toolchain's, not ours.**
  `mabda 4.0.7` and `yantra 1.0.2` are left untouched by `cyrius lib sync --full`
  even though it reports a full 99-file snapshot — the same quirk `state.md` has
  recorded since 6.4.83, now affecting `mabda` as well as `yantra`. Neither is
  referenced anywhere in `src/`, `tests/` or `benches/`, so the practical impact
  is a warning and two stale vendored files.

- **Binary grew 895,592 → 899,760 bytes** (+4,168).

## [1.7.9] — 2026-07-30

**The wire stops being cut in half.** 1229 assertions (was 1180); `cyrius audit`
exits 0; 6/6 benches; both targets build; **13/13 mutations killed**.

The RX-side class 1.7.7's sweep turned up. 1.7.6 and 1.7.7 made *listings* stop
mid-line; this release makes the same guarantee one layer down, where the unit
being cut is a **protocol sequence** rather than a line of prose.

### Fixed

- **A full queue cut Telnet escapes in half.** `session_consume_rx_max` drained
  the negotiation reply with a plain `session_appendtx` — which truncates at a
  BYTE boundary — and then called `telnet_tx_consume` **unconditionally**, so
  whatever did not fit was discarded. Measured by driving the real consumer with
  a queue 4001 bytes full and 50 `IAC DO 42` triples:

  | | TX after | complete triples | trailing PARTIAL escape |
  |---|---|---|---|
  | before | **4096 — run dry** | 31 | **yes** |
  | after | 4034 | 11 | no |

  The partial is a bare `IAC WONT` with no option byte, and a conformant client
  then takes the next data byte as the option code — corrupting everything after
  it. Appends of indivisible sequences now go through `session_appendtx_atomic`,
  which writes all of it or none.

- **The same defect at the two sites every real client hits.** `session_echo_off`
  and `session_echo_on` push a raw `IAC WILL/WONT ECHO` through the same
  truncating append, and they run from *inside* the dispatch path — after the
  passphrase prompt's prose is already queued. So they meet a full buffer sooner
  than the negotiation path does, not later. Found while reviewing the fix for
  the first site, and it is the instance that actually fires in ordinary play.

- **Neither of this server's input bounds could see any of it**, which is the
  more useful half. `RX_MAX_LINES` counts COMPLETED LINES and a negotiation
  triple yields `EV_NONE`, so `fired` stays 0. The 1.7.0 charge window bills only
  `ed25519_*` and prose bytes, and negotiation costs neither. Both were
  structurally blind.

- **The room header ran ahead of the sections 1.7.6 guarded, and could eat their
  reserve.** The title is capped by the loader (`RM_TITLE_CAP` = 80); the prose is
  not — it is a raw `(ptr, len)` borrowed straight from the parsed CYML buffer. An
  authored room with a body over ~3.5 kB truncated mid-prose *and* left the
  objects, mobs and present-player sections nothing to write into, including the
  512 bytes held back for the prompt. Guarding three sections and not the write
  that precedes them is the same partial application this line keeps finding.

- **`class_send_prompt` and `mob_swing`**, the last two loops of the 1.7.6 class.
  The menu is dormant at four shipped classes but stacks up to `RX_MAX_LINES`
  deep in one read. `mob_swing` is on the **tick path**, where `combat_flush` only
  marks the session dirty — 1.6.8 coalesced writes to one per session per tick —
  so every mob latched onto one player appends into the same 4 kB queue before
  anything drains it. Both follow 1.7.7's rule: the damage, the death check and
  the room broadcast happen regardless; only the echo is rationed.

### Notes

- **The first cut of this fix was worse than the bug, and the review caught it.**
  It refused to *read* input while the queue was full. That coupled input to
  output and deadlocked: with TX full and bytes retained, every pass consumed
  nothing, `drain_pending_rx` re-armed off `SS_RX_LEN > 0`, and the event loop
  clamped its timeout to zero — a **100% CPU spin doing no work**, which the idle
  sweep could not collect because `session_on_readable_max` refreshes the activity
  stamp off retained bytes alone. One connection writing ~8 kB and then not
  reading would have pinned the loop indefinitely. Bounding the OUTPUT has
  neither problem, and a test now pins that difference.

- **A comment's arithmetic, corrected before anyone inherited it.** An earlier
  draft of the bound said one fed byte can emit 3 + 34 bytes. It cannot: a
  negotiation byte returns `EV_NONE` and `session_push_line_byte` runs only under
  `EV_DATA`, so the two are mutually exclusive and the maximum is 34. Nothing
  turned on it — which is exactly how a wrong number survives.

- **Roadmap item Y is settled as WON'T FIX, and the roadmap was the thing that
  was wrong.** `_restore_inv` enforces no carry cap, and this project's own
  roadmap has recorded that as *closed* since 1.7.2. Measured: a crafted record
  restores at most **1,583** items (not the "~4000" claimed — `SLURP_CAP` bounds
  it); `item_new` uses **`fl_alloc`, not the bump allocator**, and the memory is
  **fully reclaimed at disconnect on every exit path**; and a record a real server
  can produce already holds up to **~685** items, because the binding constraint
  is the writer's byte budget and never the carry cap. **Clamping to `MAX_INV` on
  load would destroy real players' belongings** — which is what the source comment
  has said all along. The code was right; the document was wrong for five
  releases. Severity: low, no code change.

- **Carried, not fixed:** item **AA** (16 bytes of bump arena per completed TCP
  handshake, from a boxed `Ok(cfd)` in `lib/net.cyr` — the allocation is upstream,
  the connection count is ours), and the stateless-refusal amplifier
  (`telnet_respond_refuse` answers every repeat of an untracked option, and the
  Q-state arrays to fix it already exist). Neither blocks the gate; both are in
  the roadmap.

## [1.7.8] — 2026-07-30

**AGNOS persistence, and the pre-auth parse.** 1180 assertions (was 1118);
`cyrius audit` exits 0; 6/6 benches; both targets build; 12/14 mutations killed
(the two exceptions are stated below rather than rounded up).

The last two high findings from the gate re-run. Both had been true for many
releases; neither could fail a test, for two different and instructive reasons.

### Fixed

- **On the AGNOS build, a player record was never published at all.**
  `player_save` renamed its temp file with a raw `syscall(82)` and retired the
  legacy flat copy with `syscall(87)`. Those are `rename` and `unlink` on x86_64.
  On AGNOS they are **`SYS_GPU_DISPATCH` and `SYS_GPU_BLIT_SHM`** — the latter
  annotated in the stdlib, in as many words, *"UNLINK on Linux — DELETES A
  FILE"*. The record directories were not created either: `sys_mkdir` takes a
  **mode** on Linux and a **path length** on AGNOS, and the call passed 0755.

  So on `--agnos`: character creation warned it could not write, every autosave
  and disconnect save failed the same way, and **every reconnect was offered a
  brand-new character.** README and `docs/guides/running.md` had advertised
  AGNOS persistence as working identically since 1.1.0.

  All three now go through the portable `lib/io.cyr` wrappers (`file_rename`,
  `xunlink`) or one new `_mkdir_portable` helper carrying the `#ifdef` shape
  `player_exists` already used. **The stdlib was never wrong** — `lib/io.cyr` has
  had correct AGNOS branches since before this bug, and the comment at the 1.7.4
  audit-rotation rename says to use them "not the raw syscall above". That
  release fixed its own new code and did not go back six lines.

- **Every login attempt against an existing name permanently consumed 2,248
  bytes.** `player_auth_load` parsed the whole record with `toml_parse` *before*
  checking the passphrase, and that memory never comes back: the bump allocator
  has no free at all, and the freelist never munmaps. Reachable by anyone who can
  open a socket — no account needed, and the login prompt itself answers which
  names exist. Five guesses per connection is ~11 kB gone forever per connection,
  and 1.7.1's rollup window correctly suppresses the repeated audit entries, so
  the instrument stays quiet while it happens.

  The decision needs only `salt` and `pubkey`, both written by `_fhex` as exactly
  `<key> = "<hex>"` on their own line, so both are now read straight out of the
  slurp buffer and the parse is deferred until the passphrase has proved itself.
  **Measured: 2,248 bytes per attempt → 0.** This is 1.7.0's argument one resource
  along — that release stopped a wrong passphrase paying for a 7 ms
  `ed25519_verify` it could not use, and left the parse where it stood. Unlike
  CPU, arena never comes back.

  It also removes a **null-dereference reachable from the unauthenticated login
  path**: `str_new` returns 0 under memory pressure and bayan's parser
  dereferences it immediately, so exhausting the arena crashed the server.

### Changed

- **CI builds the AGNOS target.** *The cause, not the instance.* `--agnos` was
  never built here, which is the whole reason a defect of this size lived in the
  tree. A compile is not proof the target works — nothing executes the AGNOS
  binary — but a signature change in an `#ifdef CYRIUS_TARGET_AGNOS` branch now
  breaks the build instead of rotting until someone runs the server.

- **`docs/guides/running.md` stops claiming what was not true.** Its AGNOS
  persistence paragraph is rewritten to say what broke, what changed, and — since
  nothing here boots AGNOS — that end-to-end persistence on that kernel has not
  been re-verified since the fix.

### Notes

- **The fast path is an optimisation, never a second record format.** The raw
  scanner is deliberately stricter than bayan, which accepts a leading indent,
  `salt="x"`, tabs around the `=`, and more. The first version of this fix
  returned a terminal `-2` whenever the strict scan failed — which would have
  turned every one of those shapes from "loads fine" into "your character is
  corrupt". A failed scan now **falls through** to the parser and the original
  code path, unchanged, and the fast path additionally declines any record not
  beginning `[player]` so it never reasons about sections it cannot see. Both
  behaviours are asserted.

- **The fix could have opened a worse hole than it closed, and the guard against
  it is verified rather than assumed.** Two readers now look at one record. bayan
  and the scanner both take the *first* match on a duplicate key, so a loose
  decoy line placed ahead of the real one is read by bayan and skipped by the
  scanner — measured on all four loose shapes. Without a guard, a crafted record
  could authenticate against the scanner's salt while every field was restored
  from bayan's. A validly-signed crafted record now proves the guard fires; an
  equal-prefix decoy proves the length half is load-bearing too.

  The first version of that test spliced a decoy into an existing record, which
  changed the signed prefix — so `ed25519_verify` refused it and the assertion
  passed **with the guard deleted**. Three mutations survived on it. A player owns
  their signing key (ADR 0004); the adversary signs their own crafted record, and
  so must the test.

- **Two mutations were not killed, stated rather than rounded up.** The pubkey
  half of the differential guard survives, because `filepk` is re-decoded from the
  *parsed* pubkey and the signature must verify under it — a pubkey differential
  is already fatal three steps later. It is kept anyway, because that subsumption
  is a fact about today's ordering rather than an invariant anyone declared. One
  further mutation was a stale pattern in the harness that failed to apply, which
  the harness reports as `BAD-PATTERN` rather than as a survivor — the 1.7.4
  lesson that *a mutation script that fails to apply reports a false SURVIVED.*

- **The only guard that could have caught the AGNOS bug reads the source.** No
  test running on x86_64 can distinguish `rename` from GPU dispatch, because there
  syscall 82 genuinely *is* rename; and a raw number compiles fine on both
  targets, so the new CI build does not catch it either. A suite assertion now
  requires `src/persist.cyr`, `src/session.cyr` and `src/item.cyr` to contain no
  raw numeric `syscall(` outside a comment, and proves itself non-vacuous by
  finding a planted one.

## [1.7.7] — 2026-07-30

**Carry the fixes to the sites they were never applied to.** 1118 assertions
(was 1048); `cyrius audit` exits 0; 6/6 benches; 17/17 mutations killed.

Two of the four findings that returned **DO-NOT-CLOSE** on the 1.x gate. Neither
is a new defect. Both are a rule this project had already written down, applied
at some sites and not at the others — and in both cases the correct code was
already in the tree, in one instance 230 lines below the broken one.

### Fixed

- **`get` of a container ignored what was inside it, and the next save destroyed
  the overflow.** `ilist_push` moves an object **and everything hanging off its
  `OI_CONTENTS`**, but both `get_from` arms asked only `inv_full(s)` — "am I at
  the cap right now" — which is a different question. Measured on this tree:
  holding 99, `oi_move_count` of a bag of 99 is 100, and the old guard returned
  **0 (allow)**. One ordinary `get` therefore landed the player at **199 against
  a cap of 100**, with the server saying only "You take …". Pushed further by the
  gate sweep: 721 carried, `_build_record` filling 4048 bytes of `SAVE_CAP` 4096,
  `player_save` returning **SUCCESS**, and the reload coming back with 591 —
  **130 items destroyed, silently.**

  The counting now lives in one function, `oi_move_count`, shared by `get` and
  `cmd_give`. `cmd_give` had computed it correctly since 1.7.3 and it was
  open-coded there, which is exactly why `get` kept the wrong question for four
  releases. The 1.7.2 `inv_owns_slot` exemption is unchanged and re-asserted: a
  move out of your own bag changes no total and must still be allowed at the cap.

- **`get all` no longer abandons the whole sweep because one thing did not fit** —
  a regression introduced by the fix above and caught by its own class sweep.
  Aborting on refusal was correct while the only question was "are you full": if
  you are, nothing else fits either. Once the question became per-item it stopped
  being correct, and one oversized bag would have made `get all` take **nothing**
  for a player carrying nothing. The arm now skips what does not fit and keeps
  going, and still exits early when genuinely at the cap, where walking the rest
  of an unbounded floor buys nothing.

- **The refusal message learned which of two facts is true.** "Your hands and
  pockets are full" told to someone carrying nothing — who simply reached for a
  bag bigger than the cap — is a lie the player can see, and counting contents is
  what made it reachable. At the cap the message is unchanged; below it the
  answer is now "You can't carry all of that." Both branches are asserted.

- **`inventory`, `who`, `drop all`, `get all` and `@who` ended mid-line with no
  prompt.** The defect 1.7.6 shipped a whole release to remove from `look`, at
  five sibling loops that release did not touch. Each wrote one coloured line per
  element into the 4 kB queue with no fit check; `session_appendtx` truncates at a
  **byte** boundary and returns a short count nobody reads, so the reply was cut
  wherever the buffer ran out — colour never closed, and **no prompt**, which
  leaves the session looking hung.

  Measured by driving the old loops against the real buffer:

  | listing | last size that worked | first size that lost the prompt |
  |---|---|---|
  | `inventory`, longest authored name (30 B) | 94 items, 4063 B | **95 items, 4096 B** |
  | `who`, 16-char names + Hub room titles | 78 players, 4062 B | **79 players, 4096 B** |

  **95 is under the game's own `MAX_INV` of 100** — a limit the server hands the
  player rather than one they have to work to reach. At 90 sessions the `who` cut
  landed on byte `0x80`, a UTF-8 continuation byte: the em-dash separator sliced
  in half mid-character.

  All five now stop at a whole item with the 512-byte reserve intact and report
  what they omitted. `@who` is dormant (the `@`-namespace is off unless
  `YD_ADMIN=1`) and was fixed in the same pass anyway — leaving the sleeping twin
  of a defect in place is how three of these four findings came to exist.

- **Rationing the echo must never ration the effect.** `drop all` and `get all`
  are commands, not reports. The fit check wraps only the echo; the move happens
  either way, so a player who types `drop all` ends up carrying nothing however
  much of the receipt fits on the wire. Both directions are asserted, and the
  mutation that pulls the move inside the check is killed by them.

### Changed

- `room_append_more` gained a general form, `list_append_more(s, n, what, tail)`.
  1.7.6 hard-coded " here.", which is a false statement in `who` — a listing whose
  entire subject is players who are somewhere else. The three room sections keep
  their original wording through the old name.

### Notes

- **Why none of this failed a test before.** The suite was green at 1048
  assertions with both defects present. Neither had a test, so neither could
  fail. Sixteen releases of mutation-testing each new guard never built the habit
  of testing the guard's **siblings** — the sites the same rule should have
  reached.

- **A mutation survived, and the test was what was wrong.** The first version of
  the `get all` coverage used bare floor items, and for a bare item
  `oi_move_count` is 1 — so the old guard and the new one are *the same
  function*. The test looked like it covered the arm and could not have failed
  whatever the arm did. Discriminating needs a floor container whose contents
  overflow the cap on their own (50 held + a bag of 99). Fourteenth instance of
  this project's standing rule: *a mutation that fails to fail is a signal about
  the test, not about the mutation.*

- **Sweeping the class is what found the next class.** Both defect classes were
  swept across the whole tree rather than patched at the two named sites, with
  every candidate adversarially refuted before being recorded. **Neither class had
  another instance** — the five listing sites and the three cap sites are all of
  them. What the sweep turned up instead was a *different* unbounded class, on the
  **RX** side: a pre-auth peer can drive the server's own Telnet reply buffer past
  `TX_CAP` three bytes at a time, and **both** of this server's input bounds are
  structurally blind to it (`RX_MAX_LINES` counts completed lines, and a
  negotiation triple completes none; the 1.7.0 charge window bills only `ed25519_*`
  and prose bytes, and negotiation costs neither). Eight items, filed as roadmap
  **W–Z** and *not* fixed here.

- **A correction to the roadmap, not to the code.** That sweep also established
  that `_restore_inv` enforces no carry cap at all, while the roadmap has recorded
  issue **E** as closed since 1.7.2. The source made a deliberate and defensible
  different choice — a record that already holds more than the cap must come back
  intact, because the cap exists to stop you acquiring, not to destroy what you
  have — but the roadmap was never corrected to say so. It has therefore claimed a
  bound that does not exist for five releases: *a comment is not a bound*, one
  level up from the code.

## [1.7.6] — 2026-07-29

**A room listing could break the terminal.** 1039 assertions (was 1024).

### Fixed

- **`look` output ended mid-escape-sequence with no prompt.** `session_show_room`
  wrote its sections as a run of unchecked `session_appendtx` calls, and that
  primitive truncates at a **byte** boundary and returns a short count nobody
  reads. Measured, by driving the real `cmd_on_line(s, "look", 4)`:

  | floor | bytes queued | objects rendered | prompt reaches client |
  |---|---|---|---|
  | 85 | 4,094 | 85 | yes |
  | **86** | **4,096 (= TX_CAP)** | 85 | **NO** |
  | 2,000 | 4,096 | 85 | NO |

  At 86 the 86th object's `ansi_item()` wrote 2 of its 5 bytes, leaving the stream
  ending `" here."` then a bare `ESC [` — an incomplete SGR, no CRLF, no colour
  reset, **no prompt**. A conformant terminal then eats the opening characters of
  whatever arrives next. The threshold is **71–87** depending on room header size
  and name lengths, and it never recovers, because a floor only grows.

  This is a **wire-correctness** bug of the same class as M10's sanitizer work —
  not a performance one — and **1.7.5's ground decay does not fix it**: a busy
  town square passes 86 items well inside the 30-minute decay window.

  All three listing sections — objects, mobs, present players — now stop at a
  **whole item** with a byte reserve held back, and say how many they omitted
  (`...and N more items lie here.`). Silently showing fewer things than are
  present is how a player walks past what they came for.

  The fit check in the player list runs **before** the separator, deliberately:
  writing `", "` and then finding the name does not fit leaves a dangling
  separator — a different malformed line than the one this release removes.

  Chosen over `session_tx_reserve` (which flushes to make room) because that needs
  a live socket and can still fall short if it does not drain; stopping at an item
  boundary is deterministic and correct regardless of socket state.

### Changed

- **Per-attempt creation auditing is restored, reversing G3 (1.6.12).** G3 moved
  `create.fail` to fire once at the cap because each entry cost 1,944
  permanently-unreclaimable bytes and the attacker set the rate. 1.7.1's rollup
  window removed that constraint — later occurrences tally at **zero allocation**
  — so per-attempt now costs the same arena and reports a truer number. **A flood
  is visible from the first attempt instead of the fifth**, and the rollup's count
  is the real attempt total rather than a count of sessions that reached the cap.

  A trade made under a constraint, taken back once the constraint was gone, rather
  than left in place because the code looked deliberate.

## [1.7.5] — 2026-07-29

**Ground decay — the last item of the 1.6/1.7 audit line.** 1024 assertions
(was 1007).

### Fixed

- **Nothing reclaimed a dropped item.** `obj_free` could not reach a non-corpse
  object on a room floor, so ordinary play — kill, loot, drop, quit — grew the
  floor forever: measured **40 cycles taking it from 0 to 80, monotonic**. And
  `look` walked that floor every time, **801 µs at 10,000 objects**, billed
  **zero** by 1.7.0's charge meter because the cost is unbounded in the *world
  state* rather than in the line. No budget of any denomination fixes that.

  Player-dropped items now decay after **two zone-reset intervals** — 30 minutes
  at the authored 900 s cadence, 720 ticks.

**Three decisions worth stating, because each has a trap behind it:**

- **Intervals, not reset events.** `maybe_zone_reset` *defers* while a player is
  in the zone and deliberately does not advance its timestamp when it does. So
  counting reset events would mean a permanently-occupied zone never decays
  anything — and a town square, the case this exists for, is the zone that is
  never empty.
- **`OI_AGE == 0` means "not armed".** `item_new` memsets, so authored zone
  furniture is minted unarmed and never decays; only a player putting something on
  a floor arms the clock. No new field, no new flag, and a reset's own furniture
  cannot expire out from under the room between resets.
- **Anchored to `reset_secs`, so there is no new knob.** A zone authored with a
  faster rhythm reclaims faster, and an operator lowering `YD_RESET_SECS` gets
  faster decay for free. ADR 0007 stays clean. Floored at `GROUND_TICKS_MIN` so a
  `reset_secs = 1` zone still leaves time to pick something up.

Re-dropping restarts the clock, so passing something hand to hand does not hand
along an almost-expired timer. A dropped bag decays as one unit — `obj_free`
already recurses through `OI_CONTENTS`.

### Note — the donation bin already exists

Items put into a **room container** are deliberately not armed, and authored
containers never decay, so a town barrel is a permanent shared stash. That is the
"donation bin" shape and it predates this release — but it is **unbounded**:
nothing caps a room container's contents and `look` does not walk them. Documented
at `cmd_put` and filed as a 2.0 item, where a real bin needs a zone field, a cap,
and persistence — all frozen surfaces in 1.x. A container a *player* dropped is
armed and decays with its contents.

## [1.7.4] — 2026-07-29

**Audit-log rotation ships.** 1007 assertions (was 971). The mechanism ADR 0009
decided in 1.7.1 and 1.7.3 deliberately deferred — because its crash window needed
to be the subject of a release, not a fifth item in one.

### Added

- **Audit-log rotation, seal-and-continue** ([ADR 0009](docs/adr/0009-audit-log-rotation.md)).
  On crossing 8 MiB the live log is renamed to `data/audit.libro.<N>` and appending
  continues to the same path with the **same streaming chain**, so the first entry
  after the rename carries the sealed segment's tail as its `prev_hash`. **The
  boundary is recorded by the chain itself, not by external metadata** — which is
  why no on-disk format change was needed and no libro release.

  On-disk growth is now a constant the code owns: `8 MiB × AUDIT_SEG_KEEP (4)` =
  32 MiB of sealed history plus a live file, **with no traffic term in it**.

- **The crash window is closed, and that is the load-bearing part.** Rename
  succeeds, process dies before the first append: the live file is gone, and a
  naive boot restarts the chain at genesis — one broken link per boundary,
  indistinguishable from a deletion, which is the H11 bug of 1.6.6 reintroduced as
  a feature. `_audit_resume_head` now falls back to the newest **segment**. Its
  mutation test deletes the live file and asserts the chain still resumes.

- **Deletions are attested before they happen.** `audit.prune` is written *before*
  the unlink, carrying the victim segment's head hash — a marker naming a file
  with no hash attests nothing. The test captures that hash before pruning and
  requires it in the marker, which is what makes the ordering mutation-visible.

- **Rotation refuses to clobber a sealed segment.** `rename(2)` replaces its target
  silently, so a stale segment cache — an operator dropping a file in mid-run —
  would be an unrecoverable deletion of attested history. It refuses, drops the
  cache, and self-heals on the next check.

- The size probe is metered by tick count, not by a clock: `sys_uptime_ms` is
  documented frozen on AGNOS, so a `now - last` rule would silently disable
  rotation on one of the two supported targets. It costs nothing on 23 ticks in 24.

### Notes

- Rotation reuses `audit_size_warn_due` and `AUDIT_SIZE_WARN_BYTES` — the same
  predicate and constant as 1.7.1's boot-time warning — so the warning and the
  rotation cannot disagree about where the line is.
- `dir_list` was rejected for segment enumeration: it `alloc()`s 4 kB of bump arena
  per call, permanently, and rotation calls it forever. That is the leak class
  1.7.1 spent a release removing. `file_exists` probing is ~2 µs and zero arena.
- Verification is no longer a single-file operation. The procedure is in ADR 0009;
  a `validate` argv verb is M14-E.

### Still open

- **The uncapped room floor** — nothing reclaims a dropped item, `look` costs
  801 µs at 10,000 floor objects, and the charge meter bills it zero. Design work
  was in flight when this released; it is the last item of the 1.6/1.7 audit line.
- Restoring 1.6.12's audit granularity, now affordable under the rollup window.

## [1.7.3] — 2026-07-29

971 assertions (was 946). Four of 1.7.2's six items; **audit-log rotation did not
land** — see below, and it is not a silent omission.

### Fixed

- **`give` did not count what was inside the gift.** It tested `>= MAX_INV` and
  then transferred the item *and its contents*, so handing a full bag to someone
  under the cap pushed them well past it — measured **141 against a cap of 100**,
  from one 51-item bag. Same shape as the carry-cap hole 1.7.2 closed on the
  acquisition path: the check counted one collection, the transfer moved another.
  Now asks "would this transfer exceed the cap", because the answer depends on
  what is being handed over.

- **A failing save retried on every tick.** `player_save` clears `SS_SAVE_DIRTY`
  only after a successful rename, and stamps "last saved" only on success — so a
  session whose save failed stayed dirty *and* stayed due, forever. Four signed
  saves every 2.5 s from sessions merely sitting there, and under ENOSPC the audit
  log grows fastest exactly when it can least afford to. A new attempt stamp backs
  the retry off to `SAVE_RETRY_MIN_MS` (30 s) — deliberately shorter than the
  autosave interval, so a transient failure recovers in seconds rather than
  minutes.

- **The resumed audit chain-link held a borrow into a reused buffer.** `str_new`
  stores the pointer rather than copying, so `_audit_resume_head` left the chain's
  prev-link pointing into `g_persist_slurp` — the same buffer `player_auth_load`
  reads player records into. Now copied into owned storage.

  **Stated precisely, because I could not prove the consequence:** this removes a
  real hazard (a stored reference to a buffer other code overwrites) but I did
  **not** demonstrate it producing a broken link — a probe reports zero breaks
  both with and without the copy. The working log does contain exactly one broken
  link, at record 554 of 39,245, and **its cause is unknown**; attributing it to
  this would be a guess. A latent hazard removed cheaply, not a diagnosed outage.

### Added

- **Two guards that had never had a test**, both found by coverage checks rather
  than by failure — reverting either changed nothing:
  - the `passwd` candidate block's **secret-key wipe** before it returns to the
    freelist. `fl_free` reuses blocks without zeroing, so an unwiped candidate
    hands the next allocation someone's private key.
  - the **double-login refusal at its call site**. The predicate had a test; the
    refusal did not, so replacing it with a constant false broke nothing. Two
    sessions on one character means two writers to one record — the inventory
    duplication 1.6.6 fixed.

### Not done, and why

- **Audit-log rotation (the ADR 0009 mechanism) did not land.** The decision and
  the seam shipped in 1.7.1; the rename/reopen, segment prune, markers and the
  rename-then-die crash window did not. Deferred rather than rushed: the crash
  window is the load-bearing part (a crash between rename and first append
  restarts the chain at genesis — the H11 bug reintroduced as a feature), and it
  belongs in a release where it is the main subject. **1.7.4.**
- **The uncapped room floor** and **restoring 1.6.12's audit granularity** also
  remain. The floor is the larger of the two and is object-lifetime work.

## [1.7.2] — 2026-07-29

**The carry cap becomes a bound, and the operator gets a say.** 946 assertions (was 921). The class sweep this release was named for found the defect **inside
1.7.1's fix for it**, which is the most useful thing in these notes.

### Fixed

- **A carried container flattened past the carry cap and poisoned the save —
  player-armable data loss, no malice required.** Two halves of one defect:
  - `inv_count` walked only the top-level chain while `cmd_put` moved items into
    a container *without counting them*, so the item left `SS_INV` and the count
    **dropped**. Fill your hands to 100, put 99 in a sack, acquire 99 more, repeat
    without bound. Nothing on the acquisition path could see it, because the
    collection it counted was not the collection the cap is about.
  - `_build_record` **flattens** one level back into the same `inv` field (F11),
    so the bytes a save must write are the *total*. When it ran out of budget the
    inner contents loop set `SAVE_ERR` — which M11-D turns into "refuse the whole
    record" — **ten lines below a comment saying, in those words, to truncate and
    not poison the record.** G1's 1.6.13 fix was real for the outer walk and undone
    for the inner one, so a player silently stopped persisting (room, HP, class,
    everything) until they happened to drop something. Verified: with the fix
    reverted, `player_save` returns `-1`.

- **The sixth instance of the defect class was inside 1.7.1's fix for the fifth.**
  The audit rollup's count arm **re-stamped `AKE_WOPEN`**, pushing the window's
  start forward on every fire, so above 136 events/sec the 60 s clock arm never
  came due again and the freshness guarantee vanished — while the comment beside
  it asserted the ceiling *"carries NO rate term in it"*. Measured flat at 120
  entries/hour to the crossover, then 441/hour at 1000 ev/s. The re-stamp is gone
  and the arithmetic is corrected to `2040/hour + events/8192`. **The bound held;
  the description was the defect.** Same shape as G2's `SS_FAILS = 0` reset — a
  cap that resets its own counter — which is why 1.7.1 existed at all.

- **The carry cap then over-applied.** Counting bag contents (above) made
  `get <x> from <your own bag>` fail at the cap: the total is unchanged by that
  move, but `inv_full` refused it, so a player at 100 could never retrieve their
  own belongings. A regression introduced by the fix, caught by the sweep. The cap
  now asks whether the *source* is already yours.

- `AUDIT_VERBATIM_MAX` was **read by no code at all** — it appeared in exactly two
  places, both prose, including the arithmetic that multiplies by it. Now compared.
  Noted honestly in-source: at its current value of 1 this is behaviourally
  identical to the old test, so the mutation back survives and no runtime test can
  distinguish them.

- `_path_for` **bounded at the primitive**. `PATH_CAP` sized the two destination
  buffers and was compared against nothing. Not reachable — `login_name_ok` gates
  the only write to `SS_NAME_LEN` and the only `player_exists` call on the login
  path — but it is the 0.9.0 `hex_decode_into` shape (a primitive trusting its
  caller), and this release makes the output longer, so the bound goes in first.

### Added

- **Operator configuration — `data/server.cyml`.** Optional; absent means
  defaults. `max_accounts` bounds how many player accounts may exist, and
  **defaults to `0` = unlimited**, because that is an operator's decision and not
  this server's. A negative or unparseable value is treated as unlimited, so a
  typo cannot lock an operator out of their own world. Overridable with
  `YD_MAX_ACCOUNTS` for container deployments.

  The count is taken once at boot and tracked in memory — `dir_list` allocates
  from the bump arena, so counting per creation would have been a permanent
  allocation per creation, which is the defect class 1.7.1 spent a release
  bounding.

- **Player records are sharded** into `data/players/<c>/<name>.cyml`, so a world
  with thousands of accounts is not one directory holding thousands of files.
  **No migration step:** the flat layout is still read and each record moves
  itself on its next save. A pre-1.7.2 `data/` converts as people log in.

### Changed

- [**ADR 0007 amended**](docs/adr/0007-frozen-1.0-surface.md) to admit one
  additive env knob and the config file, on a stated argument: the freeze's
  purpose is compatibility, and a knob defaulting to today's behaviour preserves
  it. The four frozen names are untouched; verbs, save schema, wire behaviour and
  the zone format stay frozen. A sixth knob would need its own argument —
  "1.7.2 did it" is explicitly not one.

### Note for anyone with a pre-1.7.2 `data/`

Nothing to do — the flat layout is read and each record migrates on its next
save. But be aware the compatibility fallback makes **stale** flat records visible
again: a name whose sharded record you delete stays "taken" while a legacy copy
remains. That is correct (a record exists), and it is worth knowing if you have
been hand-managing files. The suite's `_player_unlink` helper clears both layouts
for the same reason.

### Known-unbounded (tracked, not fixed here)

- **The room floor has no cap at all** — no constant to grep for, which is why
  five passes missed it. `corpse_of` mints loot with no max-exist check (unlike
  `zone_reset_room_objs`), and `obj_free` is reachable from three sites, none of
  which frees a non-corpse object on a floor. Ordinary play — kill, loot, drop,
  quit — measured **40 cycles → floor 0→80, monotonic**. It makes `look` cost
  801 µs at 10,000 objects while the 1.7.0 charge meter charges it **zero**, and
  >99% of that work emits nothing because tx truncates at TX_CAP after ~46 items.
  This is roadmap item J; only object lifetime fixes it.
- `cmd_give` can overshoot `MAX_INV` to ~199: the `>= MAX_INV` test runs before a
  transfer that moves the gift *and* its contents, and it never inspects
  `oi_contents`.
- Audit-log rotation (ADR 0009) remains 1.7.3 — the decision and seam shipped in
  1.7.1; the mechanism, its prune, and the rename-then-die crash window did not.

## [1.7.1] — 2026-07-29

**Bound what the reconnect rate sets.** Three items, one of them a live
data-integrity bug found while measuring the other two. 873 assertions (was 821);
all 19 new guards mutation-verified.

### Fixed

- **436 records in the audit log reported themselves as tampered with.** libro's
  read path substitutes `{}` for an absent or empty `details`, and the entry hash
  covers the details — so an entry *written* with `""` is *read back* as `{}`,
  recomputes to a different hash, fails `entry_verify`, and breaks chain
  verification from that point on. Every `audit_event` call site passes
  `SS_NAME_LEN`, which is 0 until a name is accepted, so any audit on an unnamed
  session wrote one. Measured in the working log at the time of the fix: **436 of
  37,902 records**, all `create.fail` / `create.dup` / `save` / `char.create`.

  A tamper-evident log that manufactures its own tamper reports is worse than no
  log, because it teaches an operator to ignore the alarm. `audit_event` now writes
  what the reader will reconstruct, so the round trip is hash-stable.

  **The existing 436 records are deliberately not repaired.** Rewriting a
  hash-chained log is the one thing it exists to prevent. The code path is closed
  and the suite no longer creates more.

- **The test suite had written 1,545 records into the operator's audit log.** Every
  group calling `persist_init()` appended to the real `data/audit.libro` —
  permanently interleaved with operational history, in a log that by design cannot
  be edited afterwards. The suite now writes to a fixture. Verified empirically:
  a full run adds **zero** records to the live log.

- **1,944 bytes were permanently lost per audit event, 667 MiB/hour under a
  reconnect flood, unauthenticated.** The roadmap's figure was 1,640 and "~224 of
  it ours". Both were wrong, in opposite directions:
  - Descent's own code allocates **48** bytes (three `str_from`/`str_new` headers;
    `str_new` borrows rather than copies). 1,592 is inside `lib/` — the 224 was
    `chain_append`'s total, 176 of which is libro's `entry_new`.
  - There is a further **304 bytes/event of freelist** that nothing ever frees —
    libro's `hasher_new` and its SHA-256 context, for which **there is no
    `hasher_free`** — and the freelist never munmaps, so an un-freed block is as
    permanent as a bump byte. Any budget written against 1,640 alone understates
    the bug by 18.5%.

  Fixed by an **audit rollup window**: the first occurrence of each
  (severity, action) key in a 60 s window is written byte-for-byte as before, and
  every later occurrence increments an `i64` in a fixed 3 kB table and allocates
  **nothing** — measured as a hard zero over 5,000 suppressed occurrences. One
  durable entry lands per key per window carrying the exact suppressed count plus
  up to six distinct names, so **a flood is still visible**. Reduction: ~3,000× on
  memory, ~2,600× on disk.

  The key is a **compile-time call-site constant**, never a string and never
  attacker data — keying on `details` would hand the attacker the key space, and a
  growing map would itself become the leak.

- **`passwd` had no rate limit.** G2 (1.6.12) capped the attempts inside one
  re-key, then cleared `SS_FAILS` and returned to the prompt — so `passwd` could be
  re-entered immediately, forever. `PHASE_CHPASS_CONFIRM` is the dearest line in
  the game reachable without a victim's credential (a keypair derive **and** a
  record sign, 2,461 µs measured), and registration is open, so the
  "authenticated" account costs an attacker four lines.

  This is the **fourth** appearance of "a per-item cap is not a bound on how many
  items there are". `grep -n MAX_LOGIN_FAILS src/` was always the whole answer —
  what grep does not show is where the counter gets **reset**.

- `passwd.fail` at the H10 re-key-save-rollback site is now `passwd.rollback`. One
  string naming two unrelated events was imprecise before; under per-key rollup
  counting it would report a disk failure and a mistyped passphrase as one number.

### Added

- **[ADR 0009 — Audit-log rotation](docs/adr/0009-audit-log-rotation.md)**, at
  status Accepted. The investigation came back **"no on-disk format change
  needed"**, so this is a 1.7.x item rather than 2.0: `verify_chain` never checks
  `entries[0].prev_hash`, so a sealed segment is a valid standalone file, and the
  streaming chain's carried head hash records the boundary itself. The mechanism
  lands in 1.7.2; the reasons for that ordering are in the ADR.

  Recorded there because it is the dangerous part: **libro's own `chain_rotate` is
  a no-op here.** It reads the in-memory entries vec, which a streaming chain
  always leaves empty, so it would silently do nothing. `chain_head_hash` returns 0
  for the same reason.

- A boot-time `audit.size` warning, and `audit_size_warn_due` — the same predicate
  and the same constant 1.7.2's rotation trigger will use, so the two cannot drift
  apart. **This is the first signal an operator has ever had** that the log is
  large; the working one is 13.3 MB over 37,902 records and was silent.

- `audit-coalesce`, `audit-verifiable` and `chpass-rate` test groups (+52
  assertions), and a hard-zero arena budget on the suppressed path in
  `bench_persist`.

### Changed

- Audit assertions count exact entries via `g_audit_emitted` instead of diffing
  the store file's byte length. The old form needed a 64 MB read buffer and a
  "refuse to assert if the read saturates" guard (it had silently always passed
  once), and could only ever say `after > before` — which cannot tell one entry
  from a hundred, the exact claim those assertions exist to make.
- Three comments corrected where 1.7.1 disproved their premises — most importantly
  1.6.12's "the authenticated `passwd` path keeps its per-attempt entry, because a
  real player sets that rate", which was false, and "one entry per session at the
  cap", which was never true (`SS_FAILS` keeps incrementing past the cap, so
  post-cap lines audit again).

### Known-unbounded (tracked, not fixed here)

Named so they are not mistaken for covered; each is a roadmap item:

- **A container flattens past the carry cap and poisons the save.** `inv_count`
  walks only the top-level chain and `cmd_put` moves items into a carried container
  with no count check, so 3 top-level items plus 200 in one bag refuses the whole
  record — the 1.6.13 defect reachable through a bag. **Player-armable data loss.**
- **`save.fail.sweep` fires per tick, not per 300 s.** `SS_SAVE_DIRTY` clears only
  after a successful rename, so once saves fail every session stays due forever.
- **No account-creation rate limit.** Names are 2–16 alnum, nothing caps the number
  of accounts, and each leaves a permanent file — a disk lever independent of the
  audit log, and the reason "authenticated" is not a rate bound anywhere here.
- Sustained CPU is still bounded only by `MAX_LOGIN_FAILS`, `MAX_SESSIONS` and the
  pre-auth idle timeout; the rollup window bounds bytes, not rate.
- Four upstream libro issues to file: `filestore_head_hash`, a size accessor, a
  `hasher_free`, and the empty-`details` substitution that caused the bug above.

## [1.7.0] — 2026-07-29

**The tick budget becomes a budget.** The gate sweep found that every per-tick
budget in the tree was justified in a comment and nothing summed them. One
event-loop pass with every budget at its cap measured **261 ms**, from sixteen
connections sending wrong passphrases. No account required.

The measured pre-tick-check quantity — the one a scheduled tick actually waits
on — goes from **~247 ms to 4 ms**, and a wrong passphrase from **8006 µs to
1066 µs**. 821 assertions (was 751), 6 benches (was 5), all 13 new guards
mutation-verified.

### Fixed

- **A wrong passphrase paid 7107 µs to learn what 1077 µs already knew.**
  `player_auth_load` tests two things that must both pass — is the record
  intact (`ed25519_verify`), and is this the right passphrase (`ident_derive` +
  compare) — and it evaluated them verify-first. Same conjunction, cheaper
  order. **8006 → 1066 µs, 7.5×**, on the costliest line an unauthenticated peer
  can queue for free. Nothing is trusted earlier: `salt` and `pubkey` are
  exact-length-checked and decoded independently of the signature, and the verify
  still gates every field restore. There was in-file precedent forty lines above,
  where H5 (1.6.2) hoisted the passphrase *length* bounds ahead of the same
  verify for the same reason.

  One nuance, accepted deliberately and documented at the site: a tampered record
  now reports `load.tamper` once a passphrase matching its pubkey is typed. For
  the realistic tamper — edit a field, leave salt+pubkey — that is unchanged, so
  the audit entry is preserved; only a full pubkey substitution degrades to a
  wrong-passphrase result, and that requires write access to `data/players/`.

- **Both per-pass line budgets were sized against the wrong worst case.** The
  `DRAIN_LINES_MAX` comment budgeted `16 × ~1.08 ms (a keypair derivation)`. A
  keypair derivation was not the costliest unauthenticated line — a wrong
  passphrase against a name that exists was, at ~8.2 ms, because it paid a full
  verify. The correct figure was **already written down twice within thirty lines
  of that comment** and it used neither. Replaced by a charge meter; the counts
  stay at 16 as backstops, so 1.7.0 can only ever admit *fewer* lines than
  1.6.15, never more.

- **A count budget cannot see cost.** One line spans 1.7 µs (rejected on length)
  to 8411 µs (a successful login) — a ~4800× spread — so no value of N was right:
  16 dear lines was 211 ms, and the N that fits one dear line is 1, which starves
  `look`. Replaced with a window that charges from **counters at the four
  expensive call sites** (`ed25519_keypair`, `ed25519_sign`, `ed25519_verify`,
  and bytes escaped by `session_appendtx_prose`). A table mapping a line to a
  predicted cost can be wrong the way the old comment was wrong; a call-site
  counter cannot be wrong about how many times the expensive thing ran. It also
  catches the `ed25519_sign` the `save` verb reaches from `PHASE_CMD`, which no
  phase table would see.

- **Refused lines waited up to a full tick interval, and the comment saying
  otherwise was wrong.** The epoll loop claimed "an unserviced socket re-fires
  immediately". Level-triggered means *readable*, and a session already drained
  to EAGAIN is not readable — the refused bytes are in `SS_RX_BUF`, not the
  kernel. `drain_pending_rx` ran once per tick from `advance_tick`, so a metered
  pass would have handed its leftovers 2500 ms of latency. This is why "just
  lower the count" was never the fix it appeared to be. The drain now runs once
  per **pass** in both loop bodies, and `g_rx_backlog` clamps the epoll timeout
  to 0 / skips the agnos sleep while work is retained.

- **The condemned-session teardown was the unbudgeted one.** `drain_pending_rx`'s
  `SS_QUIT` arm never consulted `budget`, and `drop_session`'s first act is an
  unconditional `player_save` — an `ed25519_sign`. So N condemned *authenticated*
  sessions cost N signs in one walk with nothing bounding N: **81 ms measured at
  64, ~325 ms projected at MAX_SESSIONS**, inside the very function E2 (1.6.10)
  added a line budget to. Both the line budget and the charge window *looked*
  like they covered this walk. Neither did, because the expensive work here is
  not a line. It is now charged rather than deferred — deferring the save would
  need a queue holding a pointer `fl_free` is about to reissue, which is the
  H1 / M12-C use-after-free shape.

### Added

- **`benches/bench_tick_budget.bcyr`** — gates one event-loop pass against the
  drift allowance. This is the instrument whose absence let the mis-derived
  budget stay green for eight releases: `bench_combat` gated the combat tick,
  `bench_persist` reasoned about four saves in a comment, and **nothing summed a
  pass**. It also carries a calibration tripwire that fails when the host is far
  slower than the charge table assumes — a ratio catches that where an absolute
  threshold cannot.

- **`charge-window` and `auth-order` test groups** (+70 assertions). The reorder
  has no observable result to assert, by design, so its guard is the verify
  **call count**: a wrong passphrase must perform zero verifies. Deterministic —
  no clock, no timing assertion.

### Changed

- `docs/adr/0001-tick-based-combat-over-cooldowns.md` now states the drift
  allowance. It previously contained **no number at all** — the 50 ms lived only
  in the roadmap and the benches, which is how three gates could disagree about
  it without anything failing. Two allowances are now named and distinguished:
  **drift** (50 ms p99, bounding work that delays a scheduled tick) and
  **tick-body occupancy** (250 ms, 10% of the interval). A pre-work drift sample
  cannot see tick-body cost, so summing the two against one threshold — which an
  earlier draft of the roadmap did — mixes quantities.

### Corrected

- The roadmap's "252 ms = 504% of the ADR 0001 drift budget" conflated the two
  quantities above, and cited a number ADR 0001 did not contain. `save_sweep` and
  `sweep_idle` are tick-body; only the event batch delayed a scheduled tick.
  The defect was real and the arithmetic was loose in the same way as the comment
  it indicted. Both are fixed here, and the bench now gates the drift-relevant
  quantity and *reports* the rest.

### Known-unbounded (tracked, not fixed here)

Named so they are not mistaken for covered. Each is a roadmap item:

- **Sustained CPU is not bounded — only per-pass latency.** The meter converts a
  421 ms stall into sustained Ed25519 work and does not cap the rate. What bounds
  pre-auth CPU is `MAX_LOGIN_FAILS`, `MAX_SESSIONS` and the 30 s pre-auth idle
  timeout, none of which is part of this fix. Relatedly, **`passwd` has no rate
  limit at all** (no `SAVE_MIN_INTERVAL_MS` analogue).
- **Nothing in the tree reclaims a dropped item**, so `session_append_objs` on
  every `look` goes 1 µs → 563 µs at 4000 floor objects. Charged nothing by the
  meter (no crypto, no prose) and bounded only by the line count. Only fixing
  object lifetime fixes it.
- **`combat_tick_all`'s broadcast fan-out is O(sessions²)** — 43.3 ms of tick
  body at 256 co-located players (`bench_combat`, passing). Untouched here, and
  deliberately *not* subtracted from the drift allowance.
- **The host factor is one data point.** Every charge is a reference-host
  measurement; on much slower hardware each under-values real cost. Only the new
  bench's ratio tripwire catches it, and ADR 0007 blocks a `YD_*` escape hatch.
- **The `g_rx_backlog` clamps are reviewed, not test-gated** — both loop bodies
  sit behind a socket and a signalfd. The suite asserts the flag is *set*; that
  the loops *read* it is not covered.

## [1.6.15] — 2026-07-29

**The documentation truth pass.** No code changes. The 1.6.0 sweep found the
README and the architecture overview describing a *different game* — and unlike
a stale version number, that is the first thing a new contributor reads and
believes.

### Changed

- **`docs/architecture/overview.md` documented a combat model that was never
  built.** Every claim in §2–§4 was checked against the source, and most of them
  were wrong:
  - **Hit roll** was documented as `1d20 + DEX modifier + weapon accuracy`. DEX
    is not involved at all — it is `1d20 + the class's authored hit bonus +
    the defender's AC`, with `+2` while `stim` is up. A natural 1 always misses
    whatever the bonus, which was undocumented and is exactly the detail that
    made a test flaky in 1.6.12.
  - **Damage** was documented as `weapon dice + STR or TEC modifier`. Neither
    STR nor TEC touches the auto-attack.
  - **The attribute table** described four stats by intent. In fact **STR does
    nothing at all** today — it is stored, shown by `examine me`, and read by no
    game rule. DEX rides `backstab` only, CON drives out-of-combat regen (not
    maximum HP), and TEC rides four Splicer/Chaplain abilities. The table now
    says what each one does, and points at **M16** for the rest.
  - **`rest` and `sleep` verbs, and safe-room recovery** — described in §4.3 and
    never implemented. HP regenerates automatically anywhere, out of combat.
  - **Guild territory** — described as high-level play; it is M22 and unbuilt.
  - **The sample combat transcript** showed a `[Tick N]` prefix and per-limb hit
    locations, neither of which exists. Replaced with output captured from a
    running server.
- **`README.md` was five releases stale** — "v1.2.0", "298 assertions" — and its
  three headline parser examples were unverified. Two of the three I could not
  make resolve against a live server, so they were replaced with commands I did
  watch work end to end rather than swapping one unchecked claim for another.
- **Both now document what 1.6.13 changed for players**: the 100-item carry cap
  (and *why* it exists), and that an unauthenticated connection is dropped after
  30 s regardless of `YD_IDLE_MS`. Those are the two user-visible changes of the
  whole 1.6.x line and neither had reached the docs.
- `docs/guides/running.md` and `docs/guides/commands.md` picked up the same two
  facts.

### Verified, not assumed

Every remaining factual claim in the README was checked against the tree rather
than left alone: 21 Hub rooms ✓, 4 classes ✓, 12 abilities ✓, ADRs 0001–0007 ✓,
all four referenced guides exist ✓.

## [1.6.14] — 2026-07-29

**The dormant tail.** Five items that could not fire in the shipped
configuration — an ARM build, a config typo, a caller that does not exist yet.
Nothing here was reachable by a player; all of it was a trap for the next
change.

### Fixed

- **An ARM build would have read session pointers from the wrong bytes.** The
  dispatch loop hardcoded `EPOLL_EVENT_SIZE = 12` and read the tag at `+4`,
  which is the x86_64 *packed* layout. aarch64 Linux leaves the struct unpacked:
  16 bytes, tag at `+8`.

  The stdlib already knew this — `epoll_event_new` ships separate x86_64 and
  aarch64 versions, and the aarch64 one carries a comment explaining the split.
  Descent used that helper to **write** events and then hardcoded its own
  constants to **read** them back, so the write path was portable and the read
  path was not. Two sources of truth for one fact.

  Both halves now go through `epoll_ev_size()` / `epoll_data_off()`, so a layout
  right for one is right for the other by construction.
- **…and that removed a per-connection allocation.** `epoll_event_new` allocates
  16 bytes from the bump allocator, which has no free, so every accept and every
  EPOLLOUT arm/disarm leaked 16 bytes for the life of the process. `epoll_ctl`
  copies the struct, so it is dead the moment the syscall returns and one
  reusable buffer serves every call — which is also what put the writer on the
  same constants as the reader.
- **Class IDs had no room for a terminator.** A 32-byte id filled its 32-byte
  slot exactly, while the two fields beside it copy at `CAP - 1` for precisely
  that reason. Safe only because every reader goes through `CL_ID_LEN` — the
  same shape as the object-id mismatch 1.6.6 fixed, in the one place 1.6.6 did
  not sweep.
- **The 1.6.7 sign sweep, finished.** `str` / `dex` / `con` / `tec` and the
  damage-dice profile were clamped where a saved character is **read** and
  unclamped where one is **made**. An authored negative reached the session
  directly, and `ndice` is a `roll()` loop trip count — an authored `999999d6`
  parses fine and is not malformed, just absurd. Bounded on both the class and
  mob paths, with the same limits `player_auth_load` already used.

### Changed

- **Two dead functions deleted, two misleading comments corrected.** Rather than
  deleting all four flagged symbols:
  - `session_class` — deleted. Never called, and its comment claimed a use ("for
    who / stats") that does not exist; both read `SS_CLASS` directly.
  - `room_set_obj_head` — deleted. Never called, and its own comment said why.
  - `mt_level` and `g_zone_name` — **kept**. Both are authored zone-format
    fields frozen by ADR 0007 §5, so removing them would be a format change, and
    both have a named future consumer (M16 and M18). Their comments overstated
    them — "flavour only so far" and "for prompts / Joshua" named consumers that
    do not exist — and now say plainly that nothing reads them yet.

### Testing

- 732 → **751 assertions**; new `hygiene-tail` group and a
  `longid.classes.cyml` fixture.
- 9 mutations. **Two initially failed to fail**, and the reasons are worth
  keeping:
  - The class-id assertion checked the shipped file, whose ids are ~8 bytes and
    round-trip either way — so reintroducing the bug changed nothing it could
    see. Now driven through the real loader over a 32-byte-id fixture, which is
    the only length at which `CAP` and `CAP - 1` differ. Same trap the hex
    encoder hit in 1.6.8.
  - The aarch64 offset mutation is **structurally invisible on x86**: an
    x86-only mistake cannot be caught by a test running on x86. Covered three
    other ways instead — the writer/reader round-trip invariant is asserted at
    the audit gate on whatever arch is built, `--aarch64` compiles clean, and
    the branch is provably live (poisoning it fails the aarch64 build while x86
    still passes). Stated here rather than counted as tested.

## [1.6.13] — 2026-07-29

**The three open issues that could reach an operator or a player.** All three
came from the 1.6.0 sweep and none had ever been tracked — they were found by
reconciling that sweep's output against the tree, after the 1.6.5 roadmap wrote
a remaining-work count that did not subtract.

### Fixed

- **A player who filled their inventory silently stopped saving.** The save
  record is a fixed 4096-byte buffer and nothing capped how much a player could
  carry. Measured on this tree: with the longest id the object format permits
  (31 bytes), `_build_record` starts refusing at **113 items** — and it refuses
  the *whole* record, so from that point the character's room, HP, class and
  every future change stopped persisting.

  One correction to the original finding, which called it permanent: it is not.
  Dropping a single item recovers it — also measured. The real defect is that it
  is **silent**. The player is never told, the audit log is the only witness, and
  nothing suggests "drop something" as the remedy.

  Two halves, because either alone is insufficient:
  - **A carry cap of 100.** Chosen to be safe at *any* authored id length: the
    record leaves 3427 bytes for inventory and 100 ids at the 31-byte maximum
    plus separators is 3200. With the Hub's short ids the true ceiling is over
    400, so this costs real play nothing. Enforced on `get`, `get all` and
    `give` — the last against the **recipient's** cap, since handing someone
    their 101st item pushes them past a limit they neither see nor chose.
  - **The record truncates instead of refusing.** M11-D's bound turned an
    over-long inventory into `SAVE_ERR`, which `player_save` reported as total
    failure. Losing the tail of an over-long inventory is a bounded, one-time,
    audited loss; losing every future save is unbounded and silent. The cap
    should make this unreachable — it is the net under it.

  Deliberately **not** enforced on the load path: a record that already holds
  more than the cap comes back intact. The cap stops you acquiring more; it
  never destroys what you have.
- **An unauthenticated connection held a slot for five minutes.** 1.6.3 added
  `MAX_SESSIONS`, which was half of the original finding; the other half — a
  *separate, shorter* deadline for connections that have not logged in — was
  never implemented, and the finding was closed anyway.

  The two deadlines are not the same job. A logged-in player is idle because
  they walked away and should be given room; a connection that has not named
  itself in **30 seconds** is broken or probing. The shorter of the two always
  wins, so a tighter operator timeout still applies.
- **A stray carriage return in a config file silently changed a value.** Config
  values were not whitespace-trimmed, and an unparseable value silently takes
  the default — so a zone or class file saved with CRLF endings could rewrite a
  setting to a number the author never typed, with no error anywhere. An
  operator editing on Windows was enough.

  Trimming is separate from strictness on purpose: whitespace is an artefact of
  how the file was saved and the intent is unambiguous, whereas rejecting
  genuinely malformed values still needs a format version to hang off (M14-D).
  Asserted both ways — `"7\r"` now parses as 7, `"7x"` still falls back.

### Testing

- 706 → **732 assertions**; new `carry-cap` group, and the `idle` group split
  across both deadlines.
- 10 mutations, all discriminating.
- **Two existing tests had to change, and both were right to break.** The H10
  re-key rollback test forced its save failure with an oversized inventory —
  exactly the failure mode this release removes by design — so it now injects an
  I/O failure instead, via a path that cannot be written. That is a truer test:
  H10 exists for ENOSPC / EIO / a failed rename. And the `idle` test asserted
  the 5-minute rule against a zeroed slab, so it had been testing the
  *unauthenticated* path against the *authenticated* rule all along; it now sets
  `SS_AUTHED` and covers both.
- The cap and the record budget were **measured, not estimated**: a probe built
  records with growing inventories at both the shortest and longest authored id
  lengths to find the exact overflow point before the cap was chosen.

## [1.6.12] — 2026-07-29

**The class, not the instance.** The second re-run sweep found a **critical** and
a **high**, and both are the same defect this line has now fixed three times on
neighbouring paths without ever fixing the pattern. That is the story of this
release, and it is worth stating before the fixes.

The defect: *a per-item cap is not a bound on a loop that walks many items.*

| release | capped | left open |
|---|---|---|
| H5 (1.6.2) | one session per readable event | the batch of events; creation; `passwd` |
| E1/E2 (1.6.10) | the tick-side drain | the event-side batch; `passwd` |
| F7 (1.6.11) | the idle reap | the event-side batch; `passwd` |
| **G1/G2 (1.6.12)** | **the event batch, both loops, and `passwd`** | — |

Each pass looked straight at the open one and fixed a neighbour. `grep -n
ident_derive src/` and "every loop that dispatches lines" were always the whole
answer, and this release finally asks those two questions instead of chasing
reports.

### Fixed

- **The epoll event batch had no aggregate work budget.** *(critical, both
  verifiers)* The dispatch loop drains up to `MAX_EPOLL_EVENTS` = 64 session
  events, each allowed `RX_MAX_LINES` = 8 line dispatches, and the tick-deadline
  check sits **outside** that loop — so the batch ran to completion whatever it
  cost.

  Measured on this tree: one event of 8 wrong-passphrase lines is **64 ms of CPU
  for 104 bytes of input**, and a full batch is **4.12 s with no tick check in
  between** — 8240% of the ADR 0001 budget and 164% of the whole tick interval,
  so an entire combat tick is skipped. The unauthenticated creation variant needs
  no account at all: I measured **559 ms → 17 ms** for that batch here, 1118% of
  budget down to 34%.

  `RX_MAX_LINES` is a per-session cap and this walks 64 sessions — which is
  verbatim what E2 wrote about `drain_pending_rx` eight weeks of releases ago.
- **…and ADR 0003's two loops had diverged, with the agnos one worse.** The
  agnos poll loop sweeps **every** session on every ~20 ms pass with no
  `MAX_EPOLL_EVENTS` analog of any kind: 256 × 64 ms = **~16.5 s per pass** at
  `MAX_SESSIONS`. Both loops now call one extracted `event_batch_step`, so they
  cannot disagree again — and that function is reachable from a test, which the
  loops themselves are not.
- **The in-world `passwd` re-key was unmetered.** *(high, both verifiers)*
  `chpass_on_new` derives a fresh Ed25519 keypair on every in-range line and
  `chpass_on_confirm` derives again to compare, rewinding on mismatch — so 100%
  of attacker lines cost a full derivation and the cycle never terminated.
  Measured: 1000 lines = 1103 ms of loop time, and afterwards `SS_FAILS` was
  still 0 and the session still cycling.

  Reachable by any authenticated player: create a character (free), type
  `passwd`, alternate two lines forever. Capped now — but unlike creation it
  does **not** disconnect: an authenticated player who fumbles is returned to the
  prompt with their passphrase untouched and may try again. That still bounds the
  work per invocation, which is the point.

### Changed

- **Attacker-paced audit events fire once per session, not once per attempt.**
  Each `audit_event` costs 1640 bytes of bump arena `alloc()` can never reclaim
  (1416 B of it inside libro's `filestore_append`, upstream and untouchable
  here) plus ~360 B appended to a never-rotated `data/audit.libro`. On the
  unauthenticated creation path that was 5 × per connection — measured **~755
  kB/s of permanently-lost arena** at single-core saturation, and reconnects are
  free, so E3's per-connection cap never bounded the aggregate.

  `create.fail` and `login.fail` now write one entry, at the cap. The event
  exists to make a flood **visible**, and every session that hammers the limit
  still writes one `SEV_WARNING` naming it — what is given up is per-attempt
  granularity on the two paths whose rate an *attacker* sets. The authenticated
  `passwd.fail` keeps its per-attempt entry, because a real player sets that
  rate. That is the whole trade, stated plainly: the dominant term remains
  upstream in libro 2.8.5.

### Testing

- 669 → **706 assertions**; new `event-budget` and `passwd-meter` groups.
- 13 mutations, all discriminating. **Six needed the test rewritten first**, and
  the reasons rhyme with the bug:
  - The first `event-budget` test **reimplemented the batch arithmetic** instead
    of calling it, so three mutations to the real code passed unseen. Fixed by
    extracting `event_batch_step` and driving that — the same seam `tick_step`
    got in 1.6.8, for the same reason.
  - `EVENT_LINES_MAX` is exactly 2 × `RX_MAX_LINES`, so a loop test only ever
    exercises `take == 8` and cannot tell a budgeted step from one that always
    takes a full slice. Now driven with budgets of 3 and 5 as well.
  - Asserting the budget *delta* cannot see a step that charges a flat 1 per
    session — that reaches the same total after servicing 16 sessions at a full
    slice each, i.e. the exact thing the budget prevents. Now asserts the session
    count too.
  - The audit probe read 4096 bytes of an 8.3 MB append-only store, so every
    length compare was equal and the check always passed. Now sized generously
    and it **refuses to assert** if the read ever saturates.
  - And `login.fail` was covered only for creation. Covering one of two
    symmetric paths is the mistake this entire release is about.
- **A 1-in-20 flake, caught by CI.** The killing-blow test set `SS_HIT = 100` on
  the assumption that made it "always hit". It does not: `combat_try_hit`
  returns 0 on a **natural 1 regardless of the bonus**, so one round was a 5%
  coin flip. It passed here and failed on CI, which simply rolled the 1.

  Now it retries until the blow lands — the mob has 1 HP and an enormous damage
  profile, so the first *hit* is the kill, and the assertion is about the killing
  blow's **tail**, which is what it was always meant to be about rather than
  about a d20. Verified by forcing every roll to a natural 1 (the test then fails
  cleanly on its bound, so it is not vacuous) and by five consecutive green runs.

  Worth noting alongside the uptime bug that CI caught in 1.6.8: both were tests
  that depended on something the test did not control. A local pass says nothing
  about either.

**Not closed.** The 1.x line still needs a re-run that comes back with no
critical or high findings. Two re-runs have now each found serious defects the
previous pass missed, which is evidence about the process, not just the code —
so the bar stays where it is.

## [1.6.11] — 2026-07-29

**The tail of the re-run.** Batch E took the critical and the highs; this takes
everything else the 1.6.9 sweep found, including one correction to the record.

### Corrected

- **`render_who` was NOT a false positive, and 1.6.9 said it was.** The finding
  reported `render_who` bounding its room index only from below. I checked
  `cmd_who` — a *different* function three hundred lines further down, which has
  always bounded both ends — declared the finding a false positive, and wrote
  that into the 1.6.9 CHANGELOG, `state.md` and the roadmap.

  `render_who` (the `@who` admin verb) tested `room >= 0` and then dereferenced.
  Now bounded at both ends, like `cmd_who`. Safe today only by an invariant held
  elsewhere — SS_ROOM is -1 or valid, never stale-and-positive — which is exactly
  the kind of accident that made `examine` a remote crash the moment it stopped
  holding. The corrected record is in the roadmap; the original claim is left
  visible rather than quietly edited away.

### Fixed

- **`world_start_room()` reported room 0 for a world with no rooms.**
  `g_start_room` is 0 by default *and* after H9 zeroes it on a rejected load, so
  a zone-less server named a valid-looking index into a null table — the most
  dangerous kind, because every `room >= 0` guard downstream reads it as placed.
  Returns -1 ("unplaced") now, which is already this codebase's word for it.
- **Three loaders left a stale table published on a rejected load.**
  `world_load_objs`, `world_load_mobs` and `world_load_classes` return
  `WL_ERR_IO` / `WL_ERR_EMPTY` / `WL_ERR_OVERCAP` *above* the line H9 (1.6.5)
  added, so those three paths never reached it. Measured: after loading a
  nonexistent objs file the count was still 10, mobs still 4, classes still 4 —
  while the caller was told the load failed. Only `world_load_rooms` was safe,
  because it routes all eight returns through `_wl_rooms_fail`. The zeroing is
  hoisted to function entry, where nothing can fail before it.
- **A parser token could claim more bytes than were stored.** `pa_emit_byte`
  stores nothing once the norm buffer is full and returns 0 — its own comment
  promises the token is "truncated rather than overrunning the buffer" — and the
  return was discarded while the length counter advanced anyway. The buffer was
  never overrun; the *length* was, and every consumer trusts it, including
  `session_appendtx_tok`, which copies straight into a player's tx queue.

  Latent only because `LINE_CAP == NORM_CAP`. That equality is now recorded as
  the load-bearing invariant it is, and the test drives the parser past it
  directly, since no socket line can.
- **Player-typed tokens were echoed with the raw appender.** M10-A's rule is
  "use the prose appender for anything a player typed"; `session_appendtx_tok`
  used the raw one. `telnet_feed` decodes `IAC IAC` into a literal 0xFF data
  byte (correct RFC 854, and the suite asserts it), which survives into the
  token — so every not-found reply echoed a lone IAC back onto the wire, which
  is the exact defect M10 exists to prevent.
- **Secret keys went back to the freelist unwiped.** `lib/freelist.cyr` hands a
  freed block to the next `fl_alloc` of that size class *without zeroing it*.
  `session_free` released both the live `SS_IDENT` block (Ed25519 secret key,
  whole session) and the `SS_IDENT_CAND` block (up to two derived candidate keys
  mid-`passwd`) with a bare `fl_free`.

  The 1.6.4 entry states the candidate is "wiped and freed on commit, on both
  rewinds, and in `session_free`". Three of those four were true. `SS_IDENT` was
  never wiped and was never claimed to be — which is worse, since it is the live
  key. Both wiped now.
- **The idle reap was a second unmetered signing site.** `drop_session`'s first
  act is an unconditional `player_save`, measured by H16 at 1.30 ms with 89% in
  `ed25519_sign` — which is why H16 capped `save_sweep` at 4 per tick. But
  `sweep_idle` could do 256 of them in one pass, in the same tick, spending the
  same budget, and nothing bounded it. No attacker required: a restart puts
  everyone on the same idle deadline, so they time out together. Same budget
  shape, same non-starvation argument.
- **Class and mob stats were unclamped where characters are made.** H12 (1.6.7)
  taught `toml_int` to read a leading `-` and H13 clamped the one caller it
  audited. `hp` and `energy` flow from `classes.cyml` into `SS_MAXHP` /
  `SS_MAXENERGY` unbounded, while `player_auth_load` clamps those same two
  fields — the invariant was asserted where a record is *read* and absent where
  a character is *made*. An authored `hp = -5` produced a player dead on
  arrival. `ac` and `hit` stay unclamped: a negative AC is meaningful in THAC0
  and is precisely what H12 existed to enable.
- **The killing blow printed no condition line and no prompt.** It returned
  straight after `mob_died`, so the one round a player most wants to read ended
  with no HP, no energy and no `>`. Every other exit from `combat_round` emits
  both, as do `mob_swing` and `ability_tail`.
- **`put X in <carried bag>` was a one-way trip, and then a data loss.**
  `cmd_put` accepts a carried container; `cmd_get`'s `from` branch searched only
  the room, so anything put into a bag in your own hands could never be taken
  out — despite `cmd_put`'s own comment calling itself "the exact inverse of
  `get X from Y`". Worse, `_build_record` walked only the top-level `SS_INV`
  chain, so the contents were never written and `session_drop_inv` then
  `obj_free`'d them recursively. Put your scrip in a sack, log out, gone.

  The lookup is symmetric now, and the save descends one level. Contents are
  **flattened** into the same comma-separated `inv` list rather than nested,
  which keeps the frozen v1 field byte-compatible (ADR 0007 §3): the items come
  back loose in your hands. Losing the arrangement beats losing the items;
  representing nesting needs a schema change, i.e. 2.0.

### Changed

- **A false justification removed from the H14 comment.** It claimed moving the
  drift sample "would double-count, because a tick that overruns already
  surfaces as the *next* tick's lateness". That is false, and it contradicted
  the H16 block 500 lines above it in the same file, which is right: the
  schedule is absolute, so a sub-interval overrun is absorbed by the next
  `epoll_wait` timeout and `@stats` reports 0 ms drift straight through it —
  which is exactly how `save_sweep` spent 332 ms in a tick for eight releases
  unseen. The conclusion stands (do not move the sample; the field is frozen),
  but the reasoning did not, and a false justification is worse than none.

### Testing

- 636 → **669 assertions**; new `tail-guards` group.
- 16 mutations, all discriminating. **Seven needed new tests first** — no
  coverage existed for `render_who`, the killing blow, `get`-from-carried, the
  save-side descent, the idle-reap budget, or either key wipe.
- Two harness bugs found on the way, both worth writing down because both
  silently truncated the run rather than failing it: a test session built by
  `_tx_sess` has `SS_FD = 0`, so `session_free` **closed stdin** and the suite
  simply stopped printing; and the same session has `SS_TS = 0`, so
  `telnet_state_free` dereferenced null. Anything handed to `drop_session` now
  goes through `_freeable_sess`.

## [1.6.10] — 2026-07-29

**Sweep batch E — what the re-run turned up.** The 1.6.9 re-run put eight
findings through adversarial verification and none was refuted. This closes the
critical, all four highs, and the two mediums with teeth.

The findings interlock, and the order matters: **`SS_QUIT` being advisory on the
tick path is what made every attempt cap in the server a suggestion.** Fixing
that first is what gives the others something to stand on.

### Fixed

- **`MAX_LOGIN_FAILS` was not enforced. At all.** *(critical)* `login_on_pass`
  has capped consecutive failures since 1.6.2 by setting `SS_QUIT` — and exactly
  one place ever acted on it: `dispatch_session`, which runs only when an epoll
  event arrives. A session whose rx buffer still held queued lines therefore
  kept being fed 8 lines per tick **after the server had decided to close it**,
  and on the returning-player path every one of those is a full
  `player_auth_load` (read + parse + 3 hex decodes + `ed25519_verify`, 7.66 ms).

  The sweep watched `SS_FAILS` climb 7, 15, 23, 31, 39, 47 across six
  consecutive ticks with `SS_QUIT` already 1 and the session still on
  `g_session_head`. ~64 ms per such session per tick, linear in session count:
  **~4.1 s per tick at 64 sessions.** A cap believed enforced for seven releases
  and enforced nowhere.

  `drain_pending_rx` now tears such a session down where it finds it — the same
  mid-walk drop `sweep_idle` has always done, with `SS_NEXT` already captured.
- **`drain_pending_rx` had no aggregate budget.** *(critical)* `RX_MAX_LINES` is
  a **per-session** cap and the sweep walks every session, so the real bound was
  8 × session count × whatever the costliest line costs, inline in the tick.
  **Measured 2.2 s in a single tick at `MAX_SESSIONS`** — 88% of the whole 2.5 s
  interval, from ~1 MB of attacker input, unauthenticated.

  This is the identical shape H16 fixed for `save_sweep` in 1.6.8; the argument
  in that comment block applies verbatim and simply had not been carried over.
  The budget is now in **lines, shared across the whole walk** — not sessions —
  so a session with one queued line costs one line rather than a whole slice.
  `session_consume_rx_max` reports how many lines it actually dispatched, which
  is what makes accurate charging possible. No cross-tick cursor, for the reason
  H16 gives: a retained session pointer is the H1 / M12-C use-after-free shape.
- **Character creation had no attempt cap at all.** *(high)* `PHASE_NEWPASS` ↔
  `PHASE_CONFIRMPASS` derived a fresh Ed25519 keypair on every line and looped
  forever on mismatch — no counter, no rate limit, and alone among the failure
  paths in `persist.cyr`, **no audit event**, so a flood left no trace. Measured
  2.16 ms of server CPU for ten bytes of input, ~215 µs per attacker byte. 1.6.2
  capped the returning-player path and left the structurally identical creation
  path open — the easier of the two to reach, since it needs no account to exist.

  Mismatches now count against `MAX_LOGIN_FAILS` and emit `create.fail`. Verified
  live: the session closes on the fifth mismatched pair.
- **Two sessions could create the same character.** *(high)* H11 (1.6.6) refused
  a second *login* for an existing character but wired the check only into
  `login_on_pass`. The creation window is not a race — it is the whole
  passphrase + confirm + class-prompt sequence, bounded only by the 5-minute
  idle reap. Both sessions forged **different** keypairs, both set `SS_AUTHED`,
  both wrote the record, and the last writer's passphrase became the only one
  that opened the account.

  Checked in `login_on_confirm`, which is the only place it can go:
  `session_already_online` requires `SS_AUTHED` on the other session, and at the
  name prompt neither is authed yet. `player_exists` is re-tested too, for the
  case where the first creator finished and disconnected inside the window.
  Verified live: B is refused, and **A's passphrase still opens the account**.

### Changed

- **The zone reset counts the whole world, not one room's floor.** *(medium)*
  `_obj_id_present` scanned the top-level object list of the single room being
  topped up, so an authored id that was anywhere else read as "missing" and a
  duplicate was minted — permanently, since `obj_free` is reached only from
  corpse decay and from a disconnecting player's inventory. Two ways to defeat
  it: carry the object to another room (pre-existing, and named verbatim in
  `server.cyr`'s H11 comment as "an unbounded `fl_alloc` growth path driven by
  ordinary play"), or —

  **— hide it in place, inside a container. That one is ours, from 1.6.7.** The
  scan walked `oi_next` and never descended `OI_CONTENTS`, and before `put`
  existed there was no way to hide an object in its own room. Reproduced live in
  `market.stalls`: `get optic` → `put optic in shard` → `@reset` → **`objs +1`**,
  a duplicate on the floor with the original still in the shard, once per reset
  cycle with no ceiling. Post-fix the same sequence reports **`objs +0`** four
  resets running.

  The reset now asks the right question — not "is this id in this room" but
  "does the world already hold as many as the zone authors". That is the classic
  max-exist count, and it fixes both drivers at once: a relocated object still
  lets its home room restock (the population is short by one), a hidden or
  duplicated one does not. Player inventories count, or logging in holding an
  authored item would restock the world for free.
- **A stunned mob that nobody was fighting stayed stunned forever.** *(medium)*
  Stun was decremented in exactly two places, both inside the player-versus-
  target round. `bash` a mob and then flee or switch target, and its `MI_STUN`
  never reached zero: `_mob_can_act` returns 0 while it is positive, so the mob
  never wandered, never assisted and never fought again — permanently inert
  furniture wherever a player last used an ability.

  The decay moved to `mob_tick_all`, the one place that runs every tick for
  every living mob, and is now the **only** place it happens — otherwise an
  engaged mob would be charged twice a tick and `emp` would be worth half what
  it claims. Equivalent for engaged mobs because `advance_tick` runs
  `combat_tick_all` before `mob_tick_all`.
- **Comments that described behaviour two releases old.** `room_broadcast`,
  `room_say_broadcast` and `deliver_to` all still asserted an immediate
  per-recipient flush and a drop-on-error that H15 (1.6.8) removed and H19
  (1.6.9) replaced. `mi_set_stun` still credited `combat_round` with the decay.
  Corrected — a comment asserting the opposite of its code is a finding, and
  this line has now produced three of them.

### Testing

- 614 → **636 assertions**; new groups `preauth-scale`, `create-guards`,
  `object-maxexist`, `stun-decay`.
- **22 mutations**, every one now discriminating — but **eight did not at first,
  and all eight were test bugs, not dead guards.** Worth listing, because the
  pattern is consistent: a test that does not reach the code cannot fail for it.
  - `var sessions[64]` is 64 **bytes**, not 64 entries. Writing 40 pointers into
    it smashed the stack. This is the first line of CLAUDE.md's Key Principles
    and I still walked into it.
  - `ilist_find_kw_nth` with a zero-length noun matches **nothing**
    (`kw_matches` returns 0 for `nlen <= 0`), so the object test silently
    selected no target and skipped the entire branch under test — hiding three
    mutations at once.
  - The drain budget is a multiple of `RX_MAX_LINES`, so the caller-supplied cap
    was only ever exercised at exactly 8 and would have looked honoured even if
    ignored.
  - The double-decay mutation needs an *engaged* mob, and the first test had no
    combat round running at all.
  - E4's `player_exists` re-test needs the first creator to have **disconnected**;
    with them still online the earlier check fires first and masks it.
- **A test that was not idempotent.** `create-guards` saves a record, so the
  second run of the suite found it already on disk and five assertions failed.
  Passed once, failed forever after. It now unlinks the record first.
- Live verification for each: creation cap closes on the fifth mismatch,
  duplicate creation refused with A's passphrase intact, and the reset reports
  `objs +0` where it reported `objs +1`.

## [1.6.9] — 2026-07-29

**Sweep batch D — coverage, and the re-run.** The last planned batch: close the
bench/soak blind spots, reconcile the documentation, and re-run the audit sweep
against the repaired tree to see whether the 1.x line can close.

**It cannot yet.** The re-run found a remotely-triggerable crash that the
original sweep missed entirely, plus a regression this line itself introduced in
1.6.8. Both are fixed here. The remaining verified findings are carried into a
new batch rather than rushed — see *Where this leaves the 1.x line* below.

### Fixed

- **`examine <anything>` killed the server outright when no zone was loaded.**
  A remote crash any logged-in player could fire, in a configuration the server
  explicitly supports and announces (`world: no zone loaded — running roomless`).

  `room_at` is documented "no bounds check — callers hold valid indices" and
  computes `g_rooms + i * RM_SIZE`. On a zone-less server `g_rooms` is 0 and
  every session sits at `SS_ROOM = -1`, so that arithmetic yields **-240** and
  dereferencing it takes the process down. `look`, `get`, `drop`, `kill` and
  `exits` all check `world_room_count() == 0` first. `cmd_examine` was the only
  verb that did not.

  Reproduced live before the fix: `look`, `get` and `kill` each answered
  politely, then `examine thing` returned nothing and the process was gone.
  Verified fixed against the same server — every `examine` variant answers and
  the process stays up.

  The guard covers the **room lookup only**, not the whole command, so a carried
  object and `examine me` still work without a world. `session_room_ok` checks
  the index rather than just the count, because the count alone does not tell
  you the session's own room is in range.

  This is the finding that matters most about the re-run: it was reachable the
  whole time, and the 1.6.0 sweep did not see it.
- **1.6.8 made `say` take up to a full tick to reach anyone.** H15 turned every
  room broadcast into a dirty flag drained at the end of `advance_tick`. That is
  right for the tick, where E combatants each broadcast to E−1 others and the
  write count is quadratic. It is wrong for **commands**, which arrive on the
  epoll path: `say`, `emote`, arrivals, departures and `kill`'s lunge all marked
  their listeners and then waited for the next tick boundary.

  **Measured: 2099 ms.** Against a 2.5 s tick, a listener waited nearly a full
  tick to hear someone speak. With the fix, **0 ms** — both numbers taken from
  the same two-client harness against a real `serve`, one binary each side.

  `dispatch_session` now drains the dirty set at the end of the event path. No
  syscall cost is given back: one command marks at most the room's population,
  which is exactly how many writes it always issued. Only the tick's own burst
  is coalesced, which is where the 2E²−E came from.

### Added

- **`bench_persist`** — the save and login paths, which nothing measured before,
  and which is where two of the three batch-C findings lived. Reports **bytes of
  bump arena per op** alongside ns/op, because `alloc()` has no free and RSS
  cannot see it. `_build_record` **0 B** (gated at a hard zero), `player_save`
  ≈1.26 ms / **1632 B** (gated at 1750), `player_auth_load` ≈7.7 ms / ≈3.9 kB.

  **A login costs ~6× a save.** That number was not known before this release
  and it immediately mattered — see the carried-forward findings below.
- **`bench_loaders`** — the boot loaders, plus the H9 (1.6.5) invariant that a
  *rejected* zone file leaves nothing published. Rooms ≈207 µs / ≈285 kB, objs
  ≈49 µs, mobs ≈39 µs.

  The bump figures are a one-time boot cost **today**, because the loaders run
  exactly once each from `cmd_serve` — verified, not assumed. They become a
  per-reload permanent cost at **M15 (zone registry)**, which is the reason to
  have the number now rather than after.
- Both new benches are **gated and verified as guards**, not just printed:
  reverting `_fhex` trips the persist bench's bump ceiling, and reverting the H9
  loader fix trips the loader bench's rejected-file check.

### Changed

- **Documentation sweep.** The worst offender: `state.md` documented
  `cyrius test src/test.cyr` as the form CI uses — which is precisely the bug
  1.2.0 fixed, since `src/test.cyr` is a no-op stub and that form ran nothing
  for the whole 1.1.x line. Corrected, and `src/test.cyr` is now described as
  the stub it is.

  Also: the test-group list stopped at M5 and was missing 17 of 30 groups; the
  `bench_combat` figure was stale by 3×; the session struct was listed at 328 B
  (it is 376); the fixtures list was three short; the "in flight" section
  carried two contradictory and both-stale paragraphs; and the parked-upstream
  item still described the audit-chain bound that libro 2.8.4 closed in 1.6.1.
- **Source comments reconciled with the roadmap.** Five comments referenced
  "M8 / Joshua", and two carried a `roadmap.md#m8-…` link to an anchor that no
  longer exists — Joshua moved to the backlog and the operator work is M18.
  Every roadmap anchor referenced from `src/` and the docs now resolves,
  checked mechanically.

### Where this leaves the 1.x line

**Not closed.** The re-run put eight findings through adversarial verification —
two independent lenses each, one instructed to refute and one to reproduce — and
**all eight survived; none was refuted.** One is critical: `MAX_LOGIN_FAILS` is
not actually enforced, because `SS_QUIT` is only honoured on the epoll event
path. That is a 1.6.2 fix which does not do what its own CHANGELOG entry says,
which is worse than a missing fix — it was believed done for seven releases.

They are filed as **batch E (1.6.10)** on the roadmap, with the verifiers'
corrected severities rather than the finders' claims. One filed finding was a
false positive (`render_who` bounds its room index both ways, not just from
below) and is recorded as such rather than quietly dropped.

**One of them is ours, from 1.6.7.** The zone reset re-mints an authored object
whenever `_obj_id_present` cannot see it, and that scan walks `oi_next` without
descending `OI_CONTENTS`. Before `put` existed, hiding an object from it
required carrying the object to another room. Now it can be hidden in place.
Reproduced live in `market.stalls`: `get optic` → `put optic in shard` →
`@reset` → **`objs +1`**, a duplicate on the floor with the original still in
the shard, repeatable once per reset cycle with no ceiling. Filed with both
halves of the fix, since the older relocate-driver is still open too.

**On the question the roadmap asked** — did the finding count fall? It is not
answerable as posed, and pretending otherwise would be the wrong lesson. The
first sweep's 44 was never a measure of what was there: it missed a remote crash
on a first-class command verb. What the re-run does establish is narrower and
more useful — every fix from batches A–C is still in place, and the new findings
cluster precisely where the first sweep had no instrument. Batch D is where
those instruments got built, which is why the second pass could see them.

### Testing

- 573 → **581 assertions**; new `roomless-safety` group.
- Three mutations on the crash guard; **two of them fail by segfault**, which is
  the correct failure mode for a crash regression.
- **Soak**: 240 session lifecycles of connect → login → move → kill → loot →
  save → quit. Tick drift p99 stayed at **1 ms** throughout (budget 50 ms).

  RSS grew **linearly**, ~9.2 kB per session lifecycle, and a second soak
  discriminated why: **240 connections that never authenticate moved RSS by
  +8 kB total.** So the growth is entirely on the authenticate/save path — the
  known libro bump leak, at a rate matching `bench_persist`'s per-op figures —
  and nothing else leaks.

  Worth recording: the soak script's first verdict function called that
  "PLATEAU". It tested `second_half <= first_half`, which steady linear growth
  satisfies. Fixed to require the second half to actually decay.

## [1.6.8] — 2026-07-28

**Sweep batch C — resource & timing hygiene.** Five findings about what the
server *costs* rather than what it gets wrong. Nothing here is reachable as an
attack; all of it is waste, drift, or an unbounded appetite. Two of the five
turned out to be materially different from how the sweep filed them, and one
had a fix that would have been worse than the bug — those are called out below.

### Fixed

- **Room broadcasts cost O(engaged × room population) `write(2)` calls.**
  `room_combat_line`, `room_broadcast` and `room_say_broadcast` each walked the
  session list and flushed every recipient *inside* the loop, so a tick with E
  engaged players co-located in one room issued 2E² − E writes. Measured on the
  bench at **81.4 ms p99 for 256 players — 163% of the entire ADR 0001 50 ms
  drift budget in a single tick**, flushing to `/dev/null`, the cheapest sink
  there is.

  The write is now deferred: broadcasts mark `SS_TX_DIRTY` and
  `flush_dirty_sessions` writes each session once, as the last statement of
  `advance_tick`. That takes the tick from 2E² − E writes to E.

  | co-located players | before | after |
  |---|---|---|
  | 32  | 1.31 ms | 0.53 ms |
  | 128 | 20.1 ms | 7.0 ms |
  | 256 | 81.4 ms (**over budget**) | 28.3 ms |

  Only the *write* moved — never the append. That distinction is what makes this
  legal on a frozen wire surface: per-client byte order is decided entirely by
  append order and a stream socket has no segment semantics, so deferring the
  syscall cannot reorder anything. Deferring the *append* would have been a real
  bug: `mob_died` broadcasts and then frees the instance into a freelist class
  the next spawn re-issues, so a queue holding `mi_name_ptr(m)` would resolve to
  a live, different mob.
- **…and the obvious version of that fix silently truncates output.** Worth
  stating on its own, because the sweep's suggested remedy — "append during the
  tick, flush each dirty session once at the end" — does exactly this. `TX_CAP`
  is 4096, `session_appendtx` truncates at it, and it reports the short write
  only through a return value that none of its ~200 callers read. A whole tick's
  coalesced prose overflows that cap at **36** co-located combatants; at 128,
  every session pins at `TX_CAP` and most lose their own damage line, condition
  line and prompt. The player hurt worst is the one last in the walk, because it
  accumulates everybody else's third-person lines before its own prose is
  appended.

  So coalescing ships with a capacity valve. `session_tx_reserve` writes out
  what is queued when the next append would come near the cap: in the ordinary
  case — a handful of players in a room — it never fires, and in the
  pathological case the session degrades to roughly the old per-line flushing
  instead of dropping bytes on the floor. That is what makes the fix safe at any
  population rather than at the one that happened to get measured.
- **A partial drain left dead space at the front of the tx buffer.**
  `session_drain` stored the offset and returned, so bytes already written to
  the socket went on occupying the buffer until a *complete* drain reset it —
  and `session_appendtx` measures its room as `TX_CAP - SS_TX_LEN`, with no idea
  the front is dead. A backpressured client therefore hit the cap early and lost
  prose silently. Pre-existing, but coalescing would have turned it from rare
  into routine. The remainder is now compacted to offset 0.
- **The autosave sweep saved every dirty session in one tick.** `save_sweep` ran
  every 300 s and signed the lot inline: measured **41 ms at 32 dirty sessions
  and 332 ms at `MAX_SESSIONS`=256** — 664% of the drift budget, and 13% of the
  entire 2.5 s tick interval, gone in one pass.

  It went unnoticed for a reason worth writing down: the tick schedule is
  absolute, so a sub-interval overrun is absorbed by the next `epoll_wait`
  timeout and `@stats` reports **0 ms drift straight through it**. The tick was
  not late. It was simply gone for a third of a second, and nothing in the
  server could see that.

  The cost is 89% `ed25519_sign` (1.30 ms per save, measured) and only ~5% file
  I/O, so batching writes is not the lever — doing fewer *signs* per tick is.
  `save_sweep` now runs every tick and saves at most `SAVE_BATCH_MAX` = 4
  sessions (5.2 ms worst case), with the 5-minute cadence moved from the sweep
  to the session via `save_sweep_due`. Per-session behaviour is unchanged; the
  burst is gone.
- **`reset_secs` had no floor and an unchecked `× 1000`.** Authored in the zone
  *file*, not just the `YD_RESET_SECS` operator knob. An authored `0`, a
  negative, or a value large enough to wrap `parse_uint` (which accumulates
  `v * 10 + d` with no overflow check) all drove `interval_ms` to zero or
  negative, making the elapsed-window test false forever — a reset attempt on
  every tick. `clamp_reset_secs` now bounds it at both sources and at the point
  of use.

  Note the interaction: **1.6.7 opened one of those doors.** Teaching `toml_int`
  to read a sign made an authored `reset_secs = -1` reach the interval, where
  before it fell back to the default. This clamp is the other half of that
  change.

### Changed

- **The tick reschedules off a clock sampled *after* the tick, not before.** The
  snap-forward exists for exactly one situation — the tick body ran long, we
  blew past a boundary, and we must not then fire a burst of catch-up ticks —
  and it read a pre-work sample, so in the one case it was written for it
  under-snapped by one interval and fired the doubled tick it exists to prevent.
  Self-limiting (the next pass recovers), so one extra tick per overrun, not a
  pile-up. Split into `tick_step` / `tick_reschedule` so both event loops share
  one implementation instead of drifting apart, and so the arithmetic is
  reachable from a test at all.

  **The drift metric is deliberately unchanged, and that matters.** The sweep
  filed this as "a long tick mis-measures its own drift", which invites moving
  the single sample after the work. That would be actively harmful:
  `record_tick_drift(now - next_tick)` on a *pre*-work sample is scheduling
  lateness, which is what the ADR 0001 budget is about and what `@stats` prints
  (a frozen field, ADR 0007 §41). It would also double-count, since an
  overrunning tick already surfaces as the next tick's lateness. There is a test
  asserting the metric does *not* absorb tick duration, specifically to fail
  anyone who "fixes" it that way.
- **`_build_record` allocates nothing.** It called `hex_encode` three times —
  salt, pubkey, signature — and that function allocates its output from the bump
  allocator, which has no `free` at all. Measured at **248 bytes per save,
  permanently, on a five-minute cadence**. `_hex_at` now writes hex straight
  into the record.

  Byte-identity was the whole risk here: these bytes sit inside the signed
  prefix, so a single character of divergence would make every record already on
  disk fail its own Ed25519 check at the owner's next login — they would be told
  the record was tampered with, and the character would be gone. `_hex_at` is a
  separate function precisely so a test can assert it agrees with
  `lib/sigil_hex.cyr` byte-for-byte rather than relying on anyone rereading the
  constants.

  **Scope honesty: this is 248 of 1880 bytes per save (13%).** The remaining
  1632 B/save is inside libro's `chain_append` / `filestore_append`, which
  `CLAUDE.md` forbids modifying — that needs an upstream release, the same shape
  as the 1.6.1 chain fix. Measured before and after: `_build_record` 248 → **0**
  B/call, whole `player_save` 1880 → **1632** B/call. The growth is reduced, not
  stopped, and should not be described as stopped.
- **The never-saved sentinel is tested explicitly, not inferred from the clock.**
  `save_sweep_due` first shipped relying on `now - 0` exceeding the five-minute
  interval for a session that had never saved. That is a statement about how
  long the *machine* has been up: `clock_now_ms()` is `CLOCK_MONOTONIC`,
  milliseconds since **boot**, not since the epoch. On a freshly-booted host —
  a reboot, or a CI runner — every character created in the first five minutes
  of uptime would silently skip the autosave. `SS_LAST_SAVE_MS == 0` is now
  tested outright, exactly as `save_rate_limited` directly above it always has.

  Caught by CI, which is the only machine here with an uptime under five
  minutes. The comment that had been written into the source asserted the
  opposite and was simply wrong; `save_rate_limited`'s comment carried the same
  bad reasoning (its *code* was right) and has been corrected too.
- **Autosave gap under full occupancy.** The metered sweep drains 4 sessions per
  tick against an arrival rate of at most 2.13, so the backlog is stable and a
  session that loses a batch is strictly more overdue next tick — no starvation.
  The one slow case is a synchronised cohort: all 256 becoming eligible on the
  same tick puts the last one 64 ticks (160 s) late, so the worst-case
  per-session gap widens from 300 s to ~460 s. This costs nothing on a clean
  disconnect (`drop_session` saves unconditionally) and only shows up on a hard
  crash, but it is a real cadence change rather than a pure optimisation.
- **Packetization, not byte order.** A client that used to receive its prompt in
  its own `write(2)` now receives it batched with the rest of the tick. Byte
  order is identical and every broadcast line still opens with `\r\n`, so a line
  landing after a prompt still starts on a fresh row. No conformant Telnet
  client cares, but it is the one observable difference and it belongs here
  rather than being discovered later.

### Not done, deliberately

- **No cross-tick save cursor.** The sweep proposed one. A full 256-session scan
  running the complete predicate measures 950 ns — 1/1400th of a single save —
  so a cursor optimises something already free, and buys a session pointer held
  across ticks in exchange. `SS_SIZE` lands in a freelist class that `fl_free`
  does not zero and the next `accept` re-issues, which is the exact shape of
  use-after-free that H1 and M12-C already exist to prevent. Metering the saves
  gets the same result with no pointer.
- **`parse_uint` still wraps silently.** It has no overflow check, so an absurd
  authored literal still lands on an arbitrary in-range value. The `reset_secs`
  clamp makes that value *harmless*, not *correct*. Fixing it properly affects
  every `toml_int` caller — class stats, save fields, zone fields — which is a
  wider change than a patch release should carry. Recorded as a follow-up.

### Testing

- 500 → **573 assertions**; new groups `reset-bounds`, `tick-schedule`,
  `tick-coalescing`, `tx-compaction`, `save-meter`, `hex-identity`.
- 25 mutations across the five fixes, each reverting one guard.
- **The timing groups use synthetic clock values, not `clock_now_ms()`.** The
  first version of `save-meter` read the real clock and was therefore measuring
  the host's uptime — it passed on a long-running desktop and failed on CI. Two
  further assertions carried the same assumption (a 2500 ms cadence needs 2.5 s
  of uptime to discriminate; `clock_now_ms() - interval - 1` goes negative on a
  fresh host) and were rewritten the same way.
- `benches/bench_combat.bcyr` gains a 256-player co-located broadcast scenario —
  it measures 28.3 ms with the fix and **fails the budget at 81.4 ms without
  it**, so it is a real guard and not just a number. This also closes the "no
  bench touches room broadcasts" gap the roadmap had filed under 1.6.9.

**Two testing notes worth carrying.** First, three of the coalescing mutations
initially failed to fail, and all three were test gaps rather than dead guards —
the sharpest being that `combat_flush`'s dirty mark is invisible at 64 players,
because every session is already marked by *somebody else's* broadcast. Only a
**solo** combatant can see it, which is also the most common case in an actual
MUD. Second, and worse: the mutation that makes `_hex_at` emit uppercase — the
one that would destroy every save on disk — **passed a test whose comment
claimed it covered "every byte value"**. It built a 256-byte probe and then only
ever encoded the first 64 bytes, so the high nibble never reached 10 and the
`a`-`f` branch was never executed. A test that claims coverage it does not have
is worse than no test, and the only thing that surfaced it was mutating the
constant and watching nothing happen.

## [1.6.7] — 2026-07-28

**Sweep batch B — content + parser correctness.** Four findings where the game
said it did something and did not. Nothing here is a crash or a leak; all four
are the server lying to the player.

### Fixed

- **The `N.X` qualifier was parsed everywhere and honoured nowhere.**
  `qual_parse` has returned `QUAL_NTH` with a count since M2-E, and every caller
  threw the count away: `cmd_get` and `cmd_drop` read only `QUAL_ALL` and handed
  the *base* noun to `ilist_find_kw`, which returns the head-most match, and
  `cmd_kill` never called `qual_parse` at all. So `get 2.ration` took the first
  ration; `kill 2.scavver` searched for a mob whose keywords are literally
  spelled "2.scavver", found none, and answered "You see no 2.scavver here to
  attack" with two of them standing in the room.

  Both scans are now ordinal-aware — `ilist_find_kw_nth` (objects) and
  `mob_in_room_by_kw_nth` (mobs) — and `qual_single` folds a token down to
  (base noun, ordinal) for every verb that acts on one thing: `get`, `drop`,
  `put`, `give`, `examine`, `kill`, and the container half of `get X from Y`.
  Unqualified nouns resolve to ordinal 1, which is exactly the old behaviour,
  so this is additive against the frozen 1.x surface (ADR 0007 §1). `all.X` maps
  to the first match for these verbs, since none of them has a plural form; the
  mass verbs keep reading `QUAL_ALL` from `qual_parse` directly.
- **`put` and `give` answered a placeholder from M2.** Both parsed fully and then
  replied *"but the Under-Grid is empty — items arrive at M3"* — which stopped
  being true when M3 shipped, and read as a broken server for four releases
  afterwards. Both are implemented.

  `put` is the exact inverse of `get X from Y`, and like that verb it lets any
  object hold things: 1.x objects carry no container flag, so the two halves
  agree rather than one of them enforcing a rule the other does not. Nesting is
  capped at one level — a container that already holds something cannot go into
  another. That reads as a game rule ("empty it first"), but it is load-bearing:
  `obj_free` walks `OI_CONTENTS` recursively, so unbounded nesting is unbounded
  stack and a cycle would not terminate at all. Depth 1 makes both impossible by
  construction rather than by argument, and an explicit self-containment guard
  covers the one-object cycle directly.

  `give` hands an object to a player in the same room and flushes the recipient
  in the same tick, the way `tell` does — an item that arrives silently and only
  surfaces on the next command reads as a lost item.
- **`wear` / `remove` / `wield` now say why they cannot.** These are still
  unimplemented, but for a real reason: there are no equipment slots to wear
  anything into, objects carry no slot or wear-flag field, and adding one is a
  zone-format change the frozen 1.x surface does not permit — the loadout system
  is M17 (2.1.0). They now resolve the noun for real and answer honestly, so a
  player carrying a jacket learns the verb is unfinished rather than that their
  item vanished.
- **`bash` and `emp` printed their status prose after a killing blow.** Both set
  the stun, struck, and then unconditionally added "It reels, stunned." / "Its
  servos lock up." — describing a mob that had already collapsed two lines
  earlier. `ability_strike` now returns 1 when the blow kills and both callers
  gate their follow-up on it. Verified *not* a use-after-free: every ability sets
  the stun **before** the strike and none touches the instance afterwards.

### Changed

- **`toml_int` accepts a leading `-`.** It routed every value through
  `parse_uint`, which has no concept of a sign and returns -1 for anything it
  cannot read — which `toml_int` folded into the default. An authored `ac = -3`
  did not mean "AC minus three", it meant "AC 8, the default", silently. Nothing
  in the frozen v1 schema reaches a negative today, which is why it stayed
  latent, but the save writer has always *emitted* signs, so a negative could be
  written and never read back. Closes backlog **B7**.

  **Deliberately still lenient about garbage.** The batch-B finding also asked
  that an unparseable value be an error rather than a silent default. It is not,
  and this release does not change that: rejecting a value would reject zone
  files that load today, and the zone-file format is frozen by ADR 0007 §5 for
  all of 1.x. Strictness needs a format version to hang off — that is the 2.0
  conversation (M14 / ADR 0008), and it is recorded there.

### Documentation

- **`help` advertises the qualifier.** It has worked in the parser since M2-E and
  nothing has ever told a player it exists.
- **`docs/guides/commands.md` documented all five item verbs as working**, which
  is how three of them went four releases without anyone noticing they answered a
  placeholder. `put` and `give` now match the guide; the `wear` / `remove` /
  `wield` row says plainly that they are not implemented in 1.x and why, and the
  intro no longer claims nouns resolve against "worn/wielded slots" that do not
  exist. The qualifier and container-nesting rules are written down.

### Testing

- 448 → **500 assertions**; new `item-verbs` group covering the ordinal on both
  scans and end to end through `drop` / `kill` / `examine`, `put`'s cycle and
  nesting guards, `get X from Y` round-tripping what `put` stored, `give`'s
  transfer and same-tick notification, the equipment verbs' honest answer, the
  kill-report return, and `toml_int`'s sign handling.
- Ten mutations, each reverting one guard; every one fails between 1 and 8
  assertions.
- Live two-client run against a real `serve`: `put`, `give` (transfer, sender
  echo, recipient notified), `wear`, and `examine 2.scavver` / `kill 2.scavver`
  in the two-scavver room, with `examine 3.scavver` correctly not found.

## [1.6.6] — 2026-07-28

**Sweep batch A — state integrity.** Three findings that could corrupt,
duplicate or silently weaken persisted state.

### Fixed

- **A character could be logged in twice, duplicating its whole inventory.**
  `login_on_name` asked only `player_exists`; nothing looked at who was already
  connected. Both sessions ran `_restore_inv` and each minted a full copy of
  every saved item — and `zone_reset_room_objs` only refills **missing** ids,
  never removes extras, so duplicates parked in rooms were never reclaimed: an
  unbounded `fl_alloc` growth path driven by ordinary play. The second half is
  worse than duplication — both sessions write the same record with no
  compare-and-swap, so whichever disconnects last wins, and the stale session's
  `player_save` silently reverts the live one's room, drops, HP and class.

  `session_already_online` now refuses the newcomer, checked **after** the
  passphrase proves identity (so it cannot be used to probe who is online) and
  **before** `session_resume_world` places them. Matching is case-insensitive:
  `_path_for` lowercases only the *filename*, so two spellings share one record.
  Takeover semantics — boot the old session and adopt the character — need rules
  for in-flight combat and an in-progress `passwd`, so that stays a 2.0 question.
- **A maximal template id could not round-trip.** The object loader wrote ids at
  `OT_ID_CAP` (32) while `item_new` copies an instance's at `OI_TPL_ID_CAP - 1`
  (31), so a 32-byte authored id was truncated on the way into the instance and
  could never match its own template on reload — and the save record stores
  inventory **by that id**. Both now cap at `CAP - 1`, keeping ids
  NUL-terminated and round-trippable.
- **The audit chain restarted at genesis on every boot.** `filestore_open` tells
  the in-memory chain nothing, so the first entry of each run recorded
  `prev_hash = ""` instead of the previous run's head. A verifier walking
  `data/audit.libro` therefore saw a **broken link at every restart boundary**,
  indistinguishable from someone removing entries — the chain was tamper-evident
  only within a single process lifetime.

  `_audit_resume_head` now seeds the streaming chain from the durable head. It
  reads the file **tail** rather than calling `filestore_load_all`, which would
  materialise every entry ever written at boot and reintroduce exactly the
  unbounded growth 1.6.1 removed. Best-effort: a missing, empty or torn store
  leaves the chain at genesis, which is correct for a first run.

  Verified end to end across three separate server processes: **0 linkage breaks
  with the fix, 2 without** — one per restart boundary.

### Notes

- Suite **431 → 448**. New fixture `tests/fixtures/longid.objs.cyml`.
- **Two of my first three mutations did not discriminate, and both were test
  bugs.** The template-id test used a real Hub id (~6 bytes), which round-trips
  whether the cap is 31 or 32 — the truncation is only observable at exactly
  `OT_ID_CAP`. Rewriting it to hand-write the copy did not help either: that
  bypassed the line under test. It now drives the **real loader** over a fixture
  with a 32-byte id, and fails 2 assertions when reverted. The audit-tail
  mutation I first chose was behaviour-neutral; replaced with one that takes the
  first hash instead of the last, which fails 1.
- `session_already_online` fails 2 when neutered.

## [1.6.5] — 2026-07-28

**A failed load leaves no world; a failed save is never reported as success.**

### Fixed

- **Four content loaders published global state before validating it.** Each of
  `world_load_rooms` / `world_load_mobs` / `world_load_objs` /
  `world_load_classes` set its count immediately after `alloc`, while every
  `return WL_ERR_*` in the parse loop sits *below* that point. A rejected file
  therefore left a live, partly-filled table: `cmd_serve` printed "no zone
  loaded" and **every `world_room_count() == 0` guard in `session.cyr`,
  `combat.cyr`, `item.cyr` and `server.cyr` was defeated at the same moment**. A
  player could log in, walk into whatever prefix happened to parse, and be
  stranded in a room with no exits — with the operator told the load had failed.

  Three of the four now publish the count only on the success return.
  `world_load_rooms` could not: it is **two-pass**, and pass 2 resolves exits via
  `room_index_by_id`, which walks `g_room_count` — so the count has to be live
  *during* parsing. Its eight error returns route through `_wl_rooms_fail`
  instead, which zeroes the count and start room on the way out. Same guarantee,
  different mechanism. (This is the shape backlog **B2** described for
  `world_load_classes`; all four are now closed.)
- **A rejected `objs` file produced no diagnostic at all.** `cmd_serve` had no
  `else` arm for `world_load_objs`, and `zone_reset_objs()` was gated on the
  **mob** result rather than the object one — so a malformed `hub.objs.cyml`
  gave a completely clean-looking boot and then spawned from a file the loader
  had rejected. Both corrected.
- **`player_save` failures were discarded at four of five call sites.** The
  sharp one is the `passwd` commit: it ignored the return, wrote a `SEV_INFO`
  `passwd.change` entry, and told the player *"Passphrase changed. Your record is
  re-keyed."* — while the on-disk record still held the **old** pubkey. The next
  login would reject the new passphrase and the retired one would still work.
  Reachable from any I/O failure (ENOSPC, EIO, a failed rename), not only the
  over-cap-inventory route M11-D added.

  `chpass_on_confirm` now checks the return **before** the audit entry and the
  success prose, and **rolls the live ident block back** — the memcpy has
  already overwritten it by then, so without the rollback the session would keep
  a key the record does not have. The other three sites (`save_sweep`,
  `drop_session`, character creation) emit a `SEV_WARNING` audit event; creation
  also warns the player, since a failed first save means there is nothing to log
  back in to. A queued session line would be dead code in `drop_session` — the
  socket is already going away — so the audit chain is the only lever that works
  everywhere.

### Notes

- Suite **420 → 431**. Mutation-verified: stopping `_wl_rooms_fail` zeroing
  fails 2; making the `passwd` commit ignore its save return fails 4 — including
  two **pre-existing** assertions, which is precisely the corruption the check
  prevents.
- One test of mine asserted `WL_ERR_EXIT`, which does not exist; the real code is
  `WL_ERR_DANGLE`. Caught by the compiler, not by a passing test.

## [1.6.4] — 2026-07-28

**Two more sweep findings — one of them a data-loss bug, one of them mine.**

### Fixed

- **The `passwd` candidate lived in a global that persistence overwrites.**
  `chpass_on_new` parked the candidate `salt|pk|sk` in `g_persist_dec[0,112)`
  and returned to the event loop across a network round trip. That is
  byte-for-byte where `player_auth_load` decodes `salt` / `pubkey` / `sig`, and
  it overlaps `_build_record`'s signature buffer. **Any interleaved save or
  login destroyed it** — including a *failed* login against any account, since
  `hex_decode_into` writes before the signature verify. It needed no second
  player: `cmd_on_line` dirties the session on `passwd` itself, so the ~5-minute
  `save_sweep` broke it on an idle single-player server.

  The rare tail was worse than a refusal. If the interloper's passphrase
  happened to equal the one being confirmed, `_bytes_eq` passed against
  clobbered bytes and 64 **signature** bytes were installed as the secret key.
  `player_save` then wrote a record that cannot verify under its own pubkey — so
  the next login reported `PL_ERR_UNREADABLE`, told the player their record had
  been tampered with, and wrote a false `SEV_SECURITY "load.tamper"` entry into
  the audit chain. Permanent character loss plus a poisoned trail, and `PASS_MIN`
  is 4, so a collision is realistic rather than theoretical.

  Moved to a per-session `SS_IDENT_CAND` block, mirroring what the *creation*
  flow already does correctly. A dedicated global would fix the save/login
  interleave but not two concurrent `passwd`s; per-session fixes both. The block
  is wiped and freed on commit, on both rewinds, and in `session_free` — a
  derived secret key must not linger in a reusable freelist block. The comment
  claiming `[0..120)` while the copy is 112 bytes is corrected.
- **The M13 assist did nothing, and froze the mob that performed it.** Shipped
  in 1.5.0 and claimed in that changelog as mobs joining a room-mate's fight. It
  set `MI_TARGET` and printed *"…snaps round and joins the fight!"* and that was
  all: the only line in the tree that subtracts player HP is inside
  `combat_round`, whose attacker is the **player's** own `SS_TARGET`, and
  `combat_tick_all` walks sessions, never mobs.

  Worse, `mob_tick_all`'s engaged arm routed any mob with a target to
  `_mob_flee` **only** — which returns above `MORALE_FLEE_PCT`. An assisting mob
  is never attacked, so its HP never falls, so it never fled, never cleared its
  target, and never wandered or assisted again. At `ASSIST_CHANCE` 1-in-3 per
  tick, essentially every idle mob in a room where any fight happens latched
  within a few ticks: **M13's wander decayed to zero in exactly the rooms
  players use.** `cmd_kill` leaked the same latch on any retarget.

  Two parts. **H7-a** reaps a latch whose target has left the room, restoring
  wander and fixing the retarget leak. **H7-b** factors `combat_round`'s mob half
  into `mob_swing` and calls it for a latched, present, live session — skipped
  when the player is already fighting that mob, or it would swing twice a tick.
  H7-b is a balance change as well as a fix: a two-mob room now has two
  attackers. Only `market.stalls` ships two co-located mobs today.

### Notes

- Suite **410 → 420**. Mutation-verified: putting the candidate back on the
  shared global fails all 3 interleave assertions; removing the reap fails 2;
  removing the swing fails 1; removing the double-swing guard fails 1.
- The pre-existing `passwd` test called `chpass_on_new` and `chpass_on_confirm`
  back to back — the one ordering that **cannot** fail. The new assertions
  interleave a save, a failed login probe, and a second concurrent `passwd`.
- `SS_SIZE` 360 → 368 for the candidate slot.

### Deferred from the sweep

Fourteen lower-severity findings remain, unaddressed and listed here rather than
silently dropped: single-session login guard (duplicate inventory on double
login), `player_save` return values discarded at four of five call sites
(including the `passwd` commit, which tells the player it worked either way),
four content loaders publishing global state before validating it, audit chain
re-linking to genesis on restart, `toml_int` substituting defaults silently,
`OI_TPL_ID` one byte shorter than `OT_ID`, `reset_secs` unchecked `× 1000`,
per-save bump-arena leak, the `N.X` qualifier parsed everywhere and honoured
nowhere, five item verbs still answering the M2-era placeholder, tick
snap-forward against a stale clock sample, `bash`/`emp` prose after a killing
blow, benchmark blind spots, and a documentation sweep. None is DoS-class or
memory-unsafe.

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
