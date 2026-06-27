# Goal2901: Intake Goal2897 Review Of RayDB Perf Gate

Date: 2026-05-31
Status: accepted as external-review intake

## Purpose

Goal2897 is an independent Gemini review of the Goal2896 RayDB same-contract performance-decision gate. Goal2901 indexes that review into the v2.5 readiness packet and records its boundary conditions.

## Review Verdict

`accept-with-boundary`

Review path:

`docs/reviews/goal2897_external_review_goal2896_raydb_same_contract_perf_gate_2026-05-31.md`

The review accepts Goal2896 for v2.5 planning:

- Goal2896 is executable and reproducible;
- same-contract decision evidence is separated from diagnostic full-call baseline evidence;
- thresholds are reasonable for an internal planning gate;
- the report avoids release and public-claim overreach;
- primitive-first routing follows from the evidence for exact fused scalar grouped reductions.

## Boundary Added By Review

Before Goal2896 feeds any future v2.5 release packet:

- compiler flag alignment should be explicit enough to avoid native-vs-Triton compiler-bias concerns;
- another architecture/vendor check should be considered, such as L4 or AMD/ROCm, before broadening the performance interpretation.

These are release-packet cautions, not blockers for using Goal2896 as internal planning evidence.

## Readiness Update

Updated `src/rtdsl/v2_5_internal_readiness.py` so the internal packet requires:

- this intake report;
- the Goal2897 external review file.

It also records two allowed next actions:

- `track_goal2897_compiler_flag_alignment_before_release_packet`
- `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`

## Boundary

This is not v2.5 release consensus.

It does not authorize public speedup claims, true-zero-copy claims, whole-app RayDB reproduction, automatic Triton selection, paper reproduction, or package-install claims.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2901_goal2897_raydb_perf_gate_review_intake_test

Ran 3 tests in 0.147s
OK
```

Focused readiness validation also passed:

```text
Ran 26 tests in 0.489s
OK
```
