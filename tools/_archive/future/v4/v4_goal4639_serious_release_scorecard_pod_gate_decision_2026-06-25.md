# V4 Goal4639 Serious Release Scorecard POD Gate Decision

Status: `goal4639_serious_release_scorecard_pod_gate_passed_not_release`

Decision: `accept_release_scorecard_continue_to_docs_clean_tree_and_3ai`

## Result

Goal4639 ran the frozen Goal4638 release scorecard on the RTX A5000 POD.

Scorecard recommendation:

- `release_candidate_possible_pending_3ai`

This is a serious release-scorecard pass, not final release authorization.

## Evidence

POD:

- host repo: `/root/rtdl_v4_candidate_pod`
- GPU: NVIDIA RTX A5000
- driver: `570.195.03`
- scorecard output:
  `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/`

Primary artifacts:

- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/run.log`

Code:

- `scripts/v4_goal4639_release_scorecard_pod_gate.py`
- `src/rtdsl/v4_goal4639_release_scorecard.py`
- `src/rtdsl/v4_goal4639_release_scorecard_decision.py`

Tests:

- `tests/v4_goal4639_release_scorecard_test.py`
- `tests/v4_goal4639_release_scorecard_decision_test.py`

## Scorecard Summary

| Metric | Result |
| --- | ---: |
| Strong release-in-scope families passed | `4/4` |
| Measured surfaces passed | `8/8` |
| Partial controls passed | `4/4` |
| Deferred/excluded rows recorded | `2` |
| Failed surfaces | `0` |
| Public ratio distribution | most measured operators 1.2-1.7x vs stated baselines; any-hit flags 5.671x; point-nearest and AABB are large scale-dependent algorithmic-complexity wins |
| Internal strong representative ratio geomean | `5.1848067367961095x` |

Deferred/excluded rows remain:

- `spatial_rayjoin`
- `barnes_hut`

They are explicitly excluded by the frozen Goal4638 scorecard and do not
contribute to release geomean or V4.0 coverage claims.

## Surface Results

| Surface | Status | Representative ratio | Baseline / denominator | Scale |
| --- | --- | ---: | --- | --- |
| `v4_fixed_radius_count_threshold_2d_device_arrays` | pass | `1.69721x` | Torch brute-force/reference | script default fixture; repeat=7 warmup=1 |
| `v4_closest_hit_grouped_argmin_3d_device_arrays` | pass | `1.25677x` | Torch brute-force/reference | script default grouped-argmin fixtures; repeat=7 warmup=1 |
| `v4_ray_triangle_any_hit_flags_2d_device_arrays` | pass | `5.67055x` | Torch brute-force/reference | max_torch_reference_count=8192; repeat=5 warmup=1 |
| `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | pass | `1.38362x` | Torch brute-force/reference | ray_counts=32768,131072; group_widths=1,16,256; repeat=7 warmup=2 |
| `v4_point_group_nearest_witness_2d_device_arrays` | pass | `389.707x` | Torch/CPU-style brute-force nearest-witness reference | query_counts=32768,131072; fixture_variants=mixed4,mixed6; repeat=7 warmup=2 |
| `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | pass | `1.48181x` | Torch brute-force/reference comparable route | Goal4633 shapes=32768,131072,262144,524288 |
| `v4_fixed_radius_graph_component_union_3d_device_arrays` | pass | `1.20294x` | legacy prepared-runner wall route with Embree same-contract controls | clustered3d point_count=262144; repeat=5 warmup=1 |
| `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | pass | `164.716x` | Embree same-contract prepared AABB query control | box_count=1000000; query_count=1000; operation=all; repeats=240 |

## Family Results

Strong release-in-scope rows:

- `rt_dbscan`: pass
- `raydb_style`: pass
- `triangle_counting`: pass
- `librts_spatial_index`: pass

Partial controls:

- `hausdorff_xhd`: pass as partial control only
- `robot_collision`: pass as partial control only
- `contact_manifold`: pass as partial control only
- `rtnn`: pass as partial control only

Deferred/excluded:

- `spatial_rayjoin`: no V4.0 measured generic operator surface
- `barnes_hut`: no V4.0 measured generic operator surface

## Interpretation

This is the first V4 result that clears the frozen promoted benchmark/operator
scorecard:

- all strong rows pass;
- all measured surfaces pass their frozen floors;
- no failed surface remains;
- partial and deferred rows are recorded instead of silently dropped.

The wording must remain precise:

- allowed: V4 has measured generic RT-core operator surfaces that beat stated
  brute-force partner/CPU baselines for the documented measured scopes;
- not allowed yet: V4 release, release candidate, broad V4 speedup, whole-app
  speedup, all-benchmark speedup, near-handwritten-OptiX wording, public
  true-zero-copy, CuPy performance, Tier-3 callback support, C ABI, embedding,
  non-Python host support, or app-specific native kernels.

## Next Required Goals

Goal4639 clears the performance scorecard gate. The remaining formal release
path is:

1. Goal4640: user-facing V4 docs and example cleanup.
2. Goal4641: clean-tree reproducibility gate.
3. Goal4642: final 3-AI release authorization packet.

## Goal-Level Decision Audit

1. Was this decision stupid?
   No. The scorecard was frozen and externally amended before the POD run, then
   executed on the same RT hardware class.

2. What action would have made it stupid?
   Running a weaker, post-hoc, or partially reclassified scorecard would have
   repeated the V3 failure mode. The fixed Goal4638 floor table prevented that.

3. Was there another path?
   Yes: skip the POD run and keep calling V4 a preview. That would avoid risk
   but would not answer the release question.

4. Can the path now change to solve the real problem?
   Yes. The performance gate is no longer the blocker. The path shifts to user
   docs, clean-tree reproducibility, and final 3-AI authorization.

## Non-Authorization

Goal4639 does not authorize V4 release, V4 release-candidate wording, broad V4
speedup claims, whole-app speedup claims, all-benchmark speedup claims, public
true-zero-copy claims, Tier-3 callback support, raw OptiX callback support,
CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
