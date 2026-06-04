# Handoff: Goal3228 Claude Review of Public PIP and Normalized Count Probes

Please perform a read-only independent Claude review of Goal3227 and the
boundary-normalized Goal3225 rerun.

## Expected Output

Write the review to:

`docs/reviews/goal3228_claude_review_goal3227_public_pip_and_normalized_count_probes_2026-06-03.md`

Use one of the accepted verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Scope

Goal3227 adds a bounded public RayJoin-style PIP count probe on `pip_county512`.
It reuses Goal2159 public CDB slice materialization and compares CPU
`positive_assignment_count` against prepared OptiX point/closed-shape count.
The pod artifact records 1430/1430 across five repeats on NVIDIA A40.

After your Goal3226 review noted that Goal3225 did not explicitly include
`true_zero_copy_claim_authorized`, both public count probes were normalized to
carry that flag as `false` at the top and row levels, and Goal3225/Goal3227 were
rerun on the pod at commit `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`.

## Files to Inspect

- `scripts/goal3227_rayjoin_public_pip_count_probe.py`
- `tests/goal3227_rayjoin_public_pip_count_probe_test.py`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.md`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.json`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.stdout`
- `tests/goal3227_rayjoin_public_pip_count_probe_artifact_test.py`
- Boundary-normalized Goal3225 files:
  - `scripts/goal3225_rayjoin_public_overlay_active_count_probe.py`
  - `docs/reports/goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.md`
  - `docs/reports/goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.json`
  - `tests/goal3225_rayjoin_public_overlay_active_count_probe_artifact_test.py`
- Context:
  - `docs/reviews/goal3226_claude_review_goal3225_public_overlay_active_count_probe_2026-06-03.md`

## Review Questions

1. Does Goal3227 correctly reuse public CDB slice materialization from Goal2159
   rather than authored fixtures?
2. Does it compare the correct PIP count contract: CPU
   `positive_assignment_count` versus prepared OptiX count?
3. Does the PIP artifact provide meaningful bounded public evidence with stable
   1430/1430 counts across five repeats?
4. Did the boundary normalization correctly address the Goal3226 observation by
   adding `true_zero_copy_claim_authorized: false` to Goal3225 and Goal3227?
5. Do the reports, JSON artifacts, stdout files, and tests agree after the
   reruns at commit `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`?
6. Are all claim boundaries preserved: no release, public speedup, broad RT-core,
   true zero-copy, `RTDL beats RayJoin`, or paper-reproduction authorization?
7. What remains before stronger RayJoin benchmark or paper-level claims?

## Boundaries

This is a read-only review. Do not edit source files, reports, artifacts, or
tests other than writing the requested review file.

The expected position is that Goal3227 plus normalized Goal3225 are internal
public-data planning evidence for count/parity only. They must not authorize
release, public speedup claims, broad RT-core claims, true zero-copy claims,
`RTDL beats RayJoin` claims, or RayJoin paper-reproduction claims.
