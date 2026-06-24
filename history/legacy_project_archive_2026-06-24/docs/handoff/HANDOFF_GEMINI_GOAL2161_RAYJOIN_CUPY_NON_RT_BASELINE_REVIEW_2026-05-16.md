# Handoff: Gemini Review For Goal2161 RayJoin CuPy Non-RT Baseline

Please perform an independent read-only Gemini review of Goal2161.

## Context

Goal2161 adds a `cupy_lsi_bruteforce` backend to the reusable RayJoin public-CDB runner so RTDL/OptiX is compared not only against CPU and Embree, but also against a v2.0-style partner implementation that uses ordinary CUDA cores through CuPy `RawKernel`.

The result is intentionally conservative and somewhat negative for RTDL/OptiX:

- On `lsi_county256_soil256_count192`, medians are CPU `0.016256`, Embree `0.030044`, OptiX `0.015249`, CuPy `0.010819`.
- On the two-case warmed protocol, CuPy also beats OptiX on both `count128` and `count192`.
- All row-count and CPU-reference parity checks pass.
- The report explicitly says this does not authorize broad RayJoin, broad RT-core, paper-scale, or v2.0 release claims.

## Files To Review

- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `tests/goal2159_rayjoin_public_cdb_runner_test.py`
- `docs/reports/goal2161_rayjoin_cupy_non_rt_lsi_baseline_2026-05-16.md`
- `docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count192_pod_2026-05-16.json`
- `docs/reports/goal2161_rayjoin_public_cdb_cupy_baseline_count128_192_pod_2026-05-16.json`
- `tests/goal2161_rayjoin_cupy_non_rt_lsi_baseline_test.py`

## Review Questions

1. Does the CuPy backend correctly represent a non-RT CUDA-core partner baseline rather than an RTDL engine extension?
2. Is the negative result documented honestly and conservatively?
3. Are the claim boundaries strong enough to prevent a misleading RayJoin/RT-core speedup claim?
4. Do the artifacts and tests support the stated medians, parity, and backend classifications?
5. Is the proposed next direction, persistent-session or batched-query amortization, a reasonable engineering interpretation?

## Output Request

Write the review to:

`docs/reviews/goal2162_gemini_review_goal2161_rayjoin_cupy_non_rt_baseline_2026-05-16.md`

Use one of these verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please explicitly state that this is an independent Gemini review, distinct from Codex, and that it does not authorize v2.0 release by itself.
