# V4 Goal4705 Source-Level PTX Cache Stability

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Fix and validate the cache-stability issue exposed during Goal4703: repeated
Numba compilation of the same callback source produced different raw PTX hashes
because NumbaEnv symbols contained non-semantic `B2vN` version tokens.

The goal was to make source-level callback compiles produce stable RTDL cache
keys while still changing the key when PTX content or toolchain fingerprint
changes.

## Implementation

Updated:

- `src/rtdsl/v4_goal4698_specialized_tier3_compile_cache.py`

New:

- `canonicalize_v4_goal4698_callback_ptx_for_cache`
- `src/rtdsl/v4_goal4705_source_ptx_cache_stability.py`
- `scripts/v4_goal4705_source_ptx_cache_stability_pod.py`
- `tests/v4_goal4705_source_ptx_cache_stability_test.py`

The canonicalizer normalizes known non-semantic NumbaEnv `B2vN` token drift in
PTX cache-key hashing. The raw PTX hash remains recorded for audit but no longer
participates in the cache key.

## POD Result

POD:

- host: `root@194.68.245.170 -p 22089`
- workspace: `/root/rtdl_v4_candidate_pod`
- GPU: NVIDIA RTX A5000
- driver: 570.195.03

Classification:

`pass_source_level_cache_stability_gate_not_public_support`

Rows checked:

- `custom_scalar_reduce_weighted_sum`
- `custom_score_affine`
- `custom_threshold_flag`
- `custom_minmax_score`

Observed for every variant:

- raw PTX hash equal across repeated compile: `false`
- canonical PTX hash equal: `true`
- cache key stable: `true`
- changed PTX changes key: `true`
- changed toolchain changes key: `true`

## Evidence

- POD JSON:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.json`
- POD markdown:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.md`
- Dry-run JSON:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_dry_run_2026-06-25.json`
- Dry-run markdown:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_dry_run_2026-06-25.md`

## Validation

Commands run:

```text
py scripts/v4_goal4705_source_ptx_cache_stability_pod.py --dry-run --json-out future/v4/evidence/v4_goal4705_source_ptx_cache_stability_dry_run_2026-06-25.json --md-out future/v4/evidence/v4_goal4705_source_ptx_cache_stability_dry_run_2026-06-25.md
py -m unittest tests.v4_goal4705_source_ptx_cache_stability_test tests.v4_goal4704_specialized_tier3_support_wording_test tests.v4_goal4698_specialized_tier3_compile_cache_test
py -m py_compile src/rtdsl/v4_goal4698_specialized_tier3_compile_cache.py src/rtdsl/v4_goal4705_source_ptx_cache_stability.py scripts/v4_goal4705_source_ptx_cache_stability_pod.py src/rtdsl/v4.py
```

Observed:

- local dry-run: passed.
- unit tests: `10 tests OK`.
- `py_compile`: passed.
- POD source-level cache stability gate: passed.

## Claim Boundary

Goal4705 hardens compile-cache behavior only. It does not authorize:

- public Tier-3 support;
- arbitrary callbacks;
- raw OptiX callbacks;
- V4 release wording;
- app-level speed claims;
- broad V4 performance claims.

## Goal-Level Decision Audit

1. Was I being stupid?

The original Goal4703 checker was too weak after clarification: it verified
artifact-level repeat-key stability, but did not guarantee user-source repeated
compile ergonomics. Goal4705 fixes that gap instead of documenting it away.

2. What actions made that decision stupid?

Including the raw PTX hash as a returned cache component was fine for audit, but
letting it participate in key serialization defeated canonicalization. That was
an implementation mistake and was fixed.

3. Is there another path that avoids being stupid on one idea?

Yes. Keep raw PTX hash for audit, use canonical PTX hash for cache identity, and
verify that true PTX/toolchain changes still alter the key.

4. Can I start a different path that actually solves the problem?

Yes. Goal4706 should add negative validation and clean user-facing examples so
the constrained candidate is understandable and fail-closed.

## Next

Proceed to Goal4706: specialized Tier-3 negative validation and user-doc example gate.
