# Goal754 OptiX Robot Pose-Flags Performance Report

## Verdict

ACCEPT.

Goal754 extends the robot-collision scaled performance harness with `optix_prepared_pose_flags`, validates the new native pose-level summary path against CPU oracle pose flags, and records Linux OptiX performance evidence at two deterministic scales.

## Consensus

- Codex implementation and validation: ACCEPT.
- Gemini Flash plan review: ACCEPT, no blockers.
- Windows Codex plan review: ACCEPT_WITH_NOTES, no blockers. Its notes were applied: exact pose-flag validation, separate `pose_index_construction_sec`, and explicit GTX 1070 honesty boundary.

## Implementation

- Updated harness: `/Users/rl2025/rtdl_python_only/scripts/goal748_optix_robot_scaled_perf.py`
- Updated regression tests: `/Users/rl2025/rtdl_python_only/tests/goal748_optix_robot_scaled_perf_test.py`
- Correctness JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal754_optix_robot_pose_flags_linux_gtx1070_2026-04-21.json`
- Large no-oracle JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal754_optix_robot_pose_flags_linux_gtx1070_large_no_oracle_2026-04-21.json`

The new mode builds a dense pose-index vector from deterministic ray metadata, prepares OptiX rays and triangles once, then calls `PreparedOptixRayTriangleAnyHit2D.pose_flags_packed(...)` to return one native collision flag per pose. It does not emit per-edge witnesses or hit-ray IDs.

## Linux Environment

- Host: `lestat-lx1`
- Scratch checkout: `/tmp/rtdl_goal754_pose_perf`
- Native library: `/tmp/rtdl_goal754_pose_perf/build/librtdl_optix.so`
- GPU boundary: GTX 1070 has no NVIDIA RT cores. These results validate native OptiX traversal correctness and whole-call behavior only. They are not RTX RT-core speedup evidence.

## Correctness-Gated Run

Command shape:

```bash
python3 scripts/goal748_optix_robot_scaled_perf.py --backend embree_rows --backend optix_rows --backend optix_prepared_count --backend optix_prepared_pose_flags --pose-count 2000 --obstacle-count 1000 --repeats 5 --warmups 1 --strict --output-json docs/reports/goal754_optix_robot_pose_flags_linux_gtx1070_2026-04-21.json
```

Fixture: 2,000 poses, 1,000 obstacles, 8,000 rays, 2,000 obstacle triangles.

| Backend | Output shape | Median execute time | Prep scene | Prep rays | Pose-index prep | Result | Oracle check |
|---|---:|---:|---:|---:|---:|---:|---|
| `embree_rows` | 8,000 dict rows | 0.006464s | n/a | n/a | n/a | 5,742 hit edges | hit count matches |
| `optix_rows` | 8,000 dict rows | 0.005105s | n/a | n/a | n/a | 5,742 hit edges | hit count matches |
| `optix_prepared_count` | scalar count | 0.000066s | 0.133353s | 0.007982s | n/a | 5,742 hit edges | hit count matches |
| `optix_prepared_pose_flags` | 2,000 pose flags | 0.002172s | 0.002753s | 0.015856s | 0.002006s | 1,914 colliding poses | exact pose flags match |

The pose-flag path is 2.98x faster than `embree_rows` execute timing and 2.35x faster than `optix_rows` execute timing for the app-level question "which poses collide?" It is slower than scalar `prepared_count`, as expected, because it returns one flag per pose rather than a single scalar.

## Large No-Oracle Run

Command shape:

```bash
python3 scripts/goal748_optix_robot_scaled_perf.py --backend embree_rows --backend optix_rows --backend optix_prepared_count --backend optix_prepared_pose_flags --pose-count 20000 --obstacle-count 10000 --repeats 5 --warmups 1 --no-validate --strict --output-json docs/reports/goal754_optix_robot_pose_flags_linux_gtx1070_large_no_oracle_2026-04-21.json
```

Fixture: 20,000 poses, 10,000 obstacles, 80,000 rays, 20,000 obstacle triangles.

| Backend | Output shape | Median execute time | Prep scene | Prep rays | Pose-index prep | Result |
|---|---:|---:|---:|---:|---:|---:|
| `embree_rows` | 80,000 dict rows | 0.066862s | n/a | n/a | n/a | 59,400 hit edges |
| `optix_rows` | 80,000 dict rows | 0.050858s | n/a | n/a | n/a | 59,400 hit edges |
| `optix_prepared_count` | scalar count | 0.000235s | 0.149139s | 0.113559s | n/a | 59,400 hit edges |
| `optix_prepared_pose_flags` | 20,000 pose flags | 0.020945s | 0.024317s | 0.111123s | 0.024494s | 19,800 colliding poses |

The large run is no-oracle by design, so it is performance evidence, not independent correctness evidence. It preserves internal consistency: row backends and scalar count agree on 59,400 hit edges, while pose flags answer the different app-level question and report 19,800 colliding poses.

## Interpretation

The main result is not "OptiX beats everything." The important result is that the app gets faster when RTDL exposes the correct native summary shape:

- Row outputs are useful for debugging and witness inspection, but they pay Python dictionary materialization cost.
- `prepared_count` is the fastest path when the app only needs a scalar hit-edge count.
- `prepared_pose_flags` is the correct path when the app needs one collision decision per robot pose.
- Preparation timing remains material for one-shot calls. Prepared paths are most valuable when the scene/rays are reused across repeated queries.

## Verification

- macOS focused tests: `tests.goal748_optix_robot_scaled_perf_test`, `tests.goal671_optix_prepared_anyhit_count_test`, and `tests.goal701_robot_collision_compact_output_test`: 21 tests OK, 4 skipped.
- Linux native OptiX focused tests on `lestat-lx1`: same test set, 21 tests OK.
- `python3 -m py_compile scripts/goal748_optix_robot_scaled_perf.py tests/goal748_optix_robot_scaled_perf_test.py`: OK.
- `git diff --check`: OK.

## Remaining Work

Run the same harness on RTX-class hardware before making any RT-core speedup claim. The GTX 1070 evidence is still useful because it proves native OptiX traversal and app-summary behavior, but it cannot answer the NVIDIA RT-core performance question.
