# cyrius-yeomans-descent

**Yeoman's Descent** — a Cyrius-native text-based MUD set in a gritty techno-feudal universe. Players begin as serfs or squires and delve into the "Under-Grid": a subterranean arcology of ruined servers, rusted automated defenses, and rogue AI fiefdoms. Pure text parsing, ANSI color, deep world-building — the DikuMUD / LPMud era reproduced on a modern, sovereign stack.

Written in [Cyrius](https://github.com/MacCracken/cyrius). Part of [AGNOS](https://github.com/MacCracken/agnosticos).

## Why

- **Cyrius-native TCP server** — no external runtime, no glibc dependency
- **Verb-noun parser** — `give monoblade to kiran`, `put all.rations in backpack`
- **2.5-second combat tick** — hidden 1d20 + modifiers vs. AC, classic THAC0 math
- **Four classes** — Pikeman (tank), Splicer (caster/hacker), Courier (rogue), Chaplain (healer)
- **Zone resets** — every 15-30 minutes, but only when no players are present
- **Persistent state** — backed by [T.Ron](https://github.com/MacCracken/t-ron); managed via [Joshua](https://github.com/MacCracken/joshua)

Full design: [`docs/architecture/overview.md`](docs/architecture/overview.md).

## Quick Start

```sh
cyrius deps                                              # resolve stdlib deps
cyrius build src/main.cyr build/cyrius-yeomans-descent    # compile
cyrius test                                              # unit + integration tests
```

Connect with a standard Telnet client (Mudlet, CMUD) or a browser-based Telnet wrapper.

## Docs

- [Design overview](docs/architecture/overview.md) — combat, classes, parser, zones
- [Roadmap](docs/development/roadmap.md) — milestone plan through v1.0
- [Current state](docs/development/state.md) — live snapshot, refreshed every release
- [Getting started](docs/guides/getting-started.md) — build, test, contribute
- [Decision records](docs/adr/) — *why did we choose X over Y?*
- [Architecture notes](docs/architecture/) — non-obvious invariants

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CLAUDE.md`](CLAUDE.md). Security issues: [`SECURITY.md`](SECURITY.md).

## License

[GPL-3.0-only](LICENSE).
