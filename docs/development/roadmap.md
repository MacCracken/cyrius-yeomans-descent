# cyrius-yeomans-decent — Roadmap

> Milestone plan through v1.0. State lives in [`state.md`](state.md);
> this file is the sequencing — what ships, in what order, against
> what dependency gates. Design reference: [`../architecture/overview.md`](../architecture/overview.md).

## v1.0 criteria

- [ ] TCP/Telnet server accepts concurrent player sessions reliably
- [ ] Verb-noun parser handles the full v1.0 verb table without ambiguity
- [ ] Combat tick (2.5s) runs deterministically under load with all four classes
- [ ] Zone reset semantics enforced (no respawn while players present)
- [ ] T.Ron-backed persistence — players survive server restart
- [ ] Joshua game management interface online for live ops
- [ ] Security audit pass logged in `docs/audit/YYYY-MM-DD-audit.md`
- [ ] Benchmarks captured in `docs/benchmarks.md` (tick throughput, parser p99, connection capacity)
- [ ] CHANGELOG complete from v0.1.0 onward

## Milestones

### M0 — Scaffold (v0.1.0) — ✅ shipped 2026-05-24

- `cyrius init` scaffold landed
- Doc tree per [first-party-documentation.md](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-documentation.md)
- Core design captured in [`../architecture/overview.md`](../architecture/overview.md)

### M1 — TCP / Telnet listener (v0.2.0)

- Raw TCP socket server accepting multiple concurrent connections
- Per-connection session state with login → name prompt → MOTD
- Line-oriented Telnet handling (CR/LF, basic option negotiation)
- Graceful disconnect and connection-count metrics
- **Gate**: clean ASan/equivalent run with N concurrent dummy clients

### M2 — Verb-noun parser (v0.3.0)

- Tokenizer for the v1.0 verb table
- Direct-object / preposition / indirect-object resolution
- `all.X` and `X.N` ordinal qualifiers (`get all.rations`, `kill 2.drone`)
- Aliases and abbreviations (`n` → `north`, `inv` → `inventory`)
- **Gate**: parser fuzz harness clean against 100k random inputs

### M3 — World, rooms, movement (v0.4.0)

- Zone / room data model and loader
- Cardinal-direction navigation (`n`, `s`, `e`, `w`, `u`, `d`)
- ANSI room rendering: title, prose, exits, present entities
- **Gate**: hand-authored starter zone walkable end-to-end

### M4 — Combat tick (v0.5.0)

- 2.5s server-wide tick scheduler
- 1d20 + DEX vs AC hit resolution; weapon dice + STR/TEC damage
- Aggression model: `kill` engagement, auto-attacks, target switching, death
- Corpse generation; `get all from corpse`
- **Gate**: load test — N players × M mobs ticking without drift

### M5 — Classes & abilities (v0.6.0)

- Pikeman, Splicer, Courier, Chaplain — core commands each
- Per-class attribute scaling (STR/DEX/CON/TEC)
- Cooldowns where appropriate within the tick model
- **Gate**: each class fully playable solo through the starter zone

### M6 — Persistence via T.Ron (v0.7.0)

- Player save/load round-trip (attrs, inventory, location, HP/stamina)
- Crash-safe writes (T.Ron transactional semantics)
- **Gate**: kill -9 the server mid-tick → restart → no player data loss

### M7 — Zone resets (v0.8.0)

- Per-zone 15-30 min reset timer with player-presence gating
- Mob and loot respawn at reset
- **Gate**: empty zone resets cleanly; populated zone does not

### M8 — Joshua management interface (v0.9.0)

- Operator console: live player list, kick/ban, broadcast, zone reload
- Audit log of operator actions
- **Gate**: live ops procedures runnable from Joshua alone

### M9 — Hardening + v1.0 (v1.0.0)

- Security audit pass; CVE sweep
- Benchmark baselines locked
- Public API frozen
- Internal Summer-of-Games playtest signed off

## Out of scope (for v1.0)

- Windows client support (Telnet clients exist; not our problem)
- Web client (a Telnet-over-WebSocket wrapper is fine; a bespoke web client is not)
- PvP arenas (post-v1.0 if demand emerges)
- Player housing
- Voice / audio
- Native graphics
