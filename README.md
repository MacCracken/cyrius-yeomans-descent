# cyrius-yeomans-descent

**Yeoman's Descent** — a Cyrius-native text-based MUD set in a gritty techno-feudal universe. Players begin as serfs or squires and delve into the "Under-Grid": a subterranean arcology of ruined servers, rusted automated defenses, and rogue AI fiefdoms. Pure text parsing, ANSI color, deep world-building — the DikuMUD / LPMud era reproduced on a modern, sovereign stack.

Written in [Cyrius](https://github.com/MacCracken/cyrius). Part of [AGNOS](https://github.com/MacCracken/agnosticos).

## Why

- **Cyrius-native TCP server** — no external runtime, no glibc dependency
- **Verb-noun parser** — `give notice to kiran`, `get all from corpse`, `kill 2.scavver`
- **2.5-second combat tick** — hidden 1d20 + modifiers vs. AC, classic THAC0 math
- **Four playable classes** — Pikeman (tank), Splicer (caster/hacker), Courier (rogue), Chaplain (healer), each with three abilities
- **Zone resets** — on a per-zone timer (the Hub: 15 min), but only when no players are present
- **Persistent players** — Ed25519 identity derived from a passphrase via [sigil](https://github.com/MacCracken/sigil); crash-safe, signed per-player saves; a tamper-evident audit chain via [libro](https://github.com/MacCracken/libro)

Full design: [`docs/architecture/overview.md`](docs/architecture/overview.md).

## Status

**v1.7.22 — feature-complete, maintained.** The full game loop is implemented and
playable: the Telnet wire (RFC 854 / 1143), the verb-noun parser, a hand-authored
21-room Hub zone, the 2.5 s combat tick with THAC0 hit/damage math, four playable
classes with abilities, crash-safe player persistence (reconnect restores your
attrs / room / inventory; survives a `kill -9`), and presence-gated zone resets.

0.9.0 was a security sweep and 0.9.1 froze the public surface
([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)). **Everything since 1.6.0 has
been audit work** — 1.6.0 audited the tree and its fixes ran through 1.6.15, with
two re-run sweeps along the way; a third (gate) sweep produced the 1.7.x line.

**The first gate re-run returned DO-NOT-CLOSE** with five high findings, all now
closed: a `get` of a container ignored its contents and could destroy items on the
next save (1.7.7); five listing verbs ended mid-line with no prompt (1.7.6, 1.7.7);
**the AGNOS build never published a player record at all**, because syscalls 82/87
are GPU calls on that target (1.7.8); every login against an existing name
permanently consumed 2.2 kB before the passphrase was checked (1.7.8); and the
account cap stopped enforcing after records were sharded (1.7.6). 1.7.9 then closed
the RX-side class those releases' own sweeps turned up — a full queue could put a
half-sent Telnet escape on the wire. 1.7.10 moved the toolchain to 6.5.4, and
**1.7.22 moved it to 6.5.33** (libro `2.8.4 → 2.8.10`) — a dependency-only release
that found CI and the developer machine had been resolving different versions of a
vendored library since 1.2.0, and closed it.

**The line closes when a re-run comes back with nothing critical or high, not when
a checklist reaches zero.** Three sweeps have run and every one found real defects
the previous pass had no instrument for. See the
[roadmap](docs/development/roadmap.md#what-is-left) for every open finding with its
impact and fix size, and [current state](docs/development/state.md) for the live
snapshot.

## Quick Start

```sh
cyrius deps                                               # resolve deps into lib/
cyrius build src/main.cyr build/cyrius-yeomans-descent    # compile
cyrius test                                               # 1502 unit + integration assertions
./build/cyrius-yeomans-descent serve 4000                 # start the server on port 4000
```

Then connect with any Telnet client:

```sh
telnet 127.0.0.1 4000        # or: nc 127.0.0.1 4000
```

(Mudlet, TinTin++, `nc`, or a browser WebSocket-to-Telnet bridge all work. Your
client line-echoes what you type for names and commands; at the passphrase prompt
the server takes over echo and masks each character with `*`.)

### On AGNOS

Since **1.1.0**, Descent also builds and runs as a sovereign ring-3 service on the
[AGNOS](https://github.com/MacCracken/agnosticos) kernel itself — no Linux, no libc,
the same source behind `#ifdef CYRIUS_TARGET_AGNOS`:

```sh
cyrius build --agnos src/main.cyr build/descent-agnos     # static agnos ELF64
```

`agnsh` execs it from disk and it serves over the AGNOS kernel's TCP stack:

```
[ASSIST] > run /bin/descent serve 4000
```

> ### ⚠ EXPERIMENTAL — a player cannot log in on AGNOS
>
> This section claimed the AGNOS build was "byte-identical" to the Linux server
> and differed only internally. **Both halves were wrong**, and a QEMU harness
> built in 1.7.21 — the first thing ever to run this target on a real kernel —
> showed how:
>
> - **Authentication is broken.** The server **dies the instant a passphrase is
>   submitted** (ring-3 page fault at `ident_derive`; roadmap item **BU**).
>   **Nobody has ever logged in on AGNOS.** Everything before that works — the
>   loaders, the listener, the MOTD, the Telnet salvo, name entry.
> - **The population ceiling is 7, not 256** — the agnos syscall layer's
>   connection table has 8 slots and the listener holds one.
> - **One client that stops draining freezes the whole server** (item **BJ**).
>
> BU and BJ both land in vendored `lib/` plus the kernel's TLS and socket support,
> so **neither is fixable from this repo**; they are an upstream conversation
> alongside item AA. The build compiles, CI builds it, and the event loop, loaders
> and wire all work — but **do not deploy it.**

The internal difference is real and unchanged: AGNOS `epoll` watches only
signalfd/timerfd (never sockets) and is 3-arg, so the Linux epoll socket-multiplexer
becomes a `sleep_ms`-paced poll loop (non-blocking `sock_accept`#57 + `sock_recv`#49).
There is no signalfd, so **`@shutdown` is the only clean exit**
([ADR 0003](docs/adr/0003-single-thread-event-loop-concurrency.md),
[ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).

To boot AGNOS and drive the MUD end-to-end under QEMU:

```sh
scripts/agnos-qemu-smoke.sh        # see docs/guides/running.md for prerequisites
```

The container harness this used to name (`agnosticos/docker/descent-sweep`) was
**deleted on 2026-07-07** — that architecture was retired deliberately.

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
   also autosaves about every five minutes per character, so a `kill -9` loses
   nothing committed. You can carry 100 items — past that the server says so
   rather than silently failing to save you (1.6.13).
5. **Re-key** with `passwd` to change your passphrase.

Type `help` in-world for the full command list. The complete reference lives in
[`docs/guides/commands.md`](docs/guides/commands.md); a first-session walkthrough
is in [`docs/guides/playing.md`](docs/guides/playing.md).

### Operating

| Env var | Default | Effect |
|---|---|---|
| `YD_TICK_MS` | `2500` | Combat-tick interval (ms). Lower it for fast testing. |
| `YD_IDLE_MS` | `300000` | Idle-disconnect threshold (ms) for players who have authenticated **and chosen a class**. Two shorter deadlines sit under it and neither is tunable: **30 s** unauthenticated (1.6.13) and **90 s** parked at the class menu (1.7.19). |
| `YD_RESET_SECS` | (zone's `reset_secs`) | Override the zone-reset interval (s). |
| `YD_ADMIN` | unset (off) | Set to `1` to enable the `@stats` / `@who` / `@reset` / `@shutdown` admin verbs. Off by default ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)); real operator authentication is **M18**. |
| `YD_MAX_ACCOUNTS` | unset | Maximum player accounts; `0` = unlimited. Overrides `max_accounts` in the optional `data/server.cyml` (1.7.2). |

See [`docs/guides/running.md`](docs/guides/running.md) for the operator guide.

## Docs

- [Design overview](docs/architecture/overview.md) — combat, classes, parser, persistence, zones
- [Roadmap](docs/development/roadmap.md) — milestone history + post-1.0 plan
- [Current state](docs/development/state.md) — live snapshot, refreshed every release
- [Getting started](docs/guides/getting-started.md) — build, test, contribute
- [Playing](docs/guides/playing.md) · [Commands](docs/guides/commands.md) · [Running a server](docs/guides/running.md)
- [Decision records](docs/adr/) — *why did we choose X over Y?* (ADRs 0001–0009)
- [Architecture notes](docs/architecture/) — non-obvious invariants

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CLAUDE.md`](CLAUDE.md). Security issues: [`SECURITY.md`](SECURITY.md).

## License

[GPL-3.0-only](LICENSE).
