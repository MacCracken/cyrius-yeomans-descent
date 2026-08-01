# cyrius-yeomans-descent — Handoff

> **Written**: 2026-08-01, at **v1.7.21**.
> **Read this first, then [`roadmap.md`](roadmap.md) "What is left".**
>
> This is a point-in-time handoff, not a living document. If the date above is
> old, trust [`state.md`](state.md) and [`roadmap.md`](roadmap.md) over it.

---

## Where the project actually is

**The 1.x line is one target away from closing, and that target's defects are not
this repo's to fix.**

Six releases shipped in rapid succession — **1.7.16 through 1.7.21** — closing
roughly thirty defects across gate re-runs #3, #4 and #5. All gates are green:

| | |
|---|---|
| `cyrius audit` | exit 0 — fmt, lint, docs, tests, bench |
| tests | **1502 assertions**, 0 failed |
| benches | 6/6 · fuzz 2/2 · x86_64 **and** `--agnos` build |
| version | `VERSION`, `cyrius.cyml`, CHANGELOG and `src/main.cyr:44` all say 1.7.21 |

**Gate re-run #5 ruled DO-NOT-CLOSE at 0 critical / 3 high / 5 medium / 4 low —
and every one of the three highs was on the AGNOS build.** On x86_64 the run came
back with **zero highs for the first time in seven sweeps**, after five agents
drove a live server for hours, forced ~95 audit rotations, forged ~40 signed
records, put 250 real TCP players in sustained combat, and soaked for 39 minutes.

So the honest summary is: **the Linux server is in good shape. The 1.x gate is
held open by a second target that, until 1.7.21, nothing had ever executed.**

---

## The three things that block 2.0

### 1. BU — nobody can log in on a real AGNOS kernel *(new, and the worst)*

Found within minutes of the QEMU harness existing. A player connects, is greeted,
gives a name, is prompted for a passphrase — and the server **dies the instant the
passphrase is submitted**, `run: exit 142` (the kernel's ring-3 page-fault kill
code). **Character creation and login have never worked on AGNOS**, in any release
since `--agnos` shipped in 1.1.0.

Everything up to that point works, which is what makes the finding precise: the
zone loads, `sock_listen` binds, `sock_accept` returns a tagged fd, the 213-byte
MOTD and the Telnet `IAC WILL ECHO` salvo arrive intact, an empty line is handled,
a name is accepted, the phase advances. An idle connection is stable.

Bisected to **`ident_derive`** — the Ed25519/SHA-256 key derivation — and inside
it to the crypto's per-thread scratch banking: `cbank()`
([`lib/sigil-mldsa.cyr:560`](../../lib/sigil-mldsa.cyr:560)) calls
`crypto_tls_main_init()` and `thread_local_get`, self-installing a TLS block on
first use.

**Not fixable from this repo.** `lib/` is vendored and off-limits (CLAUDE.md), and
the other half is the agnos kernel's TLS support.

### 2. BJ — a stalled client freezes the whole AGNOS server

`session_drain` ([`session.cyr:715`](../../src/session.cyr:715)) tests exactly one
would-block code, Linux `EAGAIN` (-11). On AGNOS `sys_write` routes to `sock_send`
#48, which **blocks** and has no EAGAIN — so the arm is dead code and one client
that stops reading parks the single-threaded loop. Measured under emulation: a
bystander's `look` went 0.000 s → 15.7 s.

The read half of this got an explicit AGNOS branch at
[`session.cyr:1970`](../../src/session.cyr:1970), under a comment that is word for
word true of the write half. **agnos exposes no non-blocking send primitive at
all**, so this needs a decision, not a patch.

### 3. The upstream conversation — BU + BJ + AA, together

Item **AA** (16 bytes leaked per accept, in `lib/net.cyr`) has been waiting on the
same kind of decision since 1.7.9. All three are "what does `lib/` owe the AGNOS
target". **Have them as one conversation.** Patching around any of them
individually would be guessing at an API nobody has agreed.

> **There is a policy alternative**, and it should be taken deliberately or not at
> all: **scope AGNOS out of the 1.x gate.** That closes the gate today. Against it
> — item T (1.7.8) was an AGNOS-only defect rated high and closed as high, and
> `running.md` has advertised AGNOS as a supported deployment since 1.1.0. **If
> you take it, write it into ADR 0007 as a contract change, not into a sweep
> verdict.**

---

## What is new in the tree that a newcomer would not expect

- **`scripts/agnos-qemu-smoke.sh` + `scripts/agnos_probe.py`** — a QEMU-direct
  AGNOS harness, new in 1.7.21. It boots a real kernel and drives descent over
  TCP. **It needs no patch to the agnos kernel**: the kernel's
  `BENCH_CONNECT_SELFTEST` hook reads a command from `/etc/probe-cmd` and runs it,
  so descent is launched by staging a file. Build the kernel once with
  `BENCH_CONNECT_SELFTEST=1 sh scripts/build.sh` in the agnos checkout.
  **Do not resurrect the old agnosticos `docker/descent-sweep/` harness** — it was
  retired on purpose in July as "the dead VM-in-a-container pattern".
- **`mud_now_ms()`** ([`session.cyr`](../../src/session.cyr)) — descent's own
  monotonic clock. Every scheduling site routes through it. On AGNOS it reads
  rdtsc-based `uptime_us` #95, because #40 is documented frozen for a foreground
  `run` program. **Do not call `clock_now_ms()` directly in `src/`**; the only two
  remaining calls are that wrapper's own fallbacks.
- **`MAX_SESSIONS` is target-aware** — 256 on Linux, **7 on AGNOS**, because the
  agnos syscall layer's connection table has 8 slots and the listener holds one.
- **`@shutdown`** — a new admin verb behind `YD_ADMIN`. On AGNOS it is the *only*
  clean shutdown; that build has no signalfd.
- **The record scanner** ([`persist.cyr`](../../src/persist.cyr)) — an
  authenticated login now skips `toml_parse` entirely when `_scan_canonical`
  vouches for the record (2,332 → 84 bytes/login). If you touch record reading,
  **the two readers must agree on every field** — there is a differential test for
  exactly that.

---

## The lesson this codebase keeps re-learning

**For seven consecutive sweeps the dominant defect has been *a rule applied at one
site and not its sibling*.** In gate re-run #4 it was nine out of nine, and six of
those were siblings of fixes shipped in the three releases immediately prior.

That prescription — **when a fix changes a predicate, grep every call site of that
predicate and every caller of the function it lives in, and record the enumeration
in the fix's own comment** — measurably worked: in re-run #5 the "our own recent
fixes are incomplete" signal collapsed from 7-of-9 to **1-of-12**.

Two extensions earned since:

- **Enumerate a guard's class from the WRITER.** Item BQ covered three of four
  string fields because someone listed the ones they were thinking of;
  `_build_record` has exactly four `_fstr` calls and could have been grepped.
- **A fix can have a mirror image.** BC (1.7.19) and BL (1.7.21) are the same code
  path one release apart, in opposite directions — the compensating fix reasoned
  about the clamped case and not the un-clamped one. The cure was to stop
  compensating: moving the check earlier deleted both halves *and* the function BC
  had added.

---

## Instruments that still do not exist

Two sweeps running have named the first of these as the highest-value thing to
build, and it is still not built:

1. **The conservation invariant.** `world_count + offline_record_count ==
   authored_count`, for every authored id, **as a real test in `cyrius audit`**.
   It would have caught AM four sweeps ago; it caught two defects as a throwaway
   probe in #4; and #5 produced two more (BL, BT) that it would have caught.
   Nothing in the tree reads `g_obj_offline` directly, so every census measurement
   to date is a threshold oracle that cannot tell a phantom count of 1 from 5.
2. **A CYML loader fuzz target.** `cyrius fuzz` still has none. 31 hand mutations
   were run in #4 and found nothing; hand mutation is spent.
3. **Audit-chain self-hash verification.** Both verifiers so far checked linkage
   only.
4. **A multi-hour soak in a single run.** Best so far is 22.8 minutes.
5. **A forged-signature harness in the tree.** Two were built as throwaways and
   both are gone; ~150 lines, and it is the only way to test ADR 0004's stated
   threat model.

**Process note for the next sweep:** agents must kill servers **by port or PID,
not by name**. Two soaks in #5 were lost to a sibling agent's `pkill -f descent`.

---

## If you are picking this up cold

```sh
cyrius deps
cyrius build src/main.cyr build/cyrius-yeomans-descent
cyrius audit            # the release gate — must exit 0
```

Read, in order: [`CLAUDE.md`](../../CLAUDE.md) for the rules,
[`state.md`](state.md) for the current snapshot, [`roadmap.md`](roadmap.md)
"What is left" for the five open items, and
[`../architecture/overview.md`](../architecture/overview.md) for the design.

**The one rule worth repeating here**, because it is the one this project has
paid for most often: *do not skip tests before claiming a change works, and when
you fix something, check whether its sibling has the same bug.*
