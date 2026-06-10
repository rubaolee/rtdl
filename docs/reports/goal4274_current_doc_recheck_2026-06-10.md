# Goal4274 Current Documentation Recheck

Status: local documentation correctness pass for the current v2.10 source-tree
surface.

## Scope

This pass audits current learner/user docs, examples docs, API/reference docs,
architecture docs, feature docs, and current research-facing docs. Historical
evidence lanes remain intentionally historical and are not rewritten:

- `docs/history/`
- `docs/reports/`
- `docs/reviews/`
- `docs/handoff/`
- `docs/release_reports/`
- `docs/audit/`
- `docs/directives/`
- `docs/engineering/`
- `docs/research/archive/`
- `examples/generated/`
- `examples/internal/`
- `examples/legacy_or_backend_proofs/`
- `examples/reference/`

## Results

| Check | Result |
| --- | --- |
| Current public Markdown files scanned | 98 |
| Broken local Markdown links | 0 |
| Stale current-surface wording hits | 0 |
| Generated primitive catalog drift | 0 |
| Tutorial/example readiness tests | pass |

Blocked wording scanned in current public docs:

```text
examples/v2_0
examples\v2_0
examples.v2_0
PyTorch
Triton-first
true-zero
true zero
current released
pre-release
pre release
```

## Corrections Made

| Area | Issue found | Action |
| --- | --- | --- |
| Capability and architecture docs | Older "current released source-tree" wording could read like release-history language rather than the current user surface. | Reworded to "current source-tree Python+partner+RTDL surface." |
| Prepared execution and discovery docs | Several blocked-claim bullets still used older `true-zero-copy` wording. | Normalized to `general zero-copy or device-residency` wording. |
| Future to-do list | Future guardrail text used older `true-zero-copy` phrasing. | Normalized the guardrail while preserving the future/debt meaning. |
| RTNN benchmark README | Teaching path still used old zero-copy phrase. | Reworded the boundary to zero-copy/device-residency. |
| Examples front door | Current examples README still mentioned PyTorch in a blocked arbitrary-partner sentence. | Removed PyTorch from current user-facing partner wording; kept NumPy/CuPy/Numba/user-extension framing. |
| Primitive catalog | Generated catalog inherited old zero-copy wording from source metadata. | Updated source metadata and regenerated `docs/rtdl_primitive_catalog.md`. |
| Documentation tests | Older tests still referenced `examples/v2_0` and hard-coded an old audit count. | Updated the tests to current `examples/current` paths and dynamic current-doc link coverage. |

## Validation Commands

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal4248_current_public_docs_claim_boundary_scan_test tests.goal4271_v2_10_user_doc_cleanup_test tests.goal4272_current_examples_canonical_path_test tests.goal4273_current_tutorial_ladder_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3084_v2_7_primitive_discovery_workflow_docs_test tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test tests.goal3090_v2_7_discovery_metadata_backfill_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal513_public_example_smoke_test tests.goal514_tutorial_example_harness_refresh_test tests.goal1765_github_learner_readiness_double_check_test
```

All three validation bundles passed.

## Boundary

This recheck does not run pod/native hardware validation and does not authorize
new performance, package-install, zero-copy/device-residency, automatic-partner,
or broad RT-core claims. It is a documentation correctness and navigation pass
for the current v2.10 source-tree docs.
