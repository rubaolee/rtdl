# Goal2060 v2 Pod Mixed-Family Audit

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2060 uses the active NVIDIA L4 pod for a wider v2.0 audit after the segment/polygon hitcount and former-control-app follow-ups. The intent is to collect both positive and negative evidence across several v2 partner families:

- fixed-radius threshold family;
- robot collision screening;
- road hazard priority flags.

This is not a release gate. It is a mixed-result engineering audit to show where v2.0 is already strong and where the design still needs work.

## Pod

- Host: `66.92.198.234`
- SSH port: `11830`
- GPU: NVIDIA L4
- Driver: `570.195.03`
- CUDA: `/usr/local/cuda-12`, CUDA 12.8
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Python environment: `/root/rtdl_goal2046_venv`
- OptiX library: `/root/rtdl_goal2048_9b95e5f2/build/librtdl_optix.so`

## Fixed-Radius Family, 8192 x 8192

Artifact:

- `docs/reports/goal2060_fixed_radius_family_cupy_l4_8192.json`

Command shape:

```bash
timeout 1200 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1925_fixed_radius_family_v2_partner_perf.py \
  --partners cupy \
  --repeat 3 \
  --query-count-override 8192 \
  --search-count-override 8192 \
  --source-commit-label 05fbfccb-pod-fixed-radius-8192
```

Result:

| App | Status | v2/v1.8 prepared ratio |
| --- | --- | ---: |
| facility_knn_assignment | pass | 0.016x |
| hausdorff_distance forward | pass | 0.016x |
| hausdorff_distance reverse | pass | 0.016x |
| ann_candidate_search | pass | 0.015x |
| outlier_detection | pass | 0.015x |
| dbscan_clustering | pass | 0.016x |
| barnes_hut_force_app | pass | 0.015x |

Interpretation:

- The fixed-radius threshold family is very strong for v2.0.
- These are threshold/summary proxy rows, not full exact richer semantics such as exact KNN ranking, full DBSCAN cluster expansion, exact Hausdorff witness extraction, or Barnes-Hut force vectors.

## Robot Collision, 8192 Poses x 8192 Obstacles

Artifact:

- `docs/reports/goal2060_robot_collision_cupy_l4_8192.json`

Command shape:

```bash
timeout 900 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1928_robot_collision_v2_partner_perf.py \
  --pose-count 8192 \
  --obstacle-count 8192 \
  --partners cupy \
  --repeat 3 \
  --source-commit-label 05fbfccb-pod-robot-8192
```

Result:

| App | Status | v1.8 prepared median | v2 prepared median | v2/v1.8 prepared ratio |
| --- | --- | ---: | ---: | ---: |
| robot_collision_screening | pass | 0.000902 | 0.001188 | 1.317x |

Interpretation:

- Correctness parity passes.
- The artifact records true zero-copy metadata for ray columns, triangle scene, and output flags.
- v2 is slower than the v1.8 prepared OptiX pose-flag path at this size. This means the zero-copy partner contract is correct, but the current v2 adapter overhead still needs optimization before this row can be called a speedup.

## Road Hazard, 1024 Roads x 1536 Hazards

Artifact:

- `docs/reports/goal2060_road_hazard_cupy_l4_1024.json`

Command shape:

```bash
timeout 900 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 1024 \
  --iterations 3 \
  --partners cupy
```

Result:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX rows | 2.110957 | 1.000x |
| v1.8 prepared native OptiX rows | 0.002086 | 1.000x |
| v2 unprepared partner priority flags | 0.003913 | 1.876x vs prepared |
| v2 prepared partner priority flags | 0.002267 | 1.087x vs prepared |

Interpretation:

- Correctness parity passes.
- v2 prepared is about 931x faster than v1.8 one-shot, but about 8.7% slower than v1.8 prepared.
- The metadata records a useful whole-app true-zero-copy path, but v2 still needs adapter overhead work to beat the best prepared-native path at this size.

## Negative Finding: Road 8192

An attempted road-hazard run at `count=8192` entered:

```text
[timing] v1_8_one_shot_native_optix_road_hazard_rows iterations=3
```

with:

```text
output_capacity=100663296
```

and was stopped because it was consuming pod time in the one-shot baseline. This indicates the road-hazard runner needs the same kind of large-run prepared-only mode added in Goal2054 before it is useful for larger same-contract scaling evidence.

## What This Tells Us

v2.0 is strongest when:

- the native engine emits compact generic signals;
- the partner continuation stays GPU-resident;
- prepared scenes and output columns are reused;
- the app asks for threshold/summary outputs rather than full row materialization.

v2.0 still needs work when:

- the v2 adapter introduces overhead around an already extremely optimized prepared-native path;
- the benchmark runner forces expensive one-shot baselines at large sizes;
- the app requires richer exact continuation semantics that are not yet reusable primitives.

## Boundary

Allowed claim:

- Fixed-radius threshold/summary v2 rows are strongly faster than v1.8 prepared rows at 8192 x 8192 on L4.
- Robot collision and road hazard pass parity and exercise zero-copy metadata paths, but are not yet speedup wins against their best prepared-native rows.
- Road hazard needs a prepared-only large-run mode before large same-contract scaling can be measured efficiently.

Not allowed:

- v2.0 release readiness;
- broad all-app speedup;
- broad RT-core speedup;
- full exact KNN/DBSCAN/Hausdorff/Barnes-Hut semantics;
- robot collision speedup;
- road hazard prepared-path speedup;
- package-install readiness.

## Verdict

`accept-with-boundary`
