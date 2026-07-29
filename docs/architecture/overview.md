# Yeoman's Descent — Architecture Overview

> **Last Updated**: 2026-07-29 (v1.6.15)
>
> **This describes what the code does.** Sections 2–4 were reconciled against the
> implementation in 1.6.15, after a sweep found this file documenting a combat
> model, two attributes and two verbs that were never built. Anything still
> aspirational is now marked as such and names the milestone that would build it.
>
> System-level design for cyrius-yeomans-descent. The *what* of the system: concept, modules, data flow, and the load-bearing invariants every contributor needs in their head. Decisions (the *why*) live in [`../adr/`](../adr/); single-point non-obvious quirks live as numbered notes alongside this file.

---

## 1. High-Level Concept

**Yeoman's Descent** is a classic text-based Multi-User Dungeon (MUD) set in a gritty techno-feudal universe. Players begin as low-ranking serfs or squires and must delve into the "Under-Grid" — a massive, subterranean arcology of ruined servers, rusted automated defenses, and rogue AI fiefdoms. The game relies entirely on text parsing, ANSI color aesthetics, and deep, imaginative world-building, accurately reflecting the DikuMUD and LPMud era of the late 1980s to mid-1990s.

- **Engine & backend**: Cyrius-native TCP socket server (no external runtime)
- **State management**: per-player Ed25519-signed CYML saves with crash-safe
  `.tmp`+rename writes ([ADR 0006](../adr/0006-persistence-shape.md)); **libro**
  (append-only SHA-256 hash-chain) for the audit log + **sigil** (Ed25519
  identity, [ADR 0004](../adr/0004-identity-and-authentication.md))
- **Game management interface**: a `@`-admin verb set (`@stats`/`@who`/`@reset`,
  gated behind `YD_ADMIN`); a full operator interface (Joshua) is a post-1.0
  milestone

## 2. Combat System & Mechanics

To preserve the 90s text-MUD feel, combat avoids deterministic MMO-style cooldowns in favor of **hidden dice rolls** on a strict server-wide tick. The math leans on classic tabletop RPG paradigms adapted for digital speed.

### 2.1 Tick architecture

Combat resolves automatically once engaged (via `kill <target>`). The server calculates one combat round every **2.5 seconds (the Combat Tick)**. During this tick, both the player and the target execute their attacks, and the parser translates the math into dynamic text output.

### 2.2 Base attributes

> **Implemented as of 1.6.15.** This table used to describe an intended design;
> what follows is what the code does. Attribute scaling beyond the ability
> riders below is **M16** (XP, levels, death cost), which is where the rest of
> this becomes true.

| Attribute | What it actually does today |
| --- | --- |
| **STR** (Strength) | **Nothing yet.** Stored, shown by `examine me`, read by no game rule. Pikeman abilities use a flat bonus, not STR. |
| **DEX** (Dexterity) | `backstab` damage only — `base + dex/2`, tripling to `base*3 + dex` from stealth. Not in the hit roll and not evasion. |
| **CON** (Constitution) | Out-of-combat regeneration: `1 + CON/5` HP per tick while not engaged. **Not** maximum HP — that comes from the class's authored `hp`. |
| **TEC** (Tech) | Splicer and Chaplain ability riders: `hack` `+TEC/2`, `overload` `+TEC`, `patch` `+TEC/2`, `rally` `+TEC`. No "energy weapon scaling". |

Carrying capacity is a flat **100-item cap** (1.6.13), not a STR-scaled weight
budget. It exists because the save record is a fixed 4096-byte buffer, not as a
game mechanic.

### 2.3 Combat math

Hidden rolls computed server-side every tick:

- **Hit**: `1d20 + attacker's hit bonus + defender's AC >= 20`. A natural 20
  always hits and a **natural 1 always misses**, whatever the bonus. The hit
  bonus is the class's authored `hit`, plus `+2` while `stim` is up — **DEX is
  not involved**. Lower AC is better defence, and `brace` / `bypass` subtract
  from it at roll time.
- **Damage**: the class's authored dice profile `NdM+K`, plus `+2` while `stim`
  is up. **STR and TEC are not involved** in the auto-attack; TEC and DEX ride
  the class abilities only (see the attribute table above).

Example combat output stream:

Actual output, captured from a running server (the illustrative sample that used
to sit here showed a `[Tick N]` prefix and per-limb hit locations, neither of
which exists):

```
> kill scavver
You lunge at a hunched scrap-scavver!
You strike a hunched scrap-scavver for 8 damage.
a hunched scrap-scavver lunges at you and misses.
[ hp 40/40 | nrg 20 ]
>
```

Onlookers in the room see a third-person line for each blow. A killing blow adds
`a hunched scrap-scavver collapses, destroyed!` and leaves a lootable corpse.

## 3. Class Structure

| Class | Role | Core Commands | Attribute Focus |
| --- | --- | --- | --- |
| Pikeman | Tank / Melee | `bash`, `brace`, `cleave` | STR / CON |
| Splicer | Caster / Hacker | `hack`, `overload`, `emp` | TEC |
| Courier | Rogue / Stealth | `sneak`, `backstab`, `bypass` | DEX |
| Chaplain | Healer / Support | `patch`, `stim`, `rally` | TEC / CON |

## 4. Core Loop & Gameplay

1. **Exploration** — players navigate via cardinal directions (`n`, `s`, `e`, `w`, `u`, `d`). Rooms feature rich textual descriptions detailing the decaying architecture, exits, and present entities.
2. **Combat & looting** — players engage hostiles to acquire raw materials, rusted tech components, and credits. Loot must be manually retrieved via commands like `get all from corpse`.
3. **Recovery** — HP regenerates automatically while out of combat, anywhere, at
   `1 + CON/5` per tick. There are **no `rest` or `sleep` verbs** and no safe-room
   mechanic; both were described here and never built. Energy regenerates on the
   same tick, and ability cooldowns decay with it.
4. **Territory (Guilds)** — *not implemented.* Aspirational; guilds are M22.

## 5. Technical Architecture

The backend replicates the Telnet era while benefiting from modern stability.

- **Telnet protocol** — players connect via raw TCP sockets using standard clients (Mudlet, CMUD) or a browser-based Telnet wrapper.
- **Verb-noun parser** — verb, direct object, preposition, indirect object, with
  `all`, `all.X` and `N.X` qualifiers (e.g. `give notice to kiran`,
  `kill 2.scavver`). Note that the single-target verbs — `put`,
  `give`, `kill`, `examine` — take `all.X` to mean *the first* X, since they have
  no plural form; only `get` and `drop` act on every match.
- **Zones & resets** — the game world is compartmentalized into zones. A routine "zone reset" triggers on a per-zone timer (authored as `reset_secs`; the Hub uses 15 min), respawning mobs and loot, **but only while no active player occupies the zone** (the reset defers until it empties).

## See Also

- [`../adr/`](../adr/) — decision records for choices in this design (combat tick over cooldowns, raw TCP/Telnet over a higher-level protocol, single-thread event loop for concurrency).
- [`../development/roadmap.md`](../development/roadmap.md) — milestone plan implementing this design.
- [`../development/state.md`](../development/state.md) — live status snapshot.
