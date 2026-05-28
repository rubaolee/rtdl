# Goal2645 RayDB RT-Core Performance Findings

Status: internal engineering evidence; no public speedup claim authorized.

## Executive Conclusion

The RayDB rewrite now uses real RT traversal. The `paper_rt_optix` backend lowers
RayDB-style rows to `Triangle3D` primitives and predicate scans to +Z rays, then
executes the generic native symbol
`rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`.
The engine path is app-agnostic: it sees only rays, triangles, primitive group
IDs, i64 payloads, primitive-ID deduplication, and grouped reductions.

The performance conclusion is mixed:

- RT-core traversal itself is good: at 80k triangles / 12,072 rays / 180k hit
  events, native traversal is about 16 ms.
- App-level timing is not good yet: the current Python lowering path spends
  about 1 second at 80k rows and 10-14 seconds at 800k rows.
- Therefore RayDB is now a real RT-core benchmark candidate, but not yet a
  performance-claim-ready benchmark. The next required work is generic prepared
  typed-buffer execution, not RayDB-specific native code.

## Provenance

Main matrix artifact:

- script: `scripts/goal2645_raydb_rt_perf_pod.py`
- JSON: `docs/reports/goal2645_raydb_rt_perf_pod_2026-05-27.json`
- Markdown: `docs/reports/goal2645_raydb_rt_perf_pod_2026-05-27.md`
- pod host: `4b7c6ab4b262`
- GPU: NVIDIA RTX A5000
- source commit label: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- source status: dirty working tree captured in artifact
- OptiX SDK: 8.1 installed at `/workspace/optix-8.1`
- native build: `make build-optix OPTIX_PREFIX=/workspace/optix-8.1`

Large OptiX-only artifact:

- JSON: `docs/reports/goal2645_raydb_rt_perf_pod_optix_100k_2026-05-27.json`
- Markdown: `docs/reports/goal2645_raydb_rt_perf_pod_optix_100k_2026-05-27.md`

CPU 100k artifact:

- JSON: `docs/reports/goal2645_raydb_cpu_100k_2026-05-27.json`
- Markdown: `docs/reports/goal2645_raydb_cpu_100k_2026-05-27.md`

## Key Results

All rows matched the CPU oracle.

| workload | backend | app median s | native prepare s | native pack s | native traversal s | RT core |
|---|---|---:|---:|---:|---:|---|
| 80k rows, count | paper_rt_optix | 1.128 | 0.0045 | 0.0057 | 0.0195 | yes |
| 80k rows, sum | paper_rt_optix | 1.159 | 0.0053 | 0.0616 | 0.0159 | yes |
| 80k rows, min | paper_rt_optix | 0.981 | 0.0049 | 0.0205 | 0.0158 | yes |
| 80k rows, max | paper_rt_optix | 1.008 | 0.0047 | 0.0204 | 0.0158 | yes |
| 80k rows, avg_as_sum_count | paper_rt_optix | 1.173 | 0.0049 | 0.0206 | 0.0162 | yes |
| 800k rows, count | paper_rt_optix | 14.137 | 0.1357 | 0.0842 | 0.2060 | yes |
| 800k rows, sum | paper_rt_optix | 11.654 | 0.0440 | 0.0910 | 0.1554 | yes |
| 800k rows, min | paper_rt_optix | 10.351 | 0.0461 | 0.0869 | 0.1530 | yes |
| 800k rows, max | paper_rt_optix | 11.103 | 0.0448 | 0.0900 | 0.1590 | yes |
| 800k rows, avg_as_sum_count | paper_rt_optix | 11.226 | 0.0495 | 0.0882 | 0.1565 | yes |

For comparison, the simple CPU columnar oracle at 800k rows took about
1.25-1.49 seconds depending on mode. That CPU baseline is not the same
paper-shaped ray/triangle algorithm, but it is the same output contract and is a
useful end-to-end sanity check.

## Interpretation

The RT primitive is not the bottleneck. At 800k rows, native work is roughly:

- 44-136 ms to build the prepared triangle scene;
- 84-91 ms to pack query/group/value arrays;
- 153-206 ms for RT traversal and grouped reduction.

The missing time is app-level Python work: repeated fixture expansion,
record-to-triangle object construction, ray-list construction, and CPU oracle
checking. This directly confirms the remaining v2.x technical debt: RayDB needs
typed host/device buffers and prepared execution so Python chooses the lowering
but does not materialize millions of Python objects per benchmark query.

## Required Next Work

1. Add a generic prepared ray/triangle grouped-i64 reduction interface that can
   consume typed buffers for triangles, rays, group IDs, and i64 payloads.
2. Keep the primitive app-agnostic. The runtime must not add RayDB, SQL, table,
   SSB, scan, or database vocabulary.
3. Add prepared mode reuse: one prepared triangle scene should serve repeated
   grouped reductions where the geometry is unchanged.
4. Add a benchmark path that reports both app-level time and native-only time,
   with the native-only time clearly labeled as a sub-path, not whole-app speed.
5. Re-run the RayDB matrix after typed/prepared lowering before making any
   benchmark promotion or speedup claim.

## Decision

RayDB should remain in the benchmark-development queue, not a closed
performance benchmark. Goal2645 proves the RT-core primitive exists and is
correct, but also proves the Python lowering boundary must be improved before
RayDB can support strong performance claims.
