# Call For Review: V4 Goal4705 Source-Level PTX Cache Stability

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4705_cache_stability_continue_goal4706`
- `accept_with_required_amendments_before_goal4706`
- `reject_goal4705_cache_stability_repair_required`

## Context

Goal4703 passed the reliability matrix but exposed that separately compiled
Numba PTX artifacts can differ by non-semantic NumbaEnv `B2vN` tokens. Goal4705
adds cache canonicalization so repeated source-level compiles produce stable
cache keys while true PTX/toolchain changes still change the key.

## Review Inputs

- Completion record:
  `future/v4/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.md`
- POD JSON:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.json`
- POD markdown:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.md`
- Cache source:
  `src/rtdsl/v4_goal4698_specialized_tier3_compile_cache.py`
- Goal4705 source:
  `src/rtdsl/v4_goal4705_source_ptx_cache_stability.py`
- POD script:
  `scripts/v4_goal4705_source_ptx_cache_stability_pod.py`
- Tests:
  `tests/v4_goal4705_source_ptx_cache_stability_test.py`

## Questions For Reviewer

1. Is normalizing NumbaEnv `B2vN` token drift safe for cache identity?
2. Is it correct that raw PTX hash remains audit metadata but no longer participates in key serialization?
3. Does the POD result prove source-level repeated compile cache stability for the four current callback variants?
4. Does the changed-PTX and changed-toolchain sensitivity remain strong enough?
5. Is Goal4706, negative validation and user-doc example gate, the right next step?

## Non-Authorization

This review must not authorize public Tier-3 support, arbitrary callbacks, raw
OptiX callbacks, release wording, broad speed claims, whole-app speed claims, or
final V4 release. It can authorize only whether Goal4705 passed the cache
stability gate and whether Goal4706 may proceed.

