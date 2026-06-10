# Playing Yeoman's Descent

A first-session walkthrough. For the exhaustive command list see
[commands.md](commands.md); to run your own server see [running.md](running.md).

## Connect

```sh
telnet 127.0.0.1 4000        # or nc, Mudlet, TinTin++, a WebSocket bridge…
```

You'll get the MOTD and a name prompt.

## Create a character

```
By what name are you known? Kessa
No record answers to that name — let us forge one.
New operative — choose a passphrase (4-64 chars): ********
Confirm passphrase: ********
```

Your **passphrase never leaves your terminal in cleartext on a conformant
client** — the server sends `IAC WILL ECHO` so your client stops echoing your
keystrokes. The passphrase is *not* stored: the server derives an Ed25519
keypair from `SHA-256(salt ‖ passphrase)` and keeps only the salt and public
key ([ADR 0004](../adr/0004-identity-and-authentication.md)). Lose the
passphrase and the character is unrecoverable — by design.

Then choose a calling:

```
Choose your calling in the Under-Grid:
  1) Pikeman  — the wall the Under-Grid breaks on
  2) Splicer  — code is a weapon, if you cut deep enough
  3) Courier  — gone before the room knows you were there
  4) Chaplain — the Grid's mercy, rationed
Enter a number or name: 1
```

You materialize at **The Arcology Gate** and you're in the world.

## Get your bearings

```
look                 (or just  l)
exits
examine me           — your sheet: class, attrs, HP, energy
get notice           — there's a work-notice posted at the gate
inventory            (or  i)
north                (or  n)   — into the Lower Concourse
```

The Hub is 21 rooms across four districts — the Flagon (tavern), the Market,
the Foundry, and the flooded Under tiers. Ambient loot and flavor objects are
scattered around and **restock when the zone resets**.

## Fight

A `scavver` lurks in the Lower Concourse. Engage it:

```
kill scavver
```

Combat resolves a round every **2.5 seconds** — you don't spam attacks, you
pick your moment. Drop an ability between ticks:

```
bash                 — Pikeman: stun it
cleave               — Pikeman: a heavy swing
```

`examine me` shows your energy draining and cooldowns ticking back. Win and the
mob leaves a corpse; `get all from corpse` to loot it. Out of combat your HP
recovers on its own. If you die you wake at the gate, your gear dropped where
you fell — go back for it.

Each class clears the Hub solo and can down the Foundry's Sentinel boss: the
Pikeman tanks, the Splicer bursts, the Courier strikes from stealth, the
Chaplain outlasts.

## Persistence — you survive a restart

State is **crash-safe**. Your character saves:

- when you type `save`,
- when you `quit` (or drop / time out),
- at character creation,
- on a debounced ~5-minute timer while you play.

Saves are written atomically (`.tmp` + rename) and Ed25519-signed, so a server
`kill -9` leaves either your last complete record or the new one — never a torn
file ([ADR 0006](../adr/0006-persistence-shape.md)). Reconnect later:

```
By what name are you known? Kessa
Welcome, Kessa.
Passphrase: ********
The lock yields. Welcome back to the Under-Grid.
Last seen 2 hours ago.
```

…and you're back in the room you left, with your attributes, HP, and inventory
intact. Change your passphrase any time with `passwd`.

## Where to go next

- The full verb list: [commands.md](commands.md).
- Running and operating your own server: [running.md](running.md).
- Why the game is built the way it is: the [design overview](../architecture/overview.md)
  and the [decision records](../adr/).
