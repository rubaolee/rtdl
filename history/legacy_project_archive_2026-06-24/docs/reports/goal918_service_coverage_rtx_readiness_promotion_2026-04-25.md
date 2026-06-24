# Goal918 Service Coverage RTX Readiness Promotion

Date: 2026-04-25

## Purpose

Goal917 accepted the existing 2026-04-25 RTX artifact intake. This goal acts on
the service-coverage part only. It promotes the bounded
`service_coverage_gaps` prepared gap-summary path into `ready_for_rtx_claim_review`
and `rt_core_ready`, while keeping event hotspot and road hazard held.

## Promoted Path

App: `service_coverage_gaps`

Promoted path: `--backend optix --optix-summary-mode gap_summary_prepared`

Claim scope: prepared OptiX fixed-radius threshold traversal for compact
coverage-gap summaries.

Non-claims:

- not nearest-clinic row output,
- not full service-coverage optimization,
- not a broad whole-app speedup claim,
- not authorization for public marketing claims without final claim-review
  packaging.

## Evidence

Goal917 verified:

- RTX artifact exists:
  `docs/reports/cloud_2026_04_25/goal811_service_coverage_rtx.json.gz`
- Raw artifact hash is recorded in:
  `docs/reports/cloud_2026_04_25/goal917_intake_raw_artifact_sha256.txt`
- Artifact scale: `copies=20000`.
- Artifact phases:
  `optix_prepare=6.518379669636488s`,
  `optix_query=0.6260500205680728s`,
  `python_postprocess=0.03535711392760277s`.
- CPU and Embree same-scale local baselines match the service summary digest:
  `ffcb2b43892c5efa4feb6aa157efb20e697ede986984fbf4a15ec1ad7217273d`.
- Claude and Gemini accepted the intake:
  `docs/reports/goal917_two_ai_consensus_2026-04-25.md`.

## Changes

- `src/rtdsl/app_support_matrix.py` now marks `service_coverage_gaps` as:
  `ready_for_rtx_claim_review` and `rt_core_ready`.
- `docs/app_engine_support_matrix.md` records the same public status.
- `scripts/goal759_rtx_cloud_benchmark_manifest.py` moves service coverage from
  deferred entries to active entries with Goal917 preconditions.
- Goal759, Goal848, and Goal849 generated artifacts were refreshed.
- Tests now enforce the asymmetric state:
  service coverage is ready; event hotspot remains waiting for same-scale
  baseline cleanup; road hazard remains correctness-only.

## Held Apps

`event_hotspot_screening` remains `needs_real_rtx_artifact` /
`rt_core_partial_ready` because the committed Embree baseline artifact is still
at `copies=2000` while the RTX artifact is `copies=20000`.

`road_hazard_screening` remains `needs_real_rtx_artifact` /
`rt_core_partial_ready` because its RTX artifact proves strict parity but native
OptiX was slower than CPU reference (`7.212322797626257s` vs
`2.277230924926698s`).

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal849_spatial_promotion_packet_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal687_app_engine_support_matrix_test \
  -v
```

Result: `47 tests OK`.

Compile check:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal848_v1_rt_core_goal_series.py \
  scripts/goal849_spatial_promotion_packet.py \
  src/rtdsl/app_support_matrix.py
```

Result: OK.

Whitespace audit:

```bash
git diff --check
```

Result: clean.

## Boundary

This goal promotes exactly one bounded path to claim-review readiness. It does
not authorize a public speedup claim and does not reduce the requirement for
final release-level documentation and audit.
