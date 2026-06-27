# Kepler Fallback Review: Phoenix V3 Runner Metadata Overhead Reduction M6

Date: 2026-06-22
Status: `fallback_review_not_external_not_release`

## Verdict

`accept_local_only_need_more_runner_overhead_work`

## Review Summary

Kepler accepted that the M6 patch is generic V3 runtime-trunk work, not
app-specific tuning. It touches shared cache-key/report metadata plumbing in:

- `src/rtdsl/prepared_session_residency.py`
- `src/rtdsl/prepared_execution.py`

Kepler also accepted that claim boundaries appear preserved and that the local
50-test gate passed.

## Blocking Concern

Kepler did not authorize a focused pod validation yet. The causal concern is
that the optimized pieces mostly sit outside the measured Hausdorff
runner-vs-legacy phase-total path:

- cache key construction happens before the prepare timer starts;
- `PreparedExecutionReport.to_dict()` runs after prepare/warmup/executor timing
  is already captured.

Therefore the patch may reduce wrapper wall overhead, but it is unlikely by
itself to fix the Hausdorff M5 failed `runner_regressed_vs_legacy_phase_total`
gate.

## Recommended Next Step

Do one more generic runner-overhead pass aimed at costs that can affect measured
phase-total:

- cache lookup/hash path;
- redundant per-leg setup;
- input construction/fingerprint placement;
- runner-vs-legacy prepare timing deltas.

Then use Hausdorff M5 as the first focused canary because it is the known
failing no-regression gate and the cleanest proof that the productized trunk can
match the legacy prepared OptiX front door.

## Non-Authorization

This fallback review does not authorize:

- V3 release.
- all-app pod rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- true-zero-copy wording.
- V4 / external-buffer wording.
- focused pod validation for M6 as currently implemented.

## Goal-Level Decision Audit

Decision: accept M6 as local shared-runtime cleanup but do not run POD yet.

1. Was I foolish?

   No for this decision. The fallback review found a causal gap between the
   patch and the failed Hausdorff phase-total gate.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be spending pod money on a patch
   that likely only improves wrapper wall while the known gate failed on phase
   total too.

3. Was there another path that would have avoided getting stuck?

   Yes. Target the overhead that actually enters measured phase-total before
   running the known failing canary.

4. Can I now try a different path that actually solves the problem?

   Yes. Continue with a second generic runner-overhead pass aimed at measured
   prepare/query phase deltas, then re-review before POD.
