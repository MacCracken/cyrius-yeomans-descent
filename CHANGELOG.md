# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.0] — 2026-06-10

**Yeoman's Descent 1.0 — feature-complete.** The clean cut: a stabilisation-only
release against the frozen 0.9.1 surface ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).
No new verbs, save fields, zone fields, or env knobs — nothing observable
changed from 0.9.1. The full game loop is implemented, secured, and documented.

### The 1.0 game

- **Wire** — raw TCP / Telnet, RFC 854 IAC + RFC 1143 negotiation, per-session
  line handling, passphrase echo suppression.
- **Parser** — verb-noun with direct/indirect objects, prepositions, and
  `all.X` / `N.X` qualifiers; fuzz-clean.
- **World** — a hand-authored 21-room Hub across four districts, with ambient
  loot that restocks on reset.
- **Combat** — a 2.5 s server-wide tick, hidden `1d20`+mods vs AC, corpses + loot.
- **Classes** — Pikeman / Splicer / Courier / Chaplain, each with three abilities
  on an energy + cooldown + status framework; each clears the Hub solo.
- **Persistence** — Ed25519 identity derived from a passphrase (sigil); crash-safe,
  signed, schema-stamped per-player saves; a libro audit chain. Reconnect
  restores attrs / room / inventory; survives `kill -9`.
- **Zone resets** — presence-gated mob/loot respawn on a per-zone timer.
- **Security** — memory-safety + CVE-class swept (0.9.0); every loaded save field
  validated; the `@`-admin namespace gated behind `YD_ADMIN`.

### Documentation

- README rewritten for 1.0 (status, libro+sigil backend, real usage).
- New player/operator guides: `docs/guides/playing.md`, `commands.md`,
  `running.md`; `getting-started.md` refreshed.
- Stale-data sweep across all docs: corrected the legacy "backed by T.Ron" /
  "managed via Joshua" framing (persistence is libro+sigil; Joshua/M8 is
  deferred post-1.0), refreshed the architecture overview, roadmap, and state
  snapshot, and updated test counts (298).

### Deferred (post-1.0)

- **M8 — Joshua operator interface.** The `@`-admin verbs are groundwork; full
  operator authentication and the Joshua control channel come after 1.0.

## [0.9.1] — 2026-06-10

**Surface freeze.** The public surface is enumerated and locked for 1.0 so the
final release is stabilisation-only ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md)).
Two behaviour-affecting changes land here; 1.0.0 changes nothing observable.

### Added

- **Save-record schema version** ([ADR 0007](docs/adr/0007-frozen-1.0-surface.md) §3).
  Every record now stamps `schema = 1` (in the signed prefix); the loader
  rejects any record stamped newer than it understands. Records from
  0.7.0–0.9.0 carry no `schema` field and load as v1 (back-compatible). This is
  the migration hook for post-1.0 field changes.
- **ADR 0007 — frozen 1.0 surface.** Documents the locked surface: command
  verbs + aliases + `@`-namespace, save schema v1 fields, Telnet/wire
  behaviour, zone-file format, env knobs.

### Changed

- **The `@`-admin namespace is gated behind `YD_ADMIN` (default off).**
  `@stats`/`@who`/`@reset` only work when the server is started with
  `YD_ADMIN=1`; otherwise they read as unknown commands and are hidden from
  `help`. Closes the last unguarded surface in the default build; full operator
  authentication remains deferred to M8 (post-1.0). **Behaviour change:**
  `@stats`, always-on since M1-H, now requires `YD_ADMIN=1`.

## [0.9.0] — 2026-06-10

**Security sweep & audit.** A focused pass over the network-input and
save-file attack surface, informed by current CVE classes (telnet pre-auth
overflows à la CVE-2026-32746, Ed25519 malleability à la CVE-2020-36843).
Four memory-safety / DoS issues found and fixed; all reachable from a raw TCP
connection or a planted save file. New `security` test group (9 assertions);
the remote pre-auth vector is live-verified to no longer crash the server.

### Security

- **[Critical] Two heap buffer overflows in the auth path, both bounded now.**
  (1) `ident_derive` copied the passphrase into a 256-byte scratch using the
  raw line length (up to `LINE_CAP` = 4096) — reachable **pre-auth** at the
  returning-login passphrase prompt. (2) `player_auth_load` hex-decoded the
  record's `salt`/`pubkey`/`sig` into 16/32/64-byte slots with no length check
  **before** signature verification, so an over-long hex field in a planted
  record overflowed the heap. Fixes: `ident_derive` hard-clamps the passphrase
  to `PASS_MAX`; every derive call site bounds its length; the loader requires
  exact hex lengths before decoding.
- **[High] OOB read from an unvalidated `class` index.** A loaded `class` fed
  `class_name_ptr(cls) = g_classes + cls*CL_SIZE` with no bound — a player owns
  their Ed25519 key and can re-sign their own record with `class = <huge>`,
  leaking heap memory to the wire on the next `examine`/`help`. Now clamped to
  `[0, g_class_count)` (out-of-range → classless).
- **[Medium] Server-wide DoS from an unvalidated `ndice`.** A re-signed save
  with `ndice = 2e9` spun the `roll()` loop for billions of iterations inside
  the single-thread combat tick. Every numeric save field is now clamped to a
  sane range on load.
- **Hardening principle.** A save's Ed25519 signature proves its **author**,
  not its field **values** — so every field loaded from a player-owned record
  is now validated/clamped, not trusted on the strength of the signature.

### Notes

- **Ed25519 signature malleability** (CVE-2020-36843 / CVE-2026-33895 class:
  missing `S < L` check) was researched and judged **non-applicable**: the
  record signature is used for integrity, not signature uniqueness or
  replay-prevention, so a malleable variant cannot tamper a record; and the
  verifier lives in vendored `sigil`. No code change.
- Toolchain pin → **6.1.23**.

## [0.8.3] — 2026-06-10

Operator read-only verbs — groundwork for the M8 Joshua interface, surfacing
live server state from inside the world.

### Added

- **`@who`** — lists every in-world session (name + the room it's standing in)
  and the in-world count.
- **`@reset`** — forces an immediate zone reset, bypassing the presence gate.
  The top-up is idempotent (only dead mobs / missing objects respawn), re-arms
  the reset timer, and writes the standard reset log line. Reports
  `mobs +N, objs +M`.

### Notes

- The `@`-verb namespace (`@stats`, `@who`, `@reset`) is currently unguarded;
  M8 lands operator authentication in front of it.

## [0.8.2] — 2026-06-10

A content patch — the Hub gets lived-in. The M7-D object-respawn mechanism
finally has something to act on: ambient loot and flavor now populate the
world and restock on each zone reset.

### Added

- **Six flavor/loot object templates** (`data/zones/hub.objs.cyml`): a work
  notice, a dented tankard, a foil ration, a slag ingot, a clouded optic, and
  a shrine-token — alongside the existing scrip / cell / shard / core.
- **`objects =` spawns across 11 Hub rooms** (13 objects total), thematically
  placed: a notice at the gate and market arch, a tankard in the Flagon, a
  ration in the bunks, scrap on the stalls and through the foundry, scrip at
  the exchange, offerings at the Drowned Shrine. They render on `look` and, via
  M7-D, respawn when the zone resets — so the world restocks itself.

## [0.8.1] — 2026-06-10

A login & identity polish patch — no new milestone. Passphrases stay off the
screen, returning players get a greeting, and you can change your passphrase
from inside the world.

### Added

- **`passwd` verb.** Re-key your character from the command prompt: a fresh
  random salt + the new passphrase derive a new Ed25519 identity, the record
  is re-signed and saved ([ADR 0004](docs/adr/0004-identity-and-authentication.md)).
  Two-step (new + confirm), echo-suppressed, audited as `passwd.change`. The
  old passphrase stops working immediately.
- **Last-seen greeting.** A returning player is welcomed with `Last seen N
  <units> ago`, computed from the record's prior `last_login`.

### Changed

- **Passphrases no longer echo.** The server now sends `IAC WILL ECHO` before
  every passphrase prompt (login, new-character, and `passwd`) and `IAC WONT
  ECHO` once it's entered, so conformant Telnet clients hide the keystrokes —
  the deferred ADR-0004 item. Clients that ignore ECHO behave as before.
- `cmd_on_line` re-prompts with `> ` only when still at the command phase, so a
  verb that switches phase (like `passwd`) doesn't double-prompt.
- Toolchain pin → **6.1.22**.

## [0.8.0] — 2026-06-10

**M7 — zone resets.** The world heals itself: mobs and loot respawn to the
authored layout on a timer, but never while a player is standing in the zone.
Gate met: an empty zone resets within its window; a zone with a player in any
room defers until it empties.

### Added

- **M7-A — per-zone reset timer.** The zone header's `reset_secs` (Hub: 900)
  is read into `g_zone_reset_secs`; the clock tracks time since the last reset
  (armed at boot), not since server start. `YD_RESET_SECS` overrides it for
  testing/ops, alongside `YD_TICK_MS` / `YD_IDLE_MS`.
- **M7-B — player-presence gate.** `maybe_zone_reset` (in `advance_tick`)
  defers a due reset while any in-world session occupies the zone, retrying
  each tick until it empties — single-writer, so the snapshot can't race
  ([ADR 0003](docs/adr/0003-single-thread-event-loop-concurrency.md)).
- **M7-C — mob respawn.** `zone_reset_mobs` tops each room up to its authored
  mob multiset: for a template authored *k* times, it spawns *k − alive* fresh
  full-HP instances, so living mobs are never duplicated and a `scavver
  scavver` room refills only what died.
- **M7-D — object respawn.** `zone_reset_objs` reapplies each room's `objects`
  spawn list without duplicating objects already present (matched by the new
  `OI_TPL_ID`); corpses/dropped loot never match or block. Also wired at boot,
  so authored room objects now spawn (no Hub room declares any yet — mechanism
  is in place for future zones).
- **M7-E — reset event log.** Each reset emits one line for Joshua (M8):
  `[<epoch>] zone=<id> reset (rooms=N, mobs=M, objs=O)`.

### Changed

- Boot now reports `… mobs, … objs spawned` and arms the zone-reset timer.

### Fixed

- Removed a duplicate room-id lookup: M6's `world_room_by_id` re-implemented
  the existing `room_index_by_id` (M3-B); `persist.cyr` now calls the latter.

## [0.7.0] — 2026-06-09

**M6 — player persistence.** Players now survive a server restart. The gate
holds: `kill -9` the server mid-session → restart → the player reconnects at
their last room with full attributes and inventory. Identity is real
cryptography ([ADR 0004](docs/adr/0004-identity-and-authentication.md)); saves
are crash-safe and tamper-evident ([ADR 0006](docs/adr/0006-persistence-shape.md)).

### Added

- **M6-A — persistence dep chain.** First external (non-stdlib) dependency:
  **libro 2.7.1** (append-only SHA-256 hash-chain store), pulling **sigil
  3.6.0** (Ed25519), sakshi, patra, and agnosys transitively via
  `[deps.libro]`. The opt-in stdlib it needs (`ct`/`keccak`/`thread`/
  `thread_local`/`random`/`fs`/`process`/…) is declared in `cyrius.cyml`.
- **M6-B — Ed25519 identity (ADR 0004).** A player's identity is a sigil
  Ed25519 keypair whose seed is `SHA-256(salt‖passphrase)`. The login flow
  gained passphrase phases: a new name forges an identity (choose + confirm a
  passphrase); a known name must present it. Only salt + public key are stored
  — the secret key is re-derived from the typed passphrase and never written.
- **M6-C — player save shape.** `data/players/<name>.cyml` (one `[player]`
  TOML section): identity, class, room (by stable id), attrs, vitals, combat
  profile, inventory (template ids), and timestamps. Inventory persists via a
  new `OI_TPL_ID` on item instances and re-instantiates from templates on load.
- **M6-D — save triggers.** On `save`, on disconnect (`quit` / idle reap /
  dropped socket), at character creation, and a debounced ~5-min tick sweep of
  dirty sessions — all out of the command hot path ([ADR 0003](docs/adr/0003-single-thread-event-loop-concurrency.md)).
- **M6-E — load on login.** A returning player's record is verified and
  restored, dropping them back into their recorded room (or the start room if
  it has since been removed).
- **M6-F — crash-safe writes.** Serialize → write `<name>.cyml.tmp` →
  atomic `rename(2)`. A crash leaves the complete old or new record, never a
  torn file. Each record is Ed25519-signed over its prefix; load rejects a
  corrupt or tampered record rather than loading bad state.
- **libro audit chain.** Login / save / character-creation / auth-failure /
  tamper-rejection events append to a hash-linked `data/audit.libro`.
- **Validation.** `programs/crypto_smoke.cyr` (crypto + chain) and
  `programs/persist_smoke.cyr` (on-disk save→reload round-trip + auth + tamper)
  build and run to exit 0; 16 new `persist` unit assertions (256 total, all
  pass); a live-server `kill -9` → restart → restore exercise passes.

### Fixed

- **Corrected the M6 "blocked on a sigil bug" misdiagnosis.** The crypto
  SIGILL (exit 132) was never a sigil defect — cyrius stdlib is **opt-in,
  never auto-resolved**, so `dist/sigil.cyr` was consumed without listing
  the stdlib modules its crypto calls (`ct`/`keccak`/`thread`/
  `thread_local`/`random`). cyrius 6.1.x only *warns* on the undefined
  symbols and compiles each to a `ud2` trap, so the build passed then
  crashed the moment a crypto path ran. Fix: those modules are now opted
  in via `cyrius.cyml [deps] stdlib`, ahead of the sigil include
  (single-pass forward-resolution). Diagnosed in sigil 3.7.8's CHANGELOG.

## [0.6.1] — 2026-06-09

A polish patch that completes the lived-in feel of combat — no new
milestone, no new dependencies. Fights are now visible to bystanders, mob
health reads at a glance, and every class recovers between fights.

### Added

- **Onlooker combat visibility.** Other players in a room now see a fight
  in third person — `alice strikes a rust-drone.`, `a rust-drone hits
  alice!`, `… collapses, destroyed.` — instead of nothing. Auto-attacks,
  misses, ability strikes, and kills all broadcast (`room_combat_line`,
  non-dropping). The combatant still gets the detailed first-person line.
- **Mob health condition.** `mob_condition` reports qualitative health
  (unhurt / lightly wounded / wounded / badly wounded / near death) from
  the HP fraction; shown in the room's mob list (when hurt) and in
  `examine`. Hidden numbers stay hidden.
- **Out-of-combat recovery.** A player regenerates HP each tick while not
  engaged, scaled by CON (`+1 + CON/5`), so every class — not just the
  Chaplain — heals between fights. No regen mid-combat (abilities only).

### Changed

- `classes_upkeep` now also runs out-of-combat HP recovery.
- 8 new unit assertions (240 total): `mob_condition` thresholds, CON-scaled
  regen, no-regen-while-engaged, regen HP cap.

## [0.6.0] — 2026-06-09

M5 — the four classes go from text-table flavor to playable mechanics.
Character creation now asks your calling; each class brings its own
attributes, combat profile, and three abilities that compose with the
2.5 s tick rather than replacing it ([ADR 0001](docs/adr/0001-tick-based-combat-over-cooldowns.md)).
All four can clear the Hub solo and kill the Foundry Sentinel boss
without dying — each through its own identity (the Pikeman tanks, the
Splicer bursts, the Courier strikes from the dark, the Chaplain sustains).

### Added

- **Classes** (`src/classes.cyr`, `data/classes.cyml`). Pikeman / Splicer /
  Courier / Chaplain, each with STR/DEX/CON/TEC, a derived combat profile
  (HP/AC/hit/damage), and an energy pool. `world_load_classes` parses the
  CYML; `apply_class` stamps the chosen class onto the session, replacing
  the M4 flat defaults.
- **M5-A — Class selection.** A login sub-phase (`PHASE_CLASS`) between the
  name prompt and world entry: a numbered menu; pick by number or name
  (prefix-matched); invalid picks re-prompt.
- **M5-G — Ability framework.** Per-session energy (regenerates each tick),
  three tick-counted cooldown slots, class-gating, and status effects —
  mob stun, an AC buff (brace/bypass), a damage+hit buff (stim), and
  stealth (backstab priming) — all folded into `combat_round`. Abilities
  resolve the instant they're typed, composing with the auto-attack.
- **M5-C/D/E/F — twelve abilities.** Pikeman `bash` (stun) / `brace` /
  `cleave`; Splicer `hack` / `overload` / `emp` (TEC-scaled, stun);
  Courier `sneak` / `backstab` (triple damage from stealth) / `bypass`;
  Chaplain `patch` / `stim` / `rally` (heal + buff). Cooldown / energy
  state is legible in the per-round condition line.
- **M5-H — solo verification.** A fresh-server-per-class harness confirms
  each class kills the Sentinel without dying twice.
- **`examine me`** is now a character sheet (class, HP/energy, attributes,
  AC); in-game `help` lists the player's class abilities.
- **`YD_TICK_MS`** env override for the combat-tick interval (mirrors
  `YD_IDLE_MS`) — fast ticks make combat verification quick.
- Unit suite grown 203 → 232 assertions (class load + fields, `class_by_input`
  number/prefix/trim/invalid, `apply_class`, `classes_upkeep` regen/decay,
  effective-stat buff helpers).

### Changed

- The login flow gained the class step: `login_on_name` now advances to
  `PHASE_CLASS` (not straight to the world); `login_on_class` applies the
  class and enters the world.
- `combat_round` reads buffed effective stats (`player_eff_ac` /
  `player_eff_hit` / `player_dmg_bonus`) and skips a stunned mob's turn;
  `combat_tick_all` runs `classes_upkeep` for every logged-in session.
- The combat load bench (`bench_combat.bcyr`) now includes `classes.cyr`
  and exercises per-tick upkeep alongside combat (p99 ≈ 57 µs).

## [0.5.0] — 2026-06-09

M4 — the tick gets a job. The placeholder 2.5 s Combat Tick from M1 now
resolves combat: a player engages a mob with `kill`, and each tick both
trade hidden-roll attacks until one dies. Mobs leave lootable corpses;
players respawn at the Hub. The full gameplay loop — explore, fight, loot,
carry, die, respawn — is playable end to end. Verified under load: 32
players × 64 mobs tick at a p99 of ~62 µs, ~800× inside the 50 ms budget.

### Added

- **Mobs** (`src/mob.cyr`). Templates load from `<zone>.mobs.cyml`
  (ADR 0005, `kind = "mob"`): id, display name, keywords, level, HP, AC,
  to-hit, and an `NdM+K` damage profile. Live instances spawn into rooms
  from each room's `mobs = "..."` list, on an intrusive room-occupant
  list; `mob_in_room_by_kw` resolves a typed noun against them.
- **Items + corpses** (`src/item.cyr`). Object templates from
  `<zone>.objs.cyml` (`kind = "obj"`); instances live in rooms,
  inventories, or containers on one shared list. A mob death synthesizes
  "the corpse of <mob>" holding the mob's `loot`, and `get all from
  corpse` (the M2 parser feature) empties it. `get` / `drop` /
  `inventory` wired to the live lists.
- **Combat** (`src/combat.cyr`). M4-A registry (per-session HP/AC/target +
  per-mob target). M4-B/C hit (`d20 + hit + AC >= 20`, nat-20 hits /
  nat-1 misses) and damage (`NdM+K`), hidden, prose-rendered. M4-D
  aggression: `kill` engages and the mob fights back; `flee` breaks off
  down a random exit; death disengages. The round runs inside
  `advance_tick`, flushed per session (the tick never frees a session —
  drops are left to the epoll path — so broadcasts are non-dropping).
- **M4-E** death + respawn. Mob → corpse + loot; player → drop inventory,
  respawn at the Hub start with full HP.
- **M4-G/H** drift + load test. The M1-H drift hook now wraps the combat
  tick; `benches/bench_combat.bcyr` drives 32 engaged sessions × 64 mobs
  through 120 real ticks and asserts p99 < 50 ms (measured ~62 µs).
- **Hub bestiary + loot** — `data/zones/hub.mobs.cyml` (scavver, rust-
  drone, wire-gang enforcer, the Foundry Sentinel boss) and
  `data/zones/hub.objs.cyml` (scrip, cells, plating, the Sentinel's core),
  spawned across the zone with per-mob loot tables.
- Unit suite grown 174 → 203 assertions (dice parse, RNG bounds, hit
  distribution, mob/obj template loading, spawn/find/remove, corpse + loot).

### Changed

- `cmd_dispatch` wires `kill`/`flee`/`get`/`drop`/`inventory`/`examine`
  to combat + items; the room render lists objects and mobs; `examine`
  resolves mobs (the M2 resolver's keyword scope is now live mob/item
  keywords). The session struct gains combat stats (`SS_HP`/`AC`/`TARGET`/
  weapon dice) and `SS_INV`.
- `g_epfd` moved to `session.cyr` (ahead of `combat.cyr`); room broadcasts
  and combat flushes are now non-dropping, so the combat tick can flush
  mid-walk without freeing a session.
- `cmd_serve` loads the Hub's objects + mobs and seeds the combat RNG at
  startup.

## [0.4.0] — 2026-06-09

M3 — the world becomes physical. The server loads CYML zone files at boot
into an in-memory room tree, places players in it at login, and gives them
movement, ANSI-rendered rooms, inspection, and room-scoped social verbs.
Two players can walk the authored 21-room starter zone (the Hub) and see
each other's arrivals, departures, and speech in real time. Items, mobs,
and combat are still ahead (M4-M5); the world they move through is here.

### Added

- **ADR 0005 — Zone file format.** Decided **CYML** (`lib/cyml.cyr`): a
  TOML header + markdown prose body per entry maps onto a DikuMUD room
  (structured fields + description blob) using an already-fuzzed
  first-party parser. One file per zone per entity kind
  (`<zone>.rooms/.mobs/.objs.cyml`), mirroring `.wld`/`.mob`/`.obj`, each
  ≤ 32 entries (the parser's per-file ceiling).
- **M3-B — Zone loader + world tree** (`src/world.cyr`). Parses a rooms
  file at boot, interns ids, keeps prose zero-copy into the persistent
  CYML buffer, resolves every `exit_<dir>` to a room index, and **rejects
  dangling exits at boot** (a bad graph fails to start, not mid-walk). An
  optional `start` header field names the spawn room. Loading is once at
  startup, never in the tick (ADR 0003).
- **M3-C — Movement.** `n`/`s`/`e`/`w`/`u`/`d` traverse exits; auto-look on
  arrival; "you can't go that way" for closed directions. Departure and
  arrival lines broadcast to onlookers in the source / destination rooms
  (a published `g_epfd` lets the session layer flush them immediately).
- **M3-D — ANSI room rendering.** Bold-yellow title, default-weight prose,
  cyan exits, bold-green player names — raw SGR emitted inline rather than
  pulling the client-side `darshana` lib (kept the zero-external-deps
  stance; `\x1b` is a one-byte ESC in Cyrius strings).
- **M3-E — Inspection.** `look` / `exits` render the current room;
  `examine` inspects self or a player present in the room (the M2
  resolver's first live scope); `inventory` is empty until items land.
- **M3-F — Social presence.** `say` / `emote` broadcast to the room (the
  actor sees their own line); `tell` is a directed cross-room message;
  `who` lists every connected player and their room.
- **M3-G — The Hub.** A 21-room starter zone
  (`data/zones/hub.rooms.cyml`): the Rusted Flagon tavern hub plus three
  loops — the Cinder Market, the Foundry, and the drowned Undercroft.
  Fully connected, every exit bidirectional, walkable end to end. Doubles
  as the v1.0 demo content.
- Unit suite grown 154 → 174 assertions (zone loader: interning, exit
  resolution both directions, `start`, dangling / wrong-kind / missing-file
  rejection, `verb_to_dir`). Self-contained fixtures under `tests/fixtures/`.

### Changed

- `cmd_dispatch` (`src/session.cyr`) replaces every M3-pending placeholder
  with real handlers: movement, room display, examine, and the social
  verbs now act on the world. The M2-era placeholders remain only as the
  graceful no-zone-loaded fallback.
- New `[deps]` stdlib: `cyml`, `toml` (zone-file parsing). Still no
  external (non-stdlib) deps — T.Ron (M6) and Joshua (M8) are the first.
- The session struct gains `SS_ROOM` (current room index, -1 until login);
  `cmd_serve` loads the Hub at startup (a load failure is non-fatal — the
  server runs roomless with the placeholder verbs).

## [0.3.0] — 2026-06-09

M2 — the verb-noun parser. Lines typed at the command prompt are now
tokenized, resolved to a canonical verb, and decomposed into direct
object / preposition / indirect object with `all.X` / `N.X` qualifiers.
The echo stub behind the login gate is gone; `cmd_on_line` routes through
the parser. The world the verbs act on still lands at M3 — until then the
handlers acknowledge the *parse* rather than fake world state. Pure and
fuzz-clean: 100k random inputs, no crash / hang / unbounded growth.

### Added

- **M2-A — Tokenizer** (`src/parser.cyr`). Whitespace-split (space / tab)
  with double-quote grouping for multi-word objects and lowercase
  normalization. Tokens are length-counted copies in a norm buffer —
  never NUL-terminated — so an embedded NUL is content, not a terminator.
  One shared `Parser` (lazily allocated) serves every session; parsing is
  synchronous and never spans calls.
- **M2-B — Verb table + aliases.** The canonical v1.0 verb set (movement,
  inspection, item manipulation, combat, social, session) resolves the
  first token to a `Verb` id; aliases fold in (`n`→north, `l`→look,
  `i`/`inv`→inventory). `verb_name` / `verb_is_movement` keep the taxonomy
  in one place.
- **M2-C — Direct-object resolution.** DikuMUD-style keyword prefix
  matching against an abstract scope (array of keyword strings). A unique
  match returns its index; zero → `RES_NOTFOUND`; many → `RES_AMBIGUOUS`.
  The live scope (room + inventory + equipment) is wired at M3 — the
  matcher is the deliverable, exercised here with synthetic scopes.
- **M2-D — Preposition / indirect-object.** Preposition table
  (`in`/`on`/`to`/`from`/`at`/`with`); the first preposition after the
  verb splits the line into direct- and indirect-object phrases, each
  resolved on its head noun (`give monoblade to kiran`,
  `put rations in pack`, `get all from corpse`).
- **M2-E — Qualifiers.** `all.X` (every match), `N.X` (the Nth match in
  deterministic scan order), and bare `all` (everything in scope).
  `qual_parse` splits the qualifier off the noun; `resolve_all` /
  `resolve_nth` collect against the scope under a caller-supplied cap.
- **M2-F — Fuzz harness** (`fuzz/parser_fuzz.fcyr`, run by `cyrius fuzz`).
  Deterministic xorshift PRNG, 100k iterations of parser-significant
  random bytes plus directed adversarial cases. Every iteration asserts:
  token count ≤ cap, norm buffer ≤ cap, each token inside the buffer,
  every parse-result index in range, `resolve_all` never overruns. One
  reused parser proves no per-line leak.
- Unit suite grown 52 → 154 assertions (tokenizer, verb table, resolution,
  preposition split, qualifiers).

### Changed

- `cmd_on_line` (`src/session.cyr`) replaces the M1-E echo stub with full
  verb dispatch. Social verbs echo the case-preserved message; object
  verbs reflect the parsed structure; movement / look / inventory return
  M3-pending placeholders; unknown verbs prompt `help`.
- **`quit` now disconnects.** A new `SS_QUIT` session flag, set by the
  verb and checked in `dispatch_session` after the goodbye flushes, tears
  the session down cleanly.
- The login welcome no longer advertises the echo stub — it points new
  players at `help`.

## [0.2.0] — 2026-06-09

M1 close — the binary now opens a port, walks the Telnet protocol,
negotiates options, runs a real login flow, reaps idle clients, and
surfaces loop observability, all over the single-thread epoll loop and
2.5 s tick from 0.1.0. Combat / world / verbs remain empty; the wire and
the heartbeat are complete.

### Added

- **M1-C — Telnet IAC parser** (`src/telnet.cyr`). Pure, side-effect-free
  RFC 854 §11.2 state machine (DATA / IAC / OPT / SB / SB_IAC). `telnet_feed`
  consumes one wire byte and emits EV_NONE / EV_DATA / EV_SB; escaped
  `IAC IAC` → literal `0xFF`; malformed subnegotiation recovers to DATA so
  hostile input can't pin the parser. One `TelnetState` per session in the
  reserved `SS_TS` slot. Decoded data bytes flow into a per-session line
  accumulator (`session_on_line`).
- **M1-D — Option negotiation** (RFC 1143 Q-method). Opening salvo
  `IAC WILL ECHO` + `IAC WILL SUPPRESS_GO_AHEAD` on connect, ahead of the
  banner. Per-option us/him Q-state; tracked options (ECHO, SGA) negotiate
  to agreement, everything else naive-refuses (WILL → DONT, DO → WONT). No
  renegotiation loops.
- **M1-E — Login flow scaffold.** MOTD → name prompt → MOTD-2 → command
  prompt. Names are captured (not authenticated — real auth at M6) and
  validated: 2–16 alphanumerics, must start with a letter, reserved handles
  (`system`, `admin`, leading `_`) refused with a re-prompt.
- **M1-F — Idle timeout & graceful disconnect.** Slowloris defense: a
  per-tick sweep reaps sessions silent past 5 minutes (intrusive
  active-session list threaded through `SS_NEXT` / `SS_PREV`). Threshold
  overridable via the `YD_IDLE_MS` env var for testing / ops. EOF / RST /
  write-error teardown drains in-flight tx best-effort.
- **M1-G — Benchmark harness** (`benches/bench_telnet.bcyr`). IAC-parser
  hot path; M1-close baseline ≈ 6 ns/byte mixed traffic, ≈ 5 ns/byte pure
  data. Re-run at every minor through 1.0 (roadmap M9-C).
- **M1-H — Observability.** `@stats` admin verb surfaces live connections,
  sessions logged in, ticks since boot, and tick-drift p99 (ms, over a
  512-sample ring). Becomes a Joshua input at M8.
- Test suite grown to 52 unit assertions across the parser, Q-method
  negotiation, name validation, and the idle predicate
  (`tests/cyrius-yeomans-descent.tcyr`).

### Changed

- Toolchain pin bumped `6.0.1` → `6.1.17` (`cyrius.cyml [package].cyrius`).
- The M1-B CRLF echo stub is now the `PHASE_CMD` placeholder behind the
  login gate, retained as a regression baseline until the M2 verb parser
  replaces it.

## [0.1.0] — 2026-05-24

First tag. Greenfield scaffold + the three load-bearing design ADRs +
the first slice of M1 (event-loop listener through per-connection
sessions, M1-A and M1-B). Echo stub on the wire; Telnet parser and
verb dispatch land at M1-C / M2.

### Added

- Project scaffold via `cyrius init` — `cyrius.cyml` manifest, `src/main.cyr`,
  `src/test.cyr`, `tests/cyrius-yeomans-descent.{tcyr,bcyr,fcyr}`,
  full first-party doc tree (`docs/adr/`, `docs/architecture/`,
  `docs/development/`, `docs/guides/`, `docs/examples/`).
- ADR 0001 — tick-based combat over real-time cooldowns. 2.5 s server-wide
  Combat Tick; hidden 1d20 + DEX-modifier vs AC rolls per tick.
- ADR 0002 — raw TCP / Telnet as the transport. Browser clients ride
  external Telnet-over-WebSocket bridges; we don't speak WebSocket natively.
- ADR 0003 — single-thread event loop for connection concurrency.
  Rules out fork-per-accept (cannot express shared world state) and
  thread-per-accept (mutex audit surface across every world-state mutation).
- `docs/architecture/overview.md` — system design: classes, parser shape,
  zones, transport.
- `docs/development/roadmap.md` — milestone plan M0 → M9, sub-bites under
  each milestone, v1.0 criteria, open-ADR queue.
- `docs/development/state.md` — live-state snapshot template; refreshed
  every release.
- M1-A — event-loop skeleton (`src/server.cyr`). Non-blocking listener
  via `lib/net.cyr`; `epoll`-shape multiplex; absolute-time tick scheduling
  with drift-resistant catch-up; SIGINT / SIGTERM shutdown via `signalfd`
  in the same epoll set. No-op `advance_tick()` placeholder for M4.
- M1-B — per-connection session struct (`src/session.cyr`). Heap-alloc
  via `lib/freelist.cyr` at accept, freed at disconnect per ADR 0003.
  Holds: fd, login phase, rx line buffer (4 KB), tx queue (4 KB),
  last-activity timestamp, and stub slots for the Telnet parser state
  (M1-C) and player id (M6). EPOLLOUT armed on demand when a write
  would block; disarmed when the tx queue drains. Echo stub processes
  complete CRLF lines as a sanity check pending the M1-C parser.
- CLI: `serve [port]` opens the listener (default 4000); `version` prints
  the version string; `help` shows usage.

### Notes

- Validated locally on Linux x86_64: 32-client concurrent fanout green
  (banner delivered + per-client echo round-trip); 100-line round-trip on
  a single session byte-exact; SIGINT shutdown clean (exit 0). Iron
  validation deferred until M1 closes.
- Binary: ~83 KB (`CYRIUS_DCE=1 cyrius build`).
