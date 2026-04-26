# Goal964 Generated Spatial Gate Resync

Date: 2026-04-26

## Scope

Resynchronize generated RTX/status artifacts after the Goal963 local audit and
verify that older spatial gate packets no longer understate the current
post-Goal917/918/919/941 readiness state.

This is local-only maintenance. It does not start cloud resources, authorize a
release, or authorize new public speedup claims.

## Problem Found

Regenerating the public RTX/status packets exposed a stale spatial gate path:

- `scripts/goal860_spatial_partial_ready_gate.py` still classified the
  `event_hotspot_screening` Embree required baseline as invalid.
- The old Goal835 Embree artifact for that app used `copies=2000`.
- Goal919 intentionally added the accepted same-scale replacement artifact at
  `docs/reports/goal919_event_hotspot_same_scale_embree_baseline_2026-04-25.json`
  using `copies=20000`, without mutating the older Goal835 file.
- Goal860/862 did not know about that Goal919 replacement, so regenerated
  packets could regress to `needs_required_baselines` even though later
  consensus had already promoted the bounded prepared count-summary path.

There was also a validator strictness issue:

- Goal835 plan scale may specify only required keys, for example
  `{"copies": 20000}`.
- Baseline artifacts may include additional audit keys, for example
  `{"copies": 20000, "iterations": 3}`.
- Exact dictionary equality incorrectly rejected those valid artifacts.

## Changes

- `scripts/goal836_rtx_baseline_readiness_gate.py`
  - `benchmark_scale` validation now accepts artifact scale dictionaries that
    contain all expected plan keys with matching values, even if they include
    extra audit dimensions such as `iterations`.
- `scripts/goal860_spatial_partial_ready_gate.py`
  - adds a narrow baseline artifact override for
    `event_hotspot_screening / prepared_count_summary / embree_summary_path`
    pointing to the Goal919 same-scale Embree baseline.
- `tests/goal860_spatial_partial_ready_gate_test.py`
  - now asserts the current spatial gate state is `ready_for_review`, with
    four valid required artifacts and valid RTX artifacts.
- `tests/goal862_spatial_rtx_collection_packet_test.py`
  - now asserts Goal862 carries valid required baselines rather than the stale
    invalid-baseline state.
- Regenerated generated artifacts:
  - `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
  - `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`
  - `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.json`
  - `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.md`
  - `docs/reports/goal849_spatial_promotion_packet_2026-04-23.json`
  - `docs/reports/goal849_spatial_promotion_packet_2026-04-23.md`
  - `docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.json`
  - `docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.generated.md`
  - `docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.json`
  - `docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.md`

## Current Generated State

| Artifact | Current state |
| --- | --- |
| Goal860 spatial gate | `status: ready_for_review`; `required_valid_artifact_count: 4`; `required_invalid_artifact_count: 0` |
| Goal862 spatial packet | `source_goal860_status: ready_for_review`; `row_count: 2`; required spatial baselines valid |
| Goal824 pre-cloud gate | `valid: true` |

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal860_spatial_partial_ready_gate_test \
  tests.goal862_spatial_rtx_collection_packet_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal847_active_rtx_claim_review_package_test \
  tests.goal849_spatial_promotion_packet_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal939_current_rtx_claim_review_package_test
```

Result:

```text
Ran 38 tests in 2.204s

OK
```

Additional check:

```bash
git diff --check -- \
  scripts/goal836_rtx_baseline_readiness_gate.py \
  scripts/goal860_spatial_partial_ready_gate.py \
  tests/goal860_spatial_partial_ready_gate_test.py \
  tests/goal862_spatial_rtx_collection_packet_test.py \
  docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.json \
  docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.generated.md \
  docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.json \
  docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.md
```

Result: pass.

## Claim Boundary

Allowed statement:

- The local generated spatial gate and packet now reflect the accepted same-scale
  Goal919 baseline and the current ready-for-review state.

Disallowed statement:

- Do not claim a release is authorized.
- Do not claim new public RTX speedups.
- Do not claim new cloud execution was performed by this goal.
- Do not claim the old Goal862 packet is the current active cloud execution
  packet; the accepted Goal962 packet remains the next all-group pod packet.

## Verdict

Local generated-artifact resync verdict: PASS, pending peer review.
