# Handoff: Gemini Review For Goal3593 Public-CDB RayJoin Same-Contract Probe

Please perform a read-only independent review of Goal3593 and write the review to:

`docs/reviews/goal3594_gemini_review_goal3593_rayjoin_public_cdb_cupy_same_contract_2026-06-06.md`

## Context

Goal3593 extends the Goal3589 RayJoin same-contract CuPy-vs-RTDL/OptiX pressure test from authored square/tiled fixtures to bounded public CDB slices on an RTX A5000 pod.

The key measured result is mixed:

- PIP public county 512: CuPy CUDA-core dense count is faster than current RTDL/OptiX.
- LSI public county/soil 512: RTDL/OptiX is much faster than CuPy dense all-pairs.
- Overlay public county/soil 512: RTDL/OptiX is much faster than CuPy dense all-pairs.

## Files To Read

- `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`
- `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`
- `tests/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test.py`
- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json`
- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`

## Review Questions

1. Does Goal3593 preserve the same-contract comparison boundary between the CuPy CUDA-core baseline and the RTDL/OptiX prepared routes?
2. Is the `SegmentColumns2D` support added to Goal3589 safe and generic, rather than a public-CDB-only hack?
3. Do the A5000 artifact and report accurately state the measured numbers and count-parity status?
4. Does the README route guidance correctly distinguish authored fixtures from bounded public CDB slices?
5. Are the claim boundaries strong enough: no RayJoin paper reproduction claim, no public RT-core speedup claim, no release claim, no automatic-dispatch claim, no zero-copy claim?
6. What must be fixed before using this evidence in a larger v2.8/v2.9 performance packet?

## Required Review Shape

- Start with `Verdict: accept`, `Verdict: accept-with-boundary`, `Verdict: needs-more-evidence`, or `Verdict: reject`.
- Lead with findings, ordered by severity.
- Include exact file references.
- State whether this review is independent Gemini review and distinct from Codex.
- Do not edit source code or reports except for writing the review file above.
