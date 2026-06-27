# V4 Goal4703 Specialized Tier-3 Reliability Matrix POD Result

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Run the frozen Goal4702 reliability matrix on POD for the constrained
specialized Tier-3 support candidate:

> module-specialized Numba C-ABI scalar device callback called as a direct
> device function from an RTDL-generated OptiX hit-program route.

This goal checks reliability and correctness only. It is not a performance
claim and not a public support authorization.

## POD

- host: `root@194.68.245.170 -p 22089`
- workspace: `/root/rtdl_v4_candidate_pod`
- GPU: NVIDIA RTX A5000
- driver: 570.195.03
- Python used: `/usr/bin/python3`

## Result

Final classification:

`pass_reliability_gate_not_public_support`

Summary:

- total attempts: `20`
- successful compile/link/launch attempts: `20`
- success rate: `1.0`
- correctness passed: `true`
- cache checks passed: `true`
- stage failures: none

Callback variants:

- `custom_scalar_reduce_weighted_sum`
- `custom_score_affine`
- `custom_threshold_flag`
- `custom_minmax_score`

Correctness datasets:

- `dense_hits`
- `sparse_hits`
- `no_hit_empty_reduction`

## Evidence

- POD JSON:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.json`
- POD markdown:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.md`
- Local dry-run JSON:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_dry_run_2026-06-25.json`
- Local dry-run markdown:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_dry_run_2026-06-25.md`
- Result contract:
  `src/rtdsl/v4_goal4703_specialized_tier3_reliability_result.py`
- POD script:
  `scripts/v4_goal4703_specialized_tier3_reliability_matrix_pod.py`
- Tests:
  `tests/v4_goal4703_specialized_tier3_reliability_result_test.py`

## Validation

Local validation:

```text
py scripts/v4_goal4703_specialized_tier3_reliability_matrix_pod.py --dry-run --json-out future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_dry_run_2026-06-25.json --md-out future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_dry_run_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4703_specialized_tier3_reliability_result.py scripts/v4_goal4703_specialized_tier3_reliability_matrix_pod.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4703_specialized_tier3_reliability_result_test tests.v4_goal4702_specialized_tier3_reliability_protocol_test tests.v4_goal4701_specialized_tier3_support_candidate_test
```

Observed:

- local dry-run: passed.
- local `py_compile`: passed.
- local unit tests: `6 tests OK`.
- POD matrix: `20/20` attempts passed.

## Cache-Key Note

The first POD matrix run exposed a checker bug: it treated separately generated
Numba PTX text as if it had to be byte-stable across repeated compilation. That
was stricter than Goal4702's frozen contract.

The corrected check matches the protocol:

- the same callback PTX artifact/toolchain/symbol repeats the same deterministic cache key;
- changed PTX changes the key;
- changed toolchain fingerprint changes the key.

The final evidence records that separately compiled Numba PTX hashes are not
stable across attempts. That is an engineering note for future source-level
cache canonicalization, not a failure of the Goal4702 artifact-level cache
contract.

## Claim Boundary

Goal4703 does not authorize:

- public Tier-3 support;
- arbitrary Python callbacks;
- action or side-effect callbacks;
- raw OptiX callback support;
- V4 release wording;
- app-level speed claims;
- broad V4 performance claims.

## Goal-Level Decision Audit

1. Was I being stupid?

Partly during the first checker run: the engineering run was valid, but the
cache-check interpretation exceeded the frozen protocol by requiring Numba
recompilation PTX byte stability.

2. What actions made that decision stupid?

I initially compared cache keys across independently recompiled PTX artifacts
and called that "same input." The actual protocol said same PTX/toolchain/symbol,
and independently recompiled PTX is not necessarily the same artifact.

3. Is there another path that avoids being stupid on one idea?

Yes. Test exactly the frozen cache contract and explicitly record the separate
engineering observation that source-level PTX canonicalization is not yet
guaranteed.

4. Can I start a different path that actually solves the problem?

Yes. Goal4704 should convert this support-candidate result into bounded wording
and remaining-hardening gates, without claiming public Tier-3 support before
external 3-AI review.

## Next

Proceed to Goal4704: specialized Tier-3 support wording and docs gate. This
must remain bounded and must not convert Goal4703 into public support or a
performance claim without external review.
