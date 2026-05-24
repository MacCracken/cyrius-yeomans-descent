# cyrius-yeomans-decent — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).
>
> **Last refresh**: 2026-05-24

## Version

**0.1.0** — scaffolded 2026-05-24 via `cyrius init`. No releases yet. Design captured; implementation has not begun beyond the scaffold `main()`/`test()` stubs.

## Toolchain

- **Cyrius pin**: `6.0.1` (in `cyrius.cyml [package].cyrius`)

## Source

- `src/main.cyr` — `println("hello from cyrius-yeomans-decent")` scaffold; no server, no parser yet
- `src/test.cyr` — top-level test entrypoint (empty)

Next-up module surface (per [roadmap M1](roadmap.md#m1--tcp--telnet-listener-v020)): TCP socket listener, per-connection session state.

## Design

- [`../architecture/overview.md`](../architecture/overview.md) — combat tick, classes, parser, zones, transport
- [`../adr/0001-tick-based-combat-over-cooldowns.md`](../adr/0001-tick-based-combat-over-cooldowns.md) — combat tick rationale
- [`../adr/0002-raw-tcp-telnet-protocol.md`](../adr/0002-raw-tcp-telnet-protocol.md) — transport rationale

## Tests

- `tests/cyrius-yeomans-decent.tcyr` — primary suite (smoke; passes on `cyrius test`)
- `tests/cyrius-yeomans-decent.bcyr` — benchmark stub (no-op)
- `tests/cyrius-yeomans-decent.fcyr` — fuzz stub

## Dependencies

Direct (declared in `cyrius.cyml`):

- stdlib — string, fmt, alloc, io, vec, str, syscalls, assert, bench

No external (non-stdlib) deps yet. T.Ron and Joshua integrations land later — see [roadmap M6](roadmap.md#m6--persistence-via-tron-v070) and [M8](roadmap.md#m8--joshua-management-interface-v090).

## Consumers

_None yet._

## In flight

Nothing in flight. Next slot is **M1 — TCP / Telnet listener** ([roadmap.md](roadmap.md#m1--tcp--telnet-listener-v020)).
