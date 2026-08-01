# Getting started with cyrius-yeomans-descent

This guide is for **building and contributing**. To *play*, see
[playing.md](playing.md); to *run/operate* a server, see [running.md](running.md);
for the full command list, [commands.md](commands.md).

## Build & run

```sh
cyrius deps                                               # resolve dependencies
cyrius build src/main.cyr build/cyrius-yeomans-descent    # compile
cyrius test                                               # run [build].test + tests/*.tcyr
./build/cyrius-yeomans-descent serve 4000                 # run; connect via `telnet 127.0.0.1 4000`
```

## Layout

- `src/main.cyr` — entry point. Top-level `var r = main(); syscall(SYS_EXIT, r);`.
- **`tests/cyrius-yeomans-descent.tcyr` — the test suite. Put unit cases HERE.**
  1502 assertions; `cyrius test` auto-discovers it.
- `benches/*.bcyr` — **the real benchmarks** (`cyrius bench`): `bench_loaders`,
  `bench_telnet`, `bench_persist`, `bench_tick_budget`, `bench_combat`. Several
  gate on both time *and* bytes of never-reclaimed arena.
- `fuzz/*.fcyr` — **the real fuzz targets** (`cyrius fuzz`): `parser_fuzz` and
  `record_fuzz` (the pre-auth record scanner).
- `scripts/agnos-qemu-smoke.sh` — boots a real AGNOS kernel under QEMU and drives
  the server over TCP. Not part of `cyrius audit`; run it deliberately.

> **Three deliberate no-ops, so you do not add code to a file nobody runs.**
> `src/test.cyr` is a stub referenced by `cyrius.cyml [build].test` — its own
> header says *do not* add cases there, because it runs outside the `.tcyr`
> harness and reports only a bare exit code. **This project shipped a 298-test
> suite that never ran in CI for exactly that reason.** Likewise
> `tests/*.bcyr` and `tests/*.fcyr` are scaffold placeholders that announce
> themselves as asserting nothing; the real ones are in `benches/` and `fuzz/`.

**The gate is `cyrius audit` exiting 0** — fmt, lint, docs, tests and benches —
not `cyrius test` alone.

## Adding a feature

1. Edit `src/main.cyr` (or add a new module and `include` it).
2. Add a test case to `tests/cyrius-yeomans-descent.tcyr`.
3. Run `cyrius test`.
4. Bump `VERSION` and add a CHANGELOG entry before tagging.

See [`../adr/template.md`](../adr/template.md) when a non-trivial design choice deserves an ADR.
