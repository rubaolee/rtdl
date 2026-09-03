# Goal5842 V9 pre-execution freeze and V10 source-contract correction

## Status

V9 was frozen locally before any V9 formal GPU transaction. Its preregistration
file SHA-256 is
`417ae18b5c249d439d9794bb6bd7a5d0bf890ea7a39203a38b9caa7f0146355a`
and its internal seal is
`88543c367920697e6d9e11052c923af2e79e8d373c87aea480e55d9a52c54e28`.
It records zero registered timing observations and zero formal GPU executions.
Worker zero was not reached.

An inherited source-contract regression was found after that freeze and before
commit or formal execution. Goal5798's immutable-input test requires the
historical PyOptiX worker to retain an explicit bulk-copy statement. V9 used a
semantically equivalent conditional expression, but that expression broke the
older source contract. The correction restores the explicit statement inside
an `if not public_output_only` branch, so the legacy default still bulk-copies
and the Goal5842 public-only path still performs no per-ray host copy.

The V9 source manifest differs from V10 candidate source at exactly one
existing path:

- `experiments/goal5798_premeasurement/pyoptix_worker.py`: frozen V9 SHA-256
  `b144b9d48ba68f5dd0c9c0fbe18aacb119b0ca229dc2e28305c95d536e162019`;
  corrected SHA-256
  `b97d299a5a9021ddc49fba969c31f692dfe4416be727b4173d47a639b002c4c7`.
The frozen V9 review remains exactly 3,835 bytes with SHA-256
`c692655f54e8be377c5d8d4d727ba1720b487cbbbad61bec35dd8d092285f4cd`.
V10 adds this repair record and a separate V10 hostile review instead of
rewriting V9 history.

V10 preserves all tasks, values, estimands, schedules, statistics, witness
contracts, baseline timing boundaries, hardware design, and claim ceilings.
It is a pre-execution source-contract correction, not a result-dependent retry.
No V9 row exists and none can be pooled.

## Claim boundary

V9 is neither a performance result nor a failed scientific cohort. V10 must be
committed before formal execution, execute from a clean exact checkout, and
still satisfy the two-generation and external-review gates before any CGO
performance statement is authorized.
