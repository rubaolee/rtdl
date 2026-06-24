# Goal 509: Robot and Barnes-Hut Linux Performance Check

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

This goal extends the v0.8 application performance evidence beyond the Hausdorff app by testing the other two paper-derived apps on the Linux validation host:

- `examples/rtdl_robot_collision_screening_app.py`
- `examples/rtdl_barnes_hut_force_app.py`

This is not a release authorization. It is a correctness-gated performance evidence report.

## Raw Evidence

- Full Linux raw result: `/Users/rl2025/rtdl_python_only/docs/reports/goal509_app_perf_linux_raw_2026-04-17.json`
- Linux smoke raw result: `/Users/rl2025/rtdl_python_only/docs/reports/goal509_app_perf_smoke_raw_2026-04-17.json`
- Benchmark harness: `/Users/rl2025/rtdl_python_only/scripts/goal509_app_perf_linux.py`
- Local harness tests: `/Users/rl2025/rtdl_python_only/tests/goal509_app_perf_harness_test.py`

## Host

- Host: `lx1`
- Platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- GPU: `NVIDIA GeForce GTX 1070, driver 580.126.09`
- Embree runtime: `(4, 3, 0)`
- OptiX runtime: `(9, 0, 0)`
- Vulkan runtime: `(0, 1, 0)`

Important caveat: GTX 1070 is a Pascal GPU and has no NVIDIA RT cores. OptiX and Vulkan results here are GPU/backend execution evidence, not RT-core performance evidence.

## Fairness Contract

- Robot collision screening: every backend runs the same `robot_edge_ray_hitcount_kernel` on identical edge rays and obstacle triangles. The CPU oracle is `rt.ray_triangle_hit_count_cpu`. A backend must match row count, hit rows, total hits, and colliding pose count before its timing can be accepted.
- Barnes-Hut app: every backend runs the same `barnes_hut_node_candidate_kernel` on identical bodies and one-level quadtree nodes. Candidate timing is reported separately from full-app timing.
- Barnes-Hut full-app timing includes Python opening-rule and force-reduction work. This is reported as application wall time, not as pure RTDL backend time.
- Each full benchmark entry uses deterministic data generation and three iterations; reported times are medians.

## Robot Collision Screening

Input shape: generated discrete robot poses, four edge rays per pose, 256 rectangular obstacles encoded as 512 triangles.

Correctness summary:

- CPU, Embree, and OptiX match the CPU oracle at all tested sizes.
- Vulkan does not match the CPU oracle for per-edge hit counts. It preserves `colliding_pose_count` in these cases, but `hit_rows` and `total_hits` are lower than the oracle. Therefore robot Vulkan timing is rejected as performance evidence and the public robot app CLI does not expose `vulkan`.

Accepted timing:

| Poses | Rays | Triangles | CPU median (s) | Embree median (s) | Embree speedup vs CPU | OptiX median (s) | OptiX speedup vs CPU |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 4,000 | 512 | 0.141220 | 0.004954 | 28.50x | 0.049086 | 2.88x |
| 5,000 | 20,000 | 512 | 0.706561 | 0.021715 | 32.54x | 0.242961 | 2.91x |
| 10,000 | 40,000 | 512 | 1.436576 | 0.049898 | 28.79x | 0.490786 | 2.93x |

Rejected Vulkan evidence:

| Poses | Oracle hit rows | Vulkan hit rows | Oracle total hits | Vulkan total hits | Vulkan median (s) | Verdict |
|---:|---:|---:|---:|---:|---:|---|
| 1,000 | 2,811 | 1,874 | 4,685 | 3,725 | 0.009824 | rejected: correctness mismatch |
| 5,000 | 14,061 | 9,374 | 23,435 | 18,631 | 0.023356 | rejected: correctness mismatch |
| 10,000 | 28,125 | 18,750 | 46,875 | 37,266 | 0.041718 | rejected: correctness mismatch |

Robot conclusion:

- Embree is the strongest current backend for this app on the tested Linux host.
- OptiX is correct but slower than Embree on GTX 1070 for this workload.
- Vulkan needs ray/triangle hit-count correctness work before it can be exposed as a supported robot collision backend.

## Barnes-Hut Force App

Input shape: deterministic 2D bodies, one-level quadtree nodes, RTDL candidate generation followed by Python opening-rule and force reduction.

Correctness summary:

- CPU, Embree, OptiX, and Vulkan all match the CPU candidate oracle at tested sizes.
- Full-app reductions match the CPU reference reduction for all tested backends.
- Exact O(N^2) force comparison is included for 256 bodies and skipped for 1,024 bodies to keep the performance gate bounded.

Candidate-generation timing only:

| Bodies | Candidate rows | CPU median (s) | Embree median (s) | OptiX median (s) | Vulkan median (s) |
|---:|---:|---:|---:|---:|---:|
| 256 | 1,024 | 0.001499 | 0.001492 | 0.001322 | 0.003517 |
| 1,024 | 4,096 | 0.005974 | 0.004543 | 0.003910 | 0.006440 |

Candidate-generation speedup vs CPU:

| Bodies | Embree | OptiX | Vulkan |
|---:|---:|---:|---:|
| 256 | 1.01x | 1.13x | 0.43x |
| 1,024 | 1.31x | 1.53x | 0.93x |

Full application timing:

| Bodies | CPU median (s) | Embree median (s) | OptiX median (s) | Vulkan median (s) |
|---:|---:|---:|---:|---:|
| 256 | 0.020643 | 0.020653 | 0.019922 | 0.022299 |
| 1,024 | 0.316162 | 0.314267 | 0.312323 | 0.318473 |

Barnes-Hut conclusion:

- RTDL candidate generation is correct across CPU, Embree, OptiX, and Vulkan.
- OptiX is the fastest candidate-generation backend in this bounded test.
- Full-app timing is almost flat across backends because Python force reduction dominates the app after RTDL candidate generation.
- This app demonstrates the current v0.8 model honestly: RTDL owns the spatial candidate query; Python owns application-level force math.

## Local Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal509_app_perf_harness_test tests.goal503_robot_collision_screening_app_test tests.goal504_barnes_hut_force_app_test -v
```

Result: `Ran 10 tests in 0.486s`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_robot_collision_screening_app.py examples/rtdl_barnes_hut_force_app.py scripts/goal509_app_perf_linux.py tests/goal509_app_perf_harness_test.py && git diff --check
```

Result: passed.

## Release Meaning

## Post-Goal748 Erratum

Goal748 later found and fixed a native OptiX short-ray correctness bug in the
2D ray/triangle any-hit path: the custom intersection program reported a fixed
`t=0.5`, which can drop valid short rays whose traced interval is below `0.5`.
The robot fixture contains short vertical link-edge rays, so pre-fix OptiX
robot evidence in this Goal509 report is now treated as suspect for
correctness-sensitive robot claims.

The CPU and Embree robot evidence remains usable. Post-fix OptiX robot evidence
is recorded in Goal748 and should be used instead of this report for current
OptiX robot correctness/performance discussion. GTX 1070 timing remains
whole-call OptiX traversal evidence only, not RTX RT-core speedup evidence.

Goal509 supports the following bounded claims:

- The robot collision app has repeatable Linux performance evidence for CPU and Embree, with Embree showing about 29x-33x speedup over the CPU oracle on this synthetic benchmark. The original OptiX robot evidence in this report is superseded by the Goal748 post-fix rerun.
- The robot app must not claim Vulkan support yet because the Vulkan hit-count output fails the oracle parity gate.
- The Barnes-Hut app has repeatable Linux correctness evidence for CPU, Embree, OptiX, and Vulkan.
- Barnes-Hut backend performance must be described as candidate-generation performance, not full force-solver acceleration.

Goal509 does not support these claims:

- It does not prove RTDL is faster than specialized robotics collision libraries.
- It does not prove RTDL is faster than specialized Barnes-Hut or N-body libraries.
- It does not prove RT-core acceleration, because the Linux GPU used here has no RT cores.
- It does not make Vulkan a supported robot collision backend.

## AI Review Consensus

- Claude review: `PASS`, with a minor non-blocking observation that GPU JIT warmup is visible in `max_sec` and the median-of-3 evidence should be treated as bounded internal evidence rather than publication-grade benchmarking.
- Gemini Flash review: `ACCEPT`.
- Codex conclusion: `ACCEPT`. Goal509 is fair, correctness-gated, repeatable within its stated scope, and honestly documented.
