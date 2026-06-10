# 0003 — Single-thread event loop for connection concurrency

**Status**: Accepted
**Date**: 2026-05-24

## Context

A MUD has to fan a single TCP listener out to many simultaneous players and keep them all on the same world clock. Three properties of Yeoman's Descent shape the choice and rule out the obvious "one process per session" pattern:

1. **The 2.5s combat tick is server-wide** ([ADR 0001](0001-tick-based-combat-over-cooldowns.md)). Every engaged combatant — players and mobs — resolves a round in lockstep. The tick reads and writes a single shared combat state.
2. **Rooms hold multiple players at once.** When player A says `kill drone`, every other player in that room must see the resulting prose immediately. Movement, speech, emotes, deaths, loot drops — all are multi-subscriber events on shared room state.
3. **Zone resets are global** and gated on player-presence ([roadmap M7](../development/roadmap.md#m7--zone-resets-v080)). The reset scheduler reads "which rooms currently contain players" across the whole world, then mutates mob and loot tables in rooms it finds empty.

All three are operations on **shared world state**. A connection-isolation concurrency model (each session in its own address space, no shared memory) can only support them via IPC, which moves the problem rather than solving it.

There are also two transport realities that the model has to coexist with:

- The Telnet wire is **byte-at-a-time** with an IAC escape machine ([ADR 0002](0002-raw-tcp-telnet-protocol.md)). Reads block on the network; the parser is already a state machine over incoming bytes.
- The Cyrius stdlib's `lib/net.cyr` exposes the portable BSD-socket surface (`sock_accept` / `sock_send` / `sock_recv`) plus the non-blocking and multiplexing primitives needed for an event loop.

### Candidate concurrency primitives

- **(F) fork-per-accept** — kernel-isolated processes. Used by agora (sibling project, see its ADR 0007). Per-session globals are isolated by address space; kernel reclaims memory at child exit. **No shared memory across sessions** without IPC.
- **(T) thread-per-accept** — one kernel thread per connection over `lib/thread.cyr`. Threads share an address space, so world state is reachable. But every read and write to shared state (room occupancy, combat queues, zone reset tables) needs explicit synchronization, and every helper that touches the world becomes a thread-safety audit target.
- **(E) single-thread event loop** — one kernel thread multiplexes all connections via `poll` / `epoll` over non-blocking sockets, plus a timerfd / sleep for the tick. World state is touched by exactly one thread at a time, by construction.
- **(H) hybrid I/O thread + tick thread** — one thread for socket I/O, one for the tick scheduler, shared queues between them. Useful at scale; an obvious refactor target if the single thread saturates.

### Candidate tick-scheduling primitives

- **(α) `timerfd_create` + read** — kernel-backed periodic fd that delivers ticks into the same `epoll` set as the sockets. The tick is just another readable fd; no special case in the event loop.
- **(β) Manual `clock_gettime` + computed `epoll_wait` timeout** — every loop iteration computes "ms until next tick" and passes it as the timeout. Portable to any platform whose `lib/net.cyr` has a `poll`-shape primitive.
- **(γ) `setitimer` + `SIGALRM`** — periodic signal interrupts the loop. Signal handlers in Cyrius land on the same `rt_sigaction` trampoline that `lib/darshana.cyr` documents as historically fragile.

## Decision

**(E) single-thread event loop**, with **(β) computed `epoll_wait` timeout** as the tick scheduler. One kernel thread owns the listening socket, every connected client fd, and every byte of world state. The loop is:

```
on startup:
  bind, listen, set listener non-blocking, add to epoll set
  next_tick = now + 2500ms

loop forever:
  timeout_ms = max(0, next_tick - now)
  events = epoll_wait(timeout_ms)

  for each event:
    if fd == listener:        accept, set non-blocking, add to epoll set,
                              allocate session, send MOTD
    else:                     read available bytes, feed Telnet parser,
                              when a complete line lands, dispatch to verb
                              parser, queue output

  if now >= next_tick:
    advance_combat_tick()     # resolves every engaged combatant
    flush_pending_zone_resets()
    next_tick = next_tick + 2500ms     # absolute, not "now + 2500" —
                                       # drift-resistant

  for each session with queued output:
    drain its tx buffer to the socket (non-blocking; partial writes re-queue)
```

**In scope**: single kernel thread, non-blocking sockets, `epoll`-shape multiplexing via the relevant `lib/net.cyr` primitive, absolute-time tick scheduling with drift-resistant catch-up, per-session connection structs (not globals) allocated at `accept` and freed at disconnect.

**Out of scope**:

- **Multi-threaded scaling.** The hybrid (H) shape stays in the file as the documented escape hatch for when a single thread saturates. We don't implement it speculatively; we measure first.
- **Multi-process scaling.** Fork-per-accept (F) is rejected outright; agora's choice does not generalize to a MUD.
- **Generic green-thread / fiber runtime.** Out of scope for v1.0; the explicit event loop is more debuggable and the tick gives the loop a natural cadence.
- **Per-connection idle-disconnect handling at this ADR.** Slowloris-style timeout lives in M1's listener implementation; it's a property of the read path, not the concurrency model.

## Consequences

**Positive**

- **World state is single-writer by construction.** No mutexes, no lock-ordering bugs, no torn reads of room occupancy mid-tick. The whole class of concurrency bugs that would dog a threaded MUD is absent.
- **The tick is a first-class part of the loop**, not a side process that has to coordinate with I/O. Combat resolution happens between epoll wakeups; there's no question of "what if a player's command arrives during the tick" — the loop drains input, then advances the tick, then writes output, in sequence.
- **The Telnet IAC machine drops in unchanged.** The parser is already byte-at-a-time and side-effect-free; it doesn't care whether bytes arrive from a blocking read or a non-blocking one. Treating sessions as state machines fed by available bytes is exactly the shape the parser already expects.
- **Deterministic load profile.** CPU work per loop iteration is bounded by `O(active sessions + active combatants)`. Easy to reason about, easy to benchmark (M4 gate: tick drift under load).
- **Low overhead per connection.** No process table entry, no thread stack, no per-connection address space — just a session struct in the bump allocator. The v1.0 target of a few dozen concurrent players sits well inside what one thread handles.
- **Debuggable.** A single stack trace contains the entire server state at the moment of any bug. Crash dumps and logs need no cross-thread reconstruction.

**Negative**

- **One CPU core is the ceiling.** A hot loop that pegs a single core caps total throughput. The hybrid (H) split is the documented escape hatch, but until then the upper bound is real.
- **Any blocking call stalls every player.** A synchronous disk write inside the loop pauses combat, movement, and chat for everyone. The persistence layer (M6) must offer either non-blocking writes or a queue-and-flush model. _(Resolved at M6: persistence is libro+sigil — [ADR 0006](0006-persistence-shape.md) — with queued, debounced, never-inline saves; the original "T.Ron" framing was dropped.)_
- **A bug in one player's command path can hang the world.** A parser infinite loop on a malformed input freezes every other player. The verb parser fuzz harness (M2 gate) earns its keep here — protection that wasn't strictly necessary in a fork-isolated model is necessary now.
- **No "trivial" per-session resource isolation.** A pathological client cannot crash the server (no per-conn address space to corrupt the parent through), but it can consume the loop's CPU budget. Input rate limiting and slowloris-style timeouts move from "operational nicety" to "load-bearing safety net."

**Neutral**

- **Cross-platform reach follows `lib/net.cyr`.** Whatever `epoll`-shape primitive cyrius stdlib exposes is what we use. Linux today; macOS (kqueue-backed in stdlib) and Windows (IOCP-backed in stdlib) follow as stdlib backends mature.
- **The hybrid (H) refactor is a single split, not a redesign.** If we ever need it: move the tick into a second thread, put a single SPSC queue between it and the I/O thread for input events, and another for output deltas. The world-state owner stays single-writer.
- **Per-session bump-allocator growth is bounded by session count, not session-hours.** Sessions are short-lived relative to the server process; a small per-session arena freed at disconnect handles the long-running-process memory shape without requiring a global allocator change.

## Alternatives considered

- **(F) fork-per-accept.** Rejected. The MUD's defining feature — server-wide combat tick over shared world state — cannot be expressed across address spaces without IPC. Agora's choice (its ADR 0007) is correct *for a BBS where sessions don't interact*; the moment they do, the model breaks. Even if we accepted the IPC cost, the shared-state path would dominate the loop and we'd be paying fork-and-IPC overhead to simulate the event loop we're proposing here.
- **(T) thread-per-accept.** Rejected. Solves the address-space problem but introduces a synchronization problem of equal weight: every room, every mob list, every combat queue, every zone reset table becomes a mutex audit target. The combat tick's read-and-modify pass across all engaged combatants is exactly the pattern that's hardest to lock correctly. Single-writer-by-construction is strictly easier to reason about than "we got the locking right."
- **(H) hybrid I/O + tick split from day one.** Deferred, not rejected. Worth doing if a measured workload says one thread can't keep up; not worth doing speculatively. The split adds a queue, a second thread, and a class of cross-thread bugs that the single-thread loop avoids. Pay that cost when there's evidence.
- **(α) `timerfd` for the tick.** Rejected for v1.0 — Linux-specific, and we want the event loop to portable to whatever `lib/net.cyr` runs on. The computed-timeout (β) shape works on every `poll`-family primitive on every platform cyrius has ever supported.
- **(γ) `SIGALRM` for the tick.** Rejected. Signal-driven scheduling collides with the `rt_sigaction` trampoline concerns documented in `lib/darshana.cyr` and forces every read in the loop to be `EINTR`-aware. The computed timeout is simpler in every direction.
- **A generic green-thread / fiber runtime that lets each session look like blocking code.** Rejected for v1.0. The explicit state-machine event loop is more debuggable, more inspectable in a crash dump, and easier to bound for resource use. A fiber runtime can be retrofitted later if the explicit loop becomes painful — but the painful case (sessions with deeply nested awaitable operations) is not the shape MUD command dispatch takes.
