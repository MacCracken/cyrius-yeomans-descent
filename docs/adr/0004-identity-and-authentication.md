# 0004 — Identity & authentication model

**Status**: Accepted
**Date**: 2026-06-09

## Context

M6 makes players persistent: a name typed at the login prompt must map to a
saved record, and only the rightful owner may load it. The login surface is
**raw Telnet** ([ADR 0002](0002-raw-tcp-telnet-protocol.md)) — a human typing
into a stock client, no TLS, no custom tooling. That constrains the realistic
identity models hard:

- A pure **name+password** scheme (DikuMUD/CircleMUD tradition) is era-correct
  and trivially typeable, but it is "just" a hashed secret and uses none of the
  AGNOS crypto surface the ecosystem standardizes on.
- A pure **Ed25519 keypair** scheme (sigil, agora-precedented) is what the rest
  of the ecosystem authenticates with, but a human cannot hold or sign with a
  private key through a typed Telnet session — it needs a client-side agent.

The earlier `cyrius.cyml` note that called M6 "blocked on a sigil bug" *also*
asserted "Ed25519 via sigil" as settled; that note was wrong on both counts
(see [`state.md`](../development/state.md) M6-A). This ADR is the real decision,
made with the dep chain landed and working.

## Decision

**Identity is a sigil Ed25519 keypair whose seed is derived deterministically
from the player's passphrase**, reconciling both models:

```
seed   = SHA-256(salt(16 random bytes) || passphrase)      # sigil
(sk,pk) = ed25519_keypair(seed)                            # sigil
```

- The player types a **passphrase** (era-correct UX). The server uses it as
  key material, not as a stored secret.
- **Stored on disk: salt + public key only.** The secret key is *never*
  written — it is re-derived from the typed passphrase at each login.
- **Authentication** = re-derive the keypair from `stored salt + typed
  passphrase` and require the derived public key to equal the stored one.
- **Record integrity** = each save file is Ed25519-**signed** over its own
  body with the derived secret key (held in-session); load verifies the
  signature before trusting any field, so silent corruption or tampering of a
  save is rejected (returns "unreadable", never loads bad state).
- New characters confirm the passphrase twice; the salt is generated with
  `random_bytes` at creation.

Scope: this is account/character auth for the MUD. It is *not* a general
sigil trust-verification deployment (no keyring, no revocation) — just the
keypair + sign/verify primitives.

## Consequences

- **Positive** — uses sigil Ed25519 for real (derive + sign + verify), stays
  fully usable over raw Telnet, and stores no replayable secret: a stolen
  save file yields only a public key + salt, not the keypair. Tamper-evident
  records fall out for free and feed the libro audit chain.
- **Negative** — the passphrase still crosses the wire in cleartext (Telnet has
  no TLS); deriving a keypair from a passphrase is, cryptographically, close to
  a salted hash — the Ed25519 value-add is the *signature*, not stronger login.
  No password-strength policy beyond a 4–64 char length bound. No passphrase
  recovery: lose it, lose the character (by design — the server can't recover a
  key it never stored).
- **Neutral** — Telnet echo suppression for the passphrase prompt is deferred
  (the passphrase locally echoes in the client); tracked as a follow-up, it
  needs the IAC WILL/WONT ECHO dance through the RFC 1143 negotiator.

## Alternatives considered

- **Name + salted-password hash.** Simplest and era-correct, but uses none of
  the ecosystem crypto and offers no record-integrity story. Rejected: the
  derived-keypair scheme is the same typing UX and strictly more capable.
- **Raw Ed25519 keypair (client holds the key).** Ecosystem-canonical and the
  strongest login, but unusable for a human in a stock Telnet client without a
  signing agent. Rejected as hostile to the ADR-0002 wire model.
- **Seed-phrase login (server generates the key, shows a recovery seed once).**
  Wallet-style; the player pastes a seed at login. Strong and stateless, but a
  worse first-run UX than a chosen passphrase and easy to lose. Rejected for
  M6; could layer on later as an optional "hardware key" tier.
