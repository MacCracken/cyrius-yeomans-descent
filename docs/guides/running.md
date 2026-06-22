# Running a server

Operating a Yeoman's Descent server. For the player experience see
[playing.md](playing.md).

## Build & run

```sh
cyrius deps                                               # resolve deps into lib/
cyrius build src/main.cyr build/cyrius-yeomans-descent    # static ELF, no runtime
./build/cyrius-yeomans-descent serve 4000                 # listen on TCP 4000
```

Other commands: `./build/cyrius-yeomans-descent version` · `… help`.

At boot the server loads the Hub zone, object/mob/class templates, spawns the
world, arms the persistence engine and the zone-reset timer, and starts the
event loop. It runs single-threaded: one kernel thread multiplexes every
connection via epoll and owns all world state ([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md)).
Shut down cleanly with SIGINT/SIGTERM; a `kill -9` is safe too (see Persistence).

## On AGNOS

Since **1.1.0** the same server builds and runs natively on the
[AGNOS](https://github.com/MacCracken/agnosticos) kernel (no Linux, no libc):

```sh
cyrius build --agnos src/main.cyr build/descent-agnos     # static agnos ELF64
```

`agnsh` runs it from disk on the booted kernel, serving over AGNOS's own TCP stack:

```
[ASSIST] > run /bin/descent serve 4000
```

What differs is entirely internal — players see no change. AGNOS `epoll` watches
only signalfd/timerfd (never sockets) and is 3-arg, so the Linux epoll multiplexer
([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md)) becomes a
`sleep_ms`-paced poll loop: drain non-blocking `sock_accept`, sweep the session
list with non-blocking `sock_recv` — same single-threaded single-owner model, same
2.5 s combat tick. Persistence (`data/players/`, `data/audit.libro`) works
identically via AGNOS's `flock`/`lseek`. Clean shutdown is in-band / process-kill
(AGNOS has no signalfd); the env knobs below are unchanged.

To boot AGNOS and play the MUD off the sovereign kernel end-to-end (QEMU — no
hardware needed), use the container harness in the **agnosticos** repo at
`docker/descent-sweep/`:

```sh
./run.sh serve        # boots AGNOS + descent, then from your host: telnet 127.0.0.1 4444
./run.sh              # or the automated assert-and-exit smoke
```

## Configuration (environment)

| Env var | Default | Effect |
|---|---|---|
| `YD_TICK_MS` | `2500` | Combat-tick interval in ms. Set low (e.g. `200`) for fast testing. |
| `YD_IDLE_MS` | `300000` | Idle-disconnect threshold in ms (slowloris reaping). |
| `YD_RESET_SECS` | per-zone `reset_secs` | Override the zone-reset interval in seconds. |
| `YD_ADMIN` | unset → off | `YD_ADMIN=1` enables the `@`-admin verbs (`@stats` / `@who` / `@reset`). |

```sh
YD_TICK_MS=200 YD_RESET_SECS=30 YD_ADMIN=1 ./build/cyrius-yeomans-descent serve 4000
```

## Admin verbs

Off by default for safety ([ADR 0007](../adr/0007-frozen-1.0-surface.md)). Start
with `YD_ADMIN=1` to enable them, then from any in-world session:

- `@stats` — connections, logged-in count, ticks, tick-drift p99, idle timeout.
- `@who` — connected players and their rooms.
- `@reset` — force an immediate zone reset.

There is **no operator authentication yet** — `YD_ADMIN=1` enables the verbs for
*every* connected player. Run with admin off on any shared/public deployment;
real operator auth (the Joshua interface) is a post-1.0 milestone.

## Persistence & data files

State lives under `data/` (created on first run, git-ignored):

- `data/players/<name>.cyml` — one signed record per player (attrs, class, room
  by id, inventory, identity salt + pubkey, signature). Atomic `.tmp` + rename
  writes ([ADR 0006](../adr/0006-persistence-shape.md)).
- `data/audit.libro` — append-only SHA-256 hash-chain audit log of security
  events (logins, saves, character creation, auth failures, tamper rejections).

Records are crash-safe: a `kill -9` mid-write leaves the previous complete
record intact. Each record is Ed25519-signed and version-stamped (`schema = 1`);
a record tampered with, or stamped for a newer server, is rejected rather than
loaded with bad state.

> **Backups / migration.** Copy `data/players/` to back up characters. Records
> are forward-gated by `schema`: a future server version that changes the field
> set will bump the schema and migrate; this server refuses records stamped
> newer than it understands. Records from 0.7.0–0.9.x (no `schema` field) load
> unchanged.

## Logs

The server writes operational lines to stdout — redirect to a file in
production:

```sh
./build/cyrius-yeomans-descent serve 4000 >> yd.log 2>&1
```

- **Zone resets**: `[<epoch>] zone=hub reset (rooms=N, mobs=M, objs=O)`.
- **Security events** also land in the `data/audit.libro` hash chain.

## Content (zones)

The world is authored as CYML zone files under `data/zones/` ([ADR 0005](../adr/0005-zone-file-format.md)):
`hub.rooms.cyml` (rooms + exits + `mobs`/`objects` spawn lists + a `reset_secs`
header), `hub.mobs.cyml` (mob templates), `hub.objs.cyml` (object templates).
The starter Hub is 21 rooms; the format is frozen for 1.x. The world is
single-zone today (one loaded zone); multi-zone is post-1.0.
