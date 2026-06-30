# Goal1925 - Fixed-Radius Family v2 Partner Perf Harness

Status: harness-ready-pod-needed

Date: 2026-05-13

## Purpose

Goal1924 identified six missing all-app v2 rows that can be implemented as one
fixed-radius decision/scalar-summary family:

- `facility_knn_assignment`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `barnes_hut_force_app`

Goal1925 adds a reusable OptiX v2 partner harness for those rows. It compares
each app-shaped Python result against the v1.8 prepared OptiX fixed-radius
contract while keeping the native engine generic.

## Harness

The runner is:

`scripts/goal1925_fixed_radius_family_v2_partner_perf.py`

It measures:

- v1.8 prepared OptiX host-row baseline through
  `prepare_optix_fixed_radius_count_threshold_2d`;
- v2 prepared OptiX partner-owned input/output columns through
  `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene`,
  `allocate_fixed_radius_count_threshold_2d_partner_device_output_columns`, and
  `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`;
- Torch and CuPy partner paths, selected with `--partners`;
- per-iteration progress lines so pod runs do not go silent.

The harness normalizes the native fixed-radius count/threshold primitive into
the app rows as Python-side result contracts:

| App row | v2 result contract |
| --- | --- |
| `facility_knn_assignment` | coverage-threshold decision |
| `hausdorff_distance` | bidirectional threshold decision over distinct query/search sets |
| `ann_candidate_search` | candidate-coverage threshold decision |
| `outlier_detection` | scalar outlier count |
| `dbscan_clustering` | scalar core count |
| `barnes_hut_force_app` | node-coverage threshold decision |

This is deliberately narrower than rewriting each app from scratch. The RTDL
primitive stays generic, and the app meaning lives in Python orchestration.

The Hausdorff threshold scenario intentionally uses a sparser, y-offset search
set so the bidirectional decision is not the degenerate identical-point-set
case. Some forward query points reach the radius threshold and some do not;
the reverse direction is checked separately.

## Claim Boundary

This goal does not authorize a v2.0 release.

It does not claim true zero-copy for this family. The fixed-radius prepared
partner path uses partner-owned input/output columns and reusable output buffers,
but the existing post-pod evidence did not approve the stronger true-zero-copy
wording for fixed-radius rows.

It does not claim whole-app speedup. It times the shared fixed-radius app
subpath under same-contract result normalization. Whole-app claims require the
final all-app report and external review.

## Pod Command

The pod command is:

Use a real RTX pod or equivalent NVIDIA host with OptiX built:

```bash
PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py \
  --apps facility_knn_assignment,hausdorff_distance,ann_candidate_search,outlier_detection,dbscan_clustering,barnes_hut_force_app \
  --partners cupy,torch \
  --repeat 5 \
  --output docs/reports/goal1925_fixed_radius_family_v2_partner_perf_pod.json
```

Expected output:

- JSON artifact with source commit, GPU string, all app rows, per-partner
  timings, parity flags, and claim boundary flags;
- regular `[goal1925]` progress lines during execution;
- `status: pass` only when every v1.8/v2 parity check passes.

## Current State

Family A is now harness-ready, but not pod-measured. The next all-app work
should either run this on the next pod or continue locally with Family B
(`robot_collision_screening` plus `segment_polygon_anyhit_rows`) while waiting
for hardware.
