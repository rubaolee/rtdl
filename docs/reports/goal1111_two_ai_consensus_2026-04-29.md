# Goal1111 Two-AI Consensus

Date: 2026-04-29

Verdict: ACCEPT

## Scope

Goal1111 adds timing-only Robot Embree chunk support to avoid per-chunk CPU-oracle validation during large timing collection.

## Consensus

Codex verdict: ACCEPT after fixing the CLI exit-code blocker.

Second-AI reviewer verdict: ACCEPT after remediation.

Consensus conclusion: the timing-only artifact mode is ready for a real Linux chunk probe.

## Accepted Contract

Timing-only Robot Embree artifacts must use:

- `status: timing_only`
- `correctness_parity: null`
- `validation.skipped: true`
- `authorizes_public_speedup_claim: false`

Validated chunks remain required separately before any comparison or public wording review.

## Boundary

This goal does not authorize public RTX speedup claims, release wording, or a complete Robot baseline comparison.
