# 0005 — Zone file format

**Status**: Accepted
**Date**: 2026-06-09

## Context

M3 makes the world physical: rooms with prose, exits, and contents; mob
and object templates; per-zone reset metadata. Authors (initially us,
later content contributors) hand-write this content, so the format has to
be **pleasant to author and read** — a room description is a paragraph of
prose, not a quoted string. The loader (M3-B) parses it at boot, validates
the exit graph, and builds the in-memory world tree; Joshua re-parses a
single zone live at M8. Every byte is untrusted input on the M9 audit
surface, so the parser is a security consumer too.

A zone entity has two distinct shapes of data:

1. **Structured fields** — room id, exit targets, mob/object spawn lists,
   numeric stats. Key/value, machine-read.
2. **Freeform prose** — the room description, the mob's look text. A
   multi-line paragraph, human-read, ANSI-rendered.

The realistic options:

1. **CYML** (`lib/cyml.cyr`) — a TOML header above `---`, a markdown body
   below; multi-entry files via `[[entries]]`. First-party, already
   fuzz-hardened, zero-copy.
2. **TOML** (`lib/toml.cyr`) — flat sections + key/value. First-party.
3. **Bespoke DikuMUD dialect** — the era-authentic `.wld` / `.mob` /
   `.obj` / `.zon` family (`#VNUM`, tilde-terminated prose, `S`/`E`
   section markers).

The project's stated lineage is "DikuMUD / LPMud tradition," which biases
toward authenticity — but authenticity has to be weighed against the cost
of four hand-written, individually-fuzzed, individually-audited parsers.

## Decision

Zone content is authored in **CYML** (`lib/cyml.cyr`). The header/body
duality is the deciding fit: a room's structured fields live in the entry
**header** (TOML), its prose lives in the entry **body** (markdown). That
is precisely the shape of a DikuMUD `.wld` room — numeric metadata
followed by a description blob — expressed in a format that already has a
working, fuzzed, first-party parser.

**File layout — one file per zone per entity kind**, mirroring DikuMUD's
own `.wld` / `.mob` / `.obj` split:

```
data/zones/<zone>.rooms.cyml     rooms
data/zones/<zone>.mobs.cyml      mob templates
data/zones/<zone>.objs.cyml      object templates
```

Each file is a multi-entry CYML document: a file-level header carrying
zone metadata (`zone`, `name`, `reset_secs`), then one `[[entries]]` per
entity. The split is not only thematic — it keeps each file under the
**32-entry-per-file** ceiling imposed by `lib/cyml.cyr` (its entry-marker
scan uses a 256-byte / 32-slot stack buffer; see *Consequences*).

**Schema (v0.4.0 / M3 scope).**

Rooms file — file header then one entry per room:

```
zone = "hub"
name = "The Hub"
reset_secs = 900
---
[[entries]]
kind = "room"
id = "hub.tavern"
title = "The Rusted Flagon"
exit_n = "hub.market"
exit_d = "hub.cellar"
mobs = ["drone"]
objects = ["notice"]
---
A low-ceilinged tavern, its neon sign guttering against the damp.
Cables snake across the floor to a humming brew-vat in the corner.
```

- `kind` discriminates the entry (`room` / `mob` / `obj`) — the loader
  rejects an entry whose `kind` does not match the file it is in.
- `id` is a globally unique dotted handle (`<zone>.<local>`); exits and
  spawn lists reference rooms / templates by id.
- `exit_<dir>` for `n s e w u d` names the destination room id; an absent
  direction is no exit. (Closed/locked doors are a post-M3 field.)
- `mobs` / `objects` are id lists spawned into the room on zone reset.
- The body (after `---`) is the room's prose, ANSI-rendered at M3-D.

Mob and object templates use the same entry shape with `kind = "mob"` /
`kind = "obj"` and their own fields (`keywords`, `level`, `hp`, attrs for
mobs; `keywords`, `type`, slot for objects) — fleshed out as M4/M5 give
them mechanics. The **`keywords` field is the noun scope** the M2 resolver
matches against (ADR 0005 closes the M2-C "scope supplied at M3" loop).

Out of scope for this ADR: doors/locks, weather, zone-to-zone portals,
procedural generation. Additive later; none break the entry contract.

## Consequences

**Positive**

- **Prose authoring is natural.** Descriptions are plain markdown body
  text — no quoting, no `\n`, no tilde terminators. The single biggest
  authoring-ergonomics win, and the reason CYML beats flat TOML.
- **One parser, already hardened.** We reuse `lib/cyml.cyr` (and
  `lib/toml.cyr` for header key/value) instead of writing and fuzzing
  four bespoke parsers. Directly shrinks the M9-A/M9-B audit surface —
  zone-file parsing is explicitly called out there.
- **DikuMUD-resonant without the DikuMUD parser.** The header+body room
  shape and the per-kind file split echo `.wld` / `.mob` / `.obj`, so the
  lineage is honoured in structure even though the on-disk syntax is CYML.
- **Zero-copy, load-once.** CYML returns pointers into the file buffer;
  parsing happens at boot / on Joshua reload (M8), never in the tick — no
  conflict with the single-thread loop ([ADR 0003](0003-single-thread-event-loop-concurrency.md)).
- **AGNOS-aligned** — first-party lib, "Own the Stack," no vendored
  external format dependency.

**Negative**

- **32 entries per file, hard.** `lib/cyml.cyr`'s entry scan stores marker
  offsets in a 256-byte stack array indexed by 8, so a file with > 32
  `[[entries]]` overflows it. We must not modify `lib/` ([CLAUDE.md](../../CLAUDE.md)),
  so the loader **enforces a ≤ 32-entry cap per file** and the content
  convention keeps zones within it (the starter Hub is ≤ 32 rooms in one
  rooms file). A zone that outgrows 32 of any kind splits into
  `<zone>-2.rooms.cyml` etc. This is a real authoring constraint, not a
  theoretical one — flagged here so M3-G stays inside it.
- **No native cross-reference validation.** CYML doesn't know an
  `exit_n` must name a real room. The loader (M3-B) owns exit-graph
  validation (reject dangling refs at boot) — work we'd have anyway.
- **Header values are untrusted.** Every field the loader reads (ids,
  exit targets, numeric stats) is bounds- and type-checked per the
  trust-no-external-data rule; ids are length-capped and charset-limited
  before they index the world tree.
- **Two libs in the path.** CYML for the entry split, TOML for header
  key/value parsing. Both first-party; the coupling is already how CYML
  is meant to be used.

**Neutral**

- Mob/object template field sets stay deliberately thin at M3 and grow as
  M4 (combat stats) and M5 (class data) give them mechanics — the entry
  contract (header fields + optional prose body) is stable across that
  growth.
- The `data/classes.cyml` referenced by [roadmap M5-B](../development/roadmap.md#m5--classes--abilities-v060)
  is the same CYML format, single-entry — this ADR sets that precedent.

## Alternatives considered

- **Flat TOML** (`lib/toml.cyr`) — rejected as the *primary* format
  because multi-line room prose in TOML triple-quoted strings is ugly to
  author and read, and that prose is the bulk of a zone file. TOML is
  retained for parsing the structured entry **header**, where key/value
  is exactly right.
- **Bespoke DikuMUD `.wld` / `.mob` / `.obj` / `.zon`** — rejected on
  cost and security. Four separate parsers for a notoriously fiddly format
  (tilde escaping, positional numeric fields, `S`/`E` markers), each a
  new fuzz target and audit item, to gain on-disk byte-authenticity we
  already capture structurally. The lineage is better served by spending
  that effort on content than on re-implementing a 1990s file format.
- **One CYML file per room (single-entry)** — rejected: a ~30-room zone
  becomes ~30 files plus mob/obj files, a directory sprawl that makes a
  zone hard to read as a whole. Multi-entry keeps one zone legible in
  three files, and sidesteps the per-room file explosion.
- **JSON** (`lib/json.cyr`) — rejected: same prose-authoring problem as
  TOML, with even less human-friendly multi-line text, and no thematic
  affinity with the MUD tradition.
