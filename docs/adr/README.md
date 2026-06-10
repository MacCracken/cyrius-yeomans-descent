# Architecture Decision Records

Decisions about cyrius-yeomans-descent — what we chose, the context, and the consequences we accept. Use these when a future reader would reasonably ask *"why did we do it this way?"*

## Conventions

- **Filename**: `NNNN-kebab-case-title.md`, zero-padded to four digits. Never renumber.
- **One decision per ADR.** If a decision supersedes a prior one, add a new ADR and set the old one's status to `Superseded by NNNN`.
- **Status lifecycle**: `Proposed` → `Accepted` → (optionally) `Superseded` or `Deprecated`.
- Use [`template.md`](template.md) as the starting point.

## ADR vs. architecture note vs. guide

| Kind | Lives in | Answers |
|---|---|---|
| ADR | `docs/adr/` | *Why did we choose X over Y?* |
| Architecture note | `docs/architecture/` | *What non-obvious constraint is true about the code?* |
| Guide | `docs/guides/` | *How do I do X?* |

## Index

- [`0001-tick-based-combat-over-cooldowns.md`](0001-tick-based-combat-over-cooldowns.md) — Accepted — combat resolves on a 2.5s server-wide tick, not per-player cooldowns; keeps text output readable and load predictable.
- [`0002-raw-tcp-telnet-protocol.md`](0002-raw-tcp-telnet-protocol.md) — Accepted — the server speaks raw TCP / Telnet; browser clients use an external WebSocket bridge.
- [`0003-single-thread-event-loop-concurrency.md`](0003-single-thread-event-loop-concurrency.md) — Accepted — one kernel thread multiplexes all connections via epoll and owns world state; rules out fork-per-accept and threaded models on shared-state grounds.
- [`0004-identity-and-authentication.md`](0004-identity-and-authentication.md) — Accepted — identity is a sigil Ed25519 keypair derived from `SHA-256(salt‖passphrase)`; server stores only salt+pubkey, re-derives to authenticate, signs saves for tamper-evidence. Telnet-usable, no stored secret.
- [`0005-zone-file-format.md`](0005-zone-file-format.md) — Accepted — zones author in CYML (TOML header + markdown prose body), one file per zone per entity kind.
- [`0006-persistence-shape.md`](0006-persistence-shape.md) — Accepted — per-player signed `data/players/<name>.cyml` (atomic `.tmp`+rename) for state; libro hash-chain audit (`data/audit.libro`) for security events. libro is the crash-safe primitive; the t-ron MCP repo is not used.
- [`0007-frozen-1.0-surface.md`](0007-frozen-1.0-surface.md) — Accepted — the public surface locked for 1.0: command verbs + `@`-namespace (gated behind `YD_ADMIN`), save-record schema v1, Telnet/wire behaviour, zone-file format, env knobs. Post-1.0 changes need a major bump or a `schema` migration.
