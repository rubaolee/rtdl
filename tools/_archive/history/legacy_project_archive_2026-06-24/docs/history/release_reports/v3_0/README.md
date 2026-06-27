# RTDL v3.0 Release Package

Status: released source-tree major-version packet for tag `v3.0`.

Version marker: `v3.0`

Release date: 2026-06-18

## Release Statement

RTDL v3.0 is the most important RTDL release so far because it closes the
ten-app benchmark route project and turns the system from a sequence of
evidence packets into a coherent source-tree language/runtime surface.

The release publishes the current V3 programming model:

- app-agnostic RTDL primitives and prepared front doors first;
- explicit CuPy, Numba, NumPy, CPU, Embree, and OptiX route choice where custom
  continuation is needed;
- a closed ten-app benchmark route matrix;
- a canonical validation command: `scripts/run_test_matrix.py --group v3_current`.

This is a source-tree release. Use it from a checkout with `PYTHONPATH=src:.`
or the optional local editable checkout. It is not a PyPI, wheel, stable SDK,
generated binding package, public true-zero-copy, or automatic optimizer
release.

## Why v3.0 Matters

v1.0 proved that Python-facing RTDL could express app-shaped traversal
workloads. v2.x cleaned the Python+partner boundary and made public wording
row-scoped. v3.0 completes the current benchmark-app route project: all ten
current routes are closed, the runtime and claim queues are empty, V4 deferrals
are explicit, and app authors now have a single route-choice policy to follow.
Embedding, SDK packaging, generated bindings, zero-copy framework interop, and
external-runtime integration are not part of V3.0; they are V4.0 scope.

## Included Release Docs

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Public Wording Boundaries](public_wording_boundaries.md)
- [Publication Note](publication.md)
- [Tag Preparation](tag_preparation.md)
- [Final Closeout](final_closeout.md)
- [Major Release Requirements Trace](major_release_requirements_trace.md)

## Evidence

- [Goal4536 V3 internal completion packet](../../reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md)
- [Goal4538 V3 completion review consensus](../../reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md)
- [Goal4544 V3 app-author strategy doc](../../reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.md)
- [Goal4546 V3 current test matrix gate](../../reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.md)
- [Goal4614 V3 current-scope completion gate](../../reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md)
- [V3.0 app-author implementation strategy](../../learn/v3_0_app_author_implementation_strategy.md)
- [Benchmark evidence index](../../learn/benchmark_evidence_index.md)

## Release Gates

| Gate | Required state |
| --- | --- |
| Version marker | `VERSION` is `v3.0`; editable metadata version is `3.0.0`. |
| Front page and docs index | Current learner-facing docs identify v3.0 as the active source-tree release. |
| Ten-app closure | Goal4614 records all ten benchmark apps as closed current targets. |
| Claim queues | Runtime, claim/evidence, design-blocker, and future-design queues are empty. |
| Route policy | V3 app-author strategy is learner-facing and linked from the main docs path. |
| V4 scope exclusion | Embedding, C ABI, SDK packaging, generated bindings, device-buffer execution, external stream ordering, zero-copy framework interop, and device-callable fusion are excluded from V3.0 release criteria. |
| Validation | Source-tree doctor passes and `v3_current` matrix passes. |
| Boundaries | Public docs block broad speedup, paper reproduction, automatic partner selection, stable SDK, true-zero-copy, and generated binding claims. |
| Release authorization | Maintainer request on 2026-06-18 explicitly authorizes publishing V3.0. |

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --json
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v3_current
```

For the complete release validation used for this packet, see
[Final Closeout](final_closeout.md).

## Release Boundary

v3.0 is released with conservative wording. It is a source-tree major release
for the current RTDL programming surface and benchmark route closure. It does
not claim broad whole-application speedups, paper reproduction, RTDL beating
specialized author code, automatic partner selection, embedding/SDK readiness,
public true-zero-copy, stable packaged SDK status, generated binding packages,
device-buffer query execution, external CUDA stream ordering, or app-specific
native-engine extension APIs.
