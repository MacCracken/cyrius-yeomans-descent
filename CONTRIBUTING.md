# Contributing to cyrius-yeomans-descent

Thanks for the interest. cyrius-yeomans-descent is a Cyrius-native MUD server in the [AGNOS](https://github.com/MacCracken/agnosticos) first-party stack — contributions follow the standards documented at [first-party-standards](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-standards.md) and [first-party-documentation](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-documentation.md).

## Before You Start

1. Read [`CLAUDE.md`](CLAUDE.md) — project identity, hard constraints, and the work loop.
2. Skim [`docs/architecture/overview.md`](docs/architecture/overview.md) — the core design (tick architecture, parser, zones, classes).
3. Check [`docs/development/roadmap.md`](docs/development/roadmap.md) for the current milestone and [`docs/development/state.md`](docs/development/state.md) for live state.

## Development Loop

```sh
cyrius deps                                              # resolve stdlib deps
cyrius build src/main.cyr build/cyrius-yeomans-descent    # compile
cyrius test                                              # run [build].test + tests/*.tcyr
```

Per [`CLAUDE.md`](CLAUDE.md):

- ONE change at a time — never bundle unrelated changes
- Test after every change, not after the feature is "done"
- Bound every buffer; validate every syscall return
- Source files only need project includes — stdlib deps auto-resolve from `cyrius.cyml`

## Pull Requests

- Reference the roadmap milestone or issue in the PR description.
- Update [`CHANGELOG.md`](CHANGELOG.md) under `[Unreleased]`.
- If the change earns one, add an ADR (`docs/adr/NNNN-*.md`) — see [`docs/adr/template.md`](docs/adr/template.md).
- Non-obvious code invariants land as an architecture note (`docs/architecture/NNN-*.md`).
- Bump [`docs/development/state.md`](docs/development/state.md) for anything that moves the live snapshot.

## Reporting Bugs and Security Issues

- Functional bugs: open a GitHub issue with a minimal reproduction.
- Security issues: see [`SECURITY.md`](SECURITY.md) — do not open a public issue.

## Code of Conduct

By contributing you agree to the terms of [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
