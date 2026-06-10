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
- `src/test.cyr` — top-level test entry referenced by `cyrius.cyml [build].test`. Add unit cases here or in `tests/cyrius-yeomans-descent.tcyr`.
- `tests/cyrius-yeomans-descent.tcyr` — primary test suite (`cyrius test` auto-discovers).
- `tests/cyrius-yeomans-descent.bcyr` — benchmarks (`cyrius bench`).
- `tests/cyrius-yeomans-descent.fcyr` — fuzz harness (`cyrius fuzz`).

## Adding a feature

1. Edit `src/main.cyr` (or add a new module and `include` it).
2. Add a test case to `tests/cyrius-yeomans-descent.tcyr`.
3. Run `cyrius test`.
4. Bump `VERSION` and add a CHANGELOG entry before tagging.

See [`../adr/template.md`](../adr/template.md) when a non-trivial design choice deserves an ADR.
