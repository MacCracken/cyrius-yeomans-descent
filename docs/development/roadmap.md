# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-07-29 (v1.7.5 — ground decay shipped; the 1.6/1.7 audit line is clear bar one low item, then the gate re-run)
>
> **This file is the remaining work.** It opens with
> [What is left](#what-is-left) — every open item, assigned to a release, worst
> first. History is below that and clearly marked as history.
>
> Per-tag chronology: [`../../CHANGELOG.md`](../../CHANGELOG.md). Live tree state
> (versions, deps, layout): [`state.md`](state.md). Design:
> [`../architecture/overview.md`](../architecture/overview.md). ADRs:
> [`../adr/`](../adr/).

---

## What is left

Everything not yet done, in the order it should happen. Nothing below is
"probably fine" — each item links to a full write-up with impact, reachability,
ownership and fix size.

| # | Next | Items | Contains | Blocks 2.0? |
|---|---|---|---|---|
| — | ~~1.7.0~~ | ~~2~~ | ✅ **Shipped.** The tick budget becomes a budget — the auth reorder, the charge window, the drain re-arm, the teardown charge, and the bench that should have caught it | — |
| — | ~~1.7.1~~ | ~~3~~ | ✅ **Shipped.** Bound what the reconnect rate sets — the audit rollup window, `passwd`'s rate limit, ADR 0009, and a live audit-log integrity bug found on the way | — |
| — | ~~1.7.2~~ | ~~5~~ | ✅ **Shipped.** The carry cap becomes a bound (both halves) · operator config + account cap · sharded player records · ADR 0007 amended. Found the defect class recurring inside 1.7.1's fix for it | — |
| — | ~~1.7.3~~ | ~~4 of 6~~ | ✅ **Shipped.** `cmd_give`'s overshoot · the per-tick save-failure retry · the two uncovered guards · the borrowed audit chain-link | — |
| — | ~~1.7.4~~ | ~~1 of 3~~ | ✅ **Shipped.** Audit-log rotation (ADR 0009 mechanism), incl. the crash window, the prune attestation, and the clobber guard | — |
| — | ~~1.7.5~~ | ~~1 of 2~~ | ✅ **Shipped.** Ground decay — player-dropped items expire after two zone-reset intervals (30 min). The last item of the 1.6/1.7 audit line | — |
| 1 | [**1.7.6**](#173--cover-the-guards-that-predate-the-mutation-habit) | 1 | Restore 1.6.12's audit granularity, now affordable under the rollup window | no |
| 3 | [**gate re-run**](#the-gate--what-closes-the-1x-line) | — | Closes the 1.x line if it returns no critical or high findings | **yes** |
| 4 | **2.0.0** | 4 | [M14](#m14--adr-0008-and-save-schema-v2-v200) contract + schema v2 · [M15](#m15--zone-registry-and-the-entry-cap-v200) zone registry · [M16](#m16--xp-levels-and-a-death-cost-v200) XP/levels/death · [broadcast fan-out](#20--bound-the-broadcast-fan-out) | — |
| 5 | 2.1.0 – 2.4.0 | 7 | [M17–M23](#m17m23--the-2x-tail), the 2.x tail | — |

**Every issue the 1.6.0 sweep and its two re-runs produced is closed** — 1.6.0
through 1.6.15. The **third (gate) sweep found 8 items, two of them high**;
**1.7.0 closed both highs** plus three findings the sweep's design work turned up
that were not in the original 8. The rest are below.

**1.7.0 also corrected two errors in this file.** The "252 ms = 504% of the
ADR 0001 drift budget" headline conflated tick-body cost with work that delays a
scheduled tick, and cited a number ADR 0001 did not contain. Both are fixed, and
the number now lives in [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md)
where the gates can agree on it. The defect was real — the drift-relevant
quantity was ~247 ms against a 50 ms allowance, now 4 ms — but the arithmetic
behind the headline was loose in the same way as the comment it indicted.

**The minimum credible 2.0 is M14 + M15 + M16** — the contract, the content
ceiling, and progression. Everything from M17 on can slip without embarrassing
the release.

---

## Open issues — 8 raised by the gate sweep; 6 closed (1.7.0–1.7.2); 2 open, +10 raised by these three releases' own investigations

From the third (gate) sweep, 2026-07-29, run against 1.6.15. Worst first. Every
item says what breaks, whether it can happen to a running server today, whose
code it is, and how big the fix is — in that order, before any label.

### ✅ 1.7.0 — the tick budget becomes a budget (SHIPPED)

Issues A and B below are **closed**. Kept in place rather than deleted, because
the reason A survived three sweeps is the more useful record than the fix.

**What shipped, and what it measured.** The drift-relevant quantity went from
**~247 ms to 4 ms**; a wrong passphrase from **8006 µs to 1066 µs**. Five changes:
the auth-path reorder (stop calling `ed25519_verify` when the answer cannot
matter), the charge window (bound by counted crypto, not by a line count), the
drain moved into both loop bodies with a `g_rx_backlog` re-arm, a charge on
condemned-session teardown, and `bench_tick_budget.bcyr`. 821 assertions
(from 751); all 13 new guards mutation-verified, two of which **survived the
first mutation pass and exposed gaps in my own tests** before being closed.

**Three findings 1.7.0 raised that the sweep had not.** Fixed in it, listed
because they were not in the 8:

1. *The auth path paid for an answer it could not use* — a 7.5× cut on the
   costliest unauthenticated line, and nobody had looked at the order.
2. *Refused lines waited up to 2500 ms* — `session_on_readable_max` drains the
   socket to EAGAIN before the line cap is consulted, so epoll never re-fires for
   the retained bytes. The comment claiming otherwise was wrong. **This is why
   this file's own scoping of issue A — "two constants, and a comment. Small." —
   was refuted:** lowering a count budget was never throughput-free.
3. *The condemned-session teardown was unbudgeted* — 81 ms measured at 64 authed
   drops, ~325 ms projected at MAX_SESSIONS, in the very function E2 added a
   budget to. Both the line budget and the charge window *looked* like they
   covered that walk.

**A. Both per-tick line budgets are sized against the wrong worst case, and the
server blocks for 252 ms in one pass — 5× the drift budget.** *(high — CLOSED in
1.7.0; the headline arithmetic is corrected above)*

- **What breaks.** [ADR 0001](../adr/0001-tick-based-combat.md) allows 50 ms of
  p99 tick drift. One pass with every budget at its cap costs **252 ms** —
  **504% of that**, and 10% of the entire 2.5 s tick. Everyone's combat round,
  regen, and prose stalls for a quarter second.
- **Can it happen today? Yes, and it needs no account.** Sixteen connections each
  sending two wrong passphrases does it. The attacker needs one name that
  exists — a wrong passphrase against a *real* name is the expensive path,
  because that is the one that pays a full `ed25519_verify`.
- **Whose code.** Ours. `DRAIN_LINES_MAX` and `EVENT_LINES_MAX` in
  [`src/server.cyr`](../../src/server.cyr).
- **Fix size.** Two constants, and a comment that states a false premise. Small.
- **Measured** (`alloc_used` + `clock_now_ns`, 16 sessions in `PHASE_PASS`
  against a real record):

  | | cost | of the 50 ms budget |
  |---|---|---|
  | `drain_pending_rx` at cap (tick side) | 121 ms | 243% |
  | `event_batch_step` at cap (**before** the tick check) | 121 ms | 242% |
  | `save_sweep` at cap (4 × 1.21 ms) | 4 ms | |
  | `sweep_idle` at cap (4 × 1.21 ms) | 4 ms | |
  | **one pass, all budgets at cap** | **252 ms** | **504%** |

- **Why it survived three sweeps.** The `DRAIN_LINES_MAX` comment does the
  arithmetic against the wrong line: it budgets `16 × ~1.08 ms (the costliest
  unauthenticated line, a keypair derivation) = ~17 ms`. A keypair derivation is
  not the costliest unauthenticated line — a wrong-passphrase verify is, at
  **7.46 ms**, seven times more, and it is reachable in `PHASE_PASS` with nothing
  but a name. `EVENT_LINES_MAX` names the right cost ("~8.1 ms for a
  wrong-passphrase verify") and then never multiplies it out. The `EVENT_LINES_MAX`
  half is the worse of the two because it is spent *before* the tick check, so it
  can swallow a tick whole.

**B. No instrument gates the aggregate, which is why A survived.** *(high — it is
the reason A exists)*

- **What breaks.** `bench_combat` gates the combat tick against 50 ms.
  `bench_persist` reasons about 4 saves against it in a comment. **Nothing sums a
  whole pass, and nothing benches the login path at all** — so a budget can be
  mis-derived by 7× and every gate stays green.
- **Whose code.** Ours.
- **Fix size.** Small — the probe that produced the table above becomes a bench
  that fails when one pass at cap exceeds 50 ms.
- **Test story for the release.** The bench gates the aggregate; unit tests assert
  each budget constant against the measured worst-case line cost, so the next
  edit that widens a budget has to move a number a test is watching.

### ✅ 1.7.1 — bound what the reconnect rate sets (SHIPPED)

Items C, D and I are **closed**. Kept in place because the corrections matter more
than the fixes.

**Two numbers in this file were wrong.** C said 1640 bytes per event with "~224 of
it ours". Measured: **1944 bytes** permanent per event (1640 of bump plus 304 of
freelist blocks nothing ever frees — libro has no `hasher_free`, and the freelist
never munmaps), of which **48** are ours. The 224 was `chain_append`'s total, 176 of
it inside libro's `entry_new`. So the flood was **667 MiB/hour**, not 563, and
Descent's own share was 2.9%, not 14%. What is entirely ours is the event *count*,
which is the only lever that exists — and that is what the rollup window bounds,
by ~3000×.

**D's scoping was wrong in our favour.** This file said rotation moves to 2.0 if it
changes the on-disk format. It does not need to: `verify_chain` never checks
`entries[0].prev_hash`, so a sealed segment is a valid standalone file and the
streaming chain's carried head hash records the boundary itself. No format change,
no libro release. [ADR 0009](../adr/0009-audit-log-rotation.md) is Accepted and the
mechanism is a 1.7.2 item. Also worth the warning it carries: libro's own
`chain_rotate` is a **no-op** on a streaming chain and would have silently done
nothing.

**A live data-integrity bug, found while measuring C.** 436 of the audit log's
37,902 records reported *themselves* as tampered with, because libro substitutes
`{}` for an empty `details` on read while the hash covers the details. And the test
suite had written 1,545 records into the operator's log. Both closed; the 436 are
deliberately not repaired, because rewriting a hash-chained log is what it exists
to prevent.

**C. 1640 bytes of memory are permanently lost per failed connection attempt —
563 MB/hour at 100 reconnects/s, and it never comes back.** *(high)*

- **What breaks.** RSS climbs and never falls. The bump allocator has **no free at
  all**; on overflow `lib/alloc.cyr` mmaps a fresh 256 MB chunk, so there is no
  ceiling to hit — it grows until the kernel refuses and `alloc()` starts
  returning 0.
- **Can it happen today? Yes, unauthenticated.** Connect, give any name, fail the
  passphrase confirm five times, disconnect, repeat. Nothing needs to exist on
  disk first.
- **Whose code — split, and the split matters.** 1416 of the 1640 bytes are inside
  libro's `filestore_append`, which is upstream and `lib/` is off-limits. The
  other 224 are ours. **But the event *count* is entirely ours**: we choose to
  emit one `audit_event` per connection, and nothing bounds reconnects. 1.6.12
  cut this 5× by logging once per session instead of once per attempt; it did not
  bound it. The code comment at
  [`src/persist.cyr:958`](../../src/persist.cyr:958) says so outright — *"E3
  bounded the attempts per CONNECTION; it did not bound reconnects, and nothing
  else did either."*
- **Fix size.** Real but contained, and entirely in our code: a per-peer rate
  limit or a coalescing window on `audit_event`, so a flood still writes a
  warning that names it without buying arena per connection. The upstream 1416 B
  needs a libro issue filed separately; it stops mattering once the count is
  bounded.
- **Measured.** 200 connect/fail/drop cycles, `alloc_used()` delta: 328000 bytes,
  exactly 1640 per cycle — one audit event's worth, confirming the rest of the
  connection lifecycle reclaims correctly. 1 GB of RSS after 654,720 attempts,
  ~109 minutes at 100/s.

**D. `data/audit.libro` is never rotated.** *(medium)*

- **What breaks.** ~360 bytes of disk per event, forever. There is no rotation
  code anywhere in the tree. C's flood is a disk flood too.
- **Can it happen today?** Yes, but it is operator-visible growth rather than
  something exploitable on its own.
- **Whose code.** Ours, and it needs a *decision*, not just a patch:
  [ADR 0006](../adr/0006-persistence-shape.md) makes the log an append-only
  SHA-256 hash chain, so rotation has to carry the head hash into the new segment
  or the chain breaks and the tamper-evidence is gone.
- **Fix size.** An ADR plus the implementation it picks. **If the chosen design
  changes the on-disk audit format this moves to 2.0** — but the decision itself
  is 1.7.1 work and is not deferred.
- **Test story for the release.** N connect/fail cycles leave arena growth
  bounded, and the audit trail still names the flood; a rotation round-trip
  verifies the chain across a segment boundary.

**I. `passwd` has no rate limit at all.** *(medium — raised by 1.7.0's cost census)*

- **What breaks.** Every other expensive verb is metered: `save` has
  `SAVE_MIN_INTERVAL_MS` (1 s), the login paths have `MAX_LOGIN_FAILS`. `passwd`
  has no analogue, and `PHASE_CHPASS_CONFIRM` is the **dearest line in the game
  that needs no victim's credential** — two Ed25519 operations in one line
  (a keypair derive *and* a record sign), measured 2461 µs.
- **Can it happen today? Yes**, from a self-created account, and open
  registration means "self-created" costs four lines. 1.7.0's charge window
  bounds what one *pass* will spend on it, so it can no longer stall a tick — but
  nothing bounds the **rate**, so it is a sustained-CPU lever.
- **Whose code.** Ours. **Fix size.** Small — the `save_rate_limited` shape
  already exists five lines away in the same file; reuse it.

### 1.7.4 — object lifetime

**J. Nothing in the tree reclaims a dropped item, and `look` pays for it.**
*(medium — raised by 1.7.0's loop census)*

- **What breaks.** `obj_free` is reached only from corpse decay and from a
  disconnecting player's inventory. Anything dropped on a floor is permanent for
  the life of the process. `session_append_objs` then walks it on **every `look`,
  every move, every login**: measured 1 µs authored → **563 µs at 4000 floor
  objects**, with a structural ceiling around 3600 µs
  (`MAX_SESSIONS × MAX_INV` in one room). Sixteen `look`s is up to 58 ms — on the
  most-typed verb in the game.
- **Can it happen today?** Yes, and it needs no malice: it is what a long-lived
  server with players who drop things looks like after a while.
- **Why 1.7.0 did not fix it.** The charge meter deliberately charges this
  **nothing** — there is no crypto and no prose in it — so it is bounded only by
  the line count, and no line count helps: one littered `look` can exceed a whole
  window on its own. **No budget of any denomination fixes this.** The cost is
  unbounded in the *world state*, not in the line, so only object lifetime fixes
  it. Stated plainly here because 1.7.0's comments could otherwise read as
  though the pass is fully bounded; what is bounded is the crypto and the fan-out.
- **Whose code.** Ours. **Fix size.** Real — it is a lifetime/ownership question
  (when does a floor object become garbage, and who decides), adjacent to M12's
  corpse decay and to **M15**'s zone registry. Related unmetered walks in the
  same class: `zone_reset_objs`' `_obj_id_world_count` (24 µs → 1467 µs) and
  `get all.X` scanning past `MAX_INV`.

### ✅ 1.7.2 — the carry cap becomes a bound (SHIPPED)

Items L, L2, O and E are **closed**, plus three defects this release's own sweep
found — two of them in code shipped days earlier.

**The class sweep's headline: the sixth instance was inside the fix for the
fifth.** 1.7.1's audit rollup re-stamped its window on every count-arm fire, so
the clock arm stopped firing under sustained load — a counter that resets itself,
which is exactly G2's `SS_FAILS = 0` shape and the reason 1.7.1 existed. Measured
120 entries/hour to the crossover, 441/hour at 1000 ev/s, against a comment
claiming no rate term. Fixed, and the arithmetic corrected to what is true.

**And the carry-cap fix introduced a regression the sweep caught**: counting bag
contents made `get <x> from <your own bag>` fail at the cap, because that move
changes no total. The cap now applies to acquisition only.

**Still open from the sweep, and moved to 1.7.3:** the room floor has no cap at
all (measured 40 cycles → floor 0→80, monotonic, from ordinary play — item J), and
`cmd_give` overshoots `MAX_INV` to ~199 because its check runs before a transfer
that moves a container *and its contents*.

### 1.7.2 — the carry cap becomes a bound (detail, retained)

Four items were added here by 1.7.1's own investigation. They are listed first
because two of them are worse than the item this release is named after.

**L. A carried container flattens past the carry cap and poisons the save.**
*(high — raised by 1.7.1; player-armable data loss)*

- **What breaks.** `_build_record`'s inner contents loop sets `SAVE_ERR` — which
  M11-D turned into "refuse the whole record" — about ten lines below a comment
  saying *"TRUNCATE the inventory here, do not poison the record."* So 1.6.13's
  defect (a player silently stops persisting) is **fully reachable through a bag**:
  `inv_count` walks only the top-level `SS_INV` chain, `cmd_put` moves items into a
  carried container with **no count check**, and F11 flattens one level into the
  same `inv` field. Probe-confirmed: 3 top-level items (well under `MAX_INV = 100`)
  plus 200 items in one bag → the record is refused whole.
- **Can it happen today? Yes**, by an ordinary player with a bag and no malice. This
  is what turns `save.fail.sweep` into a per-tick event (item N).
- **Whose code.** Ours. **Fix size.** Contained — make the container path truncate
  like the top-level one, and count contained items against the cap.
- **1.7.1 made this harder to notice, not better.** The rollup window bounds the
  arena cost of the resulting `save.fail` storm, so the symptom is quieter while the
  data loss is unchanged. Tracked for exactly that reason.

**M. Audit-log rotation — the mechanism.** *(medium — the decision is done)*

- [ADR 0009](../adr/0009-audit-log-rotation.md) is **Accepted**: seal-and-continue,
  no on-disk format change, no libro release. 1.7.1 landed the decision and the
  seam (`_audit_store_size`, `audit_size_warn_due`, the boot warning, the test
  fixture redirect). This item is the rename/reopen, segment enumeration, the
  keep-count prune, the `audit.rotate` / `audit.prune` markers, and the boot-time
  head fallback.
- **The crash window is the load-bearing part**: rename succeeds, process dies
  before the first append, the live file is empty, a naive boot restarts the chain
  at genesis — one broken link per boundary, indistinguishable from a deletion. That
  is the H11 bug (fixed in 1.6.6) reintroduced as a feature. ~8 lines, and it needs
  its own mutation test.
- **Two traps, both verified**: libro's `chain_rotate` is a **no-op** on a streaming
  chain (it reads the always-empty entries vec), and `chain_head_hash` returns 0 for
  the same reason — `chain_prev_hash` is the accessor that works. Also: do **not**
  repoint the store unless `file_rename` returned 0.

**N. `save.fail.sweep` fires per TICK, not per 300 s.** *(medium — raised by 1.7.1)*

- **What breaks.** `player_save` clears `SS_SAVE_DIRTY` only after a successful
  rename, so once saves start failing every session stays due on **every** tick —
  `SAVE_BATCH_MAX = 4` signed attempts per 2.5 s, unbounded in time, from sessions
  merely sitting there. Under ENOSPC the audit log grows fastest exactly when it can
  least afford to.
- **Note also** that `save_sweep` runs *before* `charge_window_open` in
  `advance_tick`, so this path is not charge-metered at all.
- **Whose code.** Ours. **Fix size.** Small — a backoff or a failure stamp.

**O. Nothing caps the number of accounts.** *(medium — raised by 1.7.1)*

- **What breaks.** Registration is open, names are 2–16 alnum, `player_exists` is a
  bare `stat`, and there is **no account-count or per-connection creation limit
  anywhere**. Each account costs four lines and leaves a permanent
  `data/players/<name>.cyml` — a disk lever entirely independent of the audit log.
- **Why it matters beyond disk.** It is the reason "authenticated" is not a rate
  bound anywhere in this tree: every `passwd`-path and `save`-path argument that
  leans on "a real player sets that rate" leans on this, and this does not hold.
  1.7.1's `passwd` rate limit is per-session; accounts are free.
- **Whose code.** Ours. **Fix size.** Real — it needs a policy decision (invite?
  per-IP? a cap?) before an implementation.

**P. Restore G3's per-attempt audit granularity.** *(low — now affordable)*

- 1.6.12 gave up per-attempt `create.fail` / `login.fail` entries to bound arena.
  Under 1.7.1's rollup window that granularity costs the same arena and reports a
  **truer** number, so the trade can be reversed. Deliberately not bundled with the
  window itself (one change at a time). Listed because the code will look
  deliberate and nobody will revisit it otherwise.



**E. The 100-item carry cap is not enforced when a character loads.** *(medium)*

- **What breaks.** [`_restore_inv`](../../src/persist.cyr:629) walks the whole
  saved id list with no cap, so a record can restore **~4000 items** — 40× the
  cap. `SLURP_CAP` is 8192 bytes and a one-character id plus a comma is two
  bytes. `MAX_INV` is checked at all three *acquisition* sites (`get`,
  `get from`, `give`) and at none on the load path, so the 1.6.13 cap is
  bypassable by the one route that skips those checks.
- **Can it happen today? Not remotely** — it needs the save file, either
  filesystem access to `data/players/` or the player's own key. That second one
  is not hypothetical: per
  [ADR 0004](../adr/0004-identity-and-authentication.md) the identity is derived
  from the passphrase and the server never holds the key, so a player who obtains
  their own record (a backup, a shared host, a restore workflow) can sign a valid
  one. This project's standing position — recorded when `hp` had exactly this
  shape — is that **a valid signature is not field validity**. Every numeric
  field on this path is `_clamp`ed for that reason. The inventory list is the one
  that is not.
- **Whose code.** Ours.
- **Fix size.** A counter and a bound in one function, plus an audit line when it
  truncates. Small.
- **This is the fifth appearance of one defect** — *a per-item cap is not a bound
  on a loop that walks many items.* The previous four were each fixed by capping
  one neighbour of the open hole. So this release does the **class sweep** as
  well as the instance: every per-item cap in the tree, checked against every
  loop that walks those items.
- **Test story for the release.** A crafted 4000-entry record loads exactly
  `MAX_INV` items and logs the truncation; the class sweep's findings each get an
  assertion.

### ✅ 1.7.3 — the give overshoot, the retry storm, and two uncovered guards (SHIPPED)

Items F and G are **closed**, plus `cmd_give`'s overshoot (measured 141 against a
cap of 100) and the per-tick save-failure retry. A borrowed audit chain-link was
also fixed — with the honest caveat that the hazard is real and its consequence
was **not** demonstrated; the one broken link in the working log has an unknown
cause and is not attributed to it.

**Rotation deliberately did NOT land.** The crash window is the load-bearing part
and belongs in a release where it is the subject, not bolted onto four unrelated
fixes. It is item M, now first in 1.7.4.

### 1.7.3 — cover the guards that predate the mutation habit (detail, retained)

Mutation testing became routine at 1.6.7. The guards landed before it were never
put through it. These three items are that gap.

**F. The `passwd` secret-key wipe is untested.** *(medium)*

- **What breaks.** Deleting the `memset` in
  [`sess_cand_clear`](../../src/persist.cyr:1078) breaks **no test**. The
  freelist reuses blocks **without zeroing**, so a freed candidate block still
  holding a derived Ed25519 secret key can be handed straight to the next
  `fl_alloc` of that size class.
- **Can it happen today? No** — the guard is present and correct. The risk is that
  a future edit removes it and nothing says so.
- **Whose code.** Ours. **Fix size.** Small.

**G. The double-login refusal is untested at its call site.** *(medium)*

- **What breaks.** Replacing the `session_already_online` check in `login_on_pass`
  with a constant false breaks **no test**. The predicate has a test; the refusal
  does not. Two sessions on one character means two writers to one save record —
  the inventory duplication 1.6.6 fixed.
- **Can it happen today? No** — the guard is present. Coverage hole, two call
  sites: [`src/persist.cyr:863`](../../src/persist.cyr:863) and
  [`:1027`](../../src/persist.cyr:1027).
- **Whose code.** Ours. **Fix size.** Small.

**H. The coverage check that found F and G was a sample, not a sweep.** *(tracked
so it is not mistaken for complete)*

- Six of the ~17 guards that 1.6.0–1.6.6 landed were mutation-tested. Two came
  back uncovered — F and G. **The other ~11 have not been checked.** Stated
  explicitly because "2 uncovered" otherwise reads as a finished audit. Finishing
  it is this release's main body of work.
- **Test story for the release.** Every pre-1.6.7 guard has a mutation that fails
  when the guard is reverted.

### 2.0 — the donation bin

**Q. A room container is a permanent, unbounded shared stash.** *(2.0 — needs a
zone field and a cap, both frozen by ADR 0007)*

- **What it is.** Authored zone furniture is minted unarmed, so it never
  ground-decays (1.7.5), and `cmd_put` does not arm what goes inside it. So items
  put into a town barrel stay forever — which is a **feature people will want**:
  a donation bin, a guild chest, a shared stash. It exists today by accident
  rather than by design.
- **Why it is listed anyway.** Nothing caps how much a room container holds, and
  `look` does not walk contents, so it accumulates silently — the same unbounded
  shape ground decay just closed for floors, one level down. A town barrel is the
  obvious place for it to happen.
- **What 2.0 owes it.** A real bin needs to be *authored* (a zone field marking a
  container as persistent), *capped* (how many items), and probably *persistent*
  across restarts — floors are not saved at all today, so a "stash" that a restart
  empties is a trap. All three are frozen surfaces in 1.x: zone fields and the
  save schema are ADR 0007 §3/§5.
- **Interim behaviour is deliberate and documented** at `cmd_put` in
  [`src/item.cyr`](../../src/item.cyr): a container a PLAYER dropped is armed and
  decays with its contents; authored furniture is not.

### 2.0 — bound the broadcast fan-out

**K. `combat_tick_all`'s broadcast fan-out is O(sessions²).** *(2.0 — needs a new
`@stats` field, which ADR 0007 freezes until then)*

- `room_combat_line` and `room_broadcast` each walk every session per line, with
  up to four combat lines per engaged player per round. At 256 co-located players
  that is **43.3 ms of tick body** (`bench_combat` BIGPLAYERS — **passing**, and
  1.7.0 deliberately did not tighten its gate; putting a legitimate scenario 4%
  from failing on a shared runner is a coin flip, and this repo has been burned
  twice by nondeterministic gates).
- **1.7.0's arithmetic deliberately does not subtract this from the drift
  allowance**, because a pre-work drift sample cannot see tick-body cost. That
  subtraction was proposed during the design work, would have produced budgets
  ~3.5× tighter than needed, and is refuted in
  [ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md). Do not redo it.
- Closing it means bounding fan-out at **every** broadcast site and gaining a
  tick-body occupancy counter to measure the result — a new `@stats` field, hence
  2.0 / M14. Related unbudgeted walks: `room_say_broadcast`, `cmd_who`,
  `render_who`, `room_append_present`, `find_player_global`, `room_find_player`,
  `sessions_forget_mob`.
- **The honest ceiling.** If a reviewer insists on one 50 ms reading covering
  everything, then 43.3 ms of legitimate combat plus 27 ms of worst-case input is
  70 ms and no per-pass budget can fix it — with **both** budgets set to zero, one
  pass at that population still costs 43.3 + 2 × 13.5 ms from two indivisible
  sigil calls. `ed25519_verify` is ~4.7× its own sign, `lib/` is off-limits, and
  single-threaded there is nowhere to defer it. **The highest-leverage change to
  this server's tick behaviour is a sigil release**: at 500 µs per verify the
  dearest line drops from 54 charge units to ~9. Descent's own job — which 1.7.0
  did — is to stop calling verify when the answer cannot matter, and to stop a
  count budget pretending the call is cheap.

### What the sweep checked and found clean

- **No fix has been undone.** All **49** guards the 1.6.x CHANGELOG claims are
  still present in source, verified mechanically rather than by reading.
- **The save/load trust boundary holds.** Every numeric field on the load path is
  `_clamp`ed, the room index is validated with a fallback, and the class id is
  bounds-checked — E above is the one field that escaped.
- **No bump allocation outside boot.** Every `alloc()` in `src/` is a boot-time
  loader or a one-time-init singleton, except the audit path in C.

---

## The gate — what closes the 1.x line

**The 1.x line closes when a re-run sweep comes back with no critical or high
findings.** That has not happened. It is item 5 in
[What is left](#what-is-left), and it plus 1.7.0 and 1.7.1 are what block 2.0.

Three sweeps have been done and **all three found serious defects the previous
pass had missed** — a remote crash on `examine` (found at 1.6.9), an unbounded
event batch costing 4.12 s of blocked loop (found at 1.6.12), and now a 252 ms
pass at 504% of the drift budget plus an unbounded per-connection arena loss
(the gate sweep, [open issues](#open-issues--8) A and C). The first two are
fixed; the third sweep's findings are 1.7.0–1.7.3.

The bar stays where it is because the evidence is consistent: every pass so far
has found real things, and each one found them in a place the previous pass had
no instrument for. 1.6.9 built the first benches that touched save, login and
loaders, and re-run #2 immediately found defects there. The gate sweep found A
because it was the first time anything summed a whole tick pass. Expect the next
re-run to find whatever 1.7.0's bench does not yet measure.

### How the sweep went — for context, not for tracking

The 1.6.0 audit produced 56 findings, 44 verified. Closed across thirteen
releases (1.6.0–1.6.12) in batches grouped by *kind of work* rather than
severity, so each release had one coherent theme and one test story:

| | | |
|---|---|---|
| **1.6.6** | state integrity | double login, template-id round trip, audit-chain resume |
| **1.6.7** | content + parser | the `N.X` qualifier, `put`/`give`, signed config ints |
| **1.6.8** | resource + timing | broadcast coalescing, metered autosave, the tick schedule |
| **1.6.9** | coverage, then re-run | save/login/loader benches, a soak, a docs sweep |
| **1.6.10** | re-run #1's critical + highs | disconnect on the tick path, drain budget, creation caps |
| **1.6.11** | re-run #1's tail | `@who` bounds, key wipes, loader unpublish, `put` round-trip |
| **1.6.12** | re-run #2's critical | the event batch, both loops, `passwd` |
| **1.6.13–15** | re-run #2's tail, then docs | the carry cap, the pre-auth timeout, README/overview vs code |

**Two lessons the sweep cost real releases to learn.**

*Fixing an instance is not fixing the class.* 1.6.12's critical was the fourth
appearance of one defect — *a per-item cap is not a bound on a loop that walks
many items* — after three releases each capped a neighbour of the open hole.
`grep -n ident_derive src/` and "every loop that dispatches lines" were always
the whole answer. **The gate sweep found a fifth** ([issue
E](#172--the-carry-cap-becomes-a-bound)), which is why 1.7.2 sweeps the class
rather than patching the instance.

*A finding count is not a measure of what is broken.* It measures the instruments
you had. 1.6.9 built the first benchmarks that ever touched the save, login and
loader paths, and re-run #2 immediately found things there. The gate sweep's worst
finding is itself an instrument gap ([issue
B](#170--the-tick-budget-becomes-a-budget)): a budget was mis-derived by 7× and
stayed green for eight releases because nothing measured a whole tick pass.

*A comment is not a bound.* Two of the eight open issues were **documented in the
source and still open** — the false arithmetic on `DRAIN_LINES_MAX`, and
`persist.cyr:958` stating in as many words that reconnects are unbounded. Writing
the limitation down is not fixing it, and a reader who trusts the comment reads
the first one as a completed piece of reasoning.

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

*Wanted, but blocked on something — a dependency, a foundation, or an upstream
port. Distinct from [Unclaimed](#unclaimed--available-on-demand), which is
unblocked, and from [Out of scope](#out-of-scope), which is a decision against.*


- **Joshua integration** — blocked on an upstream Cyrius port and a spec rewrite. See the backlog above. Operator control (M18) deliberately does not wait for it.
- **PvP** — needs threat, equipment and levels to be meaningful first. Post-2.0.
- **Crafting** — needs currency, shops and item modifiers underneath it.
- **Quests** — needs a state machine per player, which is a schema conversation, and a lot of authored content.
- **Skills separate from levels** — a second progression axis; not worth it until the first one is proven.
- **aarch64** — no longer blocked: the epoll-layout defect that made this unsafe
  was fixed in 1.6.14 and CI builds `--aarch64`. Deferred only because no ARM
  target is planned, so nobody has run the suite on one.
- Everything in the v1.0 **Out of scope** list below still stands, except that PvP and MUD protocol extensions move from "not our problem" to "post-2.0, on merit".

---

## Unclaimed — available on demand

**No decision has been made against anything here, and nothing blocks it.** These
are known, scoped, and simply not needed yet. Picking one up requires a reason to
want it and nothing else — no argument, no re-litigation, no "we decided that was
out of scope."

This bucket exists because the alternative is a deferral that lives only in a
source comment, where nobody can find it and a future reader treats it as
settled. If something lands here, that is a statement about *demand*, not about
merit.

- **Telnet NAWS, TERMINAL-TYPE and LINEMODE.** The negotiator currently refuses
  every option except ECHO and SGA, which is correct RFC 1143 behaviour and is
  not a stub — an unsupported option is *supposed* to be refused. Adding one
  means: a preference entry in `opt_pref_us` / `opt_pref_him`
  (`src/telnet.cyr`), subnegotiation handling for NAWS and TERMINAL-TYPE (the
  SB state machine already collects the payload — nothing consumes it), and
  whatever the feature actually wants the data for.

  Sizes: **NAWS** (client window size) is small and is what you would want first
  if room descriptions or tables ever need to wrap to width. **TERMINAL-TYPE**
  is small and would let ANSI colour be conditional rather than unconditional.
  **LINEMODE** is the largest — it means owning the full line discipline
  server-side, which is the work option 1 of the old B1 finding described, and
  it only matters if descent ever re-adopts character-at-a-time mode.

  **Note the disagreement this resolves:** [ADR 0002](../adr/0002-raw-tcp-telnet-protocol.md)
  lists "terminal-type discovery" as *in scope* for the protocol, while
  `src/telnet.cyr` deferred it to "a later milestone" that never existed. The ADR
  is the one that was right — it is available, not excluded. The source comment
  now points here instead of at an imaginary milestone.

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

*Decided against, with a reason. Reversing one of these needs a new argument —
which is exactly why nothing gets parked here for lack of demand. If it is
merely unwanted-for-now, it belongs in
[Unclaimed](#unclaimed--available-on-demand).*

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
