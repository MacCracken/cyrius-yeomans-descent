# Command reference

Every command Yeoman's Descent understands at v1.0. This surface is frozen for
the 1.x line ([ADR 0007](../adr/0007-frozen-1.0-surface.md)) — type `help`
in-world for the short version.

Commands are parsed verb-first; most take a noun resolved against your
inventory, your worn/wielded slots, and the current room. Matching is by
keyword prefix (`get rat` finds `a ration`).

## Movement

| Command | Aliases | Effect |
|---|---|---|
| `north` `south` `east` `west` `up` `down` | `n` `s` `e` `w` `u` `d` | Move through that exit; you auto-`look` on arrival, and onlookers see you leave / arrive. |

## Looking around

| Command | Aliases | Effect |
|---|---|---|
| `look` | `l` | Describe the current room: title, prose, exits, and who/what is present. |
| `examine <thing>` | | Inspect a mob, object, or yourself (`examine me` shows your character sheet). |
| `exits` | | List the room's exits. |
| `inventory` | `i` | List what you're carrying. |
| `who` | | List who else is in the world. |

## Items

| Command | Form | Effect |
|---|---|---|
| `get <obj>` | `get sword`, `get all`, `get all.ration`, `get 2.cell`, `get <obj> from <container>` | Pick up an object (or loot a corpse). |
| `drop <obj>` | `drop sword`, `drop all` | Drop an object into the room. |
| `put <obj> in <container>` | | Place an object into a container. |
| `give <obj> to <player>` | | Hand an object to someone. |
| `wear` / `remove` / `wield <obj>` | | Equip / unequip gear. |

**Qualifiers** work on any noun: `all` (everything in scope), `all.X` (every X),
`N.X` (the Nth X in scan order — `kill 2.drone`). **Prepositions**: `in on to
from at with`.

## Combat

Combat resolves on a server-wide **2.5-second tick** ([ADR 0001](../adr/0001-tick-based-combat-over-cooldowns.md)):
once engaged, you and your target trade a round every tick until one falls,
flees, or leaves. Hits are a hidden `1d20 + modifiers` vs. armour class.

| Command | Effect |
|---|---|
| `kill <mob>` | Engage a mob. Rounds resolve automatically each tick. |
| `flee` | Break off and bolt to a random exit. |

Outside combat you slowly recover HP (CON-scaled). Die, and you wake at the Hub
gate with your inventory dropped where you fell.

## Class abilities

Abilities fire the instant you type them (between ticks), composing with your
auto-attack. Each costs **energy** and locks a short **cooldown**; energy
regenerates and cooldowns decay every tick.

| Class | Abilities |
|---|---|
| **Pikeman** (tank) | `bash` (stun), `brace` (raise AC), `cleave` (heavy hit) |
| **Splicer** (caster/hacker) | `hack` (burst), `overload` (big burst), `emp` (debuff) |
| **Courier** (rogue) | `sneak` (go stealth), `backstab` (stealth opener), `bypass` (evade) |
| **Chaplain** (healer) | `patch` (heal), `stim` (buff hit/damage), `rally` (group sustain) |

Your three abilities are the ones for the class you chose at character creation.
`examine me` shows your current energy and cooldowns.

## Social

| Command | Effect |
|---|---|
| `say <text>` | Speak to everyone in the room. |
| `tell <player> <text>` | Send a private message. |
| `emote <text>` | Perform a free-form action (`emote grins`). |

## Session & identity

| Command | Effect |
|---|---|
| `save` | Write your character record now. |
| `passwd` | Change your passphrase (entered twice, echo-suppressed). Re-keys your Ed25519 identity and re-signs the record; the old passphrase stops working immediately. |
| `help` | Show the command summary. |
| `quit` | Save and disconnect. |

Your progress also autosaves on disconnect and on a debounced ~5-minute timer,
so an abrupt server stop never loses committed state. See
[playing.md](playing.md) for the persistence model.

## Admin (operators only)

These are **off by default** and only work when the server was started with
`YD_ADMIN=1` ([ADR 0007](../adr/0007-frozen-1.0-surface.md) §2). When disabled
they read as unknown commands and are hidden from `help`. Full operator
authentication is a post-1.0 item.

| Command | Effect |
|---|---|
| `@stats` | Live server counters: connections, logged-in, ticks, tick-drift p99, idle timeout. |
| `@who` | Connected players and the room each is standing in. |
| `@reset` | Force an immediate zone reset (respawn dead mobs / missing loot). |
