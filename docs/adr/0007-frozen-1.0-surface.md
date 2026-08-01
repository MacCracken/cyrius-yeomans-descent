# 0007 — Frozen 1.0 surface

**Status**: Accepted
**Date**: 2026-06-10

## Context

The 0.9.x line is stabilisation, not features: 0.9.0 was the security sweep,
0.9.1 is the surface freeze, 1.0.0 is the clean release (final hardening +
playtest sign-off). For 1.0.0 to be a *stabilisation-only* release — no
behaviour changes a client, save file, operator, or zone author could observe —
the public surface has to be enumerated and locked **now**, at 0.9.1, so that
anything added afterwards is consciously a post-1.0 change.

"Surface" here is everything outside the binary that something else depends on:
the command language a player types, the bytes on the wire, the on-disk save
schema, the zone-file format, and the operator knobs.

## Decision

The following surface is **frozen for 1.0**. Changing any of it after 1.0.0
requires either a major-version bump or a versioned migration (for saves, a
`schema` bump — see below). Additions during 0.9.1 → 1.0.0 are limited to
bug/security fixes that do not change observable behaviour.

### 1. Command verbs (`src/parser.cyr`)

- **Movement**: `n s e w u d` and `north south east west up down`.
- **Inspection**: `look` (`l`), `examine`, `exits`, `inventory` (`i`), `who`.
- **Items**: `get drop put give wear remove wield`.
- **Combat**: `kill`, `flee`.
- **Social**: `say tell emote`.
- **Session**: `quit save passwd help`.
- **Class abilities**: `bash brace cleave` (Pikeman), `hack overload emp`
  (Splicer), `sneak backstab bypass` (Courier), `patch stim rally` (Chaplain).
- **Aliases** (locked): `n…d`→long forms, `l`→`look`, `i`→`inventory`.
- Direct-object / preposition / `all.X` / `N.X` qualifier grammar (M2) is frozen.

### 2. `@`-admin namespace (`src/session.cyr` + `server.cyr`)

- `@stats`, `@who`, `@reset`, `@shutdown`. **Gated behind `YD_ADMIN` (default
  off)** — when
  disabled they read as unknown commands and are hidden from `help`. The *names
  **`@shutdown` added 1.7.21** — an amendment in the 1.7.2 style: additive, behind
  the already-frozen gate, and it exists because the AGNOS event loop had no exit
  at all (its `stop` flag was declared and never assigned, so 1.7.11's shutdown
  save was unreachable code on that target).
  The *names and output shape* are frozen; operator authentication (replacing the env gate)
  is explicitly **deferred to M8, post-1.0**.

### 3. Save-record schema — **version 1** (`src/persist.cyr`)

One `[player]` TOML section, atomic `.tmp`+rename, Ed25519-signed prefix
([ADR 0006](0006-persistence-shape.md)). Frozen v1 fields:

```
schema name salt pubkey class room
hp maxhp ac hit ndice dsize dmod
str dex con tec energy maxenergy
created last_login inv sig
```

- `schema = 1` is stamped on every write (0.9.1+). Records from 0.7.0–0.9.0
  carry no `schema` field and are read as v1 (back-compatible). A server
  **rejects** any record stamped newer than its `SCHEMA_VERSION`. Post-1.0
  field additions bump `schema` and add a migration; they do not silently
  extend v1.
- All loaded numeric/index fields are validated/clamped on read (the 0.9.0
  rule: a signature proves authorship, not field validity).

### 4. Wire / Telnet behaviour (`src/telnet.cyr`, `src/session.cyr`)

- Raw TCP, one line-oriented session per connection ([ADR 0002](0002-raw-tcp-telnet-protocol.md)).
- RFC 854 IAC framing + RFC 1143 Q-method option negotiation, naive-refuse
  (every `DO`→`WONT`, every `WILL`→`DONT`) except the server's preferred
  `ECHO`/`SGA`.
- CR (or lone LF) terminates a line; CR LF collapses to one.
- `IAC WILL ECHO` / `IAC WONT ECHO` bracket every passphrase prompt (0.8.1).

### 5. Zone-file format (CYML, [ADR 0005](0005-zone-file-format.md))

- **Zone header**: `zone`, `name`, `start`, `reset_secs`.
- **Room entry** (`kind = "room"`): `id`, `title`, `exit_{n,s,e,w,u,d}`,
  `mobs`, `objects`, prose body.
- **Mob template** (`kind = "mob"`) and **object template** (`kind = "obj"`)
  field sets are frozen. ≤ 32 entries per file.

### 6. Environment knobs (`src/server.cyr`)

`YD_TICK_MS`, `YD_IDLE_MS`, `YD_RESET_SECS`, `YD_ADMIN`. Names + semantics frozen.

> **Amended in 1.7.2 — one added knob, and a config file.**
>
> This section froze the knob surface, and the Consequences below read that as
> "new env knobs are blocked until after 1.0". 1.7.2 adds **`YD_MAX_ACCOUNTS`**
> and an optional **`data/server.cyml`**, and the reasoning for allowing it is
> narrow enough to state precisely so it is not read as the freeze being over:
>
> - **The freeze's stated purpose is compatibility** — "clients, operators, zone
>   authors, and existing save files keep working across 1.x". An *additive* knob
>   that defaults to today's behaviour breaks none of those. Nothing that runs
>   now stops running, and no operator has to change anything.
> - **The four frozen names are untouched.** Their names and semantics are
>   exactly as above; this adds a fifth, it does not redefine any of the four.
> - **The cap is off by default** (`0` = unlimited). A deployment that ignores
>   this release entirely behaves as 1.7.1 did.
> - **The config file is the preferred surface, and it is why this stays small.**
>   Operator settings from here on go in `data/server.cyml`, parsed with the same
>   CYML reader as zones and classes, so the *next* setting costs a key rather
>   than another amendment to this record. `YD_MAX_ACCOUNTS` exists because
>   container deployments configure through the environment, and it wins over the
>   file for that reason.
>
> **Still frozen, and not softened by this:** verbs, the `@`-namespace, save
> schema v1, wire behaviour, and the zone format. A new *verb* or a new *save
> field* is still a 2.0 change. If a future release wants a sixth knob, it needs
> its own argument — "1.7.2 did it" is not one.

## Consequences

- **Positive** — 1.0.0 can be a pure stabilisation release; clients, operators,
  zone authors, and existing save files keep working across 1.x. The `schema`
  stamp makes post-1.0 save evolution a managed migration rather than a silent
  break. The admin gate removes the last unguarded surface from the default
  build.
- **Negative** — new verbs / save fields / zone fields / env knobs are now
  blocked until after 1.0 (or behind a major bump) — see the 1.7.2 amendment
  above, which admits one additive knob and a config file on a stated argument —
  which slows feature work
  during the 0.9.1 → 1.0.0 window. The `@`-gate is a behaviour change: `@stats`,
  always-on since M1-H, now needs `YD_ADMIN=1`.
- **Neutral** — this ADR is a living contract for the 1.x line; a 2.0 may
  supersede it. Operator auth (M8) will replace the `YD_ADMIN` gate without
  changing the verb surface.

## Alternatives considered

- **Don't freeze; let 1.0 ship whatever's current.** Risks a 1.0 that keeps
  shifting underneath consumers, defeating the point of a 1.0. Rejected.
- **Freeze at 1.0.0 instead of 0.9.1.** Folds the enumeration into the release
  itself, leaving no buffer to catch a surface item that *should* change before
  it's locked. Rejected — the freeze wants its own checkpoint.
- **Build operator auth now instead of the env gate.** That's the M8 milestone;
  pulling it into a freeze patch is scope creep. The env gate closes the surface
  for 1.0 and M8 replaces it cleanly later. Rejected for 0.9.1.
