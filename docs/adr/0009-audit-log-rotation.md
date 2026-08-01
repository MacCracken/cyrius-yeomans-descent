# ADR 0009 — Audit-log rotation by seal-and-continue

- **Status**: Accepted
- **Date**: 2026-07-29
- **Supersedes**: none
- **Amends**: [ADR 0006 — Persistence shape](0006-persistence-shape.md) (the audit-chain half only; 0006 stays Accepted)
- **Implemented in**: 1.7.4 (mechanism) — the *decision* and the seam were 1.7.1. See [Implementation status](#implementation-status).

> **Numbering note.** This is 0009, not 0008. 0008 is **reserved for M14**, which
> supersedes ADR 0007 with the 2.x surface, and is referenced by that number in
> the roadmap, in `state.md`, and in two places in the shipped CHANGELOG.
> `README.md` in this directory says *never renumber*, and rewriting released
> history for cosmetic ordering is a worse trade than a number landing out of
> order.

## Context

`data/audit.libro` is append-only and **nothing has ever rotated it**. There is no
rotation code anywhere in the tree.

At the time of writing the working log holds **37,902 records in 13,336,880 bytes**
— about 350 bytes per event — and grows monotonically for the life of the
deployment. Nothing warns the operator, and nothing bounds it.

The forcing function is the finding 1.7.1 fixes on the memory side. Every audit
event cost 1,944 permanently-unreclaimable bytes of process memory, and a
reconnect flood could drive 667 MiB/hour of it, unauthenticated. That flood was
**also a disk flood** — 123 MiB/hour into this file — and 1.7.1's rollup window
bounds the event *count*, which cuts the disk growth by the same ~2,600×. That
removes the fire. It does not remove the need: legitimate operation still appends
forever, and an operator still has no signal and no lever.

**Truncation is not available.** [ADR 0006](0006-persistence-shape.md) makes this
log a SHA-256 **hash chain**: each entry records the hash of its predecessor, and
that linkage is the entire tamper-evidence mechanism. Deleting or rewriting any
prefix breaks verification for everything after it — which is precisely what the
chain exists to make impossible. So "rotation" here means *segmenting a chain
without breaking it*, which is a different and harder problem than rotating a log
file.

### What the investigation established

Three findings decided this, each verified against `lib/` rather than assumed:

1. **`verify_chain` never checks `entries[0].prev_hash` against anything.** It
   validates each entry's self-hash and, for `i > 0`, the link to its predecessor.
   So a segment file whose first entry points at the *previous* segment's tail is
   a **valid standalone file**, and the boundary is separately checkable by anyone
   holding both segments.
2. **No on-disk format change is required.** `filestore_append` writes one JSON
   line per entry with no header, and `filestore_open(path)` takes a path — so
   rotation is a rename plus a reopen. A pre-existing `data/audit.libro` becomes
   segment `.1` by rename, with no migration.
3. **libro's own `chain_rotate` is a trap here, not the answer.** It operates on
   the in-memory entries vec and guards its head-hash carry behind `if (n > 0)`.
   Descent uses `chain_new_streaming()`, which retains **no** entries, so that vec
   is always empty: `chain_rotate` would silently do nothing. `chain_apply_retention`
   fails the same way. Likewise **`chain_head_hash` returns 0** on a streaming
   chain because it reads the same empty vec; `chain_prev_hash` is the accessor
   that works.

## Decision

**Seal and continue, with a bounded segment count.**

On crossing a size threshold, the live file is **renamed** to the next free
`data/audit.libro.<N>` and appending continues to the same live path with the
**same streaming chain object**. Because that chain carries the head hash in its
prev-link slot, the first entry written after the rename automatically records the
sealed segment's tail hash as its predecessor. The boundary is therefore recorded
*by the chain itself*, not by external metadata.

Two markers make it legible to a human and to a verifier:

- **`audit.rotate`** — the first entry in the new live file, naming the segment
  just sealed and its head hash.
- **`audit.prune`** — written *before* unlinking the oldest segment when the
  retained count exceeds the keep limit, naming what is about to be deleted and
  its head hash, so a deletion is always attested inside the chain that survives.

Retention is a **segment count**, not a time window: it makes the on-disk bound a
simple multiplication (`threshold × keep`) rather than a function of traffic.

**Verifying a rotated chain** — the procedure an operator or a future tool follows:

1. Verify each segment independently (`filestore_load_all` → `verify_chain`).
2. For each adjacent pair, check that segment *N*'s last `"hash"` equals segment
   *N+1*'s first `"prev_hash"`. Greppable today; a `validate` argv verb is M14-E.
3. Cross-check every `audit.rotate` / `audit.prune` marker against the segment it
   names. A pruned segment is expected to be absent — the marker is the record
   that it was deleted deliberately.

**Failure handling is part of the decision, not an implementation detail:**

- If `rename` fails (ENOSPC, EXDEV, EACCES), **abort the rotation and keep
  appending to the live file.** The store must not be repointed at a fresh empty
  file while the real log is still live — that silently splits the chain.
- If the process dies after the rename and before the first append, the live file
  is empty and a naive boot restarts the chain at genesis, producing one broken
  link per boundary — indistinguishable from a deletion, and a reintroduction of
  the H11 bug fixed in 1.6.6. The boot-time head resume must therefore fall back
  to the tail of the **highest-numbered segment** when the live file yields no
  hash. This closes the only crash window and is load-bearing.

### Amended 1.7.21 — what changed under the verification walk

Three things moved after this ADR was written, and an operator running the walk
below on a current server can read a **legitimate failure as tampering**:

- **Prune sweeps, it does not pick one victim.** `_audit_prune` now walks DOWN
  from `newest - AUDIT_SEG_KEEP` to 1, so one rotation can retire several
  segments. The old single-arithmetic-victim form meant a skipped prune was never
  named again, which permanently inverted the segment numbering (item **BM**).
- **`audit.rotate.fail` is a third marker this ADR never mentions.** It is emitted
  when a prune cannot be attested (no readable tail hash) or when the `xunlink`
  fails. **A `audit.prune` marker naming a segment that is STILL ON DISK, next to
  an `audit.rotate.fail`, means the unlink failed — not that anyone tampered.**
- **Only the first `audit.prune` per 60 s window is verbatim.**
  `AUDIT_VERBATIM_MAX = 1` with a 60 s rollup window, so on exactly the
  multi-segment sweep above, the later prunes coalesce into a rollup whose
  `NAME_MAX = 16` truncation cannot carry a 64-hex hash. **Per-segment hash
  attestation is therefore not guaranteed** when several segments retire at once.

## Consequences

**Positive**

- On-disk growth becomes bounded by a constant the code owns
  (`threshold × keep`) instead of by uptime.
- Tamper-evidence is preserved *across* the boundary, and a deletion is attested
  inside the surviving chain rather than being invisible.
- Byte-identical line format. No migration, no libro release, no change to
  anything ADR 0007 freezes.
- An operator finally gets a signal: 1.7.1 already warns at boot when the log is
  over the threshold.

**Negative**

- **Verification is no longer a single-file operation.** Anyone checking the chain
  must walk segments in order and check boundaries. Until M14-E ships a tool, that
  is a documented manual procedure — a real ergonomic cost, and the main argument
  against this design.
- `grep -c '"action":"create.fail"' data/audit.libro` no longer gives a total:
  history is spread across segments, and (from 1.7.1) repeated events are
  coalesced into counts. Both are behaviour changes for anyone with existing
  one-liners.
- Pruning **deletes audit history by design**. The `audit.prune` marker records
  that it happened, which is an attestation, not a recovery.
- Rotation introduces a crash window that does not exist today. It is closable in
  about eight lines, and it needs its own mutation test.

**Neutral**

- The threshold and keep count are compile-time constants, deliberately: ADR 0007
  freezes the `YD_*` surface, so there is no operator knob. An operator on unusual
  hardware needs a code change — a named limitation, revisitable at 2.0.
- Segment files are a new operator-visible artifact under `data/`, covered by
  `.gitignore`.

## Alternatives considered

- **Truncate or delete the log.** Rejected outright: it destroys the property the
  chain exists for. Listed because it is the obvious thing and must be visibly
  refused.
- **libro's `chain_rotate` / `chain_apply_retention`.** Rejected because they are
  no-ops on a streaming chain — see Context (3). This is the most dangerous
  alternative precisely because it *looks* correct.
- **A sidecar manifest** recording each segment's starting prev-hash. Workable and
  rejected: the chain already carries the boundary, so a manifest is a second
  source of truth that can disagree with the log, and it needs its own atomic-write
  and crash story.
- **A signed Merkle tree head per sealed segment** (`merkle_build` →
  `sign_tree_head`, with `merkle_consistency_proof` showing *N+1* extends *N*).
  Strictly stronger than this design — it would also close the coherent
  whole-file-rewrite gap the chain does **not** currently detect. Deferred to 2.0
  with its own ADR. **The blocker is key management, not a missing primitive:**
  every libro primitive is present and unused, but Descent has no audit signing
  key, and [ADR 0004](0004-identity-and-authentication.md)'s whole shape is that
  the server holds no secret. An audit key is a new secret at rest with its own
  generation, storage, rotation and compromise story.
- **Time-based rotation (daily segments).** Rejected: it makes the disk bound a
  function of traffic rather than a constant, and it depends on a wall clock that
  is documented as frozen on one of the two supported targets.
- **Compressing sealed segments.** Deferred, not rejected. It is orthogonal and
  composes with this design; it just is not the bound.

## Implementation status

**1.7.1 — the decision and the seam** (shipped):

- This record, at status Accepted.
- `_audit_store_size()`, and a boot-time `audit.size` `SEV_WARNING` when the log
  is already over the threshold. The first signal an operator has ever had.
- The suite writes to a fixture audit log rather than the operator's, and audit
  assertions count exact entries instead of diffing file lengths. **This is a hard
  prerequisite:** with a size threshold and a 13 MB log, the first append during
  `cyrius test` would rotate the operator's log out from under them, and the old
  byte-delta assertions would fail.
- `.gitignore` covers `data/audit*.libro*`.

**1.7.4 — the mechanism** ✅ **SHIPPED** (was tracked in
[`roadmap.md`](../development/roadmap.md)): the rename/reopen, segment
enumeration, the keep-count prune, the `audit.rotate` / `audit.prune` markers, and
the boot-time head fallback that closes the crash window. Tracked as an explicit
roadmap item — *not* implied by this record being Accepted.

It is deferred one patch release for three reasons, all of them ordering rather
than obstacles: the test prerequisite above had to land first; the crash-window fix
is a second mechanism in the same file as 1.7.1's 15-call-site rewrite, and
CLAUDE.md says one change at a time; and 1.7.1's rollup window already took the
flood's disk growth from 123 MiB/hour to ~49 KiB/hour, at which point an 8 MiB
threshold is years away rather than hours.

## See also

- [ADR 0006 — Persistence shape](0006-persistence-shape.md) — the hash chain this
  amends.
- [ADR 0004 — Identity and authentication](0004-identity-and-authentication.md) —
  why there is no signing key to hang a Merkle head from.
- [ADR 0007 — Frozen 1.0 surface](0007-frozen-1.0-surface.md) — why the threshold
  is a constant and not an env knob.
