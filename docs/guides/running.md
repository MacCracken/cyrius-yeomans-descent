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
Shut down cleanly with SIGINT/SIGTERM — **since 1.7.11 that saves every session
still connected** before it exits, and logs how many. A `kill -9` remains safe in
the sense that no record is ever left torn (writes are `.tmp`+rename), but it
skips that save, so anything since each player's last autosave is lost. Prefer the
signal. *Before 1.7.11 the signal path saved nobody either, and this guide said
the opposite — see the CHANGELOG.*

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

AGNOS `epoll` watches only signalfd/timerfd (never sockets) and is 3-arg, so the
Linux epoll multiplexer
([ADR 0003](../adr/0003-single-thread-event-loop-concurrency.md)) becomes a
`sleep_ms`-paced poll loop: drain non-blocking `sock_accept`, sweep the session
list with non-blocking `sock_recv` — same single-threaded single-owner model, same
2.5 s combat tick. The env knobs below are unchanged.

> **What differs is NOT entirely internal, and this guide said it was until
> 1.7.21.** Two differences players see:
>
> - **The population ceiling is 7, not `MAX_SESSIONS`.** Sockets come from an
>   8-slot connection table compiled into the agnos syscall layer, and the
>   listener holds one slot for the life of the process. Before 1.7.21 descent
>   still believed 256, so the 8th client completed its TCP handshake and then sat
>   on a blank screen — no banner, no error, no close. `MAX_SESSIONS` is now
>   target-aware, so an over-capacity client gets the same polite refusal it gets
>   on Linux. The ceiling itself is a kernel-side limit, not ours.
> - **Clean shutdown needs `@shutdown`.** There is no signalfd on this target, so
>   `SIGINT`/`SIGTERM` do not reach the loop. Before 1.7.21 there was **no
>   in-band path either** — this guide claimed one and it did not exist — so the
>   only way to stop the server was to kill it, and every connected player lost
>   everything since their last autosave. Enable `YD_ADMIN=1` and use `@shutdown`.
>
> **Also unresolved on this target**, and stated rather than implied away: the
> monotonic clock. Descent schedules everything — the combat tick, the save
> sweep, the idle reaper, the zone-reset timer — off `mud_now_ms()`. Since 1.7.21
> that reads `uptime_us` (#95, rdtsc-based) on AGNOS rather than `uptime_ms`
> (#40), because the agnos syscall layer documents #40 as **frozen for a
> foreground `run` program** — interrupts are disabled, so the 100 Hz timer that
> drives it never fires. If that is accurate, a pre-1.7.21 server launched the
> documented way never ticked at all: no combat, no autosave, no reset, while it
> kept accepting logins. **Nobody has confirmed it on real hardware** — see the
> harness note below.

**Persistence (`data/players/`, `data/audit.libro`) — read this if you ran an
AGNOS build before 1.7.8.** This guide claimed persistence "works identically"
from 1.1.0, and it did not: `player_save` published records with raw
`syscall(82)` / `syscall(87)`, which are `rename` and `unlink` on Linux but
**GPU dispatch and GPU blit on AGNOS** — and it created its directories with a
`sys_mkdir` argument order only Linux uses. On that target **no player record
was ever written, and every reconnect was offered a brand-new character.** The
x86_64 suite could not see it, and CI never built `--agnos` at all.

Fixed in 1.7.8: every filesystem call now goes through the portable `lib/io.cyr`
wrappers (`file_rename`, `xunlink`) or an explicit `#ifdef CYRIUS_TARGET_AGNOS`
branch, a test asserts `src/persist.cyr` contains no raw numeric syscall, and CI
builds both targets.

**Scope of that claim, stated plainly:** CI *compiles* the AGNOS target; nothing
here *executes* it. The syscall numbers and argument orders are now correct by
construction against `lib/syscalls_x86_64_agnos.cyr`, but end-to-end persistence
on a booted AGNOS kernel has not been re-verified since the fix. If you run one,
that is the check worth reporting.

> **There is currently no way to boot AGNOS and play the MUD end-to-end.** This
> section used to point at a container harness in the **agnosticos** repo at
> `docker/descent-sweep/`. **That harness was retired on 2026-07-07** and the
> directory is gone; the instructions here outlived it by several releases.
>
> Rebuilding it — or an equivalent QEMU harness — is the single highest-value
> piece of test infrastructure this project is missing. Every AGNOS defect closed
> in 1.7.21 was found by reading two arms of a preprocessor or by running under an
> agnos→Linux syscall translator, which by its own documentation does not
> exercise the kernel's scheduler, net stack or interrupt semantics — which is
> exactly where the remaining unknowns live.

## Configuration (file)

Since **1.7.2**, operator settings live in an optional `data/server.cyml`. The
file may not exist — absent, unreadable, or missing a key all mean "defaults",
so a server that ignores this section behaves exactly as 1.7.1 did.

```
game = "yeomans-descent"
max_accounts = 2500
```

| Key | Default | Effect |
|---|---|---|
| `max_accounts` | `0` | Maximum number of player accounts. **`0` means unlimited**, which is the default — how many characters a world should hold is your decision, not the server's. Once reached, character *creation* is refused with a message; existing players are unaffected. A negative or unparseable value is treated as unlimited, so a typo cannot lock you out of your own world. |

The cap counts records on disk once at startup and tracks creations in memory, so
it costs nothing per login. It bounds **accounts**, not connection attempts — it
does not replace the login and `passwd` rate limits, and it is not a DoS control.
What it bounds is permanent disk: every account leaves a file forever.

## Configuration (environment)

Environment variables override the config file.

| Env var | Default | Effect |
|---|---|---|
| `YD_TICK_MS` | `2500` | Combat-tick interval in ms. Set low (e.g. `200`) for fast testing. |
| `YD_IDLE_MS` | `300000` | Idle-disconnect threshold in ms, for **logged-in** players. A connection that has not authenticated is dropped after 30 s regardless of this (1.6.13) — that is the slowloris reap, and it is not tunable. |
| `YD_RESET_SECS` | per-zone `reset_secs` | Override the zone-reset interval in seconds. |
| `YD_ADMIN` | unset → off | `YD_ADMIN=1` enables the `@`-admin verbs (`@stats` / `@who` / `@reset`). |
| `YD_MAX_ACCOUNTS` | unset → use `data/server.cyml` | Overrides `max_accounts` above, for container deployments that configure through the environment. `0` = unlimited. |

```sh
YD_TICK_MS=200 YD_RESET_SECS=30 YD_ADMIN=1 ./build/cyrius-yeomans-descent serve 4000
```

## Admin verbs

Off by default for safety ([ADR 0007](../adr/0007-frozen-1.0-surface.md)). Start
with `YD_ADMIN=1` to enable them, then from any in-world session:

- `@stats` — connections, logged-in count, ticks, tick-drift p99, idle timeout.
- `@who` — connected players and their rooms.
- `@reset` — force an immediate zone reset.
- `@shutdown` — **since 1.7.21.** Stop the server cleanly from in-band: it saves
  every connected session, flushes the audit tally and closes the listener, the
  same exit path `SIGINT`/`SIGTERM` takes. On Linux prefer the signal; **on AGNOS
  this is the only clean shutdown there is**, because that build has no signalfd
  (see below).

There is **no operator authentication yet** — `YD_ADMIN=1` enables the verbs for
*every* connected player. Run with admin off on any shared/public deployment;
real operator auth (the Joshua interface) is a post-1.0 milestone.

## Persistence & data files

State lives under `data/` (created on first run, git-ignored):

- `data/players/<c>/<name>.cyml` — one signed record per player (attrs, class,
  room by id, inventory, identity salt + pubkey, signature). Atomic `.tmp` +
  rename writes ([ADR 0006](../adr/0006-persistence-shape.md)).

  **Since 1.7.2 records are sharded** into a one-character subdirectory (`a`–`z`,
  by the first letter of the name) so a world with thousands of accounts is not
  one directory holding thousands of files. **No migration step is needed**: the
  old flat `data/players/<name>.cyml` layout is still read, and each record moves
  itself the next time that player saves. You can leave a pre-1.7.2 `data/` alone
  and it will convert as people log in.
- `data/audit.libro` — append-only SHA-256 hash-chain audit log of security
  events (logins, saves, character creation, auth failures, tamper rejections).
- `data/audit.libro.<N>` — **sealed segments.** See below.

### The audit log is not one file

ADR 0009 (shipped 1.7.4) gave the audit log **rotation**, and this guide did not
mention it until 1.7.21. If you have ever seen an `audit.libro.1` in your `data/`
and wondered what it was, this is it.

- **Rotation.** When `data/audit.libro` passes its size trigger it is sealed and
  renamed to `data/audit.libro.<N>`, numbered upward, and a fresh live file is
  started. The rename is atomic; a crash mid-rotation cannot lose entries.
- **Pruning and the retention bound.** Only the most recent few segments are
  kept — older ones are deleted, and each deletion is **attested inside the
  surviving chain** as an `audit.prune` entry carrying the retired segment's tail
  hash. So a gap in the history is itself recorded and is distinguishable from
  tampering. **This means the audit log has a bounded horizon by design: history
  older than the keep window is gone, permanently, and pruning is not an error.**
- **Verification is no longer a single-file operation.** To verify the chain you
  must walk the segments in chronological order and then the live file, joining
  each segment's tail hash to the next one's head. Verifying `audit.libro` alone
  proves only the current segment.
- **Never renumber or move segment files by hand.** The numbering is what tells
  the server where the chain continues after a restart. A file moved out of
  sequence — or a prune that failed and left a segment behind — made pre-1.7.21
  servers resume from the wrong segment and report the chain as *tampered with*
  when nothing had been. 1.7.21 makes that self-heal, but a hand-renumbered
  directory is still the one input the format cannot reason about.
- **If the log stops.** Since 1.7.21 the server prints
  `server: AUDIT LOG IS NOT BEING WRITTEN` **once** if the store refuses a write
  — a read-only `data/`, a full disk, wrong ownership. Before that it failed in
  complete silence: the server carried on authenticating players while writing
  nothing at all, with byte-identical output. If you see that line, the security
  log has a hole in it from that moment until you fix the disk and restart.

Records are crash-safe: a `kill -9` mid-write leaves the previous complete
record intact. Each record is Ed25519-signed and version-stamped (`schema = 1`);
a record tampered with, or stamped for a newer server, is rejected rather than
loaded with bad state.

> **Backups / migration.** Copy `data/players/` to back up characters — recursively, since 1.7.2 puts records in per-letter subdirectories.
> **To back up the audit chain you must copy `data/audit.libro` *and* every
> `data/audit.libro.<N>` segment, together and at the same moment** — a backup of
> the live file alone preserves only the current segment, and the sealed ones are
> pruned by design and will be gone. This guide said "copy `data/players/`" and
> nothing else for six releases. Records
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
