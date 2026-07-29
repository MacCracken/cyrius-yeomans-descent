# 0001 — Tick-based combat over real-time cooldowns

**Status**: Accepted
**Date**: 2026-05-24

## Context

Yeoman's Descent is a text MUD in the DikuMUD / LPMud tradition. Combat resolution can be modeled two ways:

1. **MMO-style real-time cooldowns** — each ability has a per-player cooldown timer; the server resolves actions as they come in.
2. **Server-wide tick** — every player and mob resolves one combat round per fixed interval; rolls are computed in lockstep.

Each option pulls the feel of the game in a different direction. Cooldowns reward latency and per-player skill at the keyboard. Ticks reward tactics, command pre-queuing, and slower-but-richer text output. A MUD is a text channel — every combat round produces several lines of prose per participant — and a tick model is what lets that prose stay readable.

## Decision

Combat resolves on a **server-wide 2.5-second Combat Tick**. Hidden 1d20 + modifier vs AC rolls run every tick for every engaged participant, and the parser translates the math into per-tick prose ("You swing your shock-pike... and CRUSH the drone! (12 dmg)").

In scope: all combat resolution. Out of scope: non-combat actions (movement, parser commands, item manipulation), which run on connection-driven scheduling.

## Consequences

**Positive**

- Output cadence is bounded and readable — no one's terminal scrolls faster than a player can parse.
- Server load is predictable: combat math is O(active combatants) per tick, not O(input rate).
- Faithful to the era. Players coming from EmpireMUD / GodWars / CircleMUD will recognize the feel immediately.
- Pre-queueing commands during a tick becomes a natural skill expression.

**Negative**

- No "burst" feel — players accustomed to MMO cooldown weaving will find combat slower.
- Tick drift under load is now a load-bearing property of the system. We have to keep the scheduler honest. (See [M4 gate in the roadmap](../development/roadmap.md#m4--combat-tick-v050).)

  **Amended in 1.7.0 — the allowances, stated here at last.** This consequence
  named the property and never gave it a number. The 50 ms figure that three
  separate gates cite was written only in the roadmap and in the benches, which
  is precisely how they came to disagree about what it covered: a budget comment
  in `src/server.cyr` multiplied it out against a per-line cost that was 7×
  wrong, and nothing failed. Two distinct quantities are now named, because
  conflating them is the mistake that got made:

  - **DRIFT — 50 ms p99.** Bounds work that *delays a scheduled tick*:
    `handle_accept`, the event batch, and `drain_pending_rx`. This is what
    `PASS_CHARGE_MAX` is sized against and what `benches/bench_tick_budget.bcyr`
    gates. Worst case after 1.7.0 is ~27 ms (54%); unauthenticated worst ~8.5 ms.
  - **TICK-BODY OCCUPANCY — 250 ms, i.e. 10% of the 2.5 s interval.** Bounds
    everything inside `advance_tick`: `combat_tick_all`, `save_sweep`,
    `mob_tick_all`, the zone reset. `bench_combat`'s 43.3 ms broadcast fan-out at
    256 co-located players lives here, at 17% of a budget it fits — rather than
    87% of one that was never the right instrument for it.

  These are separate because `record_tick_drift(now - next_tick)` takes a
  **pre-work** sample. Under absolute scheduling a sub-interval overrun is
  absorbed by the next `epoll_wait` timeout, so it is invisible to the drift
  metric *by construction* — which is exactly how `save_sweep` spent 332 ms in a
  tick for eight releases without being seen. **Do not derive a budget in this
  tree by subtracting a tick-body figure from the drift allowance.**

  Measuring tick-body cost properly needs its own counter, which means a new
  `@stats` field, which [ADR 0007](0007-frozen-1.0-surface.md) freezes until 2.0
  (M14). Until then the tick-body allowance is a design constraint checked by
  bench, not a runtime-observable metric. ADR 0007 freezes the *public surface* —
  verbs, save fields, zone fields, `YD_*` knobs — not these records.
- Per-ability cooldowns, if added later, have to compose with the tick rather than replace it.

**Neutral**

- The tick interval (2.5s) is calibrated for the era. Tuning it later is a balance decision, not an architectural one.

## Alternatives considered

- **Per-player cooldown timers** — rejected for the reasons above; the text-throughput problem alone disqualifies it for a MUD.
- **Hybrid (cooldowns for abilities, tick for auto-attacks)** — deferred. May resurface for specific class abilities, but the *base* combat resolution stays tick-driven so the prose stream stays readable.
- **Faster tick (1s)** — rejected as too much text per second to parse comfortably; output drowns dialog.
- **Slower tick (5s)** — rejected as sluggish; players disengage between rounds.
