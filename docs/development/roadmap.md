# cyrius-yeomans-descent — Roadmap

> **Last Updated**: 2026-07-31 (v1.7.21 — **gate re-run #5 returned DO-NOT-CLOSE**
> (0/3/5/4, items BI-BT); **ten of its twelve are closed**. Open: **BJ** (needs the
> `lib/net.cyr` decision AA is waiting on) and **BT** (belongs with M15). The 1.x
> gate is now blocked by ONE target — and **x86_64 came back with zero highs for
> the first time in seven sweeps**)
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
| — | ~~1.7.6~~ | ~~2~~ | ✅ **Shipped.** The room listing no longer breaks the wire (it ended mid-escape with no prompt at 86 floor objects) · 1.6.12's audit granularity restored | — |
| — | ~~1.7.7~~ | ~~2~~ | ✅ **Shipped.** Carried two existing fixes to the sites they were never applied to — `get` of a container (silent item loss at 199 against a cap of 100) · five listing verbs that truncated mid-line with no prompt | — |
| — | ~~1.7.8~~ | ~~2~~ | ✅ **Shipped.** AGNOS saves never published (syscalls 82/87 are GPU calls there) · the pre-auth parse, 2,248 B/attempt → **0** · CI now builds `--agnos` | — |
| — | ~~1.7.9~~ | ~~9~~ | ✅ **Shipped.** The RX-side class — a half-sent Telnet escape on a full queue, at the negotiation drain AND at the `WILL/WONT ECHO` sites every real client hits · the unguarded room-header prose · the class menu · `mob_swing` on the tick path. Item Y settled as **doc-only**, item AA carried | — |
| — | ~~1.7.10~~ | — | ✅ **Shipped.** Toolchain `6.4.86 → 6.5.4` + a refreshed dependency snapshot. No source change; closed the **sakshi shadow gap** carried since 1.2.0 and the toolchain-drift warning | — |
| — | ~~gate re-run #2~~ | — | ⛔ **Ran 2026-07-31 — DO-NOT-CLOSE.** 0 critical, **2 high**, 3 medium, 3 low. Nothing dropped; ten reports collapsed to eight distinct defects | — |
| — | ~~1.7.11~~ | ~~2~~ | ✅ **Shipped.** **AC** shutdown now saves every live session (verified against a running server) · **AD** closed at all three points — the disconnect gate, the login heal for records already on disk, and a fatal boot on an empty class table | — |
| — | ~~1.7.12~~ | ~~2~~ | ✅ **Shipped.** **AE** the refused duplicate now disowns the record · **AF** both batch loops charge the teardown — and `bench_tick_budget` gained the arm that could not fire, which now FAILS at 118% of the drift allowance when reverted | — |
| — | ~~1.7.13~~ | ~~1~~ | ✅ **Shipped.** **AG** both altitudes — `examine`'s borrowed bodies now share one clamp with the room header, and the header/exits decline whole so accumulation across a read cannot run the queue dry | — |
| — | ~~1.7.14~~ | ~~2~~ | ✅ **Shipped.** **AH** `ident_derive` and the confirm path now wipe their key scratch · **AI** the reap budget is spent only on reaps that cost a signature | — |
| — | ~~gate re-run #3~~ | — | ⛔ **Ran 2026-07-31 — DO-NOT-CLOSE.** 0 critical, **4 high**, 5 medium, 7 low. Finders could BUILD AND RUN this time; three of the four highs were demonstrated against a live server | — |
| — | ~~1.7.15~~ | ~~3~~ | ✅ **Shipped.** **AJ** a rejected objects table is now fatal (exit 1), and a dropped id is counted, audited and reported · **AN** `class` by stable id, both forms read · **AO** a healed character keeps its room | — |
| — | ~~1.7.16~~ | ~~3~~ | ✅ **Shipped.** **AK** the two tick consumers now agree what a phase means · **AM** an offline census, seeded once and moved by login/disconnect · **AL** the account is counted where the record is written | — |
| — | ~~1.7.17~~ | ~~10~~ | ✅ **Shipped.** **AP** combat is two-sided · **AQ** the fuzz gate reached `NORM_CAP` for the first time (7,988x/run) and now asserts its own coverage · **AW** two benches that could not fail · plus AR, AT, AU, AV, AX, AY; **AS** documented as a content rule | — |
| — | ~~gate re-run #4~~ | — | ⛔ **Ran 2026-07-31 — DO-NOT-CLOSE.** 0 critical, **3 high**, 3 medium, 3 low. Twelve reports collapsed to **nine distinct defects** (AZ-BH); one refuted. **Nine of nine are a rule applied at one site and not its sibling — and six are siblings of fixes from 1.7.15/16/17, one from the head commit itself** | — |
| — | ~~1.7.18~~ | ~~4~~ | ✅ **Shipped.** **BE** the ordinal bound moved out of the shared reader — `parse_uint` now closes AR's wrap by exact i64 arithmetic, and `created` survives a login · **AZ** the boot spawn runs after the census is seeded (measured 13/13/13/13 → 13/12/12/12) · **BA** a rejected rooms table is fatal, so AJ's guard is reachable at last · **BH** `WL_ERR_NOSTART` | — |
| — | ~~1.7.19~~ | ~~4~~ | ✅ **Shipped.** Sessions that are not a normal logged-in player — **BC** the refused duplicate poisons the census · **BD** `classes_upkeep` frozen in a peer-held menu (AK's other half) · **BF** the classless heal double-counts an account · **BG** the class-menu squatter's deadline (a new 90 s tier) | — |
| — | ~~1.7.20~~ | ~~1~~ | ✅ **Shipped.** **BB** — the post-auth `toml_parse`, 2,248 B on every successful login, 883 MB/h from one socket. **2,332 → 84 bytes per login (96%)**, and the bench arm that could not fail now gates at 256 and exits 1 when reverted. **Every finding from gate re-run #4 is now closed** | — |
| — | ~~gate re-run #5~~ | — | ⛔ **Ran 2026-07-31 — DO-NOT-CLOSE.** 0 critical, **3 high**, 5 medium, 4 low — 12 distinct defects from 15 reports. **All three highs are AGNOS-only; x86_64 came back with ZERO highs, a first.** The "our own recent fixes are incomplete" signal collapsed from 7-of-9 to 1-of-12 | — |
| — | ~~1.7.21~~ | ~~10~~ | ✅ **Shipped.** The target nobody had ever run — **BI** AGNOS had no clean shutdown at all (`stop` was never assigned) · **BK** descent owns its scheduling clock, since #40 is documented frozen on the `run` path · **BL** 1.7.19's mirror image, fixed by refusing the duplicate *before* the restore · plus BM, BN, BO, BP, BQ, BR, BS | — |
| 1 | [**BJ**](#open-issues--gate-re-run-5-returned-do-not-close-2026-07-31) | 1 | **Next, and it is a DECISION not a patch.** `session_drain`'s only would-block arm is Linux `EAGAIN`; AGNOS `sys_write` routes to blocking `sock_send` #48. agnos exposes **no non-blocking send at all**, so this needs the same upstream `lib/` conversation as item **AA** — take them together | **yes** |
| 2 | [**the AGNOS harness**](#the-gate--what-closes-the-1x-line) | — | **Infrastructure, and the real blocker.** `running.md`'s QEMU harness was **deleted 2026-07-07**. Until it is rebuilt, no sweep can close AGNOS and re-run #6 will report the same uncertainty #5 did | **yes** |
| 3 | [**gate re-run #6**](#the-gate--what-closes-the-1x-line) | — | After BJ and the harness. Target what #5 could not: a real kernel boot, the conservation invariant, CYML loader fuzz, a multi-hour soak | **yes** |
| 6 | [**carried**](#raised-by-177s-own-class-sweep-2026-07-30--1-high-3-medium-4-low) | 2 | Item **AA** (16 B/connection at accept, needs a `lib/net.cyr` decision) and item **AB** (the stateless-refusal amplifier) — neither blocking | — |
| 2 | **2.0.0** | 4 | [M14](#m14--adr-0008-and-save-schema-v2-v200) contract + schema v2 · [M15](#m15--zone-registry-and-the-entry-cap-v200) zone registry · [M16](#m16--xp-levels-and-a-death-cost-v200) XP/levels/death · [broadcast fan-out](#20--bound-the-broadcast-fan-out) | — |
| 3 | 2.1.0 – 2.4.0 | 7 | [M17–M23](#m17m23--the-2x-tail), the 2.x tail | — |

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

## Open issues — gate re-run #5 returned DO-NOT-CLOSE (2026-07-31)

**Ruling: DO-NOT-CLOSE. Critical 0, high 3, medium 5, low 4** — **12 distinct
defects from 15 reports**, 3 refuted, 0 cross-finder duplicates. Run against a
clean tree at `dad52fb` (v1.7.20).

Same protocol as #4 and the same bound: five finders in isolated worktrees, each
required to build and run, each attacked by an independent skeptic with its own
worktree told to default to REFUTED. Eleven agents. **The surfaces were chosen to
be the ones #4 could not reach** — its own settled negatives (command
interleaving, hand-mutated CYML loaders) were explicitly excluded.

**Read the shape before the count. All three highs are on the AGNOS build, and on
x86_64 this run came back with ZERO highs — the first time in seven sweeps.** Five
agents drove a live server for hours, forced ~95 real audit rotations, forged ~40
signed records, put 250 real TCP players in sustained combat and soaked for 39
minutes. The x86_64 findings are four mediums and four lows, none
player-destructive.

AGNOS counts, and the precedent is this project's own: item **T** (1.7.8) was an
AGNOS-only defect, rated high and closed as high, and `running.md` has advertised
AGNOS as a supported deployment since 1.1.0.

### The pattern — the shape held, the recency broke

| | #4 | #5 |
|---|---|---|
| Sibling shape ("a rule at one site and not its sibling") | 9 / 9 | 11 / 12 |
| Siblings of the **previous three releases** | 6 / 9 | **1 / 12** |
| Introduced by the head commit | 1 | 1 (an incomplete guard, not a regression) |
| **Pre-existing** defects found | ~2 / 9 | **10 / 12** |

**#4's diagnosis — "the sweep is now finding the incompleteness of its own recent
fixes at roughly the rate the fixes retire them" — is no longer true.** Nine fixes
shipped across 1.7.18/19/20 and left one-and-a-half siblings between them, down
from six. The process change #4 prescribed (grep every call site of a changed
predicate, record the enumeration in the fix's own comment) is working.

**The reason this run found ten pre-existing defects instead of two is not that
the code got worse — it is that four instruments existed for the first time, and
every one of them paid.**

### ✅ 1.7.21 — the target nobody had ever run (SHIPPED)

**Items BI, BK, BL, BM, BN, BO, BP, BQ, BR and BS are CLOSED.** 1502 assertions
(was 1476). **BJ and BT remain open** and are the two entries in *What is left*.

Verified beyond the suite where it was possible: **BO was A/B'd against a real
played-on tree** — two ordinary players each took one authored `notice` over TCP
and quit, and with the precondition disabled the suite FAILS where it now passes.
The AGNOS items are asserted structurally, because the suite is an x86_64 binary
and cannot execute the other arm; what is pinned is that **the two arms agree**,
which is the property all three violated.

### Still open

**BJ. One player whose client stops draining freezes the whole AGNOS server.**
*(high — DECISION, not a patch)*

- `session_drain` ([`session.cyr:715`](../../src/session.cyr:715)) writes with a
  bare `sys_write` and tests exactly one would-block code, `-11` (Linux EAGAIN).
  On AGNOS that routes to `sock_send` #48, whose own declaration says **BLOCKS**
  and which has no EAGAIN — so the arm is dead code, a full window parks the
  single-threaded loop, and `-1` is classified as a socket error and torn down.
- **The sibling is ten lines away in the same file.**
  `session_on_readable_max` ([`session.cyr:1970`](../../src/session.cyr:1970)) got
  an explicit AGNOS branch under the comment *"sys_read on a socket fd is the
  BLOCKING recv adapter, which would park the single-threaded poll loop on an idle
  session."* Word for word true of the write half, which never got one.
- **Measured** under emulation: a bystander's time-to-first-byte on `look` went
  0.000 s → **15.7 s**, reproducible to within 0.02 s across two fresh servers,
  the whole server frozen for ~6 skipped ticks. On a real kernel the agnosticos
  planning docs describe the same situation as a preempt-disabled **deadlock**,
  i.e. unbounded — not observed.
- **Why it is deferred rather than patched.** agnos exposes **no non-blocking send
  primitive at all**. A complete fix needs the same upstream `lib/` decision item
  **AA** has been waiting on since 1.7.9, and guessing at a chunking workaround
  here would be a patch written against an API nobody has agreed to yet. **Take
  AA and BJ as one conversation.**

**BT. Mob loot is minted outside the object ceiling.** *(low — belongs with M15)*

- `corpse_of` ([`item.cyr:365`](../../src/item.cyr:365)) mints loot with a bare
  `item_new` and no max-exist check, while `zone_reset_room_objs` consults
  `_obj_id_present`. Loot ids overlap authored ids, so a looted copy carried or
  saved pushes the count past the ceiling and the authored copies never come back.
  Controlled A/B: control → `objs +1` and the shard restocks; with one looted
  shard held by one offline player → `objs +0`, twice.
- **Not a duplicate of item J**, which was unbounded floor *growth* closed by
  ground decay. This is the same missing check producing the opposite consequence
  — a permanently **under**-stocked world.
- **Fix size: real, not small.** It is the object-lifetime/ownership question and
  belongs with M15's registry work.

### What gate re-run #5 had no instrument for

**#4's four named gaps — three now covered.**

1. **AGNOS execution — COVERED for the first time ever, and only partially.** One
   agent ran the `--agnos` build under an agnos→Linux syscall translator, served
   the MUD over TCP, and produced all three highs. It also answered `running.md`'s
   own open question: **AGNOS persistence works end to end** — record written,
   `quit` saves, an RST disconnect saves via `drop_session`, reconnect verifies and
   restores. **1.7.8's fix holds.**
   **Still open, and now the top instrument gap: nobody has booted a real AGNOS
   kernel.** The translator's own ADR states it validates agnos *userland* and does
   not exercise the kernel's scheduler, net stack or preempt/IF semantics — which
   is exactly where BK's trigger and BJ's unbounded form live. **The QEMU harness
   `running.md` pointed at was deleted 2026-07-07**; rebuilding it is a
   prerequisite for re-run #6. Also untested on AGNOS: every `YD_*` knob, zone
   reset, `save_sweep`, audit rotation, chpass, and #4's 40-cell phase × tick
   matrix on the second driver.
2. **Audit rotation under volume — COVERED.** ~95 real rotations across two
   agents, then confirmed on the stock binary at the shipped 8 MiB trigger.
   Produced BM, BN, BR and BS. Technique worth keeping: the rename→unlink window
   can be held open with unmodified code by making the next prune victim a
   **FIFO**, since `file_exists` blocks on it with no writer. Still open: rotation
   on `--agnos`, entry **self-hash** verification (only linkage was checked), the
   torn-line case, and a theoretical `file_exists`-under-fd-exhaustion bypass.
3. **Forged-signature harness — COVERED twice, and both were throwaways.**
   ~150 lines each, linking the project's own `ident_derive` / `ed25519_sign`.
   **Recommend landing one in the tree** — it is the only way to test ADR 0004's
   stated threat model, and it produced BQ. **Clean negative worth recording: the
   full scalar-clamp battery HELD everywhere** — `hp` at i64max, `maxhp` 0/-5,
   `ndice` 0/1e8, `ac` 1e6, `str` -1e6, `created` i64min, leading zeros, `+`/`-`,
   empty values, duplicate keys, key prefixes, `[player]`-in-a-value, no trailing
   newline. Every one clamps or defaults, no crash, no scanner/bayan divergence.
4. **The broadcast fan-out breach point (item K) — ANSWERED.**

> **Combat tick-body p99 = 0.432 µs x N²** for N co-located, mutually engaged
> players. **The 50 ms drift budget breaches at N ≈ 345** — bracketed 336–352
> across two independent sweeps. Against the 2.5 s interval, N ≈ 760.
> `MAX_SESSIONS = 256`, so **the breach is 1.35x the population the server will
> accept.**

Three things that make this directly actionable for M14/M15:

- **At 256 the real cost is 26–28 ms, not the 43.3 ms** item K and
  `benches/bench_tick_budget.bcyr:317` both still print. **Both need re-deriving**
  — item K's scoping argument rests on "4% from failing" and it is at 53%.
- **The limiting term was measured, not assumed.** Holding 256 sessions engaged
  and varying only the room split: `cost(k) = A/k + B` gives **A = 26.4 ms (96.7%)
  = the per-recipient prose append**, B = 0.9 ms (3.3%) = the session walk, combat
  resolution and flush combined. **It is not the room walk. Bounding fan-out means
  bounding the append.**
- **Volume: 110 x N² prose bytes per tick** — 7.24 MB/tick at 256 in-process,
  **validated over real TCP at 7.08 MB/tick with 250 co-located players, 2.2%
  apart.** Item K no longer needs a TCP probe. H15's TX valve lost **zero** prose
  at both 150 and 250 players.

**New gaps for re-run #6:** a real AGNOS kernel boot; **the conservation
invariant still does not exist** (#4 called it the highest-value instrument to
build, and #5 produced two more census defects — BL and BT — that it would have
caught); `cyrius fuzz` still has **no CYML loader target**; no multi-hour soak in
one run (best 22.8 min, ended when a sibling agent's `pkill -f descent` reached
it — **#6 must kill by port or PID, not by name**); and audit-chain **self-hash**
verification.

**Settled negatives, recorded so #6 does not re-derive them:** BE's `parse_uint`
overflow arithmetic is exactly correct at both bounds; BD's un-gating of
`classes_upkeep` costs ≤0.4% of the drift allowance at `MAX_SESSIONS`; BF/BG are
right on both flows; the rotation collision guard refused every same-name rotation
constructed; marker coalescing cannot bite at shipped settings; `AUDIT_SEG_MAX`
exhaustion needs ~5,000 years; and **per-op arena allocation is 0 bytes** across
14 command verbs, session/mob/item/telnet lifecycle, corpse decay, zone resets and
the whole `advance_tick` body, over 1.7 M churn ops.

---

## Open issues — gate re-run #4 returned DO-NOT-CLOSE (2026-07-31)

**Ruling: DO-NOT-CLOSE. Critical 0, high 3, medium 3, low 3** — **nine distinct
defects from twelve reports** (two were each found twice); one refuted. Run
against a clean tree at `0aef745`.

Five finders swept five surfaces, each in an isolated git worktree, each required
to build and run; each finder was then attacked by an independent skeptic with its
own worktree, told to reproduce or refute and to **default to REFUTED when
uncertain**. Eleven agents total. The main repo was untouched throughout.

**The count is coming down** — #2 was 0/2/3/3, #3 was 0/4/5/7, this is 0/3/3/3 —
**but the character of the findings has changed, and that is the thing to act
on.** Nine of nine survivors are the familiar shape (a rule applied at one site
and not its sibling). In earlier sweeps those siblings were *old*: a 1.6.x rule
not carried to a 1.7.x site. **Six of these nine are siblings of fixes shipped in
the last three patch releases, and one was introduced by the head commit itself.**
The sweep has essentially stopped finding pre-existing defects and is now finding
the incompleteness of its own recent fixes, at roughly the rate the fixes retire
them.

| Defect | Sibling of | The gap |
|---|---|---|
| **AZ** boot census duplication | AM (1.7.16) | Offline term added to the reset path; the boot path seeds it 53 lines too late |
| **BA** rooms→objs skip | AJ (1.7.15) | Guard correctly keyed on a return code — from a function that is never called |
| **BB** login parse leak | U (1.7.8) | Parse deferred, not removed; the post-auth half was never measured |
| **BC** refused-duplicate census | AE (1.7.12) + AM (1.7.16) | AE disowned the record; AM later made that same teardown own a census |
| **BD** `classes_upkeep` frozen | AK (1.7.16) | AK unfroze the mob half of one phase gate, not the player half, ten lines away |
| **BE** `parse_uint` in `toml_int` | AR (1.7.17) | The fix itself, applied at the wrong altitude, breaking its second caller |
| **BF** account double-count | AL (1.7.16) + AO (1.7.15) | AO added the two-flow discriminator 21 lines above; the increment never got it |
| **BG** PHASE_CLASS deadline | AI (1.7.14) | AI moved the reap *budget* to `session_persistable`; the *deadline* four lines away stayed on `SS_AUTHED` |
| **BH** silent `start` id | its own function's `WL_ERR_DANGLE` rule | Ten lines apart, opposite policies for the same shape of typo |

**The mechanical answer is small and specific, and it is a process change rather
than a code change:** when a fix changes a predicate, **grep every call site of
that predicate and every caller of the function it lives in, and record the
enumeration in the fix's own comment.** Three of these nine (`SS_AUTHED` vs
`session_persistable`, twice; `parse_uint`'s two callers) would have been caught
by one grep. Two more (AZ, BA) would have been caught by asking *"is my new guard
reachable on every path that reaches the thing it guards?"* — AJ's own note
already warns that copying a guard verbatim can be wrong; **the inverse warning,
that a correctly-keyed guard can be unreachable, is the one that was missing.**

### ✅ 1.7.18 — the boot sequence and the reader every table shares (SHIPPED)

**Items BE, AZ, BA and BH are CLOSED.** 1407 assertions (was 1387).
All four were verified A/B against a running server, not only in the suite:
the boot spawn went 13/13/13/13 → 13/12/12/12 across four restarts with one
object held offline; a one-character rooms typo now exits 1 where it used to run
on with no object table; and a typo'd `start` id now exits 1 where the boot log
used to be character-for-character identical to a correct configuration.

**Items BE, AZ, BA, BH.** *(1 medium, 2 high, 1 low — in fix order, not severity
order.)* One theme: everything that happens between process start and the first
player, plus the integer reader all of it depends on. One test story: **boot the
server against adverse data and against a populated `data/players`, and assert
what the loaders and the boot spawn actually did.**

**BE goes first and it is not negotiable** — it is a regression in the head
commit, and every hour it runs destroys more creation dates permanently.

---

**BE. AR's ordinal bound sits in the shared integer reader, so every `toml_int`
value above 1e6 silently takes its default — and `created` is destroyed on every
login.** *(medium — but FIX FIRST)*

- **What breaks.** AR added `if (v > PA_ORDINAL_MAX) { return 0 - 1; }` to
  `parse_uint` ([`parser.cyr:668`](../../src/parser.cyr:668), bound 1,000,000).
  Its comment reasons exclusively about the ordinal caller — *"this is an
  ORDINAL", "MAX_INV is 100"*. But `parse_uint` has a second caller: `toml_int`
  ([`mob.cyr:174,178`](../../src/mob.cyr:174)), the shared reader for every
  integer in every zone header, every class entry, and every field of every save
  record. `toml_int` reads `-1` as "unparseable" and returns `def`. **The value is
  not clamped — it is discarded and replaced by the default.**
- **The worst consumer** is
  [`persist.cyr:2268`](../../src/persist.cyr:2268): `store64(blk + IDENT_CREATED,
  toml_int(pairs, "created", get_epoch_secs()))`. The default is *now*, so the
  creation date is overwritten with the login moment on every login, on every
  server, and `_build_record` writes it straight back.
  `g_loaded_last_login = toml_int(pairs, "last_login", 0)`
  ([`:2341`](../../src/persist.cyr:2341)) reads 0, so the "last seen …" greeting
  at [`:2450`](../../src/persist.cyr:2450) is **dead code on every shipped
  server**. The same mechanism silently overrides operator config:
  `clamp_reset_secs`'s documented `RESET_SECS_MAX = 31536000` is now unreachable,
  and any `reset_secs` above 1e6 — a monthly cadence, well inside the documented
  range — reads as 900.
- **Demonstrated causally.** Rebuilt with the bound widened and logged the *same
  untouched on-disk record* in: `created` preserved, `last_login` advanced, and
  the login gained a line the shipped binary never prints. A four-point boundary
  probe through `data/classes.cyml` (999999 / 1000000 / 1000001 / 1000002) pinned
  the cliff at exactly `PA_ORDINAL_MAX` and showed the failure mode is
  discard-to-default, not clamp.
- **Why the suite is green, and it is damning.** Every test that plants
  `IDENT_CREATED` uses 1, 100, 999, 1234567 — or **exactly 1000000, the largest
  value that still parses**. The records in the working tree show it directly:
  `created = 1000000` beside `last_login = 1785543497`.
- **This file predicted it in writing.** M14-D says the `parse_uint` overflow fix
  affects *"every `toml_int` caller — class stats, save fields, zone fields —
  **which is why it did not land in a patch release**."* It landed in a patch
  release anyway.
- **Whose code.** Ours. **Fix size.** ~6 lines: move the bound out of `parse_uint`
  and into `qual_parse`, which is the caller that actually has an ordinal domain,
  and give `parse_uint` a real i64 overflow check instead (bail when
  `v > (I64_MAX - d) / 10`). Add a regression test that round-trips a record with
  a **genuine epoch-second** `created` rather than a small literal.

**AZ. The boot object spawn runs before the offline census is seeded, so every
restart mints a fresh copy of every object an offline player is carrying.**
*(high)*

- **What breaks.** `cmd_serve` spawns the world's objects at
  [`server.cyr:1746`](../../src/server.cyr:1746), but `persist_init()` — which
  seeds the offline census 1.7.16 added — does not run until
  [`server.cyr:1799`](../../src/server.cyr:1799), **fifty-three lines later**.
  During the boot spawn `g_obj_offline` is still zero, so the offline term at
  [`item.cyr:1026`](../../src/item.cyr:1026) contributes nothing. The boot spawn
  asks "how many are lying in rooms?", gets "none", and re-mints the full authored
  complement while offline players still hold theirs in signed records.
  `zone_reset_room_objs` only ever refills, never removes, so the surplus is
  permanent for the process — and ordinary play moves it into another player's
  record before the next restart.
- **Can it happen today? Yes, on every restart** of a live server, which
  [`running.md`](../guides/running.md) actively recommends as the shutdown path.
  No malice, no admin verb, no malformed data. One extra copy of *every* authored
  object, per restart, forever.
- **Demonstrated, twice, independently.** `relic` is authored exactly once
  (`data/zones/hub.rooms.cyml:234`); after three clean SIGTERM restarts **four
  copies were live in one world simultaneously** — three in player records, one on
  the shrine floor. Causation was then proved by patching `persist_init()` above
  the boot spawn, rebuilding, and watching the boot count drop 13 → 12 against
  byte-identical on-disk state, then reverting and watching it return to 13.
- **Not a rediscovery of AM.** AM's fix demonstrably *works* on the periodic-reset
  path in the same process where the boot path fails (`@reset` correctly answers
  `objs +0` while the boot spawn had already over-minted). **AM's own closure
  evidence was six get/quit/reset/relog cycles — no restart was ever performed.**
  The existing ordering test pins the seed against the ready flag *inside*
  `persist.cyr` and says nothing about `server.cyr`.
- **Whose code.** Ours. **Fix size.** 2–5 lines: move the boot `zone_reset_objs()`
  call below `persist_init()` — cleaner than hoisting `persist_init` up, which
  would reorder config load relative to the fatal guards. Add a test asserting the
  boot spawn count drops when `data/players` holds an authored id.
- **Fix the comment in the same edit.** [`item.cyr:1024`](../../src/item.cyr:1024)
  and `state.md` both still say the census *"refreshes at the top of each reset
  pass"*. That stopped being true in 1.7.16, and it is exactly the sentence that
  would have stopped someone noticing this hole.

**BA. One typo in the *rooms* file makes the server skip the object loader
entirely, and every player's inventory is silently and permanently emptied.**
*(high)*

- **What breaks.** `world_load_objs(DP_OBJS)`
  ([`server.cyr:1702`](../../src/server.cyr:1702)) is nested *inside*
  `if (wl == WL_OK)`, where `wl` is the **rooms**-loader result. A rooms rejection
  takes the else arm at [`:1755`](../../src/server.cyr:1755), prints *"running
  roomless"*, and carries on — so the object loader never runs and
  `g_obj_tpl_count` stays at 0. That is byte-for-byte the state AJ declared
  unsurvivable: `_restore_inv` ([`persist.cyr:1960`](../../src/persist.cyr:1960))
  resolves every saved id through `obj_tpl_by_id`, every lookup fails, the ids are
  dropped, and `drop_session` writes the emptied inventory back signed.
- **AJ's fix is present and unreachable.** AJ keyed its fatal guard on
  `world_load_objs`'s return code, which is *correct* — and on this path the
  function is never called, so the guard cannot fire. The comment at
  [`server.cyr:1715`](../../src/server.cyr:1715) warning of *"silent,
  irreversible, playerbase-wide data loss"* sits inside the block that cannot be
  reached. **A 1.7.17 server — the release that shipped AJ — still empties
  inventories.**
- **Can it happen today? Yes**, from operator error, with one character connecting
  once. Six distinct one-edit routes to a rooms rejection were confirmed: a
  dangling exit target (-6), a missing `kind` (-4), no id (-5), a NUL or oversized
  id (-6), 33+ entries (-3), an empty or moved file (-1/-2). It also fires if
  `data/zones/` is moved or the file renamed. **`hub.rooms.cyml` is the largest and
  most frequently edited file in the zone set — this is *more* likely to fire than
  AJ was.**
- **Irreversible.** Records are signed with a key derived from the player's
  passphrase (ADR 0004). The loss survives repairing the file that caused it.
- **Demonstrated** twice, on two players, via two different rejection codes. Boot
  log shows no "object templates" line at all; the server does not exit 1; a
  player who connects, authenticates, types *nothing*, and is RST-closed gets
  "Some of what you carried is no longer part of this world" and their record reads
  `inv = ""`, `room = ""`.
- **Why the suite misses it.** The existing test asserts by *source offset* that
  the objs fatal arm sits below the objs load. That is ordering. **Nothing asserts
  the objs load is *reachable* when the rooms load fails**, which is the structural
  fact that is wrong.
- **Whose code.** Ours. **Fix size.** ~10 lines: make a rooms rejection fatal the
  way objs (AJ) and classes (AD) already are. The "running roomless" affordance
  buys nothing — a roomless server cannot run the game, and its only observable
  effect is emptying inventories.
- **A note on severity.** This meets the *letter* of the critical bar —
  playerbase-wide irreversible data loss. It is graded high only to stay consistent
  with AJ, which this project graded high for identical impact through the sibling
  file. If the bar is ever re-baselined, both belong at critical.

**BH. A typo in the zone header's `start` id is silently ignored; the identical
typo in an `exit_` id refuses the whole zone.** *(low)*

- Ten lines apart in `world_load_rooms`: `exit_<dir>` naming a nonexistent room
  returns `WL_ERR_DANGLE` and tears the world down
  ([`world.cyr:405`](../../src/world.cyr:405)), while the same lookup on the
  header's `start` id has **no else arm and no diagnostic**
  ([`:414-417`](../../src/world.cyr:414)). `g_start_room` keeps its initialized 0
  and the boot log is character-for-character identical to a correct
  configuration.
- **The blast radius is wider than new characters**: `world_start_room()` is also
  the fallback for a save whose recorded room no longer resolves, and the
  death-respawn target.
- A three-way probe with a valid-but-different control confirmed the key works
  when the id resolves, so the typo case is a **silent ignore**, not a no-op key.
- **Cut from medium to low**: nothing is lost, nothing crashes, no peer can
  trigger it, the world stays playable. **The defect is the silence.**
- **Whose code.** Ours. **Fix size.** ~4 lines — a `WL_ERR_NOSTART` through
  `_wl_rooms_fail`, or at minimum a boot diagnostic naming the id that did not
  resolve.

### ✅ 1.7.19 — sessions in unusual states (SHIPPED)

**Items BC, BD, BF and BG are CLOSED.** 1436 assertions (was 1407).

**BC was proven at the counter, not at the room.** Several live A/B attempts
failed to discriminate — the end-to-end observable is whether a room restocks,
and the periodic reset drives that too, so the signal is easy to lose behind it.
Asserting `obj_offline_count` directly settled it in one test, with a
counterfactual showing the pre-1.7.19 teardown **invents 2 holdings from nothing**
after a clamped restore while the new one moves the count by 0.

**A test fixture was found lying.** `_mk_sess` memset `SS_ROOM` to 0 where
`session_new` stores -1, so every creation test had been exercising AO's *resume*
path rather than the *enter* path it meant to. That is the fixture that hid BF.

**Items BC, BD, BF, BG.** *(2 medium, 2 low.)* One theme: a session that is **not
a normal logged-in player** — a refused duplicate, a character parked in the class
or passphrase menu, a healed classless record — corrupts a counter or freezes its
own upkeep. One test story: drive a session into each non-`PHASE_CMD` state and
each refused-login path, and assert the counters and the upkeep.

**BC. A refused duplicate login makes the server believe objects still exist, and
they are then never respawned again.** *(medium)*

- `login_on_pass` calls `player_auth_load`, which restores the inventory inside
  `_restore_inv` and **debits** the offline census one per resolved id
  ([`persist.cyr:1976`](../../src/persist.cyr:1976)). Only then does AE's arm at
  [`:2405`](../../src/persist.cyr:2405) notice the character is already connected
  and refuse. But the precondition for refusing is that the live session already
  claimed those holdings, so the counter is at zero and `obj_census_adjust`'s
  underflow clamp at [`:1925`](../../src/persist.cyr:1925) swallows the debit —
  while `drop_session`'s unconditional `session_drop_inv`
  ([`server.cyr:855`](../../src/server.cyr:855)) **credits unclamped**
  ([`item.cyr:123-128`](../../src/item.cyr:123)). Net: permanent **+N phantom
  offline holdings**, N = that record's inventory size. `_obj_id_world_count` then
  believes the world is at its ceiling and the zone stops restocking.
- **AE's own comment reasons about this teardown** and concludes *"Item
  duplication was chased here too and is NOT a risk — `session_drop_inv` frees the
  copies."* True in 1.7.12; **AM taught `session_drop_inv` to credit the census
  four releases later and the arm was not re-examined.**
- **Fires by accident on the single most common MUD failure mode: link-death.** A
  player whose connection dies silently leaves a session held for `YD_IDLE_MS`
  (default 5 min); their reconnect is refused as a duplicate and poisons the
  census by their whole inventory. Needs the correct passphrase, so it is the
  owner, not an attacker.
- **Demonstrated** as matched A/B pairs by both skeptics. One escalated it: a
  *single* refused reconnect on a record holding three different authored ids
  erased all three from the world for the life of the process — twelve consecutive
  resets at `objs=0`, all three rooms visually empty to a fresh character. The
  other added two controls (a wrong-passphrase duplicate, and a duplicate on an
  empty-inventory character); both behaved like the control, **localising the
  defect precisely to `_restore_inv` running before the refusal.**
- **Severity: medium, not high.** "Permanent" here is process-scoped — the census
  is rebuilt from disk at boot. No player data is lost, nothing crashes. But it is
  the strongest medium in this set: one ordinary player carrying at the `MAX_INV`
  cap can suppress **every authored object in the world** until the operator
  restarts. Ironically **AZ then restocks the suppressed objects at that same
  restart** — which is part of why neither has been seen before.
- **Whose code.** Ours. **Fix size.** ~5–10 lines: a `session_discard_inv(s)` that
  walks `SS_INV` calling `obj_free` **without** `obj_census_adjust`, called in the
  refusal arm beside the existing `store64(s + SS_AUTHED, 0)`. The asymmetric
  clamp at `persist.cyr:1925` deserves a comment saying it is a general hazard.

**BD. Cooldowns, energy and timed buffs stop advancing the moment a player opens
the passphrase prompt.** *(medium)*

- `combat_tick_all` ([`server.cyr:1386-1390`](../../src/server.cyr:1386)) wraps
  **both** of its jobs in one `SS_PHASE == PHASE_CMD` gate: the combat round *and*
  `classes_upkeep(s)`. AK (1.7.16) fixed the half that let a player go
  invulnerable — it made `mob_tick_all` swing at a player in a non-CMD phase. It
  did not touch `classes_upkeep`, which is the only decrementer of
  `SS_CD0/1/2`, `SS_GUARD` and `SS_STIM` and the only source of energy and
  out-of-combat HP regen. **All five freeze.**
- **The phase is held open indefinitely by a peer**: `chpass_on_new` re-prompts
  forever on an out-of-range length with **no attempt counter** (unlike
  `_chpass_mismatch`, which does count), and every rejected line refreshes
  `SS_LAST_MS`, so the reaper never fires.
- **Demonstrated at three independent observables**: energy unchanged after 10–12
  ticks parked; the cooldown counter read as a *number* out of `self_prep` still
  at its authored 3 after ten ticks; and a real sustained fight against the 45-HP
  Foundry Sentinel confirming mobs do swing during the park.
- **The harm story was corrected during verification and the correction stands.**
  The finder called it "unbounded damage mitigation in a menu". The skeptic fought
  a real mob and the parked player **died anyway** — 25 damage over 12 ticks with
  GUARD held at 3. Most of the freeze runs *against* the player (no regen, no
  cooldown decay); the exploit buys −3 AC while you are helpless. Real,
  demonstrable, bounded in value. **Medium is the ceiling.**
- **Whose code.** Ours. **Fix size.** ~4 lines in `combat_tick_all` — keep the
  combat round behind the `PHASE_CMD` gate, lift `classes_upkeep(s)` out and run
  it for every session in the world (`session_room_ok`), which is exactly the set
  AK decided mobs may swing at. Plus ~5 lines to give `chpass_on_new`'s length
  rejections the counter `_chpass_mismatch` already has.
- **One measurement trap, recorded because it will bite the next sweep.** This
  test **falsely passes at a fast tick**: at `YD_TICK_MS=200` the first two runs
  read full energy and no buff, purely because 3+ ticks fired between finishing the
  re-key and reading the status. Pipelining does not help — the confirm line's
  derive+sign exhausts the per-pass crypto charge window, so the following line is
  retained. **Only a slow tick (3 s) plus a read fired ~1 RTT after acknowledgement
  separates the hypotheses.**

**BF. A character whose class no longer resolves burns a second account slot every
time it is healed.** *(low)*

- 1.7.11's classless-record heal
  ([`persist.cyr:2472`](../../src/persist.cyr:2472)) sends an **existing**
  character back to `PHASE_CLASS`, and `login_on_class` ends with AL's
  unconditional `g_account_count = g_account_count + 1`
  ([`classes.cyr:366`](../../src/classes.cyr:366)) for a record
  `accounts_count_disk()` already counted at boot. Nothing decrements. **AO
  already established twenty-one lines above that this function now serves two
  flows** and added the `SS_ROOM < 0` discriminator for the room; the account
  increment three lines further down never got it.
- Reproduced end to end by both agents: rename the four class ids in
  `data/classes.cyml`, heal two characters, and a third creation is refused with
  "This world is not accepting new characters" at cap 3 with two files on disk —
  with a restart-only control confirming the refusal was purely the phantom
  increments.
- **Cut from medium to low**: it needs an off-by-default knob (`max_accounts`)
  *and* an operator class-table edit, causes no loss, and clears on restart.
- **Fix size.** ~3 lines, using AO's existing discriminator.

**BG. A peer parked at the class menu gets the five-minute player grace instead of
the 30-second slowloris deadline.** *(low)*

- `session_is_idle` ([`session.cyr:1911`](../../src/session.cyr:1911)) keys the
  deadline on `SS_AUTHED`, which is set in `login_on_confirm` **before** the class
  menu is shown. So `PHASE_CLASS` — no class, no room, no record on disk, and
  since AL not even an account slot — gets the logged-in player's deadline.
  **`sweep_idle` already knows better**: AI (1.7.14) changed the reap *budget* to
  `session_persistable(s)` four lines away and left the *deadline* on `SS_AUTHED`.
- **The severity was refuted with a counterfactual the finder never ran**, and it
  is decisive: 256 raw sockets that send *not one byte* refused a legitimate client
  on 13 of 14 probes over 75 s, opened in 0.02 s versus 7.47 s for the class-menu
  route — **375× cheaper**, needing nothing from the login flow. Fixing this makes
  the squat churn every 30 s instead of holding seamlessly for 300, restoring
  roughly a 1-in-14 window for an honest player. **That is an availability
  improvement, not a resource exhaustion the bug enables. Low.**
- **The obvious fix has a cost the finding did not mention**: a genuine new player
  then has 30 s to read four class descriptions and choose. **Fix size.** 1–2
  lines — and consider a middle deadline (60–90 s) rather than the bare pre-auth
  one.

### ✅ 1.7.20 — the login parse (item U's second arm) (SHIPPED)

**Item BB is CLOSED, and with it every finding from gate re-run #4.**
1476 assertions (was 1436). **Measured 2,332 → 84 bytes per login, a 96% cut.**

**The instrument is the durable part.** `bench_persist`'s login arm had ceiling
`999999` — ungated — with a written rationale that the path was "dominated by the
same libro/str allocations as the save". That rationale was wrong about whose
allocation it was, and it is why item U survived its own fix for twelve releases.
The arm now gates at 256 and was **verified to FAIL (exit 1) at 2,332 B/op when
the fix is disabled**.

**`_fint` writes integers UNQUOTED and the scanner was quoted-only** — a
canonical-form test that knew one shape would have vouched for records whose every
integer then read as its default, which is 1.7.19's BE exactly. Caught because
`_scan_canonical` is strict-or-fall-through: it refused every real record until
both shapes were handled, rather than silently half-reading them.

**Item BB alone.** *(1 high.)* The largest single fix in the batch and the only
one that is a rewrite rather than a correction, which is why it gets its own
release. **File it as item U's second arm, not as a new item.**

**BB. Every successful login permanently burns 2,248 bytes the process can never
reuse.** *(high)*

- **What breaks.** `player_auth_load` calls
  `toml_parse(str_new(g_persist_slurp, n))`
  ([`persist.cyr:2109`](../../src/persist.cyr:2109)) to read the record's ~25
  fields. The bump allocator has no free (`lib/alloc.cyr`), and **`alloc_reset` is
  called nowhere in `src/`**. 1.7.8 (item U) fixed the *pre-authentication* half by
  adding the strict `_scan_kv` fast path that derives, compares and returns early,
  so a wrong passphrase now allocates nothing. **A *right* passphrase falls
  straight through that early return into the same untouched `toml_parse`** and
  pays the full cost, on every login, forever.
- **Measured twice, independently.** 2,265.9 B/login over 19,167 logins at
  106.5/s; and 2,265.1 B/login over 15,000 logins at 108.3/s — dead linear, no
  plateau. Both attributed it in-process: a bare `toml_parse` of the 506-byte
  record costs 2,248 B, and ten consecutive successful `player_auth_load` calls
  cost 22,480 B — **2,248.0 each**. That is **883 MB/hour from one sequential
  socket**, and the rate is the server's own ed25519 ceiling, not the client's.
- **Can it happen today? Yes.** Registration is unlimited by default
  (`max_accounts` defaults to 0 and no `data/server.cyml` is required), and
  **there is no login rate limit anywhere** — the `passwd` limiter (1.7.1) does not
  cover login.
- **Whose code.** Ours. **Fix size.** ~60–90 lines: extend `_scan_kv` to cover the
  post-auth field set the way 1.7.8 did for the pre-auth one, so the successful
  path never constructs a `toml_parse` vec. **Gate it with a bench that asserts
  bytes-per-login and FAILS when reverted** — that is the instrument whose absence
  let this survive 1.7.8's own fix.

### Refuted — do not resurrect

**`save_sweep` gates `player_save` on `SS_AUTHED` where `drop_session` and
`shutdown_save_all` use `session_persistable`.** The code observation is accurate
([`server.cyr:248`](../../src/server.cyr:248)), but **the cell is unreachable**,
and the finder said so themselves with an explicit negative result. Closed
independently rather than on trust: `save_sweep_due`'s first line requires
`SS_SAVE_DIRTY`, and there are exactly three writers of that flag in the tree —
[`session.cyr:1606`](../../src/session.cyr:1606) (PHASE_CMD-only dispatch),
[`item.cyr:900`](../../src/item.cyr:900) (reached only via `room_find_player`,
PHASE_CMD-gated), and [`combat.cyr:310`](../../src/combat.cyr:310) (needs a mob
whose target is this session, and both setters require the player to have attacked
first). Meanwhile `SS_CLASS < 0` exists only in `PHASE_CLASS` — three store sites.
**The conjunction has no constructor.** It is a one-line hygiene alignment, not a
defect, and it should not consume a roadmap slot.

### What gate re-run #4 had no instrument for

**The three gaps re-run #3 named:**

1. **Offline-population conservation — covered as a one-off, NOT as an
   instrument.** The conservation finder built the harness #3 said did not exist
   (an instrumented binary printing `offline / world / authored` per reset pass)
   and it immediately produced **two** of this run's defects (AZ, BC). But it was a
   throwaway probe, reverted at the end of the run.
   **`world_count + offline_record_count == authored_count` still does not exist as
   a test, a bench, or a fuzz target, and it should** — it is the assertion that
   would have caught both AM and AZ. Also: nothing in the tree reads
   `g_obj_offline` directly, so every census measurement in this run is a threshold
   oracle (`@reset`'s `objs +N` plus a `look`) that **cannot distinguish a phantom
   count of 1 from 5**. *This is the single highest-value instrument to build, and
   it belongs in `cyrius audit`.*
2. **Phase × tick — substantially covered on one driver, untouched on the other.**
   The real matrix is **8 × 5 = 40**, not #3's assumed 56: four of the seven tick
   consumers are global rather than per-session, and `drain_pending_rx` moved off
   the tick path in 1.7.0. The clean cells are recorded so they are not re-swept:
   `maybe_zone_reset` × PHASE_CHPASS (looks like a peer-held denial, is not — an
   AFK player in PHASE_CMD blocks resets identically), `render_who` vs `@stats`,
   `line_crypto_bound`'s PHASE_CLASS pre-charge, and `session_free`'s
   `SS_IDENT_CAND` wipe. **Still open:** the `--agnos` poll-loop variant of
   `advance_tick` is a **second, separate driver** and every cell would have to be
   re-checked there; and what the tick does to a session in `PHASE_CLASS` with
   `SS_ROOM >= 0` (the heal state — an in-world body that `room_say_broadcast`,
   `room_append_present`, `cmd_who` and `find_player_global` all skip on their
   PHASE_CMD gates while `zone_has_player` counts it).
3. **CYML loader fuzz coverage — still open, half-closed.** 31 hand-authored
   structural mutations (truncation at every boundary, embedded NUL, 0xFF/0xFE
   prose, duplicate ids and keys, self-referencing exits, 400-byte ids, 4000-byte
   titles, 321 entries against `MAX_ENTRIES=32`, 23-digit and negative integers)
   across all five loaders produced **no crash, hang, or out-of-bounds read** — the
   rejection arms are genuinely robust. **But 31 samples is not coverage.** AX
   closed the *record-parser* target; `cyrius fuzz` still contains **no CYML loader
   target at all**.

**Re-run #3's fourth gap — two players under one tick — is now ANSWERED, and the
answer is a clean negative worth recording.** Every contended ordering that could
be constructed — both players `get` the same object in one epoll batch, `put`/`get`
on one container, `give` across a simultaneous RST-close, a shared mob kill with a
stale `SS_TARGET`, a raced `get all from corpse` — **serialised and conserved
correctly**. The object-conservation defects live in the **census accounting**, not
in the command interleaving. **Do not re-sweep the interleavings.**

**New gaps this run leaves open — these are what gate re-run #5 should target:**

- **AGNOS has never been executed by any sweep.** All ten agents ran x86_64 only.
  `running.md` already declares AGNOS persistence unverified end-to-end since
  1.7.8. **This is now the single largest untested surface in the tree, and it is a
  second copy of the event loop.** The agnosticos repo's `docker/descent-sweep/`
  harness exists for exactly this.
- **Audit-log rotation under volume.** The heaviest run in this sweep — 19,167
  logins, 400 creations, 250 concurrent sessions — produced 47 kB of
  `data/audit.libro`, **two orders of magnitude below the 8 MiB rotation trigger**.
  Segment sealing, `_audit_prune`, the `AUDIT_SEG_KEEP = 4` window and the collision
  guard have never been exercised on a running server. Forcing it needs a lowered
  constant in a throwaway build.
- **The broadcast fan-out breach point (item K / 2.0) is still unanswered.** 250
  co-located players idle cost 0.83–2.50 ms CPU per tick with drift p99 at 13 ms
  against a 50 ms allowance; one 200-byte `say` to 250 players costs 1.75 ms
  (~7 µs/recipient). But nobody could keep 250 players in *sustained* combat — the
  horde kills the room's mob faster than resets respawn it — so the combat arm
  measured the same thing as the idle arm. **That needs a bench change, not a TCP
  probe.**
- **Nobody forged a record signature.** Several findings have a player-driven
  variant reasoned from ADR 0004's threat model (the player owns their signing key)
  rather than measured. A signing harness would close it.
- **No multi-hour soak.** The longest continuous run was ~11 minutes. BB's
  2,265 B/login slope is measured-linear across 36 MB; the OOM timeline is
  extrapolated from it, not observed.
- **Not filed as a defect:** 256 raw sockets that never send a byte refuse
  legitimate connections on 13 of 14 probes and refill instantly as the 30 s reaper
  collects them. That is inherent to a 256-slot server with no connection-*rate*
  limiting — `MAX_SESSIONS` and the 1.6.3 accept backoff bound concurrency, not
  arrival rate, **the same lever item AA already names**. Worth a decision
  alongside AA rather than a new item.

---

## Open issues — gate re-run #3 returned DO-NOT-CLOSE (2026-07-31)

**Ruling: DO-NOT-CLOSE. Critical 0, high 4, medium 5, low 7** — 16 distinct
defects from 19 candidates (two were each found twice); one refuted. Run against
a **clean tree at `84c9a3a`**.

**The change that made this run different: the finders could BUILD AND RUN.**
Re-run #2 executed nothing, and said so in its own limits. This one gave every
finder an isolated git worktree and told it to measure rather than estimate —
whereupon three of the four highs were demonstrated **against a live server over
TCP**, not inferred from source. The main repo was untouched; every probe stayed
in its worktree.

**The pattern, for the fifth consecutive sweep, and it is now unmistakable:**
three of the four highs are *a rule applied at one site and not its sibling*, and
**two of them are siblings of fixes this very release line shipped.**

### ✅ 1.7.15 — the operator-edit blast radius (SHIPPED)

Items AJ, AN and AO are **closed**. 1340 assertions (was 1310), 9/9 mutations
killed. AJ was re-verified live: the one-character typo now makes the server
**exit 1** instead of carrying on and emptying every inventory.

**AJ's boot guard is keyed on the loader's RETURN CODE**, not on
`g_obj_tpl_count == 0` the way the class guard is — a zone that authors no objects
is legitimate and loads successfully with a count of zero, so the two tests are
not interchangeable. Worth recording, because copying the class guard verbatim
would have been wrong.

**AN migrates lazily and reads BOTH forms.** ADR 0004 means there is no offline
migration and cannot be, so old records load by index and are rewritten by id at
their next save. No schema bump.

**One near-miss worth keeping:** the new audit key was first added as
`AK_LOAD_INV_DROP = 21` against `AK_NKEYS = 20`. Nothing crashes — the guard in
`audit_keyed` catches an out-of-range key and falls through to a verbatim
`audit_event` — but every occurrence then costs **1944 permanent bytes**, which is
the 1.7.1 defect reintroduced one key at a time. The comment at that guard
predicts this exact mistake, and predicting it is not the same as checking it.

### 1.7.15 — the three items (detail, retained)

**AJ. One typo in a zone objects file silently and irreversibly empties every
player's inventory.** *(high — CLOSED in 1.7.15)*

- **What breaks.** `world_load_objs` unpublishes the whole table on any failure,
  and [`server.cyr:1709`](../../src/server.cyr:1709) prints a diagnostic and
  **carries on**. With the table empty, `_restore_inv`
  ([`persist.cyr:1760`](../../src/persist.cyr:1760)) silently drops every id that
  will not resolve — no count, no audit line — and `drop_session` then saves the
  emptied inventory. **Irreversible**: records are signed with a key derived from
  the player's passphrase (ADR 0004), so no operator repair exists.
- **Measured live.** A **one-character** edit (`kind = "obj"` → `"objj"` on one of
  ten entries): a player who connects once and is RST-closed **typing nothing**
  loses everything; a player who never connects keeps their items; repairing the
  file does not bring the first player's back.
- **This is verbatim the shape 1.7.11 made fatal for `data/classes.cyml` —
  35 lines below, in the same function**, under a comment explaining exactly why
  carrying on is catastrophic. The class table got the guard; the object table
  did not. Fixing the instance and not the class, in this line's own code.
- **Fix size.** ~10 lines: make a rejected objs file fatal as
  [`:1746`](../../src/server.cyr:1746) already does, and/or refuse to SAVE an
  inventory whose ids failed to resolve. Count and audit the drop either way.

**AN. `class` is persisted as a positional index into `data/classes.cyml`.**
*(medium — CLOSED in 1.7.15)* — adding or removing a class silently re-assigns every existing
character. `room` is stored as a stable id string **four lines away**
([`persist.cyr:1498`](../../src/persist.cyr:1498)), and ADR 0006 states the rule
in the same sentence that lists `class`. Reproduced: prepend one entry and a
Chaplain logs in as a Courier — `patch` answers "You don't know how to patch."

**AO. The 1.7.11 classless-record heal throws away the loaded room.**
*(medium — CLOSED in 1.7.15)* — the heal returns without
resuming, so `login_on_class` runs `session_enter_world` and the player is
silently moved to the start room, permanently. Reproduced: `hub.flagon` →
`hub.gate`. **Fix: the heal must call `session_resume_world`.**

### ✅ 1.7.16 — reachable by a peer today (SHIPPED)

Items AK, AM and AL are **closed**, and with them **every high from gate re-run
#3**. 1362 assertions (was 1340), 10/10 mutations killed. AM re-verified live: six
get/quit/reset/relog cycles, still one copy (the sweep measured seven).

**The AM census was wrong twice before it was right**, and both were caught by
measuring rather than reviewing:
- Rebuilding it per reset is correct but costs **~70 kB of permanently lost arena
  per rebuild** (`dir_list` / `str_from` allocate; `alloc` has no free) — 1.7.1's
  item-C shape reappearing *inside the fix for a different unbounded-growth bug*.
  It is now seeded ONCE at boot and moved by login and disconnect.
- Seeding it from `persist_init` **before** the ready flag recursed forever,
  because the builder calls `persist_init` itself. A test pins the ordering.

**A pre-existing test then failed under `cyrius audit` and passed under
`cyrius test`.** The difference was real: the reset now consults offline holdings,
so anything driving `zone_reset_room_objs` depends on what is in `data/players`
when the process starts. That test now controls its own precondition — but the
coupling is new, and worth remembering before adding more reset-driven tests.

### 1.7.16 — the three items (detail, retained)

**AK. Typing `passwd` mid-fight makes you permanently immune to the mob you are
fighting.** *(high — CLOSED in 1.7.16)*

- `combat_tick_all` gates the whole round on `SS_PHASE == PHASE_CMD`
  ([`server.cyr:1383`](../../src/server.cyr:1383)); `mob_tick_all`
  ([`mob.cyr:782`](../../src/mob.cyr:782)) has **no phase check at all**, so the
  two disagree about what a phase means. `PHASE_CHPASS_NEW` re-prompts forever on
  any line under `PASS_MIN` and refreshes `SS_LAST_MS` each time, so the idle
  reaper never fires either.
- **Measured live** at the authored 2.5 s tick: engaged and idle → 8 combat lines
  in 10 s; engaged in `PHASE_CHPASS_NEW` → **0 combat lines in 40 s**, no idle
  reap; re-key completed → combat resumes on the same engagement. At 1 HP this is
  unbounded invulnerability from two shipped verbs.

**AM. An object is duplicated on every logout/reset cycle.** *(high — CLOSED in 1.7.16)*

- `_obj_id_world_count` ([`item.cyr:994`](../../src/item.cyr:994)) sums room
  contents plus **online** sessions — and `maybe_zone_reset` defers while any
  player is in-world, so the session term is **provably always zero** on that
  path. The server has no view of objects held by players who are offline, and
  `_restore_inv` mints with no ceiling.
- **Measured:** `get` / `quit` / wait one reset / log back in, six times →
  `inv = "notice,notice,notice,notice,notice,notice,notice"` against an authored
  ceiling of 2. **On the unique authored artifact: `relic` → five copies.** A
  player can mint unlimited copies of a one-of-a-kind item.

**AL. The account cap counts sealed identities, not records.** *(high — CLOSED in 1.7.16)*

- `g_account_count` is incremented when the identity is sealed
  ([`persist.cyr:2451`](../../src/persist.cyr:2451)) and **there is no decrement
  anywhere in the tree** — the record is not written until class selection.
- **Measured:** **200 slots burned in 0.46 s (436/s)** from one reused name and a
  27-byte payload, unauthenticated, with **zero records on disk**; a genuine
  player is then refused with "This world is not accepting new characters."
- **1.7.11 widened this.** Before that release, abandoning at the class menu still
  wrote a classless record, so the burn was at least backed by a real account.
  `session_persistable` correctly stops that write — and thereby made the phantom
  count permanent until restart. *(Reasoned from the code, not separately
  measured; the judge measured the current behaviour.)*
- Off by default, which is the only thing keeping it below critical.
  `docs/guides/running.md:94-97` documents behaviour the code does not have.

### ✅ 1.7.17 — mechanics and instruments (SHIPPED)

Items **AP, AQ, AR, AT, AU, AV, AW, AX, AY** are closed and **AS is documented as
a content rule** — so **every finding from gate re-run #3 (AJ-AY) is now closed**.
1387 assertions (was 1362), 9/9 mutations killed, 2/2 fuzz targets.

**The instrument work is the part worth remembering.** The M2-F fuzz gate fed a
NEGATIVE length on 49,585 of 100,000 iterations and had never once executed
`pa_emit_byte`'s cap branch — the guard F3 (1.6.11) exists for — while reporting
PASS for eleven releases. Fixing the sign was not enough: random bytes produce
delimiters, so the TOKEN cap tripped first and `PA_NORM_LEN` still peaked at 747
of 4096. A quarter of iterations now generate delimiter-free runs, `NORM_CAP` is
reached **7,988 times per run**, and **the harness asserts its own coverage** so
it fails if the inputs ever stop reaching the guards.

**Two of the six benches in the audit gate could not fail.** `bench_telnet` now
gates at 30 ns/byte (measured 5-6), verified to exit 1 when breached; the scaffold
placeholder announces itself so "6 passed" is not misread as six checks.

**A second fuzz target** covers the pre-auth record scanner (`_scan_kv`), measured
at 12,383 matches / 87,617 rejections so both paths run. **The CYML zone loaders
remain uncovered**, and that is stated rather than implied away.

**AS is a content constraint, not a parser bug.** A noun spelled like a
preposition can never be a direct object; every candidate fix changed the meaning
of inputs that DO occur (`put a in` would become "put in"). ADR 0005 now states
the authoring rule and the suite pins the behaviour.

### 1.7.17 — the items (detail, retained)

**AP. A mob cannot kill you unless you have engaged it.** *(medium — CLOSED in 1.7.17)* —
`classes_upkeep` treats `SS_TARGET == 0` as "out of combat" and regenerates
([`classes.cyr:381`](../../src/classes.cyr:381)), but a mob that assists or leashes
onto you sets **its** target, not yours. Measured live: **70 incoming swings in
60 s, 24 of them hits, HP never below 36/40** and back to full every tick.

**AQ. The M2-F fuzz gate is a no-op on half its iterations.** *(medium — CLOSED in 1.7.17)* —
`fuzz/parser_fuzz.fcyr:74` feeds a **negative length on 49,585 of 100,000
iterations**; the longest input ever fed is **319 bytes**, `PA_NORM_LEN` never
exceeds **289 of NORM_CAP 4096**, and the `pa_emit_byte` cap branch — where F3
(1.6.11) lived — **has never executed**. Reproduced by replicating the shipped
seed and generator byte-for-byte.

**Low — ALL CLOSED in 1.7.17** (AS as documentation): **AR** `parse_uint` wraps silently so a 20-digit `N.X` ordinal
resolves to a real object; **AS** the preposition split starts at token 1, so a
noun spelled like a preposition can never be a direct object; **AT** `player_died`
changes persistent state without setting `SS_SAVE_DIRTY`; **AU** the hidden-roll
RNG is seeded from host uptime in ms; **AV** the `sig` hex-length guard is the one
member of its trio with no test — and neutering it yields a *demonstrated*
record-content-driven arbitrary file write; **AW** two of the six benches in the
audit gate **cannot fail** (`bench_telnet` has no budget constant and returns 0
unconditionally; `tests/*.bcyr` is an explicit no-op), so `cyrius audit` reports
6/6 while 2 are decoration; **AX** the fuzzer covers one source file and neither
the CYML loaders nor the record parser; **AY** the `MAX_SESSIONS` cap survives
deletion — the test named for it asserts something else.

### What this sweep had no instrument for

1. **Two players interacting *under a tick*.** Nothing here or in any prior sweep
   constructed a contended interleaving — both `get` the same object on the tick a
   corpse decays; A `give`s to B while B's `drop_session` is mid-save. The
   object-conservation defects confirmed above live in exactly that accounting.
2. **The whole offline population.** AJ, AL and AM all trace to one absent
   concept: nothing in the tree reads `data/players/` and checks it against the
   live world. **A conservation harness — for every authored id,
   `world_count + offline_record_count == authored_count` — would have caught AM
   four sweeps ago.** It does not exist as a test, a bench, or a fuzz target.
3. **Phase × tick, as a matrix.** AK is one cell of a **56-cell table** (8 phases ×
   7 tick consumers) that nobody has enumerated. Two cells are known-wrong;
   `save_sweep` ([`server.cyr:249`](../../src/server.cyr:249)) is a suspected
   third.
4. **The loaders' error arms as a class.** AJ, AN and AO are all "an operator edits
   a data file and the server runs on with a half-published table". `cyrius fuzz`
   includes exactly one project file; the CYML loaders and the record parse — this
   project's own designated untrusted inputs — have **no fuzz coverage at all**.

---

## Open issues — gate re-run #2 returned DO-NOT-CLOSE (2026-07-31)

**Ruling: DO-NOT-CLOSE. Critical 0, high 2, medium 3, low 3.** Five independent
finders swept distinct surfaces; every candidate faced three skeptics with
separate lenses (correctness / reachability / novelty) and had to survive a
majority; the judge then reproduced each survivor against the shipped tree.
**Nothing was dropped** — ten reports collapsed to **eight distinct defects**.

**The pattern that matters more than any single item:** four of the eight are a
rule this tree already applies somewhere else and did not apply here — the
unmetered teardown is *verbatim* the 1.7.0 finding, fixed in `drain_pending_rx`
and not carried to the epoll batch, in the release whose own comment says "ONE
constant for BOTH dispatch sites, on purpose". That is the fourth consecutive
sweep to report the same shape.

### ✅ 1.7.11 — the two highs (SHIPPED)

Items AC and AD are **closed**. 1259 assertions (was 1229), 10/10 mutations
killed, `cyrius audit` 0, 6/6 benches, both targets build.

**Both were verified against a running server, not only in the suite.** A player
holding an item across a SIGTERM now produces `server: saved 1 session(s) on
shutdown` with `inv = "notice"` on disk; a `kind = "clas"` typo in
`data/classes.cyml` makes the server refuse to start with **exit code 1** instead
of silently demoting every character on load.

**AD needed all three fixes, and any one alone leaves a hole:** the disconnect
gate stops new classless records, the **login heal** repairs the ones already on
disk (nothing else can — records are signed with a key the server never holds),
and the fatal boot stops the operator-typo path that demotes everyone at once.

**The lesson this release paid for:** mutation testing showed that removing the
`shutdown_save_all()` **call**, and removing the fatal boot check, each broke
**no test** — because the suite cannot run `cmd_serve`. That is *exactly what AC
was*: the function existed, and nothing called it. Both call sites are now
asserted from the source, as 1.7.8 does for the raw-syscall class.

### 1.7.11 — the two items (detail, retained)

**AC. A clean shutdown saves nobody.** *(high — CLOSED in 1.7.11)*

- **What breaks.** `cmd_serve`'s exit is `println` → `audit_flush_all()` →
  `sock_close(lfd)` → `return 0` ([`server.cyr:1834`](../../src/server.cyr:1834)).
  It never walks `g_session_head`, and `handle_signal`
  ([`:1474`](../../src/server.cyr:1474)) only sets `stop = 1`. Every `player_save`
  call site in the tree — creation, the `save` verb, `save_sweep`, `drop_session`,
  chpass — is on some other path. So **every connected player loses up to
  `SAVE_SWEEP_MIN_MS` (5 minutes) of progress on every clean restart.**
- **Can it happen today? Yes**, on every operator restart. Not peer-triggered,
  which is why it is high and not critical.
- **The docs promise the opposite.** [`running.md`](../guides/running.md) says
  *"Shut down cleanly with SIGINT/SIGTERM; a `kill -9` is safe too"*, and
  [ADR 0006](../adr/0006-persistence-shape.md)'s save-trigger list does not
  include a signalled shutdown. The code draws no distinction the prose implies.
- **Whose code.** Ours. **Fix size.** ~10 lines: one bounded walk of
  `g_session_head` before `audit_flush_all()`, and the same on the AGNOS exit.

**AD. A character can be persisted with no class, permanently, and one operator
typo does it to everyone.** *(high — CLOSED in 1.7.11)*

- **What breaks.** `login_on_confirm` sets `SS_AUTHED = 1`
  ([`persist.cyr:2343`](../../src/persist.cyr:2343)) **before** `PHASE_CLASS`
  ([`:2348`](../../src/persist.cyr:2348)), and `drop_session`'s only gate is
  `SS_AUTHED == 1` ([`server.cyr:833`](../../src/server.cyr:833)) followed by an
  unconditional save. Disconnect at the class menu and a `class = -1` record is
  written. **`PHASE_CLASS` is stored in exactly one place in the whole tree** —
  that creation path — so there is no route back to the menu, ever. The record is
  validly signed, so it loads forever, and the operator cannot repair it because
  the signing key is derived from the player's passphrase (ADR 0004).
- **The second trigger is the serious one.** `world_load_classes` unpublishes the
  whole table on any failure (F6) and `cmd_serve` treats that as non-fatal —
  *"no classes loaded — players spawn classless"*
  ([`server.cyr:1659`](../../src/server.cyr:1659)). With the table empty, the load
  path's `cls >= g_class_count → cls = -1` clamp demotes **every** character, and
  the next `drop_session` writes that demotion to disk. **One typo in
  `data/classes.cyml` plus a restart is playerbase-wide, irreversible loss.**
- **Can it happen today? Yes**, both ways, with no malice.
- **Whose code.** Ours. **Fix size.** Small but two-sided: refuse to persist a
  `class < 0` record (or route such a login back to `PHASE_CLASS`), **and** make a
  failed class-table load fatal, or suppress saves while `g_class_count == 0`.

### ✅ 1.7.12 — persistence integrity (SHIPPED)

Items AE and AF are **closed**. 1270 assertions (was 1259), 5/5 mutations killed.

**AF was a real drift breach, now measured both ways.** The bench arm that could
never fire — every fixture was `memset`, so `SS_AUTHED = 0` and `drop_session`'s
save arm was unreachable — now drives 64 condemned authed sessions at the real
`MAX_EPOLL_EVENTS` bound: **2 ms / 3 torn down with the fix, 55 ms / 64 torn down
without, taking the gated pre-tick total to 59 ms — 118% of the ADR 0001 drift
allowance, FAIL.** That is the instrument whose absence let AF survive a gate
sweep in code the bench exists to watch.

**Also fixed, from the sweep's uninstrumented list:** `cmd_give` did not mark the
RECIPIENT dirty. Swept rather than patched — it is the only verb in the tree that
mutates another session's persistent state (`ability_heal` is self-only).

**Decided, not deferred:** `drop_session` still does **not** consult
`SS_SAVE_DIRTY`. The gate asked whether it should; the answer is no while the flag
has holes like the one above, because the unconditional save is what covers for
them.

### 1.7.12 — the two items (detail, retained)

**AE. A refused duplicate login reverts the real session's state.** *(medium — CLOSED in 1.7.12)*

- `player_auth_load` sets `SS_AUTHED = 1`
  ([`persist.cyr:2051`](../../src/persist.cyr:2051)); the double-login refusal
  ([`:2114`](../../src/persist.cyr:2114)) sets `SS_QUIT` and **never clears
  `SS_AUTHED`**, so `drop_session` saves the duplicate's stale snapshot over the
  live one.
- **The window is wider than a single batch.** On the retained-line path
  (`take == 0` once `EVENT_LINES_MAX` is spent), `drain_pending_rx` dispatches the
  passphrase in its *else* arm — which sets `SS_QUIT` but does not drop — and
  because that consume empties `SS_RX_LEN`, `g_rx_backlog` is not incremented and
  the loop parks in `epoll_wait` for a full tick. The stale snapshot is held **up
  to 2500 ms**, spanning a later batch, so a victim's `passwd` or `save` inside
  that window is reverted.
- **Item duplication was chased and REFUTED**: `session_drop_inv`
  ([`item.cyr:115`](../../src/item.cyr:115)) frees the refused session's minted
  copies rather than dropping them to the room.
- Attacker must already hold the passphrase, so the impact is "a compromised
  credential cannot be rotated away from", not takeover. **Fix size.** One line.

**AF. The epoll batch's teardown is unmetered — verbatim the 1.7.0 finding, not
carried across.** *(medium — CLOSED in 1.7.12)*

- `src/server.cyr:1768` drops on `keep == 0` with no `charge_spent()` consultation,
  and the teardown consumes no line budget. The signature *is* counted
  ([`persist.cyr:1573`](../../src/persist.cyr:1573)) but nothing reads it here;
  `CHG_SIGN = 10` against `PASS_CHARGE_MAX = 20` means **64 batched drops spend 640
  units inside a 20-unit window**. The AGNOS twin
  ([`:1813`](../../src/server.cyr:1813)) walks every session with no
  `MAX_EPOLL_EVENTS` analog.
- **Why no instrument saw it:** `bench_tick_budget.bcyr` memsets its fixture, so
  `SS_AUTHED` is 0 and the arm it would measure cannot fire. Fix the fixture with
  the code.
- Impact is drift, not loss. **Fix size.** Small; hoist the check, both loops.

### ✅ 1.7.13 — the tx-queue class, as ONE edit (SHIPPED)

Item AG is **closed**, both altitudes. 1295 assertions (was 1270), 7/7 mutations
killed.

**Measured before and after:** a 6000-byte authored mob body took the queue from
**4096 (run dry, no prompt) to 3606**; eight `look`s in a busy room from **4096
(last reply cut mid-number) to 3646**. Both keep their prompt.

**The clamp is a function now.** 1.7.9 fixed the room header *inline*, which is
exactly why the two `examine` arms were missed — `session_append_bounded` is the
one implementation, and the room header uses it too.

**Two alternatives were rejected, both on 1.7.9's lesson:** flushing between
dispatched lines undoes 1.6.8's coalescing (81 ms → 27 ms on the 256-player
broadcast), and refusing to dispatch while the queue is full couples input to
output and deadlocks. Bounding what is WRITTEN has neither problem. The
roadmap's suggested loader cap was also declined: the descriptions are zero-copy
borrows, so a loader cap saves no memory and only adds a second place to be wrong.

### 1.7.13 — the item (detail, retained)

**AG. The reserve is per-command; the queue is per-read.** *(medium / low — CLOSED in 1.7.13)*

- Two altitudes of one accounting error, and fixing either alone leaves the
  mechanism intact:
  - **`examine`'s authored prose is unbounded** —
    [`session.cyr:1390`](../../src/session.cyr:1390) (mob) and
    [`:1417`](../../src/session.cyr:1417) (object) are raw appends of a borrowed
    `(ptr, len)`; `mob.cyr:310` and `item.cyr:236` store `cyml_entry_body()`
    straight from the parse buffer with no `copy_str_capped`. This is the room
    header 1.7.9 fixed, at the two siblings it did not reach.
  - **Nothing flushes between the lines of one read**, so up to `RX_MAX_LINES = 8`
    commands share one 4 kB queue while `room_line_fits` re-measures the 512-byte
    reserve against the whole buffer each time. A malformed SGR and a lost prompt
    per burst; recovers on the next read.
- **Fix size.** Clamp both `examine` arms, cap `MT_DESC`/`OT_DESC` at the loader,
  and either flush between lines or re-arm the reserve per dispatch.

### ✅ 1.7.14 — hygiene (SHIPPED)

Items AH and AI are **closed**, and with them **every finding from gate re-run #2
(AC-AI)**. 1310 assertions (was 1295), 9/9 mutations killed.

**AH was worse than "the last one stays":** each `ident_derive` overwrote only a
PREFIX of its scratch, so the tail of the longest passphrase ever seen persisted
for the life of the process. The confirm-path wipe sits BEFORE the match/mismatch
branch, because the mismatch return is the path an attacker drives repeatedly.

**AI does NOT close slot exhaustion**, and should not be recorded as if it did: a
peer sending one byte every 29 s keeps a session non-idle and holds its slot
whatever the reap budget does. What it fixes is the budget being spent on work
that costs nothing — which could delay eviction of exactly the slowloris sessions
`PREAUTH_TIMEOUT_MS` exists for.

**Third release running to need a source-level guard.** Sampling the cost
predicate after the teardown is a use-after-free that no test can see (the
freelist returns blocks unzeroed, so the stale bytes read the same). The order is
pinned from the source, as 1.7.11 and 1.7.12 pin their call sites. That three
consecutive releases have needed this is itself a finding about the suite's reach.

### 1.7.14 — the two items (detail, retained)

**AH. Key material sits in never-wiped globals.** *(low — CLOSED in 1.7.14)* — `ident_derive`
([`persist.cyr:1265`](../../src/persist.cyr:1265)) leaves the passphrase at
`g_ident_scratch + 16` and the Ed25519 seed at `+200`; `login_on_confirm` leaves a
full 64-byte secret key at `g_persist_dec + 160`. Bump memory, never freed. No
wire-reachable disclosure primitive, so low — but the tree already applies this
rule at `sess_cand_clear` and `session_free`. **Three `memset`s.**

**AI. `sweep_idle` charges unauthenticated reaps against a signature budget.**
*(low — CLOSED in 1.7.14)* — the decrement at [`server.cyr:894`](../../src/server.cyr:894) is
unconditional while `IDLE_REAP_MAX`'s derivation says "every reap is a signature",
which is untrue for exactly the pre-auth reaps `PREAUTH_TIMEOUT_MS` exists to
serve. **One `if`.** Note this does *not* close slot exhaustion: a peer sending one
byte every 29 s holds a slot regardless.

### What this sweep had no instrument for

Recorded so the next pass starts here rather than rediscovering it:

1. **Nothing was executed.** Read-only meant no build, no suite, no bench, no
   running server; every arithmetic claim is derived from source. **A pass allowed
   to run the suite and the benches is the highest-value next step** — AF survived
   precisely because a bench fixture could not reach the code path, which only a
   run reveals.
2. **`parser.cyr` (788 lines) and `combat.cyr` (409) had no owner.** The parser is
   the tree's primary untrusted-input surface and got a spot check, not a sweep.
3. **The AGNOS build is reasoned about, never exercised.** 1.7.8's finding came
   from that gap and it is still open — AC and AF both have AGNOS twins judged by
   reading two arms of a preprocessor.
4. **Persisted state over TIME.** Everyone audited single load/save transactions;
   nobody modelled create → play → crash → reload → rotate → shard-migrate. AD is
   exactly that shape and was found by accident.
5. **Cross-session consistency.** `cmd_give` mutates the recipient's `SS_INV` but
   sets only the giver's `SS_SAVE_DIRTY`, so any save-boundary event — including
   AC's shutdown — can leave two records disagreeing about who owns an object.
   Item duplication across a restart is a whole class nobody instrumented.
6. **The tree moved under the audit.** One area saw README/roadmap change mid-run
   (legitimate 1.7.10 prose). **Tag the commit before the next gate.**

---

## Open issues — the gate re-run's five highs are ALL CLOSED (2026-07-30)

**The gate re-run returned DO-NOT-CLOSE** with five highs. **All five are now
closed**: R and S in 1.7.7, T and U in 1.7.8, and V (the account cap) committed
before either.

**That does not close the 1.x line.** Those two releases' own sweeps raised
**eight new items** — see below — and the gate is a *re-run coming back clean*,
not a checklist reaching zero. Next is 1.7.9, then the re-run.

**The lesson, stated once because it is the same lesson as the previous sixteen
releases:** three of the four are *a rule applied at some sites and not the
others.* Two of those are fixes from 1.7.3 and 1.7.6 that were never carried
across — the model code sits in the same file, in one case 230 lines away. And the
suite was green at 1048 assertions with all four present: **none of them had a
test, so none of them could fail.**

From the third (gate) sweep, 2026-07-29, run against 1.6.15. Worst first. Every
item says what breaks, whether it can happen to a running server today, whose
code it is, and how big the fix is — in that order, before any label.

### ✅ 1.7.7 — carry the fixes to the sites they were never applied to (SHIPPED)

Items R and S are **closed**. 1118 assertions (was 1048), 17/17 mutations killed,
`cyrius audit` 0, 6/6 benches.

**Both were confirmed by measurement before being fixed, and the numbers held.**
`get` of a bag of 99 while holding 99 landed at **199 against a cap of 100** — the
old guard `inv_full` returned *allow*. `inventory` lost its prompt at **95 items**
(94 fitted), which is **under the game's own `MAX_INV` of 100**; `who` lost it at
**79 players** (78 fitted), and at 90 the cut landed on byte `0x80` — mid-UTF-8
character, the em-dash separator sliced in half.

**The fix was carried to the class, not the instance.** `oi_move_count` is now the
single answer to "how much does this move move", shared by `get` and `cmd_give`;
five listing loops adopted `room_line_fits` / `list_append_more`, including the
dormant `@who` twin. A follow-up sweep of both classes across the whole tree found
no further instance of either — but did surface a **different** unbounded class on
the RX side (see below).

**Two things worth keeping from how it went:**

- *Rationing the echo must never ration the effect.* `drop all` and `get all` are
  commands, not reports. The fit check wraps only the echo. The mutation that
  pulls the move inside the check is killed by a dedicated assertion, because a
  fit check around the whole loop body would have passed every prompt assertion
  and silently left items in the player's hands.
- *A mutation survived, and the test was what was wrong* — fourteenth instance of
  this project's standing rule. The first `get all` coverage used bare floor
  items, and for a bare item `oi_move_count` is 1, so the old guard and the new
  one are **the same function**. The test could not have failed whatever the arm
  did. Discriminating needs a floor container that overflows the cap by itself.

### 1.7.7 — the two items (detail, retained)

**R. Picking up a container ignores what is inside it, and the next save destroys
the overflow.** *(high — CLOSED in 1.7.7)*

- **What breaks.** `get` moves a container **and its contents**, but the cap check
  asks only how much you are already holding. Hold 99, pick up a bag of 99, and
  you hold 199 against a cap of 100 — from one ordinary command, with the server
  saying only "You take a dented tankard." Push further and the record silently
  stops recording the rest: **`player_save` returns SUCCESS and the items are gone
  at next login.** Nothing is said to the player.
- **Can it happen today? Yes** — any logged-in player, no admin, no malice beyond
  hoarding.
- **Whose code.** Ours, `src/item.cyr` end to end.
- **Fix size.** Small, **and the correct version already exists 230 lines below**:
  `cmd_give` computes `moving = 1 + contents` and tests
  `inv_count(target) + moving > MAX_INV` ([`item.cyr:751`](../../src/item.cyr:751)).
  Both `get_from` arms need the same question instead of the bare `inv_full(s)`.
  The `inv_owns_slot` exemption stays.
- **Sites.** [`item.cyr:520`](../../src/item.cyr:520) (single) and
  [`:492`](../../src/item.cyr:492) (`get all`); the predicate is `inv_full` at
  [`:447`](../../src/item.cyr:447).
- **Measured**, every move typed through `cmd_on_line`: 99 held + one `get` → 199.
  Scaled: 721 carried, `_build_record` 4048 B of SAVE_CAP 4096, `player_save`
  returned 1, reload → 591. **130 items destroyed.**
- **Why no test caught it.** `test_carry_cap` uses bare floor items;
  `test_carry_cap_container` only takes items *out of* your own bag.

**S. `inventory`, `who`, `drop all` and `get all` end mid-line with no prompt.**
*(high — CLOSED in 1.7.7)*

- **What breaks.** The same defect 1.7.6 shipped a release to remove for `look`.
  Each writes one coloured line per item into the 4 kB queue with no fit check, so
  the reply is cut at whatever byte it runs out on: listing stops mid-name, the
  colour is never closed, and the prompt never arrives — the session looks hung.
  For two common items the cut lands on a bare ESC, so the terminal then eats the
  start of whatever comes next.
- **Can it happen today? Yes** — at the game's own 100-item carry cap, and for
  `who` at about 90 players online.
- **Whose code.** Ours.
- **Fix size.** Small and mechanical. `room_line_fits`
  ([`session.cyr:1149`](../../src/session.cyr:1149)) and `room_append_more`
  ([`:1159`](../../src/session.cyr:1159)) already exist, are tested, and their
  512-byte reserve already covers the prompt. **1.7.6 wired them into
  `session_show_room`'s three sections and nowhere else.** Four loops adopt them.
- **Sites.** `cmd_inventory` [`item.cyr:781`](../../src/item.cyr:781), `cmd_who`
  [`server.cyr:1355`](../../src/server.cyr:1355), `cmd_drop`'s all-branch
  [`item.cyr:596`](../../src/item.cyr:596), `get_from`'s `all` echo
  [`item.cyr:481`](../../src/item.cyr:481). `render_who`
  [`server.cyr:1064`](../../src/server.cyr:1064) is the same shape but behind
  `YD_ADMIN` (default off) — dormant, fix it in the same pass.

### Raised by 1.7.7's own class sweep (2026-07-30) — 1 high, 3 medium, 4 low

1.7.7 swept both of its defect classes across the whole tree rather than patching
the two named sites, and had every candidate adversarially refuted before it was
recorded. **Neither class had another instance** — the five listing sites and the
three cap sites are all of them. What the sweep found instead was a **different**
unbounded class, on the RX side, which no previous pass had an instrument for.
Listed worst first. None is fixed; all are new.

**W. A pre-auth peer can make the server generate its own buffer overflow, three
bytes at a time.** *(high — CLOSED in 1.7.9, by bounding the OUTPUT rather than
the input; the amplifier itself is carried, see AB below)*

- **What breaks.** `session_consume_rx_max` ([`session.cyr:1671`](../../src/session.cyr:1671))
  appends the Telnet layer's reply buffer with an unchecked `session_appendtx`
  ([`:1693`](../../src/session.cyr:1693)), then `telnet_tx_consume` **unconditionally
  clears the source** — so whatever the short write dropped is gone. Every option
  code except ECHO(1) and SGA(3) is untracked, and `telnet_respond_refuse` is
  **stateless** for untracked options, so `IAC DO 42` repeated 1365 times in one
  4096-byte write produces 1365 unconditional `IAC WONT 42` replies with no
  Q-method suppression to damp it.
- **Why no existing bound catches it.** `RX_MAX_LINES = 8` counts **completed
  lines**, and a negotiation triple yields `EV_NONE`, so `fired` stays 0. The
  1.7.0 charge window bills only `ed25519_*` and prose bytes, and negotiation
  costs neither. **Both of this server's input bounds are structurally blind to
  it.** That is the finding, more than the site.
- **Can it happen today? Yes, pre-auth**, from anyone who can open a socket.
- **The verifier's correction, kept because it matters.** One pass from an empty
  queue tops out at 1365 × 3 = **4095 bytes against TX_CAP 4096** — one byte
  short. Overflow needs the queue to be non-empty at the start of the pass, which
  three ordinary things do: mixed input in the same read (up to 8 command lines
  may interleave), a slow-reading peer whose unsent remainder `session_drain`
  compacts and keeps, and the retained-tail resume. So it is real but **not a
  one-packet kill**, and the honest statement is "reachable in ordinary
  conditions", not "guaranteed from a single write".
- **Worse than the 1.7.6/1.7.7 display sites in kind**: the unit being truncated
  is a 3-byte Telnet escape, not a text line. A bare `IAC WONT` with no option
  byte makes a conformant client eat the next data byte as the option code.
- **Whose code.** Ours. **Fix size.** Contained — the same fit-check shape, plus a
  bound on unsolicited refusals per pass.

**X. The passphrase mask is a 2× amplifier with no bound.** *(medium — CLOSED in
1.7.9. The per-byte writes are atomic now, so nothing is cut mid-sequence; the
sustained 2 TX bytes per RX byte RATE is inherent to server-side echo and is
bounded by the queue, not by a counter.)*

- `session_push_line_byte` ([`:1592`](../../src/session.cyr:1592)) emits one `*`
  per printable byte and **three** (`"\b \b"`) per BS/DEL, so an interleave of
  printable and DEL costs 4 TX bytes per 2 RX bytes: **8192 from one 4096-byte
  read, twice TX_CAP.** `LINE_CAP` equals `RX_CAP` so it bounds nothing for a
  single read, and the over-length guard *resets* `SS_LINE_LEN` rather than
  damping. `PASS_MAX = 64` is a line-dispatch check, never per byte.
- Reachable **pre-auth** in `PHASE_PASS` / `PHASE_NEWPASS` / `PHASE_CONFIRMPASS`.
  The lost tail is the over-length notice, the `WONT ECHO` salvo and the prompt —
  so the client is left echo-suppressed with no prompt.

**Y. The carry cap is not enforced on the load path, and this file said it was.**
*(medium — and a correction to this document)*

- `_restore_inv` ([`persist.cyr:1607`](../../src/persist.cyr:1607)) has **no
  counter, no cap and no budget**. The only bound is incidental: `SLURP_CAP`
  leaves ~7686 bytes of `inv` field, which at the Hub's short ids is on the order
  of a thousand items — ten times `MAX_INV`.
- **This is issue E, which this file records as CLOSED in 1.7.2. It is not.**
  What actually happened is that a *different decision* was taken and written into
  the source: the comment at [`item.cyr`](../../src/item.cyr) says the cap is
  "**deliberately NOT enforced on the load path** — a record that already holds
  more than this must come back intact. The cap stops you ACQUIRING more, it never
  destroys what you have." That is a defensible call, and refusing to destroy a
  player's belongings on load is probably the right one. **The defect is that the
  roadmap was never corrected to say so**, so this document has claimed a bound
  that does not exist for five releases — the precise failure mode this project
  has a standing lesson about (*a comment is not a bound*), one level up.
- **SETTLED IN 1.7.9 — WON'T FIX, and the roadmap was the thing that was wrong.**
  Measured rather than argued:
  - A crafted record restores at most **1,583 items**, not the "~4000" this file
    claimed — `file_read_all` truncates at `SLURP_CAP - 1` = 8191 bytes and a
    longer file loses its trailing `sig` line, so the whole record must fit.
  - `item_new` uses **`fl_alloc`, not the bump allocator**, and the memory is
    **fully reclaimed at disconnect on every exit path** — `drop_session` →
    `session_drop_inv` → `obj_free` (which recurses through `OI_CONTENTS`) →
    `fl_free`. Traced, not assumed. So "unbounded" overstated it: this is a
    transient high-water mark, not a leak.
  - A record a REAL server can produce already holds up to **~685 items**,
    because the binding constraint is the WRITER's byte budget (`SAVE_CAP` 4096,
    ~3427 bytes of `inv` field) and never the carry cap. **Clamping to `MAX_INV`
    on load would therefore destroy real players' belongings** — which is exactly
    what the source comment at `MAX_INV` has said all along.
  - Only ~2.3x separates the crafted maximum from the legitimate one, and the
    memory comes back. **Severity: low.**

  The code was right and this document was wrong for five releases. Issue E is
  **not** closed by a bound; it is closed by the deliberate decision already
  recorded in the source, which nobody ever wrote down here.

**Z. Four smaller unbounded or mis-ordered sites.** *(low — three CLOSED in
1.7.9: the room-header prose, `class_send_prompt`, and `mob_swing`. The fourth,
`drain_pending_rx`'s SS_QUIT arm, is **not a defect** — the teardown cannot be
deferred without the H1/M12-C use-after-free, the code already said so, and the
overshoot is exactly one signature per pass. Its comment now states that bound
explicitly.)*

- **`session_show_room`'s header** ([`session.cyr:1265`](../../src/session.cyr:1265))
  writes the authored room prose with a raw `session_appendtx` **ahead of** the
  three sections 1.7.6 guarded, and can consume the whole 4096 bytes *including*
  the 512-byte reserve those sections rely on. Authored prose is borrowed
  uncapped from the CYML buffer. *Note: the previous sweep dropped a room-header
  finding whose stated mechanism was wrong. This one names a different mechanism
  and was independently confirmed — it is not a re-proposal of the dropped one,
  and it should be re-checked on that basis before anyone acts on it.*
- **`class_send_prompt`** ([`classes.cyr:224`](../../src/classes.cyr:224)) — one
  unchecked line per class. Safe with the shipped 4 classes; up to 8 bad choices
  can stack menus in one TX because nothing flushes mid-slice, so an
  operator-authored `classes.cyml` reaches it.
- **`mob_swing`** ([`combat.cyr:244`](../../src/combat.cyr:244)) — combat lines per
  latched mob, unbounded by mobs-per-room.
- **`drain_pending_rx`'s SS_QUIT arm** ([`server.cyr:502`](../../src/server.cyr:502))
  consults the charge budget *after* `drop_session`'s unconditional signing save
  rather than before it, so every pass overshoots by at least one signature.
  Bounded at one; noted for correctness of the accounting, not as a risk.

### Raised by 1.7.8's own sweep (2026-07-30)

**AA. Every completed TCP handshake permanently consumes 16 bytes, before a byte
is read.** *(medium — CARRIED past 1.7.9, needs a decision not a patch)*

- **What breaks.** `sock_accept` returns `Ok(cfd)`, and the compiler boxes that
  enum payload with a bump `alloc(16)` — [`lib/net.cyr:358`](../../lib/net.cyr:358),
  and identically on the AGNOS branch at [`:343`](../../lib/net.cyr:343). The bump
  arena has no free, so it is 16 bytes per connection, forever. Reached from
  `handle_accept` (`src/server.cyr`) at the earliest possible point — before the
  MOTD is queued, before a name is typed, before anything is validated.
- **Can it happen today? Yes, unauthenticated**, from anyone who can complete a
  handshake. ~5.7 MB/hour at 100 connections/s. Small next to the 2,248 bytes
  1.7.8 removed, and unbounded in exactly the same way.
- **Whose code — split, and the split matters.** The allocation is in `lib/`,
  which is off-limits here. **The connection COUNT is entirely ours**, and so is
  the choice to consume a boxed `Result` per accept. This is the 1.7.1 shape
  again: descent's lever is the count, not the per-item cost.
- **Fix size.** Needs a decision before a patch — an upstream `lib/net.cyr` change
  (a non-allocating accept), or an accept-rate bound here. `MAX_SESSIONS` and the
  1.6.3 accept backoff bound *concurrency*, not the cumulative count.
- **Do not confuse this with `ACCEPT_BACKOFF_TICKS`**, which stands the listener
  down after an accept *error*; a healthy connect/drop flood never touches it.

**AB. The negotiation amplifier itself is still there.** *(low — raised by
1.7.9's own design review)*

- `telnet_respond_refuse` ([`telnet.cyr:269`](../../src/telnet.cyr:269)) is
  **stateless** for untracked options, so N repeats of `IAC DO 42` buy N
  unconditional `IAC WONT 42`. 1.7.9 made the reply atomic, so the wire is
  correct and the queue bounds the volume — what remains is wasted work, not a
  corruption or a leak.
- **The fix is cheap and already half-built**: the 256-byte `TS_OPT_US` /
  `TS_OPT_HIM` arrays exist and have spare state values, so an untracked option
  could be refused at most once per session. Left out of 1.7.9 deliberately —
  it changes RFC 1143 conformance on a path with no test coverage, and this
  release already reworked its own design once.

**Also confirmed, and deliberately not filed as a defect:** `cmd_put` places no
limit on a room container's contents. That is roadmap item **Q** (the donation
bin) and is already 2.0 work; the sweep verified it is no longer a `MAX_INV`
bypass, because contents of a *carried* container are counted by `inv_count`.

### ✅ 1.7.8 — AGNOS persistence and the pre-auth parse (SHIPPED)

Items T and U are **closed**. 1180 assertions (was 1118), `cyrius audit` 0, 6/6
benches, both targets build, 12/14 mutations killed (the two exceptions are named
in the CHANGELOG rather than rounded up).

**Both were measured.** The AGNOS syscall collision was confirmed in the emitted
artefact — the `0x57` immediate count in a `CYRIUS_DCE=1 --agnos` build drops by
exactly one when the raw `unlink` goes, and the rename read its number from a
global exactly as the original finding described. The pre-auth parse went from
**2,248 bytes per attempt to 0**, with the parse cost of the same record asserted
as a contrast so the zero cannot pass for the wrong reason.

**The cause was fixed alongside the instance:** CI now builds `--agnos`, and a
suite assertion requires `persist.cyr` / `session.cyr` / `item.cyr` to contain no
raw numeric `syscall(` outside a comment — the only guard that could have caught
this, since on x86_64 syscall 82 genuinely *is* rename and a raw number compiles
fine on both targets.

**Two things worth keeping:**

- *The fix nearly opened a worse hole than it closed.* Reading `salt`/`pubkey`
  with a second, stricter parser creates a differential: bayan accepts shapes the
  scanner skips, so a decoy line ahead of the real one is read by one and not the
  other. Guarded, and the guard is verified by a **validly-signed** crafted record
  — the first version of that test spliced a decoy into an existing record, broke
  the signed prefix, and therefore passed with the guard deleted.
- *A fast path must never become a second file format.* The first cut returned a
  terminal `-2` whenever the strict scan failed, which would have turned every
  hand-edited or non-canonical record from "loads" into "corrupt". It falls
  through to the parser instead.

### 1.7.8 — the two items (detail, retained)

**T. On the AGNOS build, a player record is never published at all.** *(high — CLOSED in 1.7.8)*

- **What breaks.** `player_save` asks for `syscall(82)` to rename the temp file
  into place and `syscall(87)` to unlink the old one. On AGNOS those numbers are
  **GPU dispatch and blit**, not rename and unlink. The record directory is not
  created either — the `sys_mkdir` calls pass a permission mode where AGNOS
  expects a path length. Character creation warns it could not write, every
  autosave and disconnect save fails the same way, and **every reconnect is
  offered a brand-new character.**
- **Can it happen today?** **Live on `--agnos`**, dormant on x86_64 (where 82/87
  genuinely are rename/unlink — which is why the suite is green). README and
  `docs/guides/running.md` have advertised AGNOS persistence as working
  identically since 1.1.0. **CI never builds it.**
- **Whose code.** Ours. `lib/io.cyr`'s `xunlink` (`:108`) and `file_rename`
  (`:133`) both carry correct AGNOS branches — the stdlib is fine, `persist.cyr`
  just does not call it. The *same binary* reaches syscalls 30/31 correctly from
  the 1.7.4 rotation path.
- **Fix size.** Small: three call sites plus a dead constant, using the `#ifdef`
  shape `player_exists` already carries for `sys_stat`.
- **Sites** (HEAD-relative): [`persist.cyr:1498`](../../src/persist.cyr:1498) and
  [`:1508`](../../src/persist.cyr:1508), constant at
  [`:66`](../../src/persist.cyr:66); mkdir at `:127`, `:128`, `:1151`.
- **Verified in the emitted artefact**, not the source: with `CYRIUS_DCE=1` the
  global reads 82 into `%rax` before a bare 2-arg `syscall`, and `mov $0x57,%eax`
  survives DCE. `lib/syscalls_x86_64_agnos.cyr:96` defines `SYS_GPU_DISPATCH = 82`
  annotated *"(RENAME on Linux)"* and `:101` `SYS_GPU_BLIT_SHM = 87` annotated
  *"(UNLINK on Linux — DELETES A FILE)"*.
- **The tree already knew.** The comment at
  [`persist.cyr:1049`](../../src/persist.cyr:1049) says *"file_rename, not the raw
  syscall above: that one predates io.cyr's wrapper and misses the agnos 4-arg
  form"* — 1.7.4 fixed its own new code and did not go back six lines.
- **Also fix the cause, not just the instance:** CI must build `--agnos` or this
  rots again.

**U. Every login attempt against an existing character permanently consumes
2,248 bytes.** *(high — CLOSED in 1.7.8)*

- **What breaks.** The record is parsed into memory **before the passphrase is
  checked**, and that memory can never be reused. Five guesses per connection
  before the socket closes ≈ **11 kB gone forever per attacker connection**.
- **Can it happen today? Yes**, from anyone who can open a socket. No account
  needed to find a target — the login prompt itself answers whether a name exists
  ("Passphrase:" vs "No record answers to that name").
- **And the instrument stays quiet:** 1.7.1's rollup window correctly suppresses
  the repeated audit entries, so a flood leaves one entry and a count.
- **Whose code.** Ours. The bytes land inside `lib/bayan.cyr`'s `toml_parse`,
  but **the call is ours and the whole fix is ours** — six of the seven
  `toml_parse` callers are boot-time loaders;
  [`persist.cyr:1592`](../../src/persist.cyr:1592) is the only per-request and
  only pre-authentication one.
- **Fix size.** Real but contained, ~30 lines in `src/persist.cyr`: the decision
  needs only `salt` and `pubkey`, both fixed-form, so they can be extracted
  without a full parse before the passphrase is checked.

**V. The account cap silently stopped enforcing after sharding.** *(high — FIXED,
uncommitted)*

- **What breaks.** `accounts_count_disk` counted top-level directory entries —
  right for the flat layout, wrong the moment 1.7.2 sharded records into
  `data/players/<c>/` **in the same release**. Measured on the working tree: **26
  counted against 40 real records**, converging on ~26 as records migrate. An
  operator who set `max_accounts` had a cap that would never fire.
- **Can it happen today?** Only for an operator who sets a cap — it is off by
  default.
- **Whose code.** Ours. **Fix size.** Contained.
- **Status: fixed in the working tree** ([`persist.cyr`](../../src/persist.cyr),
  `accounts_count_disk` + `_is_record_name`) with a regression test that fails
  against the old implementation (27 vs 29). **Not yet committed.**

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
findings.** That has not happened. **Gate re-run #4 came back 0/3/3/3** — see
[its open issues](#open-issues--gate-re-run-4-returned-do-not-close-2026-07-31).
Re-run #5 runs after 1.7.20, and it plus 1.7.18–1.7.20 are what block 2.0.

**The trend is real and it is downward** — #2 was 0/2/3/3, #3 was 0/4/5/7, #4 was
0/3/3/3 — but no run has yet cleared the bar.

Every sweep so far has **found serious defects the previous pass had missed**, and
each found them in a place the previous pass had no instrument for: a remote crash
on `examine` (1.6.9), an unbounded event batch costing 4.12 s of blocked loop
(1.6.12), a 252 ms pass at 504% of the drift budget plus an unbounded
per-connection arena loss (the gate sweep, items A and C), and — in #4 — an object
duplicated on **every restart** because the boot path seeds a census 53 lines too
late. 1.6.9 built the first benches touching save, login and loaders, and re-run
#2 immediately found defects there. The gate sweep found A because it was the
first time anything summed a whole tick pass. **#4 found AZ and BC because it was
the first time anything compared `data/players/` against the live world.**

**What changed at #4, and what it means for #5.** For the first time the sweep
mostly stopped finding *pre-existing* defects: six of its nine survivors are
siblings of fixes shipped in the previous three patch releases, and one was
introduced by the head commit. **The sweep is now finding the incompleteness of
its own recent fixes at roughly the rate the fixes retire them.** Two consequences:

1. **Re-running the same surfaces will yield less each time.** Five of #4's six
   surfaces are spent — the interleaving surface in particular came back a clean
   negative and should not be re-swept. **#5's value is in the surfaces #4 could
   not reach: AGNOS (never executed by any sweep, and a second copy of the event
   loop), audit rotation under volume, and a forged-signature harness.**
2. **The cheaper lever is process, not sweeping.** When a fix changes a predicate,
   grep every call site of that predicate and every caller of the function it
   lives in, and record the enumeration in the fix's own comment. Three of #4's
   nine would have died to one grep.

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
