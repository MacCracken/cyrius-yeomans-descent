# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-07-29 (v1.6.12 — re-run #2 closed; the gate is still a clean re-run)
>
> Note: this file was not refreshed across the 1.1.x line (1.1.0 – 1.1.5). Those
> releases are recorded in [`CHANGELOG.md`](../../CHANGELOG.md) only; the entries
> below jump 1.0.1 → 1.2.0. Everything outside the Version log (toolchain, deps,
> tests, boot guide) describes the **current** 1.6.12 tree.

## Version

**1.6.12** — re-run #2's findings; the unmetered-work CLASS, 2026-07-29. **706
assertions**; `cyrius audit` exits 0; 5/5 benches.

The second re-run found a **critical** and a **high**, and both were the same
defect this line had already fixed three times on neighbouring paths:

> **A per-item cap is not a bound on a loop that walks many items.**

H5 (1.6.2) capped one session per readable event; E1/E2 (1.6.10) capped the
tick-side drain; F7 (1.6.11) capped the idle reap. **Nothing ever capped the
event batch** — the path that runs first and most often — and nothing capped
`passwd`, structurally identical to the two login paths that were capped.

- **The epoll event batch** *(critical)* drained 64 events × 8 lines with the
  tick-deadline check outside the loop: **4.12 s per batch**, 164% of the whole
  tick interval, from 6.6 kB of input. And ADR 0003's two loops had diverged —
  the agnos sweep had no per-pass cap of any kind (~16.5 s at MAX_SESSIONS).
  Both now call one extracted `event_batch_step`. Measured **559 ms → 17 ms**.
- **`passwd`** *(high)* derived a keypair per attacker line, unbounded: 1000
  lines = 1103 ms with the counter still at zero. Capped, but it abandons the
  re-key rather than disconnecting — the session is a real player.
- **Attacker-paced audit events** aggregated to one per session: ~755 kB/s of
  unreclaimable arena cut 5×, flood signal intact, `passwd.fail` unchanged.

**The gate is still open.** Two re-runs, two sets of serious findings the
previous pass missed. The line closes when a re-run comes back with no critical
or high findings; that has not happened, and the evidence so far says each pass
finds real defects.

**Method note worth carrying.** The fix for a repeated defect is to enumerate
the class, not to patch the report. `grep -n ident_derive src/` lists every
expensive-line path; "every loop that dispatches lines" lists every place a cap
must be aggregate rather than per-item. Both were one command away, and three
releases asked neither.

**Testing note.** Six of thirteen mutations needed the test rewritten first, and
the reasons rhyme with the bug: the first `event-budget` test **reimplemented
the batch arithmetic** rather than calling it, so three mutations passed unseen;
`EVENT_LINES_MAX` is exactly 2× `RX_MAX_LINES`, so a loop test only ever
exercises a full slice; asserting the budget *delta* cannot see a step that
charges a flat 1 per session; and the audit probe read 4096 bytes of an 8.3 MB
store, making every comparison equal — it now refuses to assert if the read
saturates.

**1.6.11** — the sweep tail, plus a corrected record, 2026-07-29. **669
assertions**; `cyrius audit` exits 0; 5/5 benches.

- **`render_who` was NOT a false positive, and 1.6.9 said it was.** The reviewer
  checked `cmd_who` — a different function three hundred lines away that has
  always bounded both ends — and published the refutation. `render_who` (the
  `@who` verb) tested only `room >= 0` before dereferencing. Fixed; the claim is
  corrected in place rather than deleted.
- **`world_start_room()` named room 0 in a zero-room world** — a valid-looking
  index into a null table, which every `room >= 0` guard downstream believed.
- **Three loaders left a stale table published** on their pre-alloc error paths.
  Measured: after a nonexistent objs file the count was still 10, mobs 4,
  classes 4 — while the caller was told the load failed.
- **Secret keys went back to the freelist unwiped** — the live `SS_IDENT` block
  and the `passwd` candidate. The 1.6.4 entry claimed the candidate was wiped in
  four places; three of the four were true.
- **The idle reap was a second unmetered signing site** in the same tick H16
  metered, reachable without an attacker (a restart puts everyone on one
  deadline).
- **`put X in <carried bag>` was one-way and then silent data loss** — the save
  never walked container contents and `obj_free` recursed through them.
- Plus: parser token lengths, the M10 sanitizer on echoed tokens, class/mob stat
  clamps, the killing blow's missing prompt, and a **false justification**
  removed from the H14 comment.

**The line is not closed until the re-run says so.** Everything the 1.6.9 sweep
produced is now fixed, but the bar is a fresh pass against the repaired tree
coming back with no critical or high findings — and the reason that bar exists
is that the first sweep declared itself finished while a remote crash sat on
`examine`.

**Testing note worth carrying.** Two harness bugs, both of which *truncated* the
run instead of failing it: a session built by `_tx_sess` has `SS_FD = 0`, so
`session_free` **closed stdin** and the suite simply stopped printing; the same
session has `SS_TS = 0`, so `telnet_state_free` dereferenced null. A test that
dies silently reads exactly like a test that passed.

**1.6.10** — sweep batch E, the re-run's findings, 2026-07-29. **636
assertions**; `cyrius audit` exits 0; 5/5 benches.

- **`MAX_LOGIN_FAILS` was enforced nowhere.** `SS_QUIT` was read on the epoll
  event path only, so a session with queued rx kept being fed 8 lines a tick
  *after* the server condemned it — ~64 ms each per tick, **~4.1 s per tick at
  64 sessions**. A cap believed live since 1.6.2. The tick tears them down now.
- **`drain_pending_rx` had no aggregate budget** — `RX_MAX_LINES` is per
  session and the walk covers all of them. **2.2 s in one tick at
  `MAX_SESSIONS`**, unauthenticated, from ~1 MB of input. Now a line budget
  shared across the walk, mirroring what H16 did for `save_sweep`.
- **Character creation had no attempt cap and no audit trail**, and **two
  sessions could create the same character** — H11 (1.6.6) covered login only,
  and the window is the whole confirm sequence, not a race. Both closed in
  `login_on_confirm`, verified live.
- **The zone reset re-minted authored objects.** Now a world-wide max-exist
  count. Closes the pre-existing relocate driver **and the one 1.6.7's `put`
  introduced** — `objs +1` per reset before, `objs +0` after.
- **An abandoned stun never decayed**, so a mob bashed and then left alone was
  inert forever. Decay moved to the actor tick and single-sourced there.

**Still open: one more re-run.** Batch E closed the critical and every high the
1.6.9 sweep produced, but the bar for closing the 1.x line is a *re-run that
comes back clean*, and that has not been done against this tree. The first sweep
declared itself finished while a remote crash sat on `examine`; a sweep that has
not been re-run has proved nothing. 1.6.11 carries the low/nit tail and that
re-run.

**Testing note worth carrying.** Twenty-two mutations, and **eight failed to
discriminate on the first pass — every one a test bug, not a dead guard.**
`var sessions[64]` is 64 *bytes* (the first line of CLAUDE.md's Key Principles,
and I still hit it); `ilist_find_kw_nth` with a zero-length noun matches nothing,
so an object test silently selected no target and skipped the branch under test,
masking three mutations at once; a budget that is a multiple of `RX_MAX_LINES`
never exercises a partial cap; and a double-decay bug is invisible without an
*engaged* mob. Separately, `create-guards` saved a record and so failed on its
own second run — a test that is not idempotent is a landmine.

**1.6.9** — sweep batch D, coverage + the re-run, 2026-07-29. **581 assertions**;
`cyrius audit` exits 0; 5/5 benches.

- **`examine <anything>` was a remote crash** on a zone-less server — a
  configuration the server explicitly supports and logs. `room_at(-1)` computes
  `g_rooms + (-1 * RM_SIZE)`; every other room-touching verb checks
  `world_room_count() == 0` first and `cmd_examine` did not. Reproduced live
  (process dead), fixed, re-verified live (process alive, every variant answers).
  **The 1.6.0 sweep missed this entirely.**
- **1.6.8 delayed `say` by up to a full tick** — measured **2099 ms → 0 ms**.
  H15's coalescing was right for the tick's quadratic burst and wrong for
  commands, which arrive on the epoll path. The event path now drains the dirty
  set too; no syscalls given back.
- **`bench_persist` + `bench_loaders`** close the save / login / loader blind
  spots, reporting **bump bytes per op** as well as ns/op. Both verified to fail
  when what they guard is reverted. New number worth knowing: **a login costs
  ~6× a save** (≈7.7 ms, ≈3.9 kB) — which is what makes the uncapped
  creation-attempt path in batch E legible.
- **Docs sweep.** `state.md` had been documenting `cyrius test src/test.cyr` as
  CI's form — the exact bug 1.2.0 fixed. Plus 17 missing test groups, a 3×-stale
  bench figure, a wrong struct size, and five source comments linking to a
  roadmap anchor that no longer exists.

**The 1.x line did NOT close.** The re-run's whole purpose was to test whether it
could, and the answer is no: several findings survived adversarial verification,
including two rated critical. They are filed as **batch E (1.6.10)** on the
roadmap. The two fixed here are the ones that were a live crash and a live
regression.

**What the re-run actually established.** Not "the finding count fell" — the
first sweep's count was never a measure of what was there, since it missed a
remote crash on a first-class verb. What it established: every fix from batches
A–C is still in place (the regression dimension re-checked each CHANGELOG claim
from 1.6.0 onward), and the new findings cluster where the first sweep had no
instrument. Batch D is where those instruments got built.

**1.6.8** — sweep batch C, resource + timing hygiene, 2026-07-28. **573
assertions**; `cyrius audit` exits 0; `--agnos` warning-free.

- **Room broadcasts were quadratic in `write(2)`** — 2E² − E per tick for E
  co-located engaged players, measured at **81.4 ms p99 at 256 players, 163% of
  the ADR 0001 budget in a single tick**. Now one write per session per tick:
  **28.3 ms**. 128 players went 20.1 → 7.0 ms, 32 went 1.31 → 0.53 ms.
- **The obvious version of that fix silently truncates.** `TX_CAP` is 4096 and
  `session_appendtx` drops the overflow through a return value nobody reads, so
  a whole tick's coalesced prose overflows at **36** co-located players. Shipped
  with a capacity valve plus a partial-drain compaction; only the *write* was
  ever deferred, never the append.
- **`save_sweep` signed every dirty session in one tick** — 41 ms at 32, **332 ms
  at 256**. Invisible to `@stats`, because the schedule is absolute and a
  sub-interval overrun is absorbed by the next `epoll_wait` timeout: the tick was
  not late, it was gone for a third of a second. Metered to 4 saves/tick.
- **The tick snap-forward read a pre-tick clock** — a schedule bug, not the
  measurement bug it was filed as. The drift metric was already right, and
  "fixing" it the filed way would corrupt a frozen `@stats` field; there is a
  test that fails anyone who tries.
- **`_build_record` leaked 248 B of bump arena per save.** Now zero.
- **`reset_secs` had no floor and an unchecked `× 1000`** — clamped. 1.6.7's
  signed-`toml_int` change had opened a fresh path into it.

**Two residuals, both recorded on the roadmap rather than closed:** `parse_uint`
still wraps silently (folded into M14-D), and **~1632 B/save of bump arena is
inside libro** — `filestore_append` rebuilds a `str_builder` per append — which
needs an upstream 2.8.5, the same shape as the 1.6.1 chain fix. The per-save
growth is reduced, not stopped.

**A second testing note, from CI.** `save_sweep_due` shipped relying on `now - 0`
being bigger than five minutes for a never-saved session. `clock_now_ms()` is
**`CLOCK_MONOTONIC` — ms since boot**, so that is a claim about the host's
uptime, and it is false on a fresh one: every character created in the first
five minutes of uptime would have skipped the autosave. Only CI has an uptime
that short, which is exactly why it caught it. Timing tests here now use
synthetic clock values; a test that reads the real clock is measuring the
machine, not the code.

**Testing note worth carrying:** the mutation that makes the new hex encoder emit
uppercase — which would make every save record on disk fail its own signature —
**passed a test whose comment claimed it covered "every byte value"**. The probe
held all 256 values but only ever encoded the first 64, so the high nibble never
reached 10 and the `a`-`f` branch never ran. A test that claims coverage it does
not have is worse than no test; only mutating the constant and watching nothing
happen surfaced it.

**1.6.7** — sweep batch B, content + parser correctness, 2026-07-28. **500
assertions**; `cyrius audit` exits 0; `--agnos` warning-free.

- **The `N.X` qualifier was parsed everywhere and honoured nowhere.** `qual_parse`
  has returned `QUAL_NTH` since M2-E and every caller dropped the count, so
  `get 2.ration` took the first and `kill 2.scavver` searched for a mob whose
  keywords are spelled "2.scavver". Both scans are ordinal-aware now
  (`ilist_find_kw_nth`, `mob_in_room_by_kw_nth`) and `qual_single` folds a token
  down for every one-target verb. Unqualified nouns still resolve to ordinal 1,
  so it is additive against the frozen surface.
- **`put` and `give` answered the M2 placeholder** — *"the Under-Grid is empty —
  items arrive at M3"* — four releases after M3 shipped. Both implemented.
  `put` nests one level deep on purpose: `obj_free` recurses through
  `OI_CONTENTS`, so depth 1 plus a self-containment guard makes unbounded stack
  and cycles impossible by construction.
- **`wear` / `remove` / `wield` now say why they cannot.** Still unimplemented —
  there are no equipment slots, and adding a wear-flag field is a zone-format
  change 1.x cannot make. That is **M17 (2.1.0)**, and the verbs now say so
  instead of claiming the world is empty.
- **`bash` and `emp` described a corpse.** Both printed their stun prose after a
  killing blow. `ability_strike` reports the kill; both callers gate on it.
  Verified *not* a UAF — every ability sets the stun before the strike.
- **`toml_int` accepts a sign** (closes backlog **B7**, and **M14-C** early).

**Carried forward on purpose:** the batch-B finding also asked that `toml_int`
reject garbage instead of silently defaulting. It does not, and 1.6.x will not
change that — rejecting a value rejects zone files that load today, and ADR 0007
§5 freezes the zone format for all of 1.x. Strictness needs a format version to
hang off; folded into **M14-D**, not a later 1.6.x batch.

**1.6.6** — sweep batch A, state integrity, 2026-07-28. **448 assertions**;
`cyrius audit` exits 0; `--agnos` warning-free.

- **Double login duplicated a whole inventory** and raced the save file — the
  stale session's `player_save` reverted the live one's room, drops, HP and
  class. `session_already_online` refuses the newcomer after auth.
- **A 32-byte template id could not round-trip** into an instance, so it could
  never match its own template on reload — and inventory persists *by id*.
- **The audit chain restarted at genesis every boot**, so the durable chain had
  a broken link at each restart boundary, indistinguishable from deletion.
  Verified end to end: 0 breaks with the fix, 2 without, across three processes.

**Testing note worth carrying:** two of the first three mutations here did not
discriminate, and both were **test** bugs — a real Hub id is too short to expose
the truncation, and hand-writing the copy in the test bypassed the line under
test. The fix is to drive the real loader over a purpose-built fixture. A
mutation that fails to fail is a signal about the test, not the code.

**1.6.5** — loader + save-failure integrity, 2026-07-28. **431 assertions**;
`cyrius audit` exits 0; `--agnos` warning-free.

- **Four content loaders published their globals before validating.** A rejected
  file left a live half-table, so `cmd_serve` reported the failure while every
  `world_room_count() == 0` guard downstream was defeated at the same instant —
  a player could log in and be stranded in whatever prefix parsed. Three now
  publish on success only; `world_load_rooms` cannot (it is two-pass and pass 2
  walks the count), so its eight error returns route through `_wl_rooms_fail`.
- **`player_save` failures were discarded at four of five sites**, including the
  `passwd` commit — which claimed the record was re-keyed while the on-disk copy
  kept the old pubkey. Now checked, with a rollback of the live ident block, and
  the rest audit their failures.

**Next: the sweep is not finished.** Batch E (**1.6.10**) carries what the
1.6.9 re-run turned up — an unbounded per-tick drain budget, a `MAX_LOGIN_FAILS`
cap that is not actually enforced, an uncapped character-creation path, and a
duplicate-identity hole on CREATE that 1.6.6 closed only for login. See [`roadmap.md`](roadmap.md#sweep-backlog--the-remaining-16x-batches).
**2.0 / M14 does not start until 1.6.9 lands** and a re-run sweep produces no
critical or high findings.

**1.6.4** — `passwd` isolation + the assist made real, 2026-07-28. **420
assertions**; `cyrius audit` exits 0; `--agnos` warning-free.

- **The `passwd` candidate lived in `g_persist_dec`**, a global that
  `player_auth_load` decodes into and `_build_record` signs into — held across a
  network round trip. Any interleaved save or login destroyed it, including a
  *failed* login against any account. On a passphrase collision it installed 64
  signature bytes as the secret key: permanent character loss plus a false
  `SEV_SECURITY "load.tamper"` entry. Now a per-session `SS_IDENT_CAND` block,
  wiped and freed on commit, both rewinds, and `session_free`.
- **The M13 assist was prose.** It set `MI_TARGET` and printed a line; nothing
  swung, because the only HP-subtracting line is driven by the *player's*
  target. And the latch froze the mob out of wander permanently, since it was
  never attacked and so never fell below the flee threshold. Reaping stale
  latches restores wander; `mob_swing` makes the feature real. The 1.5.0
  changelog claim is now true.

**1.6.1** — audit-chain bound, via upstream libro 2.8.4, 2026-07-28. **388
assertions**; `cyrius audit` exits 0; `--agnos` warning-free.

descent's in-memory audit chain grew forever and could not be bounded from here.
libro 2.8.4 adds `chain_new_streaming()`: entries link exactly as before — the
durable chain verifies identically — but none are retained, only the head hash.
descent is a pure write-through consumer (it never reads the chain), so this is
the right shape.

**Measurement note, worth keeping:** RSS does **not** move (+624 kB vs a +636 kB
baseline) and is the wrong instrument. Entry `Str`s come from the bump allocator,
which has no free, and freelist memory is never returned to the OS. What was
removed is the *unbounded* term — a vec slot and an 88-byte struct per event.
`chain_len` is the honest instrument. The `Str` residue needs an allocator-level
fix and is recorded upstream.

Also: the 1.6.0 hardening fixes were retagged **M14-A/B/C → H1/H2/H3** — `M14`
already belongs to the 2.0 contract, and two different M14-Cs existed in one tree.

**1.6.0** — hardening sweep, closing the 1.x line, 2026-07-28. Toolchain
`6.4.83` → **`6.4.86`**, libro `2.8.2` → **`2.8.3`**. **385 assertions**;
`cyrius audit` exits 0; `--agnos` warning-free; p99 **1299 µs**.

Three fixes, each mutation-verified:

- **A use-after-free 1.5.0 activated.** `drop_session` never cleared mobs'
  `MI_TARGET`, which was harmless while that field was only ever *compared* —
  until M13's `_mob_assist` started dereferencing it. `fl_free` recycles the
  block into the next `session_new`, so the read could land on a live, different
  player. New `mobs_forget_session`, the mirror of `sessions_forget_mob`.
- **Inventory leaked at disconnect** — `session_free` never touched `SS_INV`.
  Remotely driven and unbounded. Safe to free because saves store inventory by
  template id, not by instance.
- **`hp` was never clamped against `maxhp`**, and nothing downstream lowers it.
  The 0.9.0 rule extended to *relational* invariants.

**Measurement note worth keeping:** RSS cannot show the leak fix — `fl_free`
never `munmap`s, so a 41-login soak reads +636 kB before and after. Use
`g_mob_live` / `g_obj_live`.

**1.5.0** — M13, the actor tick, 2026-07-28. **373 assertions**; `cyrius audit`
exits 0; host and `--agnos` warning-free; p99 **1338 µs** against the 50 ms
budget, so mob agency is not measurable at Hub scale.

Mobs were furniture. They now take a turn each tick: pace, join a room-mate's
fight, or break off below 20% HP. Two things the milestone did not anticipate,
both load-bearing:

- **Wander needs a leash.** The first live run walked the Foundry Sentinel —
  authored into `foundry.overseer` — the length of the zone and into `hub.gate`,
  the newbie start room. A roaming population diffuses evenly and erases the
  authored difficulty curve. Mobs are now bounded to within one room of
  `MI_HOME`. The proper per-template "does not roam" flag is a `kind = "mob"`
  key and therefore frozen surface — M19's, not 1.x's.
- **The zone reset had to change first.** Respawn counted mobs *standing in* a
  room, so a mob that wandered off left a deficit and every reset spawned a
  replacement — population climbing by one per reset, forever. `_mob_alive_count`
  now counts by `MI_HOME`.

`mob_unlink` is split from `mob_remove` (wander relinks; retire frees).
Conflating them double-frees on every move, which does not fail a test — it
corrupts the freelist into an infinite loop.

**1.4.0** — M12, instance lifecycle, 2026-07-28. **346 assertions**; `cyrius
audit` exits 0; host and `--agnos` warning-free; `bench_combat` p99 1422 µs
against 1427 µs before, so the new per-tick corpse sweep is not measurable.

The milestone under-stated its own problem. `alloc()` has **no `free()`** — it is
a bump allocator — so this was never "add a reclaim path": mob, object and corpse
instances had to *move* onto `fl_alloc`/`fl_free`, the only reclaiming allocator
descent has. `fl_alloc` reuses freed blocks **without zeroing**, which the old
bump-allocated code silently depended on, so `mob_spawn` now memsets.

Corpses were the worse half: never removed from a room at all. They now decay
after `CORPSE_TICKS = 120` (~5 min), taking un-looted contents with them.
Hardcoded on purpose — a `YD_CORPSE_TICKS` knob would be an ADR-0007 §6
frozen-surface change and belongs to 2.0.

The use-after-free trap was real and landed first: `mob_died` cleared only the
*killing* session's `SS_TARGET`, so a second attacker kept a pointer. Inert
precisely because nothing was reclaimed; the first free would have resolved it
to a live, *different* mob, since `fl_free` returns the block to a size class the
next `mob_spawn` re-issues.

**1.3.0** — the 1.3.0 pair, 2026-07-28. **M10 (wire-safe prose)** and
**M11 (migration-gate repair)**. Suite 298 → **333 assertions**; `cyrius audit`
exits 0; host and `--agnos` both build warning-free.

M10 fixed the one *live* defect: `telnet_feed` decodes `IAC IAC` to a literal
0xFF (correct RFC 854), `session_push_line_byte` drops only `b < 32` so it
survived, and `cmd_say` handed it straight to every listener — a player could
inject a bare Telnet command byte into another player's protocol stream. New
`session_appendtx_prose` doubles 0xFF and drops C0/DEL, and is a *bounded*
writer: `LINE_CAP` and `TX_CAP` are both 4096, so a full line of 0xFF escapes to
8192 and a truncation between a pair would re-create the defect. Verified
end-to-end with two real clients — before `AA\xffBB`, after `AA\xff\xffBB`.
C1 (0x80-0x9F) is deliberately kept: those are UTF-8 continuation bytes.

M11 repaired four latent defects in the save migration gate, each of which would
otherwise have shipped *with* the 2.0 bump it protects — see the CHANGELOG.
Worth carrying forward: **M11-A is unprovable until M14.** While
`SCHEMA_VERSION == 1` the old and new missing-stamp defaults agree, so its test
is a pin, not a proof. Same shape for M11-C and M11-D: they guard surfaces v1
cannot reach, so both are unit-tested directly — an end-to-end test passes
against the unfixed code and proves nothing.

**1.2.0** — toolchain + dep upgrade and the first clean audit, 2026-07-28. Cyrius
`6.3.32` → **`6.4.83`**, libro `2.7.10` → **`2.8.2`** (sigil **3.12.1**, patra
**1.12.12**, sakshi, bayan transitively). No observable game-surface change — the
frozen 1.0 surface ([ADR 0007](../adr/0007-frozen-1.0-surface.md)) holds.

`main` **did not build** at the 1.1.5 tag: cyrius 6.4.65 replaced hardcoded
thread-local slot indices with a `thread_local_alloc()` allocator, sigil 3.12.1
calls it, and the committed `lib/thread_local.cyr` predated it — and 6.4.x
*refuses to emit* on a reachable undefined function rather than emitting `ud2`.
Re-vendoring at the new pin fixed it.

Three further defects the upgrade exposed, all now fixed:

- descent included the **monolithic `lib/sigil.cyr`** on top of the thin
  capability sub-bundles libro 2.8.0 resolves — redefining every symbol and
  dragging in unused x509/RSA bignum tables. **Static data 13.4 MB → 83 KB
  (.bss), duplicate-symbol warnings 267 → 0.**
- `cyml`/`toml` **left the stdlib** (carved into bayan); the stale committed
  copies shadowed bayan's, so the zone/class loaders ran on whichever
  `cyml_parse` the include order picked. `bayan` is now a direct dep.
- the parser's `MAX_TOKENS` **collided** with patra's `MAX_TOKENS = 128` in
  Cyrius's flat enum namespace → renamed `PA_MAX_TOKENS`.

Two more defects the audit turned up, both independent of the upgrade:

- **CI never ran the tests.** The step was `cyrius test src/test.cyr`, and
  `src/test.cyr` is a no-op stub — CI compiled it, exited 0, and the
  298-assertion suite never executed. Fixed to bare `cyrius test` (+ an
  `cyrius audit` step). Every green CI run before 1.2.0 was silent about tests.
- **`player_exists()` was wrong on agnos** — `sys_stat`'s *arity* differs by
  target (agnos `(path, pathlen, statbuf)` vs `(path, buf)`), so the statbuf
  pointer landed in `pathlen`. That branch decides returning-player vs.
  character-creation. `--agnos` had been warning; the host build could not see it.

Also: `benches/bench_combat.bcyr` had stopped compiling (missing the persist
prelude → `undefined variable 'DP_ROOMS'`); `VERSION_STRING` had silently drifted
to `1.1.3`, two releases behind; `signal_ignore(SIGPIPE)` added as hardening (see
the CHANGELOG for its honest, unreproduced scope); 12 dead leaves pruned from the
committed `lib/`. **`cyrius audit` now exits 0** — 298 tests, 3/3 benches, fmt +
lint + docs clean (111 public fns documented), host and agnos both building
warning-free. See [CHANGELOG 1.2.0](../../CHANGELOG.md).

**1.0.1** — gateway-verified maintenance, 2026-06-10. No observable change from
1.0.0 — the frozen 1.0 surface ([ADR 0007](../adr/0007-frozen-1.0-surface.md))
holds (no new verbs / save fields / zone fields / env knobs; no source change).
Records Yeoman's Descent as the verified target of the **agora Descent link**
(agora 1.4.0, its ADR 0017): agora bridges a logged-in citizen here as a
*transparent TCP byte-proxy*, so the MUD's own telnet negotiation + Ed25519
login flow through unchanged — the MUD authenticates the player itself. Sigil
identity hand-off from agora is **deferred** (needs an external-identity path the
frozen surface doesn't expose — a future two-repo bite). Verified end-to-end by
agora's `20-descent.sh` smoke. Toolchain pin 6.1.23 (unchanged); tests unchanged
and green.

**0.9.1** — surface freeze, 2026-06-10. The public surface is enumerated and
locked for 1.0 ([ADR 0007](../adr/0007-frozen-1.0-surface.md)): command verbs +
`@`-namespace, save-record schema v1, Telnet/wire behaviour, zone format, env
knobs. Save records now stamp `schema = 1` (signed); the loader rejects records
newer than `SCHEMA_VERSION` and reads 0.7.0–0.9.0 (no `schema`) as v1 — the
post-1.0 migration hook. The `@`-admin namespace (`@stats`/`@who`/`@reset`) is
gated behind `YD_ADMIN` (default off): disabled → unknown commands, hidden from
`help`; operator auth stays deferred to M8. **Behaviour change**: `@stats` now
needs `YD_ADMIN=1`. 298 tests pass; admin gate live-verified both ways.

**0.9.0** — security sweep, 2026-06-10. A CVE-informed audit of the
network-input + save-file surface. Four issues found and fixed, all reachable
from a raw TCP connection or a planted save: two heap overflows (`ident_derive`
copied the passphrase using the raw line length — **pre-auth**; `player_auth_load`
hex-decoded `salt`/`pubkey`/`sig` with no length bound **before** signature
verification), an OOB read (unvalidated `class` index → `g_classes + cls*CL_SIZE`),
and a DoS (unvalidated `ndice` → unbounded `roll()` loop). Root cause: a save's
Ed25519 signature proves its *author*, not its field *values*, so every loaded
field is now bounded/validated. Ed25519 malleability (CVE-2020-36843 class) was
researched and judged non-applicable (integrity use, not uniqueness; verifier is
vendored sigil). 293 tests pass (9 new `security`); remote pre-auth vector
live-verified non-crashing. Pin → 6.1.23.

**0.8.3** — operator verbs, 2026-06-10. `@who` lists in-world sessions (name +
room) and `@reset` forces an immediate zone reset (idempotent top-up, re-arms
the timer, logs it) — read-only Joshua groundwork (`render_who`/`render_reset`
in server.cyr). The `@`-namespace is still unguarded; M8 adds operator auth.
284 tests pass; live-verified.

**0.8.2** — content patch, 2026-06-10. The Hub gets lived-in: six new flavor/
loot object templates (notice, tankard, ration, ingot, optic, shrine-token) and
`objects =` spawns across 11 rooms (13 objects) give M7-D's object respawn
something to act on — ambient loot renders on `look` and restocks on each zone
reset. Content-only; 284 tests pass, boot spawns 13 objects.

**0.8.1** — login/identity polish, 2026-06-10. Passphrases no longer echo
(server sends `IAC WILL/WONT ECHO` around every passphrase prompt — login,
new-character, and the new `passwd` verb), so conformant clients hide the
keystrokes (the deferred ADR-0004 item). Returning players get a `Last seen N
ago` greeting from the record's prior `last_login`. The `passwd` verb re-keys a
character in-world (fresh salt + new passphrase → new Ed25519 identity, re-signed
+ saved, audited; old passphrase dies immediately) via two echo-suppressed phases
`PHASE_CHPASS_NEW`/`_CONFIRM`. 284 tests pass; live-verified (echo bytes + passwd
+ last-seen + old-pass rejection). No new milestone. Toolchain pin → 6.1.22.

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

- **Cyrius pin**: `6.4.83` (`cyrius.cyml [package].cyrius`)

Two toolchain quirks at 6.4.83, worked around rather than fixed here:

- `cyrius fmt -w <file>` does **not** write. Capture `cyrius fmt <file>` on stdout
  instead. Flag order also differs per tool: `cyrius fmt <file> --check`, but
  `cyrius doc --check <file>` — and `doc` writes its findings to **stderr**.
- `cyrius lib sync --full` reports a full 99-file snapshot while leaving
  `niyama.cyr` / `yantra.cyr` untouched. Moot here (both pruned as unused).

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
  cyrius-yeomans-descent.tcyr   unit suite (706 assertions, 38 groups)
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

`cyrius test` — **706** unit assertions (bare form runs both the .tcyr corpus and [build].test):

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
- **item-verbs** (1.6.7) — the `N.X` ordinal on both scans and end to end,
  `put`/`give`, the equipment verbs' honest answer, signed `toml_int`
- **reset-bounds / tick-schedule / tick-coalescing / tx-compaction / save-meter
  / hex-identity** (1.6.8) — the reset clamp, the post-work reschedule (and the
  guard against the *wrong* fix to it), one write per session per tick with no
  truncation, partial-drain compaction, the metered autosave, and hex output
  byte-identical to `lib/sigil_hex.cyr`

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

Benchmark: `cyrius bench` → **5 benches, all gated** (each asserts a budget and
exits non-zero on breach; a bench that only prints is a bench nobody reads).

- `bench_telnet` — telnet_feed ≈ 6 ns/byte (mixed), ≈ 5 ns/byte (pure
  data), 16 M iterations, stable since 0.2.0
- `bench_combat` (M4-H) — 32 players × 64 mobs through 120 real ticks,
  including per-tick `classes_upkeep`; **p99 ≈ 525 µs** against the 50 ms drift
  budget. Was ≈1427 µs before 1.6.8 coalesced the tick's writes.
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

**Known upstream gap**: `cyrius build` warns that `./lib/` shadows the pinned
toolchain lib for **sakshi 2.4.3 (pinned 2.4.6)** — sigil 3.12.1 pins 2.4.3 in its
own manifest, so `cyrius deps` writes it over the synced 2.4.6. Needs a sigil-side
bump; no functional impact observed.

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

**No active cycle.** The tree builds, `cyrius audit` exits 0, and **706
assertions + 5 benches** pass.

**The 1.x line is NOT closed.** M10–M13, the 1.6.0 hardening sweep, and sweep
batches A–E plus two tails (1.6.6–1.6.12) are all shipped, and every one of the original 44
verified findings is closed and re-verified as still closed. But batch D's last
item was to **re-run the sweep**, and it found a remotely-triggerable crash the
first pass had missed (`examine` on a zone-less server) plus a regression 1.6.8
had introduced. Both were fixed in 1.6.9, and batch E (1.6.10) closed the critical plus every
high. What remains is the low/nit tail and, decisively, **a re-run that comes
back clean** — which has not happened yet.

The exit criterion: **a re-run sweep producing no critical or high findings.**
Batch E is landed and the audit is green; the re-run is 1.6.11's job. **2.0 /
M14 does not start before that.**

**One item is parked for upstream:** ~1632 bytes of bump arena per save (and
~3.9 kB per login), inside libro's `chain_append` / `filestore_append` —
`filestore_append` rebuilds a `str_builder` from scratch on every append, and
`hasher_new` / `sha256_init` never `fl_free`. `alloc()` has no free, so it is
permanent. Needs a **libro 2.8.5**, the same shape as the 1.6.1 fix. Descent's
own share went to zero in 1.6.8 and `bench_persist` now gates it, so a
reintroduced descent-side allocation trips the audit gate rather than a soak.
(The *previous* parked item — the unbounded in-memory audit chain — was closed
upstream in libro 2.8.4 and consumed in 1.6.1.)

Next is the **re-run sweep** — the last gate — then **2.0.0** starting with
**M14 — ADR 0008 + save schema v2**. Everything
else in the 2.0 line routes through it. Before touching it, read the critical
path in [`roadmap.md`](roadmap.md#critical-path); the binding constraint is that
records are signed with a key re-derived from the player's passphrase, which the
server never holds, so **there is no offline migration and there cannot be one** —
every 2.0 field must be additive, defaulted, and migrated lazily at login.
M11 already repaired the gate that makes the bump safe.

**M8 (Joshua) moved to the backlog**: it was blocked on an upstream Cyrius port,
and specced against a management CLI that turned out to be an AI-NPC simulation
runtime. The operator work worth doing — real operator auth replacing the
`YD_ADMIN` gate — is M18 and does not depend on it.

The full 2.0 line (M10–M23, with M14+M15+M16 as the minimum credible 2.0) is in
[`roadmap.md`](roadmap.md#milestones--the-20-line). Pick up per the boot guide below.

Carried forward from 1.2.0 (none block a release):

- **sakshi shadow warning** — sigil 3.12.1 pins sakshi 2.4.3 while the 6.4.83
  toolchain bundles 2.4.6. Fix is a sigil-side bump; nothing to do here. This is
  the only warning `cyrius build` still emits.
- **aarch64 epoll layout** — `src/server.cyr` hardcodes the x86 *packed*
  `epoll_event` (`EPOLL_EVENT_SIZE = 12`, data at +4). aarch64 Linux uses the
  unpacked 16-byte layout with data at +8. Not hit today (descent is built and run
  x86_64/agnos), but it will corrupt the session pointer the first time someone
  builds `--aarch64` and runs it. Worth an `#ifdef` before any ARM target lands.
- **`cyrius audit` is now a CI step.** If it starts failing on a style gate rather
  than a real defect, fix the code — don't drop the step; it is the only thing
  gating fmt / lint / docs.

---

## Next-agent boot guide

1.0.0 shipped, and 1.1.x / 1.2.0 have been maintenance releases on top of it. The
surface is still frozen ([ADR 0007](../adr/0007-frozen-1.0-surface.md)) — no new
verbs / save fields / zone fields / env knobs — so **M8 (Joshua) is the next real
milestone**, and it is the thing that earns the right to extend the surface.

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
cyrius test                                      # 706 assertions, all pass
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
