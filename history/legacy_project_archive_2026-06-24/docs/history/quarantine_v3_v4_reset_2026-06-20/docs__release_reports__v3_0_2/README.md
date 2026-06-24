# RTDL v3.0.2 Release Package

Status: released source-tree patch packet for tag `v3.0.2`.

Version marker: `v3.0.2`

Release date: 2026-06-18

## Release Statement

RTDL v3.0.2 is the current source-tree release for the V3.0 line. It keeps the
V3.0 benchmark-route closure and app-author programming surface, and publishes
the post-release boundary cleanup that makes the repository match the V3.0
claim boundary.

The release preserves the current V3 programming model:

- app-agnostic RTDL primitives and prepared front doors first;
- explicit CuPy, Numba, NumPy, CPU, Embree, and OptiX route choice where custom
  continuation is needed;
- a closed ten-app benchmark route matrix;
- a canonical validation command: `scripts/run_test_matrix.py --group v3_current`.

The patch release also keeps V4 preparatory embedding/C ABI/SDK/zero-copy work
out of default user paths: it is fenced under
`docs/history/v4_preparatory_embedding/`, validated by `v4_prep`, excluded
from `v3_current`, hidden from default `make help`, and absent from default
source-tree doctor output unless a reviewer explicitly asks for
`--include-v4-prep`.
Embedding, SDK packaging, generated bindings, device-buffer execution,
external stream ordering, zero-copy framework interop, and device-callable
fusion are not part of V3.0 release-line scope.

This is a source-tree release. Use it from a checkout with `PYTHONPATH=src:.`
or the optional local editable checkout. It is not a PyPI, wheel, stable SDK,
generated binding package, public true-zero-copy, or automatic optimizer
release.

## Why v3.0.2 Matters

v3.0.2 is the release users should start from. The original `v3.0` tag remains
the major-release point; `v3.0.1` performed the first boundary cleanup, and
`v3.0.2` hardens the default user front door. It removes the remaining
contradiction where reviewer-only V4 preparatory C ABI and embedding material
was still visible through default help, default doctor output, or the rendered
learner evidence index while the prose correctly said it was not V3.0 scope.

## Included Release Docs

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Public Wording Boundaries](public_wording_boundaries.md)
- [Publication Note](publication.md)
- [Tag Preparation](tag_preparation.md)
- [Final Closeout](final_closeout.md)
- [Major Release Requirements Trace](major_release_requirements_trace.md)

## Evidence

- [Codex V3.0 release review request](../../reviews/codex_v3_0_release_review_request_2026-06-18.md)
- [Claude V3.0 critical release review](../../reviews/claude_v3_0_release_critical_review_2026-06-18.md)
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
| Version marker | `VERSION` is `v3.0.2`; editable metadata version is `3.0.2`. |
| Front page and docs index | Current learner-facing docs identify v3.0.2 as the active source-tree release. |
| Ten-app closure | Goal4614 records all ten benchmark apps as closed current targets. |
| Claim queues | Runtime, claim/evidence, design-blocker, and future-design queues are empty. |
| Route policy | V3 app-author strategy is learner-facing and linked from the main docs path. |
| V4 scope exclusion | Embedding, C ABI, SDK packaging, generated bindings, device-buffer execution, external stream ordering, zero-copy framework interop, and device-callable fusion are excluded from V3.0 release criteria, default `make help`, default doctor output, and rendered learner evidence lists. |
| Validation | Source-tree doctor passes, `v3_current` passes, and archived `v4_prep` passes separately. |
| Boundaries | Public docs block broad speedup, paper reproduction, automatic partner selection, stable SDK, true-zero-copy, and generated binding claims. |
| Release authorization | Maintainer agreed to publish v3.0.2 on 2026-06-18 after pod validation. |

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --json
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v3_current
```

For the complete release validation used for this patch packet, see
[Final Closeout](final_closeout.md).

## Release Boundary

v3.0.2 is a source-tree patch release for the V3.0 line. It does not widen
V3.0. It does not claim broad whole-application speedups, paper reproduction,
RTDL beating specialized author code, automatic partner selection,
embedding/SDK readiness, public true-zero-copy, stable packaged SDK status,
generated binding packages, device-buffer query execution, external CUDA stream
ordering, or app-specific native-engine extension APIs.
