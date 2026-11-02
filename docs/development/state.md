# cyrius-yeomans-descent — Current State

> **This is the handoff.** If you are picking the project up cold, read this,
> then [`roadmap.md`](roadmap.md) "What is left". It is refreshed every release
> and is kept true of the tree as it is now.
>
> **Last refresh**: 2026-11-02 (v1.8.1, plus the unreleased probe fix)
>
> A snapshot, not a history: per-release chronology lives in
> [`CHANGELOG.md`](../../CHANGELOG.md). The long-form snapshots this file used to
> carry, and the retired `handoff.md`, are in git:
> `git show cb11b22:docs/development/state.md` and
> `git show cb11b22:docs/development/handoff.md`.
> [`CLAUDE.md`](../../CLAUDE.md) holds the durable rules.

---

## Where the project is

- **The Linux server is in good shape.** Gate re-run #5 came back with **zero
  highs on x86_64**, the first time in seven sweeps. All gates are green at 1.8.1.
- **The 1.x line is held open by the AGNOS target.**
  - **BV (high).** On a real AGNOS kernel, no save after character creation is
    ever published, so every AGNOS player loses all progress. The cause is
    agnos's ext2 `rename`, which cannot replace an existing file.
    **Decided: wait for agnos**; the issue is filed there.
  - **BJ** and **AA** are open decisions about what vendored `lib/` owes AGNOS.
  - **BU** (no AGNOS login) **no longer reproduces** on agnos 1.57.14.
- **2.0 is M14 + M15 + M16**: the contract, the zone registry and progression.
  It starts after the 1.x gate closes.
- **Unreleased since 1.8.1:** the AGNOS smoke probe's blind checks are fixed.

## Version

| | |
|---|---|
| **Version** | **1.8.1**, 2026-11-02. `VERSION`, `CHANGELOG.md`, and `VERSION_STRING` in `src/main.cyr`; `cyrius.cyml` reads `${file:VERSION}` |
| **Toolchain** | cyrius **6.7.18** |
| **Dependencies** | libro **2.11.3** → sigil **3.13.15**, patra **1.16.6**; from the fold: sakshi **2.5.10**, bayan **1.11.1** |
| **Tests** | **1502 assertions**, 0 failed (74 groups) |
| **`cyrius audit`** | exit 0: fmt, lint and docs clean; tests pass; benches 6/6 |
| **Fuzz** | 3/3 (2 real targets + a scaffold) |
| **Targets** | x86_64 Linux and `--agnos` both build, with **zero warnings** |
| **Binary** | x86_64 **1,848,000 B**, `--agnos` **1,853,360 B**; 795,328 B with `CYRIUS_DCE=1` |
| **CI parity** | `cyrius deps --locked` reports "lib/ and cyrius.lock are exactly what the tags resolve" |

⚠ **The binary grew 41.6% at 1.8.1** (from 1,305,048 B), and 57% even under DCE.
bayan 1.11's bundle is a large part of it, but its share was not separated from
the 6.7.18 compiler's. Whether release builds should use DCE is a roadmap item.

## Open work

Every open item, ordered and written up, is in
[`roadmap.md`](roadmap.md#what-is-left). In one line each:

- **BV** — AGNOS saves never publish after creation. **Waiting on agnos** to make
  `rename#31` replace an existing file; filed as agnos
  `docs/development/issues/2026-11-02-ext2-rename-cannot-replace-loses-every-descent-save.md`.
  descent adds no workaround.
- **BJ** — on AGNOS, a client that stops reading should freeze the loop, because
  `sock_send` blocks. A decision, not yet reproduced through QEMU.
- **AA** — 16 bytes leaked per accepted connection in `lib/net.cyr`. A decision.
- **Instruments for gate re-run #6** — the conservation invariant
  (`world + offline == authored`), a CYML loader fuzz target, a forged-signature
  harness in the tree, and audit self-hash verification.
- **Small 1.8.x items** — AB (refuse each untracked Telnet option once), H (about
  11 pre-1.6.7 guards never mutation-checked), CI `cyrius deps --locked`,
  binary size / DCE, and the `EPOLL_EVENT_SIZE` shadow.
- **2.0** — M14 (ADR 0008 + schema 2), M15 (zone registry, plus BT), M16 (XP and
  levels), K (broadcast fan-out), Q (donation bin).

**The one constraint to read before starting 2.0:** records are signed with a key
re-derived from the player's passphrase, which the server never holds
([ADR 0004](../adr/0004-identity-and-authentication.md)). **There is no offline
save migration, and there cannot be one.** Every 2.0 field is additive,
defaulted, and migrated lazily at login.

## The gate

The 1.x line closes when a gate re-run comes back with **no critical or high
finding**. Re-run #5 (2026-07-31, v1.7.20) ruled **DO-NOT-CLOSE at 0 / 3 / 5 / 4**.
All three highs were on AGNOS, and 1.7.21 closed ten of its twelve findings.
What blocks the gate now:

| Item | Status |
|---|---|
| **BV** | **Open, high, waiting on agnos.** Found 2026-11-02 by the first real-kernel persistence test; issue filed in agnos |
| **BU** | **Does not reproduce** on agnos 1.57.14 with 1.8.0 or 1.8.1. The cause of the fix is not attributed; 1.8.1's bump is not it |
| **BJ** | Open; needs an upstream decision with AA |
| **BT** | Open, low; belongs with M15 |

**Next:** wait for agnos on BV, settle BJ and AA, and build the instruments; then
run **gate re-run #6**.
The roadmap lists what #6 should target, and the settled negatives it should not
re-derive.

**There is a policy option:** scope AGNOS out of the 1.x gate. The case against
it: item T (1.7.8) was an AGNOS-only high, and `running.md` has advertised AGNOS
as supported since 1.1.0. If it is taken, it belongs in ADR 0007 as a contract
change.

## Running descent on a real AGNOS kernel

`scripts/agnos-qemu-smoke.sh` boots a real agnos kernel under QEMU and drives
descent over TCP with `scripts/agnos_probe.py`. It checks five scenarios: banner,
login + world, BK (does the tick run), BJ (does an unread client stall a
bystander), and persistence. On 2026-11-02 it passed **4/5 on agnos 1.57.14**,
and the one failure is BV.

- **Requirements:** qemu, OVMF, parted, sgdisk, mtools, e2fsprogs, a built
  `../gnoboot`, and an agnos kernel built **with the run hook**,
  `BENCH_CONNECT_SELFTEST=1`. The script refuses a kernel without
  `/etc/probe-cmd` in it.
- **Building that kernel without touching `../agnos`:**
  1. `git archive` agnos's HEAD into a scratch directory.
  2. Run its `sh scripts/build.sh` there with `BENCH_CONNECT_SELFTEST=1`,
     `KASHI_DIR` / `REKHA_DIR` pointed at the real siblings, and `CYRIUS_HOME`
     pointed at a home whose `bin` and `lib` link into
     `~/.cyrius/versions/<agnos's pin>`. agnos pins its own cyrius (6.6.20 today)
     and refuses toolchain drift.
  3. Pass the result as `AGNOS_KERNEL=…`.

  `../kashi` and `../rekha` are full checkouts, so the build only reads them.
- **To see a failed save,** use `KEEP=1`, then pull the ext2 partition out of
  `build/agnos-qemu/agnos-descent.img` (33 MiB in) and `debugfs` its
  `/data/players`. A stranded `<name>.cyml.tmp` is BV.
- **Through SLIRP, a BJ pass is weak:** host-side buffering may stop the guest's
  send window from ever filling. **Kill servers by port or PID, never by name.**

## Things a newcomer would not expect

- **`mud_now_ms()` is the only clock** (`src/session.cyr`). Every scheduling site
  routes through it. On AGNOS it reads the rdtsc-based `uptime_us` (#95), because
  #40 is frozen for a foreground `run` program. Do not call `clock_now_ms()` in
  `src/`; the wrapper's own fallbacks are the only two calls.
- **`MAX_SESSIONS` is target-aware:** 256 on Linux, **7 on AGNOS**. The agnos
  connection table has 8 slots and the listener holds one.
- **`@shutdown`** (behind `YD_ADMIN`) is the **only clean shutdown on AGNOS**,
  which has no signalfd.
- **Two readers parse a save record, and they must agree.** `_scan_canonical` /
  `_scan_kv` are descent's own first-match scanner, and bayan's TOML parser is
  last-wins on duplicate keys. An authenticated login skips `toml_parse` when the
  scanner vouches for the record. `player_auth_load` refuses a record whose two
  readers disagree about `salt` or `pubkey`, and its tests build the decoy-last
  attack. Touch record reading only with the differential test in view.
- **A signature proves authorship, not field validity.** Players own their
  signing key, so every loaded field is clamped and range-checked.
- **`src/test.cyr` is a no-op stub.** CI must run bare `cyrius test`; the
  explicit `cyrius test src/test.cyr` form ran nothing for the whole 1.1.x line.
- **`lib/` is vendored and committed. Do not edit it.** Never add
  `include "lib/sigil.cyr"`: the monolith redefines descent's whole sigil surface
  and drags in about 13 MB of x509/RSA tables. libro lands the thin sub-bundles
  instead.
- **`[deps.libro]` has no `path` line**, on purpose (1.7.24). To co-develop
  libro, add it locally and build with `CYRIUS_LOCAL=libro`.
- **`EPOLL_EVENT_SIZE` exists twice:** descent's enum member
  (`src/server.cyr`) and a stdlib `const` added in 6.7.12. It is harmless today;
  on the roadmap as hygiene.

## Toolchain

- **Pin:** `cyrius = "6.7.18"` in `cyrius.cyml`. It is the only source of truth;
  CI reads it and the YAML hardcodes no version.
- **Git first (6.7.6+).** A default build always builds the dep's **tag**, with
  its commit pin checked. `CYRIUS_LOCAL=<dep>` / `--local` is the only way a
  local checkout is used. `cyrius deps --locked` checks `lib/` and `cyrius.lock`
  against the tags and writes nothing.
- **`cyrius build` re-vendors the declared stdlib leaves** from the pinned
  snapshot. A hand-swapped `lib/<leaf>.cyr` does not survive a build, so A/B a
  library by moving the pin. When the pin moves while `lib/` holds stale snapshot
  files, re-locking is refused until `cyrius lib sync --full` runs.
- **A reachable undefined function is a build error** ("refusing to emit
  binary"), and it names the stdlib leaf to add. Older toolchains emitted a
  `ud2` that SIGILLed at runtime.
- **`cyrius fmt <file>…`** rewrites in place, and `--check` / `--dry` report;
  several files are accepted. The old `-w` flag is gone.
- **`cyrius audit`** is this project's release gate: fmt, lint, docs, tests and
  bench over `src`, `programs`, `tests`, `benches` and `fuzz`. Lint counts line
  length in bytes, and docs wants a comment on every public `fn`.
  - ⚠ A bench FAIL does not change audit's exit code, so read its bench summary
    line.
  - `cyrius audit --internal` is the compiler's own self-host gate. Do not run it
    here.

## Dependencies

Declared in `cyrius.cyml`:

- **stdlib** — `std` (string, fmt, alloc, io, vec, str, syscalls), plus assert,
  bench, args, net, chrono, result, tagged, fnptr, freelist, **fs** and
  **bayan**.
  - **A leaf descent's own code calls must be listed here.** From 6.6.18 a
    bundle's `.deps` sidecar names only what the bundle itself needs: libro's is
    just `hashmap`, and sigil-mldsa and patra carry `# Requires` blocks. `fs`
    (`dir_list` in `persist.cyr`) and `bayan` (`cyml_*`, `bayan_toml_*`) are
    listed for that reason.
- **libro** `2.11.3` (git, tag only) — the append-only SHA-256 hash-chain audit
  log, through its **FileStore** (`filestore_open` / `filestore_append`).
  - It brings sigil's thin sub-bundles (`sigil-mldsa`, `sigil_sha256`,
    `sigil_sha_ni`, `sigil_hex`), which hold descent's whole sigil surface:
    Ed25519, SHA-256 and hex. It also brings patra, which descent never calls.
  - descent calls bayan's TOML lookups by their 1.11.0 names,
    `bayan_toml_get_by_cstr` and `bayan_toml_get_sections_by_cstr`.

⚠ **The transitive downgrade.** `cyrius deps` writes a declared dep's copy *over*
the `lib sync --full` snapshot. So a dep pinning an older tag than the toolchain
folds silently downgrades that file, and `deps --verify` agrees with itself
because the lock is regenerated from the downgraded file. It cost CI parity
twice: sakshi from 1.2.0 to 1.7.21, and patra at 1.7.23.

**The pairing to keep:** libro's `[deps.patra]` and `[deps.sigil]` equal what the
pinned cyrius folds. Today both match (patra 1.16.6, sigil 3.13.15). When moving
the pin, pick the libro tag whose own `cyrius =` matches, and read its pins **at
the tag**:

```sh
sed -n 2p ~/.cyrius/versions/<pin>/lib/patra.cyr          # what the toolchain folds
grep -A3 -F '[deps.patra]' ~/.cyrius/deps/libro/<tag>/cyrius.cyml
cyrius deps --locked                                       # lib/ + lock == the tags
```

For a full check, copy the manifest and sources somewhere with no siblings, run
`cyrius lib sync --full && cyrius deps` there, and `diff -rq` the two `lib/`
trees; it must print nothing. A tag *newer* than the fold is an upgrade, not this
bug.

## Source layout

```
src/                       12,726 lines
  main.cyr        117      argv dispatch (serve / version / help), VERSION_STRING,
                           include order
  telnet.cyr      435      RFC 854 IAC parser + RFC 1143 negotiation; pure, no I/O
  parser.cyr      830      verb-noun parser: tokenizer, verb table, keyword-prefix
                           resolution, preposition split, all.X / N.X; pure
  world.cyr       438      CYML zone loader, rooms, exits, zone-reset cadence
  mob.cyr         845      mob templates + instances, actor tick, respawn
  item.cyr       1265      objects, corpses + loot, inventory verbs, ground decay,
                           object census, respawn
  combat.cyr      418      RNG, d20 hit + NdM damage, kill/flee, rounds, death/respawn
  classes.cyr     708      the 4 classes, selection phase, 12 abilities, classes_upkeep
  session.cyr    2105      session struct, login phases, dispatch, rendering, the
                           tx/rx queues, mud_now_ms
  persist.cyr    3416      Ed25519 identity, signed record writer + two readers,
                           crash-safe publish, sharded player paths, account cap,
                           libro audit chain + rotation (ADR 0009)
  server.cyr     2135      event loops (Linux epoll + AGNOS poll), listener, tick
                           scheduler, idle reap, save sweep, zone reset, @-admin
  test.cyr         14      [build].test no-op stub (see above)

data/        classes.cyml; zones/hub.{rooms,mobs,objs}.cyml (the 21-room Hub);
             zones/example.rooms.cyml. players/ and audit*.libro are runtime
             output and gitignored.
tests/       cyrius-yeomans-descent.tcyr (9,200 lines, 74 groups); .bcyr / .fcyr
             scaffold stubs; fixtures/ (rejection fixtures for rooms, classes,
             objs, server.cyml)
benches/     bench_telnet, bench_combat, bench_persist, bench_loaders,
             bench_tick_budget
fuzz/        parser_fuzz, record_fuzz
programs/    crypto_smoke (the libro + sigil chain resolves and runs),
             persist_smoke (a save → reload round-trip on disk)
scripts/     agnos-qemu-smoke.sh + agnos_probe.py (the real-kernel harness)
```

## Tests, benches, fuzz

**Tests.** `cyrius test` runs **1502 assertions** in 74 groups, plus the
`[build].test` stub. The suite writes to a fixture audit log, never
`data/audit.libro`. Timing groups use synthetic clocks, RNG-dependent assertions
retry, and a test must be idempotent.

**Benches.** `cyrius bench` runs five real benches. Each one gates: it asserts a
budget and fails on breach. These numbers are from this machine on 2026-11-02:

| Bench | Measures | Now |
|---|---|---|
| `bench_telnet` | IAC parser cost per byte | under its 30 ns/byte budget |
| `bench_combat` | 32 players × 64 mobs | p99 **512 µs** (budget 50 ms) |
| | 256 players co-located (broadcast) | p99 **33.4 ms** (budget 50 ms) |
| `bench_persist` | bump-arena bytes per op | `_build_record` **0 B**, `player_save` **0 B** (max 1,750), `player_auth_load` **90 B** (max 256) |
| `bench_loaders` | boot loaders + "a rejected file publishes nothing" | rooms 194 µs, objs 51 µs, mobs 43 µs (budget 20 ms) |
| `bench_tick_budget` | the charge table, and pre-tick work | `ident_derive` 871 µs against 1,750 charged; pre-tick check 6 ms of 50 |

⚠ **`bench_combat`'s broadcast case and `bench_tick_budget`'s calibration are
host-load sensitive.** Both printed FAIL at 1.7.24 on a host saturated by an
unrelated job, and both fail equally on older trees under the same load. Check
`/proc/loadavg`, and A/B against the previous tree, before believing one. The
broadcast cost grows as N²: it breaches 50 ms at about N = 345 (item K).

**Fuzz.** `cyrius fuzz` runs two targets of 100k iterations each, and the
harnesses assert their own coverage:
- `parser_fuzz` drives the M2 parser.
- `record_fuzz` drives the pre-auth record scanner `_scan_kv`.

**The CYML zone and class loaders have no fuzz target.**

## CI

- **`ci.yml`** (push and PR to `main`): install the pinned toolchain, run
  `cyrius deps`, build x86_64, build `--agnos`, run bare `cyrius test`, then run
  `cyrius audit`.
  - The `--agnos` build is compile protection only; nothing in CI executes it.
  - `cyrius deps --locked` is not adopted yet.
- **`release.yml`** checks the version, installs the toolchain, builds, and
  creates the release. It gates on `ci.yml` through `workflow_call`.

## Security posture

- **Every loaded record field is bounded:** `_clamp`, exact hex lengths, `class`
  range, passphrase length, and `schema` ≤ current.
- **The two record readers must agree on `salt` and `pubkey`.**
- **The `@`-admin namespace is off unless `YD_ADMIN=1`,** and there is no
  operator authentication yet (M18).
- **TLS is out of scope;** wrap the listener in `stunnel` or an SSH tunnel.
- The `security`, `freeze` and `persist` test groups are the regression floor.

## Lessons carried

Each of these cost at least one release to learn.

- **A rule applied at one site and not its sibling** was the dominant defect for
  seven sweeps (nine of nine in re-run #4). When a fix changes a predicate, grep
  every call site and every caller of the function it lives in, and record that
  list in the fix's comment. It worked: re-run #5's "our own fixes are
  incomplete" signal fell from 7 of 9 to 1 of 12. Two extensions:
  - **Enumerate a guard's class from the WRITER.** `_build_record` has exactly
    four `_fstr` calls; BQ covered three because someone listed them from memory.
  - **A fix can have a mirror image.** BC (1.7.19) and BL (1.7.21) were one code
    path in opposite directions. Moving the check earlier deleted both.
- **Fixing an instance is not fixing the class.** Enumerate first: `grep -n
  ident_derive src/` lists every expensive-line path, and "every loop that
  dispatches lines" lists every place a cap must be aggregate.
- **A comment is not a bound.** Write the number down, then make a bench assert
  it.
- **A finding count measures the instruments, not the code.** Each sweep found
  serious defects exactly where the previous one had no instrument. The QEMU
  harness found BU within minutes, and the first real-kernel persistence test
  found BV.
- **A mutation that fails to fail is a signal about the test.** Recurring causes:
  - `var buf[N]` is N **bytes**.
  - A test reimplements the logic instead of calling it.
  - A budget that is an exact multiple of the cap.
  - Asserting a derived total instead of the thing itself.
- **A test that dies silently reads like a pass.** Anything handed to
  `drop_session` goes through `_freeable_sess`.
- **RSS is the wrong instrument for a bump-arena leak.** Use `alloc_used()`; use
  a control arm for freelist leaks.
- **An instrument can be wrong too.** The stock AGNOS probe reported a frozen
  clock and a stalled loop that were not there. Run a new probe against Linux
  first, and give it a negative control.

## Picking it up cold

```sh
cyrius deps --locked                                   # lib/ + lock match the tags
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius build src/main.cyr build/cyrius-yeomans-descent-agnos --agnos
cyrius test                                            # 1502 assertions
cyrius audit                                           # the release gate — must exit 0
./build/cyrius-yeomans-descent serve 4000              # then: telnet localhost 4000
```

If `cyrius audit` does not exit 0, you have inherited a regression; fix it
before new work. Read, in order:
1. [`CLAUDE.md`](../../CLAUDE.md) for the rules and the release process;
2. this file;
3. [`roadmap.md`](roadmap.md) "What is left";
4. [`../architecture/overview.md`](../architecture/overview.md) for the design;
5. [`../guides/running.md`](../guides/running.md) for the `YD_*` knobs and
   operation.

**Release drill.** Do this beyond `cyrius audit`, for a release that touches
behaviour:
- an adversarial pass at every prompt;
- a playtest in which each class clears the Hub, reconnect restores state, room
  and inventory, resets restock, and `passwd` re-keys;
- surface conformance against [ADR 0007](../adr/0007-frozen-1.0-surface.md);
- version sync across `VERSION`, `CHANGELOG.md` and `VERSION_STRING`.

The 1.x surface is frozen: no new verbs, save fields, zone fields or env knobs
until ADR 0008.

## ADRs

0001–0007 and 0009 are Accepted; **0008 is reserved for M14**. ADR 0006's atomic
publish stands: BV is being left to agnos rather than worked around. M18's operator
channel will earn its own ADR.

## Consumers

_None._
