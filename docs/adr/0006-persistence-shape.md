# 0006 — Persistence shape

**Status**: Accepted
**Date**: 2026-06-09

## Context

M6 must let players survive a server restart, crash-safely, without blocking
the single-thread event loop ([ADR 0003](0003-single-thread-event-loop-concurrency.md)
— disk I/O can't stall the 2.5 s tick). The roadmap framed persistence as
"T.Ron-backed," but the actual `t-ron` repo is an MCP security monitor, not a
store; the crash-safe primitive in its dependency chain is **libro** (an
append-only SHA-256 hash-linked log). M6-A landed **libro + sigil** as the
persistence stack (see [`state.md`](../development/state.md)).

Two shapes of state to persist, with different access patterns:

1. **Player records** — read by name at login, rewritten wholesale on save.
   Random-access, last-writer-wins. *Not* a natural fit for an append-only log.
2. **Security events** — login success/failure, character creation, saves.
   Append-only, never rewritten, want tamper-evidence. *Exactly* a hash chain.

## Decision

**Player state lives in one file per player; security events live in a libro
audit chain. Both writes are crash-safe.**

- **Player record**: `data/players/<c>/<lower(name)>.cyml`, a single `[player]`
  section. **Sharded into a one-character subdirectory since 1.7.2** (36 buckets,
  by the first character of the name) so a world with thousands of accounts is not
  one directory of thousands of files. Pre-1.7.2 records sit flat at
  `data/players/<lower(name)>.cyml`; the load path still reads them and the next
  save migrates the record and unlinks the flat copy. **An operator looking for a
  character's file must look in the shard, not the top level.**
  TOML section (reusing the project's existing toml/cyml reader — same family
  as [ADR 0005](0005-zone-file-format.md) zones). Fields: identity (salt +
  pubkey per [ADR 0004](0004-identity-and-authentication.md)), class, room
  (by **stable id string**, not index — survives zone reload), attrs
  (STR/DEX/CON/TEC), vitals (HP/MAXHP/AC/ENERGY/…), combat profile, inventory
  (comma-joined template ids, re-instantiated on load), and created /
  last-login timestamps. The record ends with an Ed25519 `sig` over its own
  prefix; load verifies before trusting any field.
- **Crash-safe write (M6-F)**: serialize → write to `<name>.cyml.tmp` →
  `rename(2)` over the live file. Rename is atomic, so a crash leaves either
  the complete old record or the complete new one — never a torn file. A stale
  `.tmp` from a crashed write is simply overwritten next save.
- **Save triggers (M6-D)**, all out of the command hot path: on `save`, on
  disconnect (`quit` / idle reap / dropped socket, via `drop_session`), at
  character creation, a **debounced ~5-minute sweep** in the tick that writes only
  sessions flagged dirty since their last save, and — **added 1.7.11** — on
  **signalled shutdown**, which walks every live session before the process exits.
  That last one was missing for the whole 1.x line: this list was the specification
  and the code matched it, so a clean SIGTERM silently discarded up to five minutes
  of progress for every connected player. A trigger list is a contract; the gap was
  in the contract as much as in the code.
- **Not every authenticated session is persistable.** `SS_AUTHED` is set before
  class selection, so `session_persistable` (1.7.11) also requires a chosen class:
  a character abandoned at the class menu has no room, no inventory and no
  progress, and writing `class = -1` for it produced a record nothing could repair
  — records are signed with a key derived from the passphrase, which the server
  never holds (ADR 0004). Such records are healed at login by returning the player
  to the class menu.
- **Audit chain**: a libro `FileStore` hash chain at `data/audit.libro`;
  every login/save/creation/auth-failure/tamper-rejection appends a signed,
  hash-linked entry — the tamper-evident "T.Ron" trail the roadmap named.
- **Transient state is not persisted**: combat target, cooldowns, buffs,
  stealth reset on load. A restored player respawns *at their room*, not
  mid-fight — which is the correct resolution of "killed during combat."

## Consequences

- **Positive** — O(1) load by name; whole-record rewrite is simple and matches
  how player state actually changes; atomic rename gives crash-safety without a
  journal or WAL; the audit chain gives tamper-evidence and exercises libro for
  real. Reusing the toml reader meant zero new parser surface **at 1.0. That is no longer
true**: 1.7.8 added a strict raw scanner for the pre-auth `salt`/`pubkey` read, and
1.7.20 extended it so that an authenticated login whose record is canonical is read
**entirely by the scanner** (`_scan_kv` / `_scan_kv_bare` / `_scan_canonical`),
skipping `toml_parse` altogether — 2,332 bytes/login of never-reclaimed arena down
to 84. A "NO PARSER DIFFERENTIAL" guard and a per-field agreement test keep the two
readers honest. **Anyone scoping a fuzz target from this sentence would fuzz
`lib/toml.cyr` and miss the reader that actually runs**.
- **Negative** — one file per player doesn't scale to millions of accounts (fine
  for a MUD; revisit with `PatraStore` if it ever matters). Records are
  human-readable/editable on disk, but the Ed25519 signature makes unauthorized
  edits detectable. The debounced sweep means up to ~5 min of progress can be
  lost on a crash *between* saves — acceptable for a MUD; tighten the interval
  or add per-event saves if a zone demands it.
- **Neutral** — `rename(2)` isn't wrapped in the x86_64 stdlib, so persist.cyr
  calls syscall 82 directly (documented). Timestamps use wall-clock
  `get_epoch_secs` (libro); created is preserved across saves via the in-session
  identity block.

## Alternatives considered

- **libro FileStore as the player store** (state as JSON in append entries;
  load = scan latest per name). One mechanism, crash-safety for free — but
  append-only growth and an O(n) load scan for what is fundamentally
  last-writer-wins random-access data. Rejected as a poor fit; kept libro for
  the append-only thing it's actually good at (audit).
- **Sigil-only + hand-rolled atomic files, no libro.** Lightest path to the
  gate, but throws away the tamper-evident audit trail the design wanted.
  Rejected — libro is already in the chain via [ADR 0004](0004-identity-and-authentication.md)'s
  sigil dependency, so the audit chain is cheap to add and worth it.
- **Single transactional store for all players (one file + index).** Tighter on
  disk and one fsync per batch, but reintroduces the torn-write problem the
  per-file rename trivially avoids, and needs its own locking. Rejected for M6.
