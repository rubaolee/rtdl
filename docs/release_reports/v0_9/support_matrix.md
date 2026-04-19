# RTDL v0.9 Support Matrix

Date: 2026-04-18

Status: `v0.9.1` released

## Scope

The v0.9.0 goal is to bring HIPRT to parity with the already-supported
RTDL workload families where the current language/runtime surface can express
the workload, and to close the RTXRMQ paper workload gap that required a
closest-hit ray/triangle primitive.

The current accepted matrix evidence is:

- 18 workloads tested through `run_hiprt`
- 72 backend/workload parity checks across HIPRT, Embree, OptiX, and Vulkan
- 0 backend unavailable results
- 0 failures
- exact row parity against `cpu_python_reference`

Canonical evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_v0_9_pre_release_test_gate_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_correctness_matrix_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal563_v0_9_documentation_audit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal564_v0_9_release_candidate_flow_audit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal564_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal564_gemini_flash_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal565_hiprt_prepared_ray_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal565_hiprt_prepared_ray_perf_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_hiprt_prepared_nn_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_hiprt_prepared_nn_perf_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_hiprt_prepared_graph_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_hiprt_prepared_graph_perf_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal569_v0_9_post_goal568_release_gate_refresh_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal570_v0_9_final_pre_release_test_doc_audit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal570_hiprt_correctness_matrix_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal570_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal571_rtxrmq_paper_workload_engine_compare_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal572_v0_9_post_rtxrmq_release_addendum_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_feature_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal574_v0_9_post_closest_hit_release_addendum_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal575_v0_9_final_release_gate_after_closest_hit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal575_codex_final_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal575_gemini_flash_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal576_v0_9_archive_link_audit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal576_codex_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal576_gemini_flash_review_2026-04-18.md`

## Backend Status

| Backend | v0.9 role |
| --- | --- |
| `cpu_python_reference` | exact truth path for matrix parity |
| Embree | existing CPU RT backend comparison target |
| OptiX | existing NVIDIA RT backend comparison target |
| Vulkan | existing portable GPU backend comparison target |
| HIPRT | released backend via HIPRT/Orochi CUDA mode on Linux |
| Apple RT | released v0.9.1 backend slice via Apple Metal/MPS on macOS Apple Silicon |

## HIPRT Workload Matrix

The accepted Goal 560 matrix covers:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- `ray_triangle_hit_count_2d`
- `ray_triangle_hit_count_3d`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`
- `fixed_radius_neighbors_2d`
- `fixed_radius_neighbors_3d`
- `bounded_knn_rows_3d`
- `knn_rows_2d`
- `knn_rows_3d`
- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Closest-Hit / RTXRMQ Matrix

Goal 573 adds the first exact bounded RTXRMQ-style workload from
`/Users/rl2025/Downloads/2306.03282v1.pdf`.

| Primitive / workload | CPU Python reference | `run_cpu` | Embree | OptiX | Vulkan | HIPRT |
| --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_closest_hit` 3D | supported | supported | supported | future work | future work | future work |
| exact bounded RTXRMQ-style RMQ | supported | supported | supported | future work | future work | future work |

Linux Goal 573 evidence:

- values: `4096`
- query rays: `2048`
- triangles: `8192`
- max query range: `128`
- CPU Python reference median: `11.408521s`
- Embree median: `0.027440s`
- exact RMQ parity: yes for both measured backends

This closes the missing language/runtime primitive for CPU reference, `run_cpu`,
and Embree. It does not claim OptiX, Vulkan, or HIPRT native closest-hit
support.

## Apple RT / v0.9.1 Matrix

Goal 578 adds the first Apple RT backend slice in `v0.9.1`.

| Primitive / workload | CPU Python reference | `run_cpu` | Embree | Apple RT | OptiX | Vulkan | HIPRT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_closest_hit` 3D | supported | supported | supported | supported | future work | future work | future work |

Local Apple M4 evidence:

- build command: `make build-apple-rt`
- focused command: `PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v`
- result: `Ran 4 tests ... OK`
- backend path: `/Users/rl2025/rtdl_python_only/build/librtdl_apple_rt.dylib`
- implementation report: `/Users/rl2025/rtdl_python_only/docs/reports/goal578_v0_9_1_apple_rt_backend_bringup_2026-04-18.md`
- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal578_gemini_flash_review_2026-04-18.md`
- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal578_claude_review_2026-04-18.md`

Boundary:

- Apple RT currently means the macOS Metal/MPS `MPSRayIntersector` path.
- `run_apple_rt` currently supports only 3D `ray_triangle_closest_hit`.
- No full Apple backend parity, performance-leading claim, or measured Apple
  hardware RT-core speedup is claimed yet.

## Prepared API Status

`run_hiprt` is the broad v0.9.0 dispatch surface.

`prepare_hiprt` is narrower than `run_hiprt`: it currently covers prepared 3D
`ray_triangle_hit_count` reuse, prepared 3D `fixed_radius_neighbors` reuse, and
prepared graph CSR reuse for `bfs_discover` and `triangle_match`, plus prepared
bounded DB table reuse for `conjunctive_scan`, `grouped_count`, and
`grouped_sum`.

## Platform Boundary

Validated path:

- Linux host `lx1`
- NVIDIA GeForce GTX 1070
- NVIDIA driver `580.126.09`
- HIPRT SDK `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- HIPRT/Orochi CUDA mode

Explicit non-claims:

- no AMD GPU validation yet
- no HIPRT CPU fallback
- no RT-core speedup claim from the tested GTX 1070 path
- no OptiX, Vulkan, or HIPRT support yet for `ray_triangle_closest_hit`

## Performance Boundary

Goal 560 timing is a one-repeat small-fixture smoke comparison. It includes
backend startup, JIT/module setup, geometry build, and dispatch overhead.

It is valid for release-smoke availability and parity timing. It is not a
throughput benchmark and must not be used as a speedup claim.

The current HIPRT timings are correct but not performance-leading. The next
performance goal is prepared context reuse and larger repeatable throughput
tests after setup cost is amortized.

Goal 565 adds the first post-matrix performance mitigation result: on a 1024-ray
/ 2048-triangle 3D ray/triangle fixture, one-shot HIPRT took `0.5655s`, while
the prepared HIPRT query median was `0.00206s` after a `0.5238s` prepare phase.
That supports prepared HIPRT as the recommended path for repeated-query 3D
ray/triangle applications, but it does not imply broad prepared support for all
18 v0.9 workloads.

Goal 566 extends the mitigation to 3D fixed-radius nearest-neighbor search: on a
1024-query / 4096-search fixture, one-shot HIPRT took `0.5981s`, while the
prepared HIPRT query median was `0.00353s` after a `0.5481s` prepare phase.
That supports prepared HIPRT as the recommended path for repeated-query 3D
point-neighbor applications, but it does not yet cover 2D neighbors or KNN rank
helpers.

Goal 567 extends prepared reuse to graph CSR build data. On a 512-vertex /
4096-edge fixture, deterministic BFS one-shot HIPRT took `0.6699s`, while the
prepared HIPRT query median was `0.02046s` after a `0.7238s` prepare phase.
Triangle-match one-shot HIPRT took `0.5744s`, while the prepared HIPRT query
median was `0.00220s`. BFS remains serialized for deterministic global dedupe;
triangle-match now uses one GPU thread per seed. This is a repeated-query HIPRT
setup-mitigation result, not a claim that HIPRT graph is performance-leading on
this fixture.

Goal 568 extends prepared reuse to bounded DB table data. On a 100k-row Linux
fixture, HIPRT prepared query medians were `0.00184s` for `conjunctive_scan`,
`0.00229s` for `grouped_count`, and `0.00244s` for `grouped_sum`, after roughly
`1.79s` to `1.83s` of HIPRT prepare time. The same run included indexed
PostgreSQL query medians of `0.00327s`, `0.01059s`, and `0.01118s`, with
PostgreSQL setup/index phases of roughly `5.1s` to `5.7s`. This is a bounded
repeated-query RTDL DB-kernel result, not a general DBMS or arbitrary-SQL claim.
