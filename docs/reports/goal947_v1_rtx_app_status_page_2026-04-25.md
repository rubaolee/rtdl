# Goal947 v1.0 RTX App Status Page

Date: 2026-04-25

## Verdict

ACCEPT locally, pending independent peer review.

Goal947 creates one public, release-facing source of truth for v1.0 NVIDIA RTX app status:

- `docs/v1_0_rtx_app_status.md`
- `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`
- `scripts/goal947_v1_rtx_app_status_page.py`
- `tests/goal947_v1_rtx_app_status_page_test.py`

The page is generated from live `rtdsl` matrices rather than hand-maintained prose.

## What The Page Answers

For every public app, the page records:

- app file
- readiness and RT-core maturity status
- bounded RT-core subpath
- claim-sensitive command or profiler command
- evidence/goals
- explicit non-claim boundary
- cloud action

Current summary:

```text
public app rows: 18
NVIDIA-target rows ready for claim review: 16
non-NVIDIA target rows: 2
public speedup claim authorized: False
```

This is intentionally narrower than saying “all apps are accelerated.” It says the 16 NVIDIA-target apps have bounded RT-core-backed subpaths ready for claim review, and it keeps Apple RT / HIPRT app rows outside NVIDIA RTX batches.

## Public Doc Integration

Updated:

- `README.md`
- `docs/README.md`
- `docs/v1_0_rtx_app_status.md`

`README.md` now points readers to `docs/v1_0_rtx_app_status.md` for the current app-level RTX boundary. `docs/README.md` adds the new page to the new-user path and live-doc list.

## Command Audit Integration

Updated:

- `scripts/goal515_public_command_truth_audit.py`
- `docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

The new public page is included in the command truth audit.

Current command audit:

```text
valid: true
public_doc_count: 15
command_count: 296
```

## Verification

Focused Goal947 gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test -v

Ran 23 tests
OK
```

Broader release/RT-core gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
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

Ran 96 tests in 3.767s
OK
```

`git diff --check` passed.

## Boundary

Goal947 does not run cloud resources, does not add new RTX performance evidence, and does not authorize public speedup claims.

Allowed wording remains bounded:

```text
RTDL includes a bounded NVIDIA OptiX/RTX-backed subpath for <app>: <allowed claim>.
```

Forbidden wording remains:

- RTDL accelerates the whole app
- RTDL beats CPU, Embree, PostGIS, or another baseline without a later same-semantics review
- all graph/database/spatial work is RT-core accelerated
- `--backend optix` alone means RT cores were used

## Next Step

After peer review, Goal948 should produce the cloud-ready execution packet. It should use the Goal947 page as the public status source and preserve the no per-app pod restart policy.
