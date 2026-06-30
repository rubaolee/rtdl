# Goal946 Release-State Consolidation Audit

Date: 2026-04-25

## Verdict

ACCEPT locally, pending independent peer review.

Goal946 audited the current v1.0 RT-core readiness worktree after Goal945. The goal was not to add a feature or produce new RTX evidence. It checked whether the public docs, generated readiness state, command audit, and focused release gates agree with the current Goal941/Goal942/Goal945 state.

## Current Source-of-Truth State

Current NVIDIA RT-core app board:

```text
readiness Counter({'ready_for_rtx_claim_review': 16, 'exclude_from_rtx_app_benchmark': 2})
maturity Counter({'rt_core_ready': 16, 'not_nvidia_rt_core_target': 2})
```

Interpretation:

- 16 public NVIDIA-target apps have bounded RT-core-backed subpaths ready to enter claim review.
- 2 engine-specific apps are intentionally out of the NVIDIA RTX benchmark target: Apple RT demo and HIPRT ray/triangle hitcount.
- No public speedup claim is authorized by this state.

## Corrective Patch

One stale generated-packet contradiction was found and fixed:

- `scripts/goal849_spatial_promotion_packet.py`
- `tests/goal849_spatial_promotion_packet_test.py`
- regenerated `docs/reports/goal849_spatial_promotion_packet_2026-04-23.json`
- regenerated `docs/reports/goal849_spatial_promotion_packet_2026-04-23.md`

Problem:

The packet listed both `service_coverage_gaps` and `event_hotspot_screening` as `ready_for_rtx_claim_review` and `rt_core_ready`, but the packet-level flag `ready_for_rtx_claim_review_now` was still hardcoded to `false`.

Fix:

The packet now derives `ready_for_rtx_claim_review_now` from the per-app readiness/maturity rows. It is `true` only when all tracked spatial apps are `ready_for_rtx_claim_review` and `rt_core_ready`.

Verification:

```text
PYTHONPATH=src:. python3 scripts/goal849_spatial_promotion_packet.py
PYTHONPATH=src:. python3 -m unittest tests.goal849_spatial_promotion_packet_test -v
Ran 3 tests
OK
```

## Focused Release Gate

Focused public-doc, readiness, runbook, and claim-boundary gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal515_public_command_truth_audit_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal815_db_rt_core_claim_gate_test \
  tests.goal816_polygon_overlap_rt_core_boundary_test \
  tests.goal817_cuda_through_optix_claim_gate_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal846_active_rtx_claim_gate_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal849_spatial_promotion_packet_test \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal862_spatial_rtx_collection_packet_test \
  tests.goal878_segment_polygon_native_pair_rows_app_surface_test \
  tests.goal937_ready_rtx_claim_review_packet_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal939_current_rtx_claim_review_package_test -v

Ran 92 tests in 9.449s
OK
```

Public command truth audit:

```text
valid: true
command_count: 280
coverage_counts:
  goal410_harness_exact: 226
  goal410_harness_family: 18
  goal513_front_page_smoke_exact: 6
  goal593_public_example_smoke_exact: 4
  goal821_require_rt_core_doc_gate_exact: 5
  goal878_optix_doc_gate_exact: 8
  goal878_optix_doc_gate_family: 4
  goal942_claim_review_command_exact: 8
  postgresql_validation_command: 1
```

`git diff --check` passed.

## Active-Package Caveat

`scripts/goal847_active_rtx_claim_review_package.py` is now a legacy active-package view over the older mandatory baseline set:

```text
row_count: 5
missing_cloud_row_count: 3
source_goal846_status: ok
source_goal762_status: ok
```

This is not a blocker for Goal946 because the current source of truth is Goal939/current readiness plus the app support matrices. The Goal847 script already records missing cloud rows instead of crashing. It should not be treated as the authoritative v1.0 all-app claim-review index.

Recommended follow-up:

- Goal947 should publish one current public app status page/table sourced from Goal939 and `rtdsl.app_support_matrix`, so older partial package names do not confuse users or reviewers.

## Cloud Policy

No cloud run was started.

The current policy remains:

- do not rent or keep a paid pod for one-off app checks
- run bootstrap first
- then run OOM-safe groups A-H
- copy artifacts after every group
- use current Goal941/Goal942/Goal945 state as local preflight evidence

## Boundary

Goal946 does not authorize public RTX speedup claims. It only audits consistency and fixes one stale packet flag.

Public wording must continue to say that each app has a bounded RT-core-backed subpath ready for claim review, not that RTDL accelerates the entire app or beats CPU/Embree/PostGIS.
