# Yeoman's Descent — Architecture Overview

> **Last Updated**: 2026-06-10 (v1.0.0 — feature-complete)
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

| Attribute | Effect |
| --- | --- |
| **STR** (Strength) | Modifies physical damage and carrying capacity (weight limits were vital in classic MUDs) |
| **DEX** (Dexterity) | Increases evasion chance and strike accuracy |
| **CON** (Constitution) | Determines maximum HP and stamina regeneration |
| **TEC** (Tech / Intelligence) | Powers Splicer / Chaplain abilities and energy weapon scaling |

### 2.3 Combat math

Hidden rolls computed server-side every tick:

- **Hit calculation**: `1d20 + DEX modifier + weapon accuracy vs. target Armor Class (AC)`. Traditional THAC0 system — lower AC numbers provide better defense.
- **Damage roll**: each weapon has a dice profile (e.g., a Shock-Pike is `2d6`). Total damage = `weapon dice + STR or TEC modifier`.

Example combat output stream:

```
> kill drone
You charge the deactivated security drone!
[Tick 1] You swing your shock-pike... and CRUSH the drone! (12 dmg)
[Tick 1] The security drone fires a rusted laser... but misses you entirely.
[Tick 2] You thrust your shock-pike... grazing the drone. (4 dmg)
[Tick 2] The security drone's rusted laser SEARS your left arm! (8 dmg)
```

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
3. **Rest & recovery** — endurance and health regenerate over time, but players must locate safe rooms (Hubs / Taverns) and use the `rest` or `sleep` commands to recover effectively, creating natural social gathering points.
4. **Territory (Guilds)** — high-level play involves aligning with tech-fiefdoms to secure and hold zones within the Descent.

## 5. Technical Architecture

The backend replicates the Telnet era while benefiting from modern stability.

- **Telnet protocol** — players connect via raw TCP sockets using standard clients (Mudlet, CMUD) or a browser-based Telnet wrapper.
- **Verb-noun parser** — a robust NLP-lite parser designed to interpret complex string commands (e.g., `give monoblade to kiran` or `put all.rations in backpack`).
- **Zones & resets** — the game world is compartmentalized into zones. A routine "zone reset" triggers on a per-zone timer (authored as `reset_secs`; the Hub uses 15 min), respawning mobs and loot, **but only while no active player occupies the zone** (the reset defers until it empties).

## See Also

- [`../adr/`](../adr/) — decision records for choices in this design (combat tick over cooldowns, raw TCP/Telnet over a higher-level protocol, single-thread event loop for concurrency).
- [`../development/roadmap.md`](../development/roadmap.md) — milestone plan implementing this design.
- [`../development/state.md`](../development/state.md) — live status snapshot.
