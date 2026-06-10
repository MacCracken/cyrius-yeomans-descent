# cyrius-yeomans-descent

**Yeoman's Descent** — a Cyrius-native text-based MUD set in a gritty techno-feudal universe. Players begin as serfs or squires and delve into the "Under-Grid": a subterranean arcology of ruined servers, rusted automated defenses, and rogue AI fiefdoms. Pure text parsing, ANSI color, deep world-building — the DikuMUD / LPMud era reproduced on a modern, sovereign stack.

Written in [Cyrius](https://github.com/MacCracken/cyrius). Part of [AGNOS](https://github.com/MacCracken/agnosticos).

## Why

- **Cyrius-native TCP server** — no external runtime, no glibc dependency
- **Verb-noun parser** — `give monoblade to kiran`, `put all.rations in backpack`, `kill 2.drone`
- **2.5-second combat tick** — hidden 1d20 + modifiers vs. AC, classic THAC0 math
- **Four playable classes** — Pikeman (tank), Splicer (caster/hacker), Courier (rogue), Chaplain (healer), each with three abilities
- **Zone resets** — on a per-zone timer (the Hub: 15 min), but only when no players are present
- **Persistent players** — Ed25519 identity derived from a passphrase via [sigil](https://github.com/MacCracken/sigil); crash-safe, signed per-player saves; a tamper-evident audit chain via [libro](https://github.com/MacCracken/libro)

Full design: [`docs/architecture/overview.md`](docs/architecture/overview.md).

## Status

**v1.0.0 — feature-complete.** The full game loop is implemented and playable:
the Telnet wire (RFC 854 / 1143), the verb-noun parser, a hand-authored 21-room
Hub zone, the 2.5 s combat tick with THAC0 hit/damage math, four playable
classes with abilities, crash-safe player persistence (reconnect restores your
attrs / room / inventory; survives a `kill -9`), and presence-gated zone resets.
0.9.0 was a security sweep; 0.9.1 froze the public surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).
See the [roadmap](docs/development/roadmap.md) and [current state](docs/development/state.md).

## Quick Start

```sh
cyrius deps                                               # resolve deps into lib/
cyrius build src/main.cyr build/cyrius-yeomans-descent    # compile
cyrius test                                               # 298 unit + integration assertions
./build/cyrius-yeomans-descent serve 4000                 # start the server on port 4000
```

Then connect with any Telnet client:

```sh
telnet 127.0.0.1 4000        # or: nc 127.0.0.1 4000
```

(Mudlet, TinTin++, or a browser WebSocket-to-Telnet bridge all work. A
conformant client honours the server's `WILL ECHO` and hides your passphrase.)

## Playing

1. **Log in.** Enter a name. A new name forges a character — you choose a
   passphrase (4–64 chars, entered twice, echo-suppressed). A known name asks
   for its passphrase. Your identity is an Ed25519 keypair *derived* from the
   passphrase; the server stores only a salt + public key, never the passphrase.
2. **Pick a calling** — Pikeman, Splicer, Courier, or Chaplain.
3. **Explore and fight.** `look`, `n`/`s`/`e`/`w`/`u`/`d`, `exits`, `get`/`drop`,
   `kill <mob>`, your class abilities (`bash`, `hack`, `backstab`, `patch`, …).
4. **Persist.** `save` writes your record; `quit` saves and disconnects; a
   reconnect restores you where you left off, with a "last seen" greeting. State
   also autosaves on a debounced timer, so a `kill -9` loses nothing committed.
5. **Re-key** with `passwd` to change your passphrase.

Type `help` in-world for the full command list. The complete reference lives in
[`docs/guides/commands.md`](docs/guides/commands.md); a first-session walkthrough
is in [`docs/guides/playing.md`](docs/guides/playing.md).

### Operating

| Env var | Default | Effect |
|---|---|---|
| `YD_TICK_MS` | `2500` | Combat-tick interval (ms). Lower it for fast testing. |
| `YD_IDLE_MS` | `300000` | Idle-disconnect threshold (ms). |
| `YD_RESET_SECS` | (zone's `reset_secs`) | Override the zone-reset interval (s). |
| `YD_ADMIN` | unset (off) | Set to `1` to enable the `@stats` / `@who` / `@reset` admin verbs. Off by default ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)); operator authentication is a post-1.0 item. |

See [`docs/guides/running.md`](docs/guides/running.md) for the operator guide.

## Docs

- [Design overview](docs/architecture/overview.md) — combat, classes, parser, persistence, zones
- [Roadmap](docs/development/roadmap.md) — milestone history + post-1.0 plan
- [Current state](docs/development/state.md) — live snapshot, refreshed every release
- [Getting started](docs/guides/getting-started.md) — build, test, contribute
- [Playing](docs/guides/playing.md) · [Commands](docs/guides/commands.md) · [Running a server](docs/guides/running.md)
- [Decision records](docs/adr/) — *why did we choose X over Y?* (ADRs 0001–0007)
- [Architecture notes](docs/architecture/) — non-obvious invariants

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CLAUDE.md`](CLAUDE.md). Security issues: [`SECURITY.md`](SECURITY.md).

## License

[GPL-3.0-only](LICENSE).
