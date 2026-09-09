# Natural-scale Particle predecessor status

Date: 2026-09-09

Status: `PRESERVED_PREDECESSOR_BASELINE_LAYOUT_NOT_FINAL`

## What this transaction established

At source commit `7e4362ef98933c7390d7a86b536323b7fbfd236d`, the
create-only transaction completed all 16 formal workers, eight balanced paired
blocks, 48 timed samples, and 16 warmups with zero retry, discard, timeout, or
incorrect output.  Every worker returned the same complete `uint32[160000000,3]`
output identity.  A separate stdlib-only implementation reconstructed the raw
worker records, ledger, artifacts, source closure, and statistics.

The controller and recount both obtained:

- paired median RTDL / public PyOptiX: `0.5077664774832833`;
- worst block: `0.5421895177471076`;
- deterministic block-bootstrap interval:
  `[0.4935468195386611, 0.536064837543972]`.

These values are preserved observations, not final comparison claims.

## Why it is not the final strong-baseline transaction

Post-transaction source review found an avoidable physical-layout disadvantage
in the public PyOptiX arm.  Its device program wrote three output columns and
the host owner exposed the required `(query_count,3)` result as a non-contiguous
strided view.  The timed exact-output check therefore traversed three widely
separated memory streams.  RTDL returned the same semantic output as contiguous
AoS rows.

The two arms transferred the same number of output bytes and performed the same
semantic check, so this is not a correctness defect.  It is nevertheless a
competent-baseline defect because a handwritten PyOptiX implementation can
write the public AoS result directly without changing the algorithm or output
contract.  The approximately twofold RTDL advantage cannot be used until that
avoidable disadvantage is removed and the fixed baseline is measured in a new
transaction.

## Preservation and successor rule

- Raw archive SHA-256:
  `b1b44fdc79b4214e419ed60f5b2f16a75e1ea9d0fcece680740cc9ca769790d0`.
- Separate-script recount SHA-256:
  `3189c9d57bf4a5c32817e1404778db4b8701f371dd45c2084df0cf1c0adb5ea9`.
- Controller result SHA-256:
  `5f2822598d9990d3eaef63f22e2055cebc452b3f3a14d9a7dcf5993bdf2381d7`.
- Lead independent recount remains pending.
- Public and paper claims remain unauthorized.

The successor may change only the public PyOptiX output layout and evidence
identities needed for that repair.  It must retain the same 160M distinct
strict-interior transition ensemble, complete ordered U32x3 output, correctness
oracle, prepared resident-query endpoint, balanced eight-block protocol,
engineering thresholds, and zero-retry/zero-discard rule.  This predecessor
must not be pooled with or relabeled as the successor.
