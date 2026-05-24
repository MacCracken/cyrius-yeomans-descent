# Security Policy

## Reporting a Vulnerability

cyrius-yeomans-decent is a multi-user TCP service. A vulnerability in the parser, session handling, or tick loop can compromise every connected player.

**Do not open a public GitHub issue for security reports.**

Email the maintainer (`yeoman.maccracken@gmail.com`) with:

- A description of the issue and the impact you observed
- A minimal reproduction (commands, packet sequence, save state — whatever applies)
- The version (`VERSION` file) and toolchain pin (`cyrius.cyml [package].cyrius`) you tested against
- Any disclosure timeline you'd like respected

You'll get an acknowledgement within 7 days. Fixes ship as a patch release with a `Security` section in [`CHANGELOG.md`](CHANGELOG.md) and, for CVE-class issues, a pointer into `docs/audit/`.

## Scope

In scope:

- The TCP socket server and any state it persists
- The verb-noun parser (string handling, buffer bounds, command dispatch)
- The combat tick loop and any cross-player effects it computes
- Persistence backed by T.Ron
- Zone reset logic and any privilege boundaries between players

Out of scope:

- Social engineering of admins or players
- DoS via raw connection flood (network-layer concern, not application)
- Bugs that require operator-level access to reproduce

## Hardening Process

Every release runs the [first-party security hardening pass](https://github.com/MacCracken/agnosticos/blob/main/docs/development/first-party/first-party-standards.md#security-hardening-required-before-every-release):

1. Input validation on every external surface
2. Buffer safety — every `var buf[N]` audited; N is bytes
3. Syscall review — args checked, returns handled, error paths complete
4. Pointer validation on untrusted input
5. No command injection — no `sys_system()` with unsanitized input
6. No path traversal — file paths from external input validated
7. Known CVE review against current databases
8. Findings filed under `docs/audit/YYYY-MM-DD-audit.md`

Severity levels: **CRITICAL** (remote / privilege escalation), **HIGH** (moderate effort), **MEDIUM** (specific conditions), **LOW** (defense-in-depth).
