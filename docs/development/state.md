# cyrius-yeomans-descent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-07-29 (v1.6.14 — only a docs pass left before the gate)
>
> A **snapshot of the current tree**, not a history. Per-release chronology lives
> in [`CHANGELOG.md`](../../CHANGELOG.md); sequencing and what is planned live in
> [`roadmap.md`](roadmap.md).

## Version

**1.6.14** — 2026-07-29. **751 assertions**; `cyrius audit` exits 0; 5/5 benches.

Closed the dormant tail: the **epoll_event layout** is now per-architecture on
both the read and write paths (an ARM build would have read session pointers
from the wrong bytes — the stdlib had this right and descent hardcoded the x86
offset for reads only), which also removed a **16-byte allocation per accepted
connection**; the **class-id terminator**; and the **rest of the 1.6.7 sign
sweep** — `str`/`dex`/`con`/`tec` and the damage dice were clamped on the load
path and unclamped on the creation path.

Two flagged "dead symbols" were kept rather than deleted: `mt_level` and
`g_zone_name` are authored zone-format fields frozen by ADR 0007 §5, with named
consumers at M16 and M18. Their comments claimed uses that did not exist; that
was the defect.

**All that remains before the gate is a documentation pass** (1.6.15): the
README says v1.2.0 and the architecture doc describes a combat model that was
never built.

**The 1.x line still needs a clean re-run sweep to close.**

---

## Lessons carried

Durable and hard-won; each cost at least one release to learn. Collected here
because they are about *how to work on this tree*, not about any one release.

**Fixing an instance is not fixing the class.** 1.6.12's critical was the fourth
appearance of one defect — *a per-item cap is not a bound on a loop that walks
many items* — after three releases each capped a neighbour of the open hole.
When a finding feels familiar, enumerate the class first: `grep -n ident_derive
src/` lists every expensive-line path; "every loop that dispatches lines" lists
every place a cap must be aggregate. Both were one command away.

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

- **Cyrius pin**: `6.4.86` (`cyrius.cyml [package].cyrius`)

Two toolchain quirks (first hit at 6.4.83, still present at 6.4.86), worked
around rather than fixed here:

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
  cyrius-yeomans-descent.tcyr   unit suite (751 assertions, 46 groups)
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

`cyrius test` — **751** unit assertions (bare form runs both the .tcyr corpus and [build].test):

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

**No active cycle.** Status, the open gate and the parked upstream item are in
[Version](#version) above — not repeated here, because they were, and the two
copies had already drifted apart.

**Next: another re-run sweep**, then 2.0.0 starting with **M14 — ADR 0008 + save
schema v2**. Before touching M14, read the critical path in
[`roadmap.md`](roadmap.md#critical-path): records are signed with a key
re-derived from the player's passphrase, which the server never holds, so **there
is no offline migration and there cannot be one** — every 2.0 field must be
additive, defaulted, and migrated lazily at login. M11 already repaired the gate
that makes the bump safe.

**Carried, none blocking:**

- **sakshi shadow warning** — sigil 3.12.1 pins sakshi 2.4.3 while the toolchain
  bundles 2.4.6. A sigil-side bump; nothing to do here.
- **Toolchain drift** — `cyrius.cyml` pins `6.4.86`; the installed `cycc` is now
  **6.5.0**, so `cyrius audit` emits a drift warning. Not a failure and nothing is
  broken, but the next toolchain bump is a release of its own (1.2.0 is the
  precedent: an upgrade repaired a `main` and a bench that had both silently
  stopped compiling), so it should not be folded into a feature change.
- **aarch64 epoll layout** — `src/server.cyr` hardcodes the x86 *packed*
  `epoll_event` (`EPOLL_EVENT_SIZE = 12`, data at +4); aarch64 Linux uses the
  unpacked 16-byte layout with data at +8. Not hit today (x86_64 / agnos only),
  but it corrupts the session pointer the first time someone builds `--aarch64`.
  Tracked as roadmap **B4**.
- **`cyrius audit` is a CI step.** If it fails on a style gate rather than a real
  defect, fix the code — do not drop the step. It is the only thing gating
  fmt / lint / docs.

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
