# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-07-31 (v1.7.18 — **gate re-run #4 returned DO-NOT-CLOSE**
> (0/3/3/3, items AZ-BH); its first batch **BE, AZ, BA, BH is closed**. Next is
> 1.7.19 — BC, BD, BF, BG)
>
> A **snapshot of the current tree**, not a history. Per-release chronology lives
> in [`CHANGELOG.md`](../../CHANGELOG.md); sequencing and what is planned live in
> [`roadmap.md`](roadmap.md).

## Version

**1.7.18** — 2026-07-31. **1407 assertions**; `cyrius audit` exits 0; 6/6 benches;
**2/2 fuzz targets**; both targets build.

**The boot sequence and the reader every table shares** — the first of three
batches from gate re-run #4.

**1.7.17 shipped a regression and this release is why that matters.** AR put an
ordinal ceiling of 1e6 inside `parse_uint`, which `toml_int` also calls — and
`toml_int` folds an unparseable value into its caller's **default**. Every
player's `created` was therefore overwritten with the login moment on every login;
`last_login` read as 0, making the "last seen…" greeting dead code on every
shipped server; and `RESET_SECS_MAX` became unreachable. The bound now sits in
`qual_parse`, the only caller with an ordinal, and `parse_uint` closes AR's wrap
with exact i64 arithmetic.

**Two silent, irreversible data-loss paths closed, both measured A/B against a
running server.** The boot object spawn ran fifty-three lines above the
`persist_init()` that seeds the offline census, so **every restart minted a fresh
copy of every object an offline player held** — 13/13/13/13 across four restarts
before, 13/12/12/12 after. And a rejected *rooms* table used to print "running
roomless" and carry on with the object loader **never called**, which is exactly
the inventory-emptying state AJ declared unsurvivable — **AJ's guard was keyed
correctly and was simply unreachable on that path.**

**Lessons carried, added this release:**

- *A correctly-keyed guard can be unreachable.* AJ's own note warns that copying a
  guard verbatim can be wrong. BA is the inverse, and nobody had written it down.
  **Asserting a guard EXISTS — which AJ's test does, by source offset — does not
  assert it can RUN.** The new assertion is on reachability.
- *A shared reader has no domain.* BE is the first defect this project has shipped
  *inside a fix for another defect*, one release later. When a fix changes a
  predicate, **grep every caller of the function it lives in**; one grep would
  have found `toml_int`.
- *Small fixtures cannot see a bound.* Every prior `IDENT_CREATED` fixture used 1,
  100, 999, 1234567 — or exactly 1000000, the largest value that still parsed. The
  suite stayed green throughout. The new assertions use a genuine epoch second,
  because that is the only value that separates the two behaviours.

**1.7.17** — 2026-07-31. **1387 assertions**; `cyrius audit` exits 0; 6/6 benches;
**2/2 fuzz targets**; both targets build; **9/9 mutations killed**.

**Mechanics and instruments** — the tail of gate re-run #3, and with it **every
finding from that run (AJ-AY) is closed**.

**A mob could not kill an unengaged player.** Combat is two-sided and the sides
are stored separately; `classes_upkeep` only looked at the player's half, so
anyone who never typed `kill` regenerated every tick while being hit — 70 swings,
24 hits, HP never below 36/40. Also: `parse_uint` wrapped so a 20-digit ordinal
resolved to a real object; death did not mark the record dirty; and the
hidden-roll RNG was seeded from **uptime**, so a server started at a repeatable
point in an init sequence replayed every combat roll identically.

**The instrument findings are the ones to remember.** The M2-F fuzz gate fed a
NEGATIVE length on 49,585 of 100,000 iterations and had **never executed** the
`pa_emit_byte` cap branch it exists to defend, while reporting PASS for eleven
releases. And two of the six benches in the audit gate **could not fail**.

**Lessons carried, added this release:**

- *Fixing the generator is not the same as reaching the guard.* Correcting the
  fuzzer's sign raised the max input to 5999 bytes and `PA_NORM_LEN` still peaked
  at 747 of 4096, because random bytes trip the TOKEN cap first. Coverage had to
  be engineered deliberately — and is now **asserted by the harness**, so it fails
  if the inputs stop reaching the guards rather than going quietly green.
- *A guard's observable is not always its return code.* Removing the `sig`
  hex-length bound still returns -2, because the signature fails to verify anyway
  — which is exactly why it had no test. What it prevents is a 2500-byte write
  through a 256-byte buffer, so the assertion is on a memory sentinel.
- *Some findings are content rules, not code bugs.* A noun spelled like a
  preposition cannot be a direct object, and every fix considered broke inputs
  that do occur. ADR 0005 states the rule; the suite pins the behaviour.

**1.7.16** — 2026-07-31. **1362 assertions**; `cyrius audit` exits 0; 6/6 benches;
fuzz clean; both targets build; **10/10 mutations killed**.

**The peer-reachable highs** — the last three of gate re-run #3, and with them
**every high that run found**.

**`passwd` mid-fight granted permanent immunity.** `combat_tick_all` gates the
round on `PHASE_CMD`; `mob_tick_all` deferred to that round whenever the player
was targeting the mob. Outside `PHASE_CMD` neither side swung. The deferral now
asks the question its own comment already stated — *will combat_round actually
swing this?*

**An object was duplicated on every logout/reset cycle**, because the reset
ceiling counted rooms plus ONLINE sessions and the reset only fires when nobody is
online. There is now an offline census, seeded once at boot and moved by login and
disconnect. Re-verified live: six cycles, still one copy.

**The account cap counted sealed identities**, with no decrement anywhere — 436
phantom slots/s, unauthenticated, no records written. 1.7.11 widened it without
noticing, by correctly removing the record that used to make the count true.

**Lessons carried, added this release:**

- *A fix for unbounded growth can be unbounded growth.* The census's first design
  rebuilt itself from disk every reset — measured at ~70 kB of permanently lost
  arena per rebuild, which is item C's shape inside the fix for item AM. Measuring
  the fix, not just the defect, is what caught it.
- *A test that depends on disk state left by an earlier run is a landmine, and a
  change can arm one that was never there.* Making the reset consult offline
  holdings coupled a pre-existing assertion to `data/players`, so it passed under
  `cyrius test` and failed under `cyrius audit`. Both commands were right; the
  test had to learn to control its precondition.
- *Two guards ordered wrongly can be worse than one missing.* Seeding the census
  from `persist_init` before the ready flag recursed forever, because the builder
  calls `persist_init` itself. The order is now pinned by a test, since only the
  order makes it terminate.

**1.7.15** — 2026-07-31. **1340 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **9/9 mutations killed**.

**The operator-edit blast radius** — the first three findings of gate re-run #3,
sharing one trigger: an operator edits a data file and the server runs on with a
half-published table or a positional reference that has moved.

**A rejected `hub.objs.cyml` was non-fatal**, so every saved inventory id failed
to resolve, `_restore_inv` dropped the lot in silence, and the next disconnect
wrote the emptied inventory back — irreversibly, since records are signed with a
key the server never holds. Re-verified live: a one-character typo, and the server
now exits 1. **1.7.11 made exactly this fatal for the class table thirty-five
lines below, in the same function.**

**`class` was a positional index** into `classes.cyml`, so adding a class
re-assigned every character; `room` has been a stable id one line away all along.
**And 1.7.11's own classless heal threw away the room it had just restored**,
because the class menu's exit path always called `session_enter_world`.

**Lessons carried, added this release:**

- *Copying a guard is not the same as porting it.* AJ's boot check keys on the
  loader's RETURN CODE, not on a zero count the way the class guard does — a zone
  with no authored objects is legitimate and loads with a count of zero. The
  obvious copy-paste would have refused to start on a valid world.
- *An enum bump is part of adding an enum value.* The new audit key was first
  added past `AK_NKEYS`, where the range guard silently downgrades it to an
  unrolled event costing 1944 permanent bytes per occurrence — the 1.7.1 defect,
  one key at a time. The comment at that guard predicts the mistake; a prediction
  is not a check.
- *Three test bugs, each of a kind this file already names.* `cl_at` returns a
  POINTER into the table, so holding it across a swap compares an entry with
  itself; a hand-built "legacy" record without salt/pubkey fails at -2 long before
  the field under test; and `room_broadcast` EXCLUDES the arriving session, so an
  arrival-prose assertion must watch an onlooker.

**1.7.14** — 2026-07-31. **1310 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **9/9 mutations killed**.

**Hygiene — and with it, every finding from gate re-run #2 is closed (AC-AI).**

**Key material outlived the operation that made it.** `ident_derive` left the
plaintext passphrase and the Ed25519 seed in `alloc`ed scratch that is never
freed, and each derive overwrote only a PREFIX — so the tail of the longest
passphrase ever seen persisted for the life of the process. `login_on_confirm`
separately left a full 64-byte secret key in scratch every session shares. The
rule was already in force at `sess_cand_clear` and `session_free`; these were the
third and fourth holders and nobody had looked.

**`sweep_idle` charged unauthenticated reaps against a signature budget** whose
entire derivation is "every reap is a signature" — untrue for exactly the pre-auth
reaps `PREAUTH_TIMEOUT_MS` exists to serve, so a slowloris burst could exhaust the
budget and delay their own eviction. **It does not close slot exhaustion**: a peer
sending one byte every 29 s holds a slot regardless.

**Lessons carried, added this release:**

- *A test can pin the right constant with the wrong population.* The idle-reap
  assertion had always used unauthenticated fixtures — the sessions the cap was
  never about — so it measured `IDLE_REAP_MAX` against work that costs nothing. It
  failed when the behaviour was corrected, which was the test being right about
  the wrong thing.
- *Three releases running have needed a source-level guard.* 1.7.11 (a call site
  the suite cannot reach), 1.7.12 (a guard needed at N sites, where presence is
  not enough), and now an ORDERING that no test can observe because the freelist
  returns blocks unzeroed. That is a finding about the suite's reach, not just
  three separate workarounds.

**1.7.13** — 2026-07-31. **1295 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **7/7 mutations killed**.

**The reserve is per-command; the queue is per-read.** One accounting error at two
altitudes, fixed as one edit because either alone leaves the mechanism.

**`examine` rendered authored bodies unbounded** — mob and object descriptions are
raw `(ptr, len)` borrowed from the parsed CYML buffer with no `copy_str_capped` on
the path, and `item_new` propagates the object pointer into every instance. A
6000-byte body ran the queue dry and the prompt never arrived. 1.7.9 had fixed the
same thing for the room header and clamped it INLINE, which is why the two
`examine` arms were missed; the clamp is now `session_append_bounded`, shared.

**Output accumulated across a whole read.** Nothing flushes between the lines of
one read — 1.6.8 coalesced writes on purpose — so eight commands share one 4 kB
queue while `room_line_fits` re-measures its reserve against the whole buffer each
time. Eight `look`s in a busy room ran it dry, the last reply cut mid-number
inside its own truncation notice. The header and exits line now decline whole.

**Lessons carried, added this release:**

- *Clamp once, in a function.* Three call sites needed the same bound and the
  fourth was missed because the third was written inline. An inline fix is a fix
  that cannot be reused, and this tree keeps finding the sites that reuse would
  have covered.
- *A guard with two callers, tested through one, is a guard tested through none.*
  The exits guard survived mutation because `session_show_room` returns before
  reaching it — but the `exits` VERB calls it directly, and that is the path where
  it earns its place.
- *A fixture that cannot distinguish the guard from its absence proves nothing.*
  That assertion first filled the queue to one byte past the reserve line, where
  the line still fits, and so passed with the guard deleted.

**1.7.12** — 2026-07-31. **1270 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **5/5 mutations killed**.

**Persistence integrity, and the bench that could not see the defect it was
written to watch.**

**A refused duplicate login reverted the live session.** The refusal set `SS_QUIT`
and left `SS_AUTHED` set, so `drop_session` wrote the duplicate's load-time
snapshot over everything the real session had done. The window is up to a full
tick, not one batch: on the retained-line path `drain_pending_rx` condemns without
dropping, and the drop lands on a later walk. One line.

**Both batch loops tore sessions down unmetered** — `CHG_SIGN = 10` per teardown
against a 20-unit window, so 64 condemned sessions spent 640 units while the pass
believed itself metered. **Verbatim the 1.7.0 finding**, fixed there for
`drain_pending_rx` and never carried to the batch loops.

**Lessons carried, added this release:**

- *A bench that cannot reach the expensive path reports a budget that is met and
  tells you nothing.* Every fixture in `bench_tick_budget` was `memset`, so
  `SS_AUTHED = 0` and the teardown arm could not fire — which is why AF survived
  a gate sweep **in the code that bench exists to watch**. Measured now, both
  ways: 6 ms / PASS with the fix, **59 ms / 118% of the drift allowance / FAIL**
  without. Build the fixture that reaches the arm, or the gate is decoration.
- *A presence check is not a wiring check.* The first source assertion for AF only
  proved the drop arms were no longer one-liners, and passed with either loop's
  meter deleted — the exact state that shipped for eleven releases. Guards that
  must exist at N sites need a COUNT.
- *Do not gate an unconditional save on a flag with known holes.* The gate asked
  whether `drop_session` should consult `SS_SAVE_DIRTY`. It should not: the
  `cmd_give` hole this release fixed is evidence the flag is not trustworthy, and
  the unconditional save is what has been covering for it.

**1.7.11** — 2026-07-31. **1259 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **10/10 mutations killed**.

**The two highs from gate re-run #2**, both operator-facing data loss, neither
needing an attacker.

**A clean shutdown saved nobody.** `cmd_serve`'s exit never walked
`g_session_head`, so SIGINT/SIGTERM discarded up to five minutes of progress for
every connected player, on every restart — while `running.md` promised the
opposite and ADR 0006's trigger list did not mention shutdown at all. Verified
live: a player holding an item across SIGTERM now yields
`server: saved 1 session(s) on shutdown` with the item on disk.

**A character could be persisted with no class, permanently.** `SS_AUTHED` is set
before the class menu and `drop_session` gated on it alone, so closing the window
at the menu wrote `class = -1` — and `PHASE_CLASS` is stored in exactly one place
in the tree, so nothing ever sent a player back. Worse, a failed `classes.cyml`
load was non-fatal, which demoted **every** character on load and wrote it to disk
on the next disconnect. Closed at three points: the disconnect gate, a **login
heal** for records already on disk, and a fatal boot (exit 1) on an empty table.

**Lessons carried, added this release:**

- *A guard the suite cannot reach is a guard that is not there.* Mutation testing
  showed that deleting the `shutdown_save_all()` **call site**, and deleting the
  fatal boot check, each broke **no test** — the suite cannot run `cmd_serve`,
  which parks in `epoll_wait`. That is precisely what AC was: every save path in
  the tree existed and none was wired to shutdown. Both call sites are now
  asserted by reading the source, as 1.7.8 does for raw syscalls. **When the
  failure is invisible to every instrument you have, build the instrument.**
- *Fix the record you already wrote, not just the code that wrote it.* A save-side
  guard alone would have left every existing classless record unrepairable,
  because the operator cannot re-sign a player's file. The load-path heal is the
  half that reaches them.
- *A group that asserts ABSENCE is the easiest place to leave a landmine.* This
  release's own mutation passes — which run with the guards removed — wrote the
  very records the tests assert are absent, poisoning every later run until the
  group learned to unlink its fixtures first.

**1.7.10** — 2026-07-30. **1229 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build. **No source change.**

**Toolchain 6.4.86 → 6.5.4, and the dependency snapshot with it.** Taken as a
release of its own per the 1.2.0 precedent — that upgrade repaired a `main` and a
bench which had both silently stopped compiling, and that is not something to
discover folded into a feature change. `cyrius lib sync --full` moved 9 vendored
files (`bayan`, `sigil`, `sigil-mldsa`, `sakshi`, `sandhi`, `yukti`, `io`,
`regex`, `vec`) and `cyrius deps` rewrote the lock.

**Two long-carried entries in this file closed with it.** The toolchain-drift
warning is gone, and the **sakshi shadow gap** — open since 1.2.0, and recorded
here as needing a sigil-side bump — resolves cleanly to **2.4.7** at 6.5.4 with no
upstream change required.

**Two things were verified rather than assumed**, because the code that depends on
them shipped in the previous two releases and `io.cyr` / `bayan.cyr` were both
among the files that moved:

- `lib/io.cyr` still carries the `#ifdef CYRIUS_TARGET_AGNOS` branches in
  `file_rename` / `xunlink`, with the length-carrying arities 1.7.8's persistence
  fix routes through.
- `lib/bayan.cyr` went 1.2.1 → 1.3.0, and the TOML behaviour 1.7.8's
  parser-differential guard reasons about still holds — the `preauth-alloc`
  group's crafted, validly-signed records pass unchanged.

**Faster for free:** `bench_combat` p99 **530 µs → 444 µs**, gated pre-tick total
**4 ms → 3 ms**. Recorded because those numbers are quoted elsewhere in this file
and nothing in the tree changed to earn them.

**1.7.9** — 2026-07-30. **1229 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **13/13 mutations killed**.

**The wire stops being cut in half.** 1.7.6 and 1.7.7 stopped *listings* ending
mid-line; this release makes the same guarantee one layer down, where the unit
being cut is a **protocol sequence**. `session_consume_rx_max` drained the Telnet
negotiation reply with a truncating append and then consumed the source
unconditionally, so a full queue put a bare `IAC WONT` on the wire — and a
conformant client takes the next data byte as the option code. Measured: at a
4001-byte-full queue, 31 triples out and a trailing partial; after, no partial.

**The same defect at the sites every real client hits.** `session_echo_off` /
`session_echo_on` push a raw `IAC WILL/WONT ECHO` through the same truncating
append, from *inside* the dispatch path — after the passphrase prompt's prose is
already queued, so they meet a full buffer sooner than the negotiation path, not
later. Found while reviewing the fix for the first site.

Also: the room header's authored prose ran unguarded ahead of the three sections
1.7.6 bounded and could eat their 512-byte reserve; and the last two loops of
that class — `class_send_prompt` and `mob_swing` — adopted the fit check.
`mob_swing` matters because it is on the TICK path, where `combat_flush` only
marks the session dirty, so every latched mob appends into one 4 kB queue before
anything drains it.

**Lessons carried, added this release:**

- *Bound the output, not the input.* The first cut of this fix refused to READ
  while the queue was full, and that deadlocked: every pass consumed nothing,
  `drain_pending_rx` re-armed off `SS_RX_LEN > 0`, and the loop clamped its
  timeout to zero — a 100% CPU spin the idle sweep could not collect, because
  `session_on_readable_max` refreshes the activity stamp off retained bytes
  alone. **The fix was worse than the defect**, and only an adversarial read of
  the design caught it before it shipped. Coupling input to output on a
  single-threaded server is a livelock waiting for a slow reader.
- *Truncation is acceptable for prose and never for a sequence.* The right
  primitive was missing rather than misused: `session_appendtx_atomic` writes all
  of an indivisible thing or none of it. Dropping a whole negotiation reply is
  protocol-legal; half of one is not.
- *Check whether the document or the code is the thing that is wrong.* Roadmap
  item E has been recorded as closed since 1.7.2 and never was — but the code was
  right: a record a real server can produce already holds ~685 items, so clamping
  the load path to `MAX_INV` would destroy real belongings. Five releases of a
  false claim in the tracker, resolved by measuring instead of patching.

**1.7.8** — 2026-07-30. **1180 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **12/14 mutations killed** (the two exceptions are named in
the CHANGELOG rather than rounded up).

**AGNOS persistence, and the pre-auth parse.** The last two highs from the gate
re-run. Both had been true for many releases, and neither could fail a test — for
two different and instructive reasons.

**`player_save` never published anything on `--agnos`.** It renamed with a raw
`syscall(82)` and unlinked with `syscall(87)`; those are rename and unlink on
x86_64 and **GPU dispatch and GPU blit** on AGNOS, the latter annotated in the
stdlib as *"UNLINK on Linux — DELETES A FILE"*. Directories were not created
either — `sys_mkdir` takes a **mode** on Linux and a **path length** on AGNOS. So
on that target every save failed and **every reconnect was offered a brand-new
character**, while the x86_64 suite stayed green because there the numbers are
genuinely correct. Confirmed in the emitted artefact, not just the source.

**The stdlib was never wrong.** `lib/io.cyr` has carried correct AGNOS branches
throughout, and the comment at the 1.7.4 rotation rename says to use them "not the
raw syscall above". 1.7.4 fixed its own new code and did not go back six lines.

**A wrong passphrase cost 2,248 permanently-lost bytes; now it costs 0.** The
record was fully parsed before the passphrase was checked, and the bump allocator
has no free. `salt` and `pubkey` are now read straight from the slurp buffer and
the parse deferred until the passphrase has proved itself. This also removes a
null-dereference an attacker could reach by exhausting the arena — `str_new`
returns 0 on OOM and bayan's parser dereferences it immediately.

**Lessons carried, added this release:**

- *The guard has to be able to see the defect.* No test on x86_64 can tell rename
  from GPU dispatch, and a raw syscall number compiles fine on both targets, so
  neither the suite nor the new CI `--agnos` build would catch a regression. What
  catches it is a suite assertion that **reads the source** and requires no raw
  numeric `syscall(` outside a comment. When the failure is invisible to every
  instrument you have, the instrument is what needs building.
- *A fast path must never quietly become a second file format.* The first cut
  returned a terminal "corrupt record" whenever its stricter scanner failed, which
  would have broken every hand-edited or non-canonical save. It falls through to
  the parser instead, and the optimisation applies only to the canonical shape —
  which is all real traffic.
- *A fix that adds a second reader adds a differential.* Two parsers over one
  security-relevant input disagree on shapes neither author considered; the guard
  against it is only worth having if a test can make it fire, and making it fire
  needed a **validly-signed** crafted record. The first version of that test broke
  the signed prefix, so the signature check refused it and the assertion passed
  with the guard deleted.

**1.7.7** — 2026-07-30. **1118 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; **17/17 mutations killed**.

**Carry the fixes to the sites they were never applied to.** Two of the four
findings that returned DO-NOT-CLOSE. Neither was a new defect: both were a rule
this project had already written down, applied at some sites and not the others,
with the correct code already in the tree — in one case 230 lines below the broken
one.

**Both were measured before being fixed, and the numbers held.** `get` of a bag of
99 while holding 99 landed at **199 against a cap of 100**, because the old guard
asked "am I at the cap" while `ilist_push` moved the object *and its contents* —
two different questions. `inventory` lost its prompt at **95 items** (94 fitted),
which is **under the game's own `MAX_INV` of 100**; `who` at **79 players**, and at
90 the cut landed on byte `0x80` — mid-UTF-8, the em-dash separator sliced in half.

The class, not the instance: `oi_move_count` is now the single answer to "how much
does this move move", shared by `get` and `cmd_give`; five listing loops adopted
`room_line_fits` / `list_append_more`, including the dormant `@who` twin.

**The fix introduced a regression, and the sweep caught it — the seventh time this
tree has done exactly that.** Making the guard per-item made the old
abort-the-whole-sweep-on-refusal behaviour wrong: one oversized bag would make
`get all` take **nothing** for a player carrying nothing, and tell them their hands
were full. The arm now skips what does not fit and keeps going, exits early only
when genuinely at the cap, and the refusal message learned to distinguish "you are
full" from "that one thing is too big" — two different facts, and saying the wrong
one is a lie the player can see.

**Lessons carried, added this release:**

- *Rationing the echo must never ration the effect.* `drop all` and `get all` are
  commands, not reports. A fit check around the whole loop body would have passed
  every prompt assertion in the suite and silently left items in the player's
  hands; it takes a separate assertion, on the world rather than on the wire, to
  tell those two fixes apart.
- *A mutation that fails to fail is a signal about the test* — fourteenth
  instance. The first `get all` coverage used bare floor items, and for a bare
  item `oi_move_count` is 1, so the old guard and the new one **are the same
  function**. The test could not have failed whatever the arm did.
- *Sweeping the class is what finds the next class.* Neither defect had a second
  instance — but looking for one turned up eight new items on the **RX** side,
  where a pre-auth peer drives the server's own reply buffer past `TX_CAP` and
  **both** of this server's input bounds are structurally blind to it. Roadmap
  items W–Z.

## Gate re-run #3 — DO-NOT-CLOSE (2026-07-31)

**The 1.x line does not close.** 0 critical, **4 high**, 5 medium, 7 low — 16
distinct defects, roadmap items **AJ-AY**. Run against a clean tree at `84c9a3a`.

**The one change that mattered: this time the finders could BUILD AND RUN.**
Re-run #2 executed nothing and said so in its own limits; this run gave each
finder an isolated git worktree and told it to measure rather than estimate.
Three of the four highs were then demonstrated **against a live server over TCP**
rather than inferred. The main repo was never touched.

**Fifth consecutive sweep to find the same pattern, and it is no longer a
coincidence: three of the four highs are a rule applied at one site and not its
sibling — and TWO of them are siblings of fixes shipped in this very release
line.** A rejected `data/classes.cyml` is fatal at boot (1.7.11, AD); a rejected
`hub.objs.cyml` **35 lines above, in the same function** prints a warning and
carries on — and then silently, irreversibly empties every player's inventory.
The 1.7.11 classless-record heal loses the player's room. 1.7.11's
`session_persistable` gate made the account-cap phantom permanent.

**The single highest-value thing the next pass could build**, named by the judge
and worth repeating here: **an offline-population conservation harness** — for
every authored id, `world_count + offline_record_count == authored_count`. Nothing
in this tree reads `data/players/` and checks it against the live world, and three
of the four highs trace to that absent concept. It would have caught the
duplication defect four sweeps ago.

**Two of the six benches in the audit gate cannot fail.** `bench_telnet` has no
budget constant and returns 0 unconditionally; `tests/*.bcyr` is an explicit
no-op. `cyrius audit` has been reporting 6/6 while 2 of the 6 are decoration —
which is the 1.7.12 lesson (*a bench that cannot reach the path reports a budget
that is met and tells you nothing*) recurring one level up, in the gate itself.

## Gate re-run #2 — DO-NOT-CLOSE (2026-07-31)

**The 1.x line does not close.** Five independent finders swept distinct surfaces;
every candidate faced three skeptics with separate lenses and had to survive a
majority; the judge reproduced each survivor against the shipped tree. **Nothing
was dropped.** Ten reports collapsed to **eight distinct defects** — roadmap items
**AC-AI**. Critical 0, **high 2**, medium 3, low 3.

**The two highs are both operator-facing data loss, and neither needs an attacker:**
a clean SIGINT/SIGTERM shutdown **saves nobody** (up to 5 minutes of progress for
every connected player, on every restart — while `running.md` promises the
opposite), and a character can be persisted with **no class**, permanently, because
`SS_AUTHED` is set before class selection and `PHASE_CLASS` is stored in exactly one
place in the tree, so there is no route back to the menu. That second one has a far
worse trigger: a failed `classes.cyml` load is non-fatal, the load path then clamps
every character to `class = -1`, and the next disconnect writes the demotion to
disk. **One operator typo plus a restart is playerbase-wide, irreversible loss** —
irreversible because records are signed with a key derived from the player's
passphrase, which the server never holds.

**The pattern, for the fourth consecutive sweep:** four of the eight are a rule this
tree already applies somewhere else and did not apply here. The unmetered epoll
teardown is *verbatim* the 1.7.0 finding — fixed in `drain_pending_rx`, never
carried to the batch loop, in the release whose own comment reads "ONE constant for
BOTH dispatch sites, on purpose".

**What the sweep could not see, recorded so the next one starts here:** it executed
nothing — no build, no suite, no bench, no running server — so every figure is
derived from source. That gap is not incidental: **item AF survived precisely
because `bench_tick_budget.bcyr` memsets its fixture, leaving `SS_AUTHED = 0` so the
arm it would measure cannot fire.** Only a run reveals that. Also unowned:
`parser.cyr` (the primary untrusted-input surface) and `combat.cyr`; the AGNOS build,
still judged by reading two arms of a preprocessor; persisted state evolving over
time rather than per transaction; and cross-session consistency — `cmd_give` mutates
the recipient's inventory while setting only the giver's dirty flag, so any save
boundary can leave two records disagreeing about who owns an object.

## Gate re-run #1 — DO-NOT-CLOSE (2026-07-29)

**The 1.x line does not close.** Four high findings survived adversarial
refutation and were reproduced by the sweep's judge on the shipped tree; a fifth
was found alongside. All five are in [`roadmap.md`](roadmap.md) as items **R-V**
with reproductions.

**Three are now closed** — R and S in 1.7.7, V (the account cap) committed. **T
and U remain and are 1.7.8**: **AGNOS saves never publish at all**, because
`syscall(82)`/`(87)` are GPU dispatch and blit there rather than rename and
unlink; and every login against an existing name permanently consumes 2,248 bytes
**before the passphrase is checked**.

The two that closed, in one line each: `get` of a container ignored its contents
(**199 held against a cap of 100 from one command; 130 items silently destroyed at
721**), and four listing verbs truncated mid-line with no prompt (**measured at 95
inventory items — under the game's own cap — and 79 players online**).

**Three of the four are the same defect the previous sixteen releases kept
finding — a rule applied at some sites and not the others.** Two are fixes from
1.7.3 and 1.7.6 that were never carried across; in one case the model code is 230
lines away in the same file.

**The lesson worth keeping:** the suite was green at 1048 assertions with all four
present. *None of them had a test, so none of them could fail.* Sixteen releases
of mutation-testing new guards did not create a habit of testing the guard's
SIBLINGS — the sites the same rule should have reached.

The sweep also did the discipline it was asked for: it **dropped a survivor it
could not stand behind** (a room-header finding whose stated mechanism was wrong),
and it recorded what was refuted — the audit-segment cold scan, the short-write
publish in `player_save`, the `epoll_wait` EINTR path, the `_audit_tail_hash`
short read — so none of it gets re-proposed.

**1.7.6** — 2026-07-29. **1039 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; suite green against an empty `data/players`.

**A room listing could break the terminal.** `session_show_room` wrote its
sections as unchecked `session_appendtx` calls, and that primitive truncates at a
BYTE boundary and returns a short count nobody reads. At 86 floor objects the
stream ended `" here."` then a bare `ESC [` — an incomplete SGR, no CRLF, no
colour reset, **no prompt** — and a conformant terminal then eats the opening
characters of whatever arrives next. Threshold 71–87 by room; it never recovers,
because a floor only grows.

**Ground decay did not fix this**, which is worth remembering: 1.7.5 bounds a
floor to 30 minutes of accumulation, and a busy town square passes 86 items well
inside that. Two fixes for the same collection, addressing different failures —
memory and wire-correctness — and neither substitutes for the other.

All three sections (objects, mobs, present players) now stop at a whole item with
a byte reserve held back, and report what they omitted. The player-list fit check
runs BEFORE the separator, because writing `", "` and then finding the name does
not fit leaves a dangling separator — a different malformed line.

**Also: per-attempt creation auditing restored**, reversing G3 (1.6.12). G3 made
it fire once at the cap because each entry cost 1944 unreclaimable bytes; 1.7.1's
rollup window removed that constraint, so a flood is now visible from the FIRST
attempt and the rollup's count is the true attempt total. A trade made under a
constraint, taken back once the constraint was gone.

**Lessons carried, added this release:**

- *The wire is a correctness surface, not a rendering detail.* A truncating
  appender whose short return nobody reads produced a malformed escape sequence
  and a missing prompt — found by a probe that was looking for wasted CPU, not
  for a bug.
- *Ask what a background agent was actually asked.* The design fleet's most
  valuable output was not the design it was commissioned for; the cost-curve agent
  found this while measuring something else, and the two design agents it was
  waiting on were superseded before they finished.

**1.7.5** — 2026-07-29. **1024 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build.

**Ground decay — the last item of the 1.6/1.7 audit line.** Player-dropped items
expire after two zone-reset intervals (30 min at the authored cadence). Nothing
had ever reclaimed a dropped item: ordinary play grew a floor 0 -> 80 across 40
kill/loot/drop cycles, and `look` walked it at 801 us per call for 10,000 objects
while the charge meter billed it zero.

The design is anchored to `reset_secs` rather than a new constant, so a faster
zone reclaims faster and `YD_RESET_SECS` tunes it for free — no new knob, ADR 0007
clean. Two traps avoided: reset INTERVALS rather than reset EVENTS (resets defer
while a zone is occupied, so a town square would never have decayed anything), and
`OI_AGE == 0` as "not armed" so authored furniture never expires out from under a
room.

**The donation bin already exists, unbounded.** Items in an authored room
container never decay — that is the shape players want, and nothing caps it.
Documented at `cmd_put`, filed for 2.0.

**Lessons carried, added this release:**

- *Check whether the assertion is testing the rule or the clamp.* A threshold test
  used a value below its own floor, so it asserted the clamp while claiming to
  assert the derivation.
- *Fixtures left armed contaminate the next measurement.* An instance count came
  out one low because an earlier test's item was still decaying during it.

**1.7.4** — 2026-07-29. **1007 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; suite green against an empty `data/players`.

**Audit-log rotation ships** — the ADR 0009 mechanism 1.7.1 decided and 1.7.3
deliberately deferred so its crash window could be a release's subject rather than
its fifth item. On-disk audit growth is now `8 MiB x 4 segments` plus a live file:
**a constant the code owns, with no traffic term.**

The three parts that carry the risk, each mutation-verified:

- **The crash window.** Rename succeeds, process dies before the first append —
  the live file is gone and a naive boot restarts the chain at genesis, which is
  the H11 bug of 1.6.6 reintroduced as a feature. The head resume now falls back
  to the newest segment; its test deletes the live file and requires the chain to
  resume anyway.
- **Attest before deleting.** `audit.prune` is written before the unlink and
  carries the victim's head hash. A marker naming a file with no hash attests
  nothing, which is exactly what unlink-first produces.
- **Never clobber a sealed segment.** `rename(2)` replaces silently, so a stale
  cache would be an unrecoverable deletion of attested history.

**Lessons carried, added this release:**

- *Search for what only the guard produces.* Two rotation assertions initially
  proved nothing: the sealed hash appears in BOTH the marker's details and the
  entry's own `prev_hash`, so searching the line for the hash found it either way.
  Asserting the marker TEXT — "<segno> <hash>" — is what discriminates. The weaker
  form let two mutations survive.
- *A mutation script that fails to apply reports a false SURVIVED.* One pattern did
  not match, the run printed "survived", and it took a second look to see the
  mutation had never been applied. Assert the substitution happened.

**1.7.3** — 2026-07-29. **971 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build; suite green against an empty `data/players` (the fresh-checkout
check CI taught us in 1.7.2).

Four of 1.7.2's six items. `cmd_give` counted the gift but not its contents
(measured 141 against a cap of 100 — the 1.7.2 carry-cap shape again, one release
later, on the verb nobody re-checked). A failing save retried every tick because
"last saved" only advances on success. And the two guards that had never had a
test — the `passwd` secret-key wipe and the double-login refusal — are now covered
and mutation-verified.

**Rotation did not land, deliberately.** The ADR 0009 crash window (rename, then
die, then the chain restarts at genesis — H11 as a feature) is the load-bearing
part and belongs in a release where it is the subject. It is first in 1.7.4.

**Lessons carried, added this release:**

- *State what was proven, not what is plausible.* The borrowed audit chain-link is
  a real hazard and its consequence was never demonstrated — a probe showed zero
  broken links either way. The one break in the working log has an unknown cause.
  Writing "confirmed at record 554" would have put a guess into the record where a
  future reader would inherit it as fact.
- *A probe that measures the wrong quantity is worse than none.* Two drafts of that
  probe compared a chain link across an operation that legitimately advances it,
  so "the link changed" proved nothing either time.

**1.7.2** — 2026-07-29. **946 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build.

**The carry cap becomes a bound, and the operator gets a say.** A carried
container flattened past the cap and poisoned the save — player-armable data loss
with an ordinary bag: `inv_count` counted the top level while `cmd_put` moved
items out of it, and `_build_record` flattened them back in and then refused the
whole record rather than truncating. Both halves fixed. Plus an optional
`data/server.cyml` (`max_accounts`, default 0 = unlimited), records sharded into
`data/players/<c>/`, and ADR 0007 amended to admit the config surface.

**The sweep's real finding: the defect class recurred inside its own fix.**
1.7.1's audit rollup re-stamped its window on every count-arm fire, so the clock
arm stopped firing under sustained load — a counter that resets itself, which is
G2's `SS_FAILS = 0` shape and the reason 1.7.1 existed. And the carry-cap fix
introduced a regression in the same release (the cap over-applied to your own
bag). Both caught by mutation testing, not by review.

**Lessons carried, added this release:**

- *Fixing the class is not the same as being immune to it.* A release whose whole
  subject was "a cap that is not a bound" shipped a cap that reset its own counter.
- *A test that passes because of leftover state is not a test.* Removing the shard
  `mkdir` survived mutation until a test deleted the directory first — the
  directories existed from earlier runs, so a first-boot outage looked covered.
- *Assert the thing that distinguishes.* Two assertions this release could not tell
  success from failure: a total unchanged whether an item moved or the move was
  refused, and a config fixture whose value never reached the clamp under test.
- *An unchecked write is a lie with a delay.* Sharding broke a forged-record test
  on CI, which reported `-1 instead of -2` — "no record" rather than "tampered" —
  because `file_write_all` into a not-yet-existent shard directory failed and
  nobody looked at the return. The symptom pointed nowhere near the cause. Test
  fixtures that write records now go through `_write_record_raw`, which creates the
  directory and asserts the write. **Reproduce a CI failure by making the local
  environment match** — `rm -rf data/players` reproduced it exactly, and is now
  the check to run before claiming a persistence change is green.

**1.7.1** — 2026-07-29. **873 assertions**; `cyrius audit` exits 0; 6/6 benches;
both targets build (`x86_64` + `--agnos`).

**Bound what the reconnect rate sets.** The audit rollup window takes a reconnect
flood's permanently-lost memory from **667 MiB/hour to ~229 KiB/hour** (~3000×) and
its disk growth by ~2600×, by bounding the event COUNT — the only part of the cost
that is ours. Measured hard zero: 5000 suppressed occurrences allocate 0 bytes.

Three corrections to numbers this project had published:

- **1944 bytes per audit event, not 1640.** There is a further 304 B/event of
  freelist that nothing ever frees (libro's `hasher_new` + SHA-256 context; there is
  **no `hasher_free`**, and the freelist never munmaps, so an un-freed block is as
  permanent as a bump byte).
- **48 bytes of it are ours, not 224.** The 224 was `chain_append`'s total, 176 of it
  inside libro's `entry_new`. Descent's share is 2.9%.
- **Rotation needs no on-disk format change**, so it is 1.7.x work rather than 2.0.
  [ADR 0009](../adr/0009-audit-log-rotation.md) is Accepted; the mechanism is 1.7.3.

And a live data-integrity bug, found while measuring the above: **436 of the audit
log's 37,902 records reported themselves as tampered with**, because libro
substitutes `{}` for an empty `details` on read while the entry hash covers the
details. Every call site passes `SS_NAME_LEN`, which is 0 until a name is accepted.
Separately, **the test suite had written 1,545 records into the operator's log**;
it now writes to a fixture, verified as a zero-record delta on a full run. The 436
are deliberately **not** repaired — rewriting a hash-chained log is precisely what
it exists to prevent.

**Lessons carried, added this release:**

- *A per-item cap is not a bound on how many items there are* — fourth appearance
  (`passwd`). `grep` finds the cap; what it does not show is where the counter gets
  **reset**, which is where three of the four hid.
- *Reach for the obviously-named library function last.* libro's `chain_rotate` and
  `chain_head_hash` both look like the answer to rotation and both silently do
  nothing on a streaming chain, because they read an entries vec that is always
  empty here.
- *A latency meter cannot see a byte leak.* 1.7.0's charge window was the first
  thing tried for this bug and structurally could not work: its quantifier is
  per-pass cost, this needed per-lifetime accumulation, and one audit event rounds
  to zero charge units while costing 1944 permanent bytes.

**The tick budget becomes a budget.** The drift-relevant quantity — work that
delays a scheduled tick — went from **~247 ms to 4 ms**, and a wrong passphrase
from **8006 µs to 1066 µs**. Five changes, in descending order of leverage:

1. **The auth path stopped paying for an answer it could not use.**
   `player_auth_load` verified the record signature (7107 µs) *before* checking
   whether the passphrase even derived the right key (1077 µs). Both must pass, so
   the order was free to change. 7.5× on the costliest line an unauthenticated
   peer can queue. The 0.9.0 length checks and hex decodes already established
   every input the moved code reads, and the verify still gates all field restore.
2. **A charge window replaced the line counts.** One line spans 1.7 µs to 8411 µs,
   so no line count was ever a bound. Charges come from **counters at the four
   expensive call sites** — a table that predicts a line's cost can be wrong the
   way the old comment was wrong; a counter cannot be wrong about how many times
   `ed25519_verify` ran.
3. **`drain_pending_rx` moved into both loop bodies**, with `g_rx_backlog`
   clamping the epoll timeout / skipping the agnos sleep. Without this a metered
   pass would hand its refused lines up to 2500 ms of latency, because a session
   drained to EAGAIN is not readable and epoll never re-fires for bytes already in
   `SS_RX_BUF`.
4. **Condemned-session teardown is charged.** That arm never consulted any budget,
   and `drop_session` opens with an unconditional signed save: 81 ms at 64 authed
   drops, ~325 ms projected at MAX_SESSIONS.
5. **`bench_tick_budget.bcyr`** gates a whole pass, with a calibration tripwire
   for slower hosts.

Two of the thirteen new guards **survived the first mutation pass**, which meant
my tests were wrong, not the mutations: the prose charge only used cases where
escaped == offered, and nothing drove the teardown arm at all. Both closed.

A documentation truth pass, no code changes. The README was five releases stale
and `docs/architecture/overview.md` documented a combat model that was never
built — a `1d20 + DEX` hit roll (DEX is not involved), STR/TEC damage scaling
(neither touches the auto-attack), `rest`/`sleep` verbs and safe-room recovery
(neither exists), and a sample transcript with `[Tick N]` prefixes and per-limb
hit locations. **STR does nothing at all today** — stored, displayed, read by no
game rule. Every claim was checked against source; what is still aspirational now
says so and names the milestone.

Both docs also picked up the two user-visible changes of the whole 1.6.x line,
neither of which had reached them: the **100-item carry cap** and the **30 s
pre-auth disconnect**.

**Six of the gate sweep's eight items are now closed** (two highs in 1.7.0, three
in 1.7.1, one in 1.7.2). Two remain, plus ten more that these three releases'
own investigations turned up — all in [`roadmap.md`](roadmap.md).

**Next is 1.7.3**: the ADR 0009 rotation mechanism, the uncapped room floor
(measured 40 cycles → floor 0→80 from ordinary play), `cmd_give`'s ~199 overshoot,
the per-tick save-failure retry, and the pre-mutation coverage gaps.

*Superseded — kept for the record.* Before 1.7.2 this paragraph read:
a **carried container flattens past the carry cap and poisons the save**, which is
player-armable data loss reachable with an ordinary bag and no malice; and
**nothing caps the number of accounts**, which is why "authenticated" is not a rate
bound anywhere in this tree. Also there: the rotation mechanism per ADR 0009, the
per-tick save-failure retry, and restoring the audit granularity 1.6.12 traded
away (now affordable under the rollup window).

**Two corrections this release made to its own prior claims**, recorded because
both were published:

- The "252 ms = 504% of the drift budget" headline **summed two different
  quantities**. `record_tick_drift` takes a pre-work sample, so tick-body cost is
  invisible to it by construction; only the event batch delayed a scheduled tick.
  The drift-relevant figure was ~247 ms against 50 ms — the defect was real, the
  arithmetic was loose in the same way as the comment it indicted.
- **ADR 0001 never contained the 50 ms figure.** It said tick drift was
  load-bearing and pointed at the M4 gate; the number lived only in the roadmap
  and the benches, which is how three gates came to disagree about what it
  covered. It is now stated in the ADR, split into a **drift** allowance (50 ms
  p99) and a **tick-body occupancy** allowance (250 ms).

---

## Lessons carried

Durable and hard-won; each cost at least one release to learn. Collected here
because they are about *how to work on this tree*, not about any one release.

**Fixing an instance is not fixing the class.** 1.6.12's critical was the fourth
appearance of one defect — *a per-item cap is not a bound on a loop that walks
many items* — after three releases each capped a neighbour of the open hole.
When a finding feels familiar, enumerate the class first: `grep -n ident_derive
src/` lists every expensive-line path; "every loop that dispatches lines" lists
every place a cap must be aggregate. Both were one command away. **The gate sweep
found a fifth instance** — the 100-item carry cap is checked at all three
acquisition sites and at none on the load path — which is why 1.7.2 sweeps the
class rather than patching the instance.

**A comment is not a bound, and a comment's arithmetic is not a measurement.**
The gate sweep's worst finding is a budget comment that multiplied out the wrong
line cost (1.08 ms for a keypair derivation, when the reachable worst case is a
7.46 ms passphrase verify) and read as finished reasoning for eight releases. A
second finding was stated outright in a source comment — *"it did not bound
reconnects, and nothing else did either"* — and left open. Write the number down,
then have a bench assert it.

**A signature proves authorship, not field validity.** Players own their signing
key (ADR 0004), so every loaded field needs a range check *and* the relational
invariants need checking too (hp vs maxhp, room index vs room count).

**A mutation that fails to fail is a signal about the test.** Roughly a third of
every batch's mutations needed the test rewritten before they discriminated, and
in every case the test was the thing that was wrong. Recurring causes:
- `var buf[N]` is N **bytes**, not N entries — the first line of CLAUDE.md's Key
  Principles, and it still smashed a stack in 1.6.10.
- A test that **reimplements** the logic instead of calling it (1.6.12's first
  event-budget test hid three mutations this way). Extract a seam and drive the
  real function — `tick_reschedule`, `event_batch_step`.
- A budget that is an exact multiple of the per-item cap never exercises a
  partial cap, so the parameter looks honoured even when ignored.
- Asserting a derived total instead of the thing itself (a budget *delta* cannot
  see a step that charges a flat 1 per item).
- `ilist_find_kw_nth` with a zero-length noun matches **nothing**, so a lookup
  that looks like "the first item" silently selects none.

**A test that dies silently reads exactly like a test that passed.** Two harness
bugs truncated a run rather than failing it: a session built by `_tx_sess` has
`SS_FD = 0`, so `session_free` closed **stdin**; and `SS_TS = 0` made
`telnet_state_free` dereference null. Anything handed to `drop_session` goes
through `_freeable_sess`.

**Tests must not depend on what they do not control.** CI has caught two: a
5-minute cadence tested against `clock_now_ms()`, which is **uptime since boot**,
not epoch (1.6.8); and a "guaranteed hit" that isn't, because `combat_try_hit`
misses on a natural 1 whatever the bonus (1.6.12). A local pass proved nothing
about either. Timing groups use synthetic clocks; RNG-dependent assertions retry.

**A test that is not idempotent is a landmine.** `create-guards` saved a record
and so failed on its own second run — green once, red forever after.

**RSS is the wrong instrument for a bump-arena leak** and the right one for a
freelist leak. `alloc()` never returns memory and `fl_free` never munmaps, so use
`alloc_used()` for the former (that is what `bench_persist` reports) and a
control arm for the latter — 1.6.9's soak isolated its growth by running the same
churn *without* authenticating.

**A comment asserting the opposite of its code is a finding.** This tree has
produced several, including a factually false justification in a comment I had
written myself two releases earlier.

---

## Toolchain

- **Cyrius pin**: `6.5.4` (`cyrius.cyml [package].cyrius`) — bumped in 1.7.10

Two toolchain quirks (first hit at 6.4.83, still present at 6.5.4), worked
around rather than fixed here:

- `cyrius fmt -w <file>` does **not** write. Capture `cyrius fmt <file>` on stdout
  instead. Flag order also differs per tool: `cyrius fmt <file> --check`, but
  `cyrius doc --check <file>` — and `doc` writes its findings to **stderr**.
- `cyrius lib sync --full` reports a full 99-file snapshot while leaving some
  bundled libs untouched. At 6.5.4 that is `mabda` (4.0.7 vs 4.0.8) and `yantra`
  (1.0.1 vs 1.0.2), which is why two shadow warnings survive a full sync. Neither
  is referenced anywhere in `src/` / `tests/` / `benches/`. **Correction:** this
  entry used to say both were "pruned as unused" — `yantra.cyr` is present in
  `lib/`, so they were vendored, just never called.

`cyrius audit` at 6.4.x is the **project sweep** (fmt / lint / docs / tests /
bench over `src` + `programs`). `cyrius audit --internal` is the different,
cyrius-internal self-host gate — do not run it in this repo.

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
  session.cyr    Session struct (376 B), login (M1-E) + class select (M5-A)
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
  test.cyr       [build].test entrypoint — a NO-OP STUB that only has to
                 compile and exit 0. Real cases live in tests/*.tcyr. This
                 stub is why `cyrius test src/test.cyr` silently passed for
                 the whole 1.1.x line without running anything (fixed 1.2.0).

data/
  classes.cyml                  the 4 player classes (M5-B)
data/zones/
  hub.rooms.cyml                the authored 21-room Hub starter zone (M3-G)
  hub.mobs.cyml                 Hub bestiary: scavver → Sentinel boss (M4)
  hub.objs.cyml                 Hub loot objects (M4)
  example.rooms.cyml            3-room schema example (ADR 0005)

tests/
  cyrius-yeomans-descent.tcyr   unit suite (1387 assertions)
  cyrius-yeomans-descent.bcyr   scaffold-family placeholder (real benches
                                live in benches/ — see below)
  cyrius-yeomans-descent.fcyr   scaffold-family stub; real fuzz harness in
                                fuzz/ (the toolchain runs fuzz/*.fcyr)
  fixtures/                     loader fixtures. loop / dangling / wrongkind
                                (zone rejection), longid.objs (a 32-byte
                                template id, the only length at which the
                                OT_ID/OI_TPL_ID cap mismatch is observable),
                                badreset + zeroreset (degenerate reset_secs)

benches/
  bench_telnet.bcyr             per-byte IAC parser cost
  bench_combat.bcyr             the combat tick, plus the 256-player
                                co-located broadcast scenario (1.6.8)
  bench_persist.bcyr            save + login: ns/op AND bump bytes/op (1.6.9)
  bench_loaders.bcyr            boot loaders + the rejected-file invariant (1.6.9)

fuzz/
  parser_fuzz.fcyr             M2-F parser fuzz harness (100k inputs);
                               `cyrius fuzz` auto-discovers fuzz/

benches/
  bench_telnet.bcyr             IAC-parser hot-path baseline (M1-G)
  bench_combat.bcyr            M4-H combat load test (32 players × 64 mobs,
                               p99 < 50 ms); `cyrius bench` runs benches/
```

Binary at `build/cyrius-yeomans-descent` — 839,816 B at 1.2.0 (753,664 text /
83,304 `.bss`). `CYRIUS_DCE=1` now makes no difference to the output size; with
the monolithic sigil bundle gone there is nothing large left for it to strip.
The `.bss` figure is the one to watch: it was **13,405,408 B** before 1.2.0
dropped the monolith, entirely x509/RSA bignum tables nothing calls.

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale
- [`../adr/0003-single-thread-event-loop-concurrency.md`](../adr/0003-single-thread-event-loop-concurrency.md) — concurrency model rationale

## Tests

`cyrius test` — **1387** unit assertions (bare form runs both the .tcyr corpus and [build].test):

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
- **persist / migration / freeze** (M6, M11) — save round-trip, wrong
  passphrase, tampered record, schema gate (missing stamp = literal v1,
  "too new" vs "tampered", signed-prefix splitting), record-writer bounds,
  the ADR 0007 frozen-surface assertions
- **reset** (M7) — mob/object top-up to the authored population, presence gate
- **login-polish / security / chpass-isolation** — re-key flow, over-long
  passphrase, forged record, `passwd` candidate isolation (1.6.4)
- **wire-hygiene** (M10) — the escaping appender, player-authored bytes,
  sanitized names, no lone IAC on the wire
- **lifecycle / actor-tick** (M12, M13) — instance free paths, corpse decay,
  MI_HOME vs MI_ROOM, the leash, the assist
- **hardening / preauth-meter / accept-limits** (1.6.0-1.6.3) — hp-vs-maxhp
  clamp, the dispatch cap and bare-CR guard, the session cap and accept backoff
- **assist-real / failure-paths / state-integrity** (1.6.4-1.6.6) — the assist
  that actually subtracts HP, loaders publishing only on success, `player_save`
  failures no longer discarded, double-login refusal, template-id round trip,
  audit-chain resume
- **rx-bounds / tick-menu-bounds** (1.7.9) — the atomic appender over its domain
  (an exact fit is written, one byte past it writes NOTHING rather than a prefix);
  no bare IAC on the wire from a full queue, at the negotiation drain and at the
  `WILL/WONT ECHO` sites; input NOT coupled to output (the livelock the first cut
  would have shipped); the room header's prose bound; the class menu; and
  `mob_swing` still landing when its prose cannot be sent
- **preauth-alloc** (1.7.8) — a wrong passphrase allocates ZERO bytes (20 attempts,
  measured against `alloc_used`), with the parse cost of the same record asserted
  as a contrast so the zero cannot pass for the wrong reason; the raw field
  scanner over its domain; the parser-differential guard, proved by a
  VALIDLY-SIGNED crafted record; the fast path falling through rather than
  refusing a record only bayan can read; and the source-level assertion that no
  raw numeric `syscall(` survives in persist/session/item
- **room-listing / listing-bounds / carry-cap-get** (1.7.6-1.7.7) — the wire is a
  correctness surface: every listing stops at a whole item with the tail reserve
  intact and reports what it omitted (`look`'s three sections, `inventory`, `who`,
  `@who`, and the `drop all` / `get all` receipts), the prompt always reaches the
  client, and the ACTION completes even when its ECHO is rationed. Plus the carry
  cap asking about what the transfer actually moves — `oi_move_count`, the
  skip-don't-abort sweep, and the two refusal messages that are each true in
  exactly one case
- **item-verbs** (1.6.7) — the `N.X` ordinal on both scans and end to end,
  `put`/`give`, the equipment verbs' honest answer, signed `toml_int`
- **reset-bounds / tick-schedule / tick-coalescing / tx-compaction / save-meter
  / hex-identity** (1.6.8) — the reset clamp, the post-work reschedule (and the
  guard against the *wrong* fix to it), one write per session per tick with no
  truncation, partial-drain compaction, the metered autosave, and hex output
  byte-identical to `lib/sigil_hex.cyr`

Fuzz: `cyrius fuzz` → **two targets**, both 100k iterations, invariants holding
and **coverage asserted by the harness itself** (1.7.17 — the parser gate had fed
a negative length on half its iterations and never reached the guard it defends):

- `fuzz/parser_fuzz.fcyr` — the M2 parser. Token/buffer bounds, index ranges, no
  `resolve_all` overrun. Reaches `NORM_CAP` ~7,988 times per run.
- `fuzz/record_fuzz.fcyr` — the **pre-auth record scanner** (`_scan_kv`), reachable
  by anyone who can open a socket and name a character that exists. ~12k matches /
  ~88k rejections, so both paths run.

**Still uncovered:** the CYML zone/class loaders. Stated rather than implied away.

End-to-end smokes validated locally on Linux x86_64 at the 0.6.0 cut:

- class selection: name → numbered class menu; pick by number or name
  prefix; invalid re-prompts; `examine me` shows the class character sheet
- abilities: class-gating ("you don't know how to hack"), energy spend,
  tick cooldowns, `bash` stun, `brace`/`stim` buffs in the condition line
- **solo verification (M5-H)**: a fresh server per class — Pikeman /
  Splicer / Courier / Chaplain each engage and kill the Foundry Sentinel
  with zero deaths (run at `YD_TICK_MS=200`)
- 0.5.0 combat / loot + 0.4.0 walk / social smokes still hold (M5 additive)

Benchmark: `cyrius bench` → **5 benches, all gated** (each asserts a budget and
exits non-zero on breach; a bench that only prints is a bench nobody reads).

- `bench_telnet` — telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte (pure
  data), 16 M iterations, stable since 0.2.0
- `bench_combat` (M4-H) — 32 players × 64 mobs through 120 real ticks,
  including per-tick `classes_upkeep`; **p99 ≈ 444 µs** at the 6.5.4 toolchain
  (was ≈ 530 µs at 6.4.86 — the 1.7.10 bump alone, no source change) against the
  50 ms drift budget. Was ≈1427 µs before 1.6.8 coalesced the tick's writes.
  This bench had **stopped compiling** before 1.2.0 (it included `server.cyr`
  without the persist prelude → `undefined variable 'DP_ROOMS'`), so the older
  ≈57 µs figure in the 1.0.x notes is not comparable — it predates both the
  persist-inclusive compilation unit and the 6.4.83 codegen.
- `bench_combat` broadcast scenario (1.6.8) — **256 players co-located in one
  room**, the population `MAX_SESSIONS` actually accepts: **p99 ≈ 27 ms**.
  Verified to FAIL at ≈81 ms with the coalescing reverted, so it is a guard and
  not just a number.
- `bench_persist` (1.6.9) — reports **bytes of bump arena per op** alongside
  ns/op, because `alloc()` has no free and RSS cannot see it. `_build_record`
  **0 B** (gated at a hard zero), `player_save` ≈1.26 ms / **1632 B** (gated at
  1750 B; the residue is libro's, see below), `player_auth_load` ≈7.7 ms /
  ≈3.9 kB. **A login is ~6× the cost of a save** — worth knowing before anyone
  designs a reconnect storm.
- `bench_loaders` (1.6.9) — boot-path loaders, plus the H9 invariant that a
  **rejected** zone file leaves nothing published. Rooms ≈207 µs / ≈285 kB,
  objs ≈49 µs, mobs ≈39 µs. The bump figures are a one-time boot cost today
  because the loaders run exactly once, from `cmd_serve` — they become a
  per-reload permanent cost at **M15 (zone registry)**, which is why they are
  measured now.
- (parser / world p99 baselines land at M9-C.)

**CI runs bare `cyrius test`, and must.** This line used to say the opposite —
that CI used the explicit `cyrius test src/test.cyr` form — which is precisely
the bug 1.2.0 fixed: `src/test.cyr` is a **no-op stub** that only has to compile
and exit 0, so CI compiled it, passed, and the real suite never ran for the whole
1.1.x line. The bare form runs both the `.tcyr` corpus and `[build].test`. See
the comment block in `.github/workflows/ci.yml`, which spells out the same thing
at the call site.

## Dependencies

Direct (declared in `cyrius.cyml`):

- **stdlib** — `std` (the built-in default group: string, fmt, alloc, io, vec, str,
  syscalls) + assert, bench, args, net, chrono, result, tagged, fnptr, freelist,
  **bayan**. The M6 crypto/store leaves (fs, process, hashmap, slice, ct, keccak,
  thread, thread_local, random, sakshi, chrono, tagged) are **not** hand-listed —
  libro's `dist/libro.deps` sidecar declares them and `cyrius deps` auto-resolves
  them in topological order, fail-loud on a missing one.
- **libro** `2.8.2` (git, `path = "../libro"`) — append-only SHA-256 hash-chain
  store (the crash-safe primitive behind "T.Ron" persistence). Pulls **sigil
  3.12.1** (Ed25519, ADR 0004 identity) + **patra 1.12.12** + **sakshi** + **bayan**
  transitively. Resolved by `cyrius deps` into `lib/` (+ `cyrius.lock`).

**bayan is a direct dep as of 1.2.0.** 6.4.83 carved `cyml`/`toml` (and earlier
`json`/`bigint`) out of the stdlib into bayan, and descent's own `world.cyr` /
`classes.cyr` call `cyml_*` — so it is a first-party need, not a libro side effect.

**sigil is included via libro's thin sub-bundles, never the monolith.** libro 2.8.0
resolves `dist/sigil-mldsa.cyr` (Ed25519) + `src/sha256.cyr` + `src/sha_ni.cyr` +
`src/hex.cyr` into `lib/`, and cyrius auto-includes them. descent's entire sigil
surface is `ed25519_{keypair,sign,verify}`, `sha256`, `hex_{encode,decode_into}` —
all six are in those bundles. Do **not** add `include "lib/sigil.cyr"` back: it
redefines all of them and costs ~13 MB of `.bss` in x509/RSA tables nothing calls.

`lib/` stays **committed** (the release tarball ships a minimal stdlib), but only
the leaves descent actually resolves. 1.2.0 pruned 12 dead ones — `cyml`, `toml`,
`json`, `bigint`, `base64`, `csv`, `u128`, `linalg`, `matrix`, `agnosys` (carved out
of 6.4.83) plus `niyama`, `yantra` (never referenced).

**The sakshi shadow gap is CLOSED (1.7.10).** It read: *sigil 3.12.1 pins sakshi
2.4.3 in its own manifest, so `cyrius deps` writes it over the synced 2.4.6; needs
a sigil-side bump.* At 6.5.4 it resolves to **sakshi 2.4.7** cleanly and no
sigil-side change was needed after all. Carried as open for five releases.

**M6 complete (0.7.0, 2026-06-09).** Full persistence shipped — see the Version
section above and `src/persist.cyr`. The dep-landing (M6-A) lesson is preserved
below because it shaped the whole milestone: the earlier "blocked on a sigil
bug" note was a **misdiagnosis**: cyrius stdlib is **opt-in, never
auto-resolved**, so
including `dist/sigil.cyr` without listing the modules its crypto calls
(`ct`/`keccak`/`thread`/`thread_local`/`random`) left those symbols
undefined — cyrius 6.1.x only *warns* and emits a `ud2`, so it built then
SIGILL'd (exit 132) the instant `sha256`/`ed25519` ran. Sigil 3.7.8's
CHANGELOG diagnosed it against this repo. (Joshua/M8 is now deferred to
post-1.0 — see the boot guide below.)

**Two things about that lesson have since changed** (both landed by 1.2.0):

1. The hand-maintained opt-in list is gone. libro's `dist/libro.deps` sidecar
   declares the leaves its fold needs and `cyrius deps` resolves them
   topologically, fail-loud. `[deps] stdlib` carries only descent's *own* direct
   surface. Don't re-add the crypto/store leaves by hand.
2. **The failure mode is no longer silent.** As of 6.4.x cyrius *refuses to emit
   a binary* with a reachable undefined function instead of emitting `ud2` and
   letting it SIGILL at runtime. The trap that cost M6 a milestone is now a
   build error — which is exactly how 1.2.0 caught `thread_local_alloc`.

## Consumers

_None yet._

## In flight

**No active cycle.** Status and the open findings are in [Version](#version)
above — not repeated here, because they were, and the two copies had already
drifted apart.

**Next: gate re-run #4.** Every finding from re-run #3 is closed (AJ-AY); the only
carried items are **AA** (16 B/connection at accept, needs a `lib/net.cyr`
decision) and **AB** (the stateless-refusal amplifier). Run it against a TAGGED
commit and let it BUILD AND RUN — that is what made #3 find three highs no
read-only pass could have. Note that 1.7.16 already built much of the
offline-population machinery #3 named as its biggest gap — which should first build the
offline-population conservation harness and the phase x tick matrix — which must be allowed to **run the suite and
the benches**, because AF survived only because a bench fixture could not reach
the code path it measures.

**Next: 1.7.0** — re-derive both per-tick line budgets from the measured worst
case and land the bench that gates a whole tick pass. Then 1.7.1–1.7.3, a gate
re-run, and only then 2.0.0 starting with **M14 — ADR 0008 + save schema v2**. Before touching M14, read the critical path in
[`roadmap.md`](roadmap.md#critical-path): records are signed with a key
re-derived from the player's passphrase, which the server never holds, so **there
is no offline migration and there cannot be one** — every 2.0 field must be
additive, defaulted, and migrated lazily at login. M11 already repaired the gate
that makes the bump safe.

**Carried, none blocking:**

- ~~**sakshi shadow warning**~~ — **closed in 1.7.10**; resolves to 2.4.7 at 6.5.4.
- ~~**Toolchain drift**~~ — **closed in 1.7.10**; the pin is `6.5.4` and matches
  the installed `cycc`. It was taken as a release of its own per the 1.2.0
  precedent, and required no source change.
- **mabda / yantra shadow** — two bundled libs `cyrius lib sync --full` does not
  actually sync. Neither is referenced by descent; a warning, not a defect.
- ~~**aarch64 epoll layout**~~ — **closed in 1.6.14.** `epoll_ev_size()` /
  `epoll_data_off()` (`src/server.cyr:111`/`:118`) now branch on the target, and
  `bench_loaders` asserts the writer and reader agree on whichever arch it runs.
  Listed here as closed rather than deleted because it sat in this list as *open*
  for two releases after it was fixed.
- **`cyrius audit` is a CI step.** If it fails on a style gate rather than a real
  defect, fix the code — do not drop the step. It is the only thing gating
  fmt / lint / docs.

---

## Next-agent boot guide

1.0.0 shipped; 1.1.x–1.5.x were maintenance, and **the whole 1.6.x line is an
audit sweep** — sixteen releases of fixes across three passes, with a fourth pass
(1.7.x) now open. The surface is still frozen
([ADR 0007](../adr/0007-frozen-1.0-surface.md)) — no new verbs / save fields /
zone fields / env knobs.

**Your next work is gate re-run #4**, not a milestone: see
[`roadmap.md`](roadmap.md#what-is-left) for every open finding and the release it
is batched into. 2.0.0 (starting with M14) is gated behind a clean gate re-run. Joshua is post-1.0 backlog, not next.

### Before you touch anything

```sh
cyrius deps && cyrius build src/main.cyr build/cyrius-yeomans-descent && cyrius audit
```

`cyrius audit` exits 0 as of 1.2.0. If it doesn't, you have inherited a
regression — fix that before starting new work. Two traps that bit 1.2.0 and will
bite again:

- **The dep chain is opt-in and order-sensitive.** A missing leaf used to build
  fine and SIGILL at runtime; at 6.4.x it is a hard `refusing to emit binary`
  error instead. Read libro's `DEPS-PATTERN.md` and its `dist/libro.deps` sidecar
  before changing `[deps]`.
- **Never re-add `include "lib/sigil.cyr"`.** See the Dependencies section.

### The old 1.0.0 checklist (kept — it is still the release drill)

1. **Adversarial pass** (extends the 0.9.0 sweep): long/binary inputs at every
   prompt; out-of-range / missing / duplicated save fields; truncated and
   over-long records; rapid connect/disconnect; idle-reap under load; a forced
   `kill -9` during combat + during a save. The `security` + `persist` test
   groups are the regression floor — add any new case you try.
2. **Full playtest** (the 1.0 gate): each class clears the Hub solo; reconnect
   restores state + room + inventory; zone resets restock an emptied Hub; the
   four classes' abilities all fire; `passwd` re-keys; `save`/`quit` round-trip.
3. **Surface conformance** — diff observable behaviour against [ADR 0007](../adr/0007-frozen-1.0-surface.md);
   nothing outside it changed. Confirm a 0.8.x save still loads (schema back-compat).
4. **Release mechanics** — `VERSION`/`cyrius.cyml`/`CHANGELOG`/`VERSION_STRING`
   to `1.0.0`; CHANGELOG closeout entry; tag is the user's job (do not commit).

### Security posture (current)

The 0.9.0 sweep fixed two heap overflows (one pre-auth), an OOB read, and a DoS
in `persist.cyr`'s load path. **Principle in force**: a record signature proves
*authorship*, not field *validity* — every loaded field is bounded (`_clamp`,
exact hex lengths, `class` range, passphrase length, `schema` ≤ current). The
`@`-admin namespace is off unless `YD_ADMIN=1`. `security`/`freeze` test groups
guard these.

### Quick boot sanity

```sh
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius test                                      # 751 assertions, all pass
./build/cyrius-yeomans-descent serve 4000
# new name → passphrase (echo-suppressed) → class → play; `save`/`passwd`/`quit`,
# reconnect → restored + "last seen". kill -9 after a save → restart → no loss.
# resets: YD_RESET_SECS=5 ...; empty the zone, watch `zone=hub reset (...)`.
# admin (opt-in): YD_ADMIN=1 ./build/... → @stats / @who / @reset.
```

### Deferred — M8 (Joshua), post-1.0

An operator interface to steer a running server (list/boot players, reload a
zone, force a reset, read counters/logs). Most hooks already exist:
`@stats`/`@who`/`@reset` (server.cyr `render_*`, behind `YD_ADMIN`),
`g_session_head` for sessions, `g_zone_last_reset_ms = 0` to force a reset, the
libro audit chain + reset log. The real work is the control channel + operator
auth (replacing the `YD_ADMIN` gate) — see [roadmap M18](roadmap.md#milestones--the-20-line). (This linked to an M8 anchor that no longer exists; the operator work was renumbered to M18 and Joshua moved to the backlog.)

### Open ADRs

None outstanding. 0001–0007 all Accepted. M8 (post-1.0) earns one if the
operator channel adds a new wire/auth surface.
