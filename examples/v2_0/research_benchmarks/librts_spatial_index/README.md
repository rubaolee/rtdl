# LibRTS-Style Spatial Index Study

This directory starts the RTDL benchmark-app track for reproducing the core
claims of:

- Liang Geng, Rubao Lee, and Xiaodong Zhang, "LibRTS: A Spatial Indexing Library by Ray Tracing," PPoPP 2025.
- DOI: `10.1145/3710848.3710850`
- Authors code: `https://github.com/RTSpatial/RTSpatial`

The goal is to reproduce the paper's spatial-index workloads with explicit
claim boundaries: point queries, range-contains queries, range-intersects
queries, and mutable insert/delete/update pressure. The current slice is not the
full paper reproduction. It establishes the semantics, deterministic fixtures,
WKT interchange files, authors-code command shape, authors-code OptiX evidence,
and a generic RTDL OptiX `AABB_INDEX_QUERY_2D` path for all three count-only
query operations.

The paper headline claims to reproduce are up to `85.1x` for point queries, up
to `94.0x` for range-contains queries, up to `11.0x` for range-intersects
queries, and up to `3.8x` for the point-in-polygon application over a prior RT
method. None of those claims is authorized by the local harness alone.

## Files

| File | Role |
| --- | --- |
| `rtdl_librts_spatial_index_benchmark_app.py` | CPU oracle, generic AABB primitive lowering, and WKT fixture generator for LibRTS-style spatial-index workloads |
| `../../../../scripts/goal2574_librts_external_runner.py` | Parser and command helper for authors `rtspatial_exec` output |
| `../../../../docs/reports/goal2575_librts_rtspatial_authors_pod_evidence_2026-05-24.md` | First authors-code pod evidence report |
| `../../../../docs/reports/goal2576_librts_generic_aabb_index_primitive_2026-05-24.md` | Generic `AABB_INDEX_QUERY_2D` primitive boundary extracted from this app |
| `../../../../docs/reports/goal2577_librts_rtspatial_mutation_pod_evidence_2026-05-24.md` | Authors-code mutation correctness evidence report |
| `../../../../docs/reports/goal2578_librts_paperlike_uniform_authors_pod_evidence_2026-05-24.md` | Paper-like small-box uniform authors-code timing evidence |
| `../../../../docs/reports/goal2579_librts_reproduction_status_and_next_targets_2026-05-24.md` | Reproduction status matrix and next RTDL engineering target |
| `../../../../docs/reports/goal2580_librts_optix_aabb_index_native_path_2026-05-24.md` | Generic RTDL OptiX AABB index path for point/range-contains |
| `../../../../docs/reports/goal2581_librts_optix_range_intersects_path_2026-05-24.md` | Generic RTDL OptiX two-pass range-intersects path and performance evidence |

## Modes

| Mode | Meaning |
| --- | --- |
| `scope` | Report paper metadata, target operations, local modes, and pod requirements |
| `cpu_reference` | Count point/range predicates with an inclusive-boundary CPU oracle |
| `cpu_reference_wkt` | Load WKT boxes/queries and count predicates with the same CPU oracle |
| `partner_grid_reference` | LibRTS app lowering through generic CPU `AABB_INDEX_QUERY_2D` with uniform-grid broadphase and exact predicate refinement |
| `optix_aabb_index` | Generic RTDL OptiX `AABB_INDEX_QUERY_2D` path for count-only point/range query operations |
| `mutation_cpu_reference` | Apply delete/update/insert pressure to the local oracle |
| `emit_wkt` | Emit LibRTS-compatible WKT files and a manifest for authors-code runs |

## Semantics

The authors' `RTSpatial` shader for range-contains checks
`indexed_envelope.Contains(query_envelope)`. This benchmark therefore fixes the
orientation as:

| Operation | Meaning |
| --- | --- |
| `point_contains` | indexed box contains query point |
| `range_contains` | indexed box contains query box |
| `range_intersects` | indexed box intersects query box |

All local CPU predicates use inclusive min/max boundaries to match the authors'
`Envelope::Contains` and `Envelope::Intersects` definitions.

## Local Commands

Scope:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode scope
```

Tiny CPU correctness:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode cpu_reference --dataset tiny
```

Uniform CPU oracle:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode cpu_reference --dataset uniform --box-count 1000 --query-count 1000 --seed 2025
```

Uniform-grid partner baseline:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode partner_grid_reference --dataset uniform --box-count 1000 --query-count 1000 --grid-resolution 64
```

OptiX AABB index path after building `build/librtdl_optix.so`:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode optix_aabb_index --dataset uniform --box-count 100000 --query-count 1000 --seed 2025 --max-box-width 0.005 --max-box-height 0.005 --max-query-width 0.005 --max-query-height 0.005 --operation all
```

Emit WKT fixtures for authors-code runs:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode emit_wkt --dataset uniform --box-count 100000 --query-count 1000 --skip-counts --output-dir scratch/librts_uniform_100k_1k
```

Load WKT fixtures into the CPU oracle:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py --mode cpu_reference_wkt --boxes-wkt scratch/librts_uniform_100k_1k/boxes.wkt --point-queries-wkt scratch/librts_uniform_100k_1k/point_queries.wkt --box-queries-wkt scratch/librts_uniform_100k_1k/box_queries.wkt
```

Build command lines for the authors executable:

```bash
PYTHONPATH=src:. python scripts/goal2574_librts_external_runner.py commands --manifest scratch/librts_uniform_100k_1k/manifest.json --rtspatial-exec /path/to/rtspatial_exec --load-factor 0.25
```

Parse authors-code output:

```bash
PYTHONPATH=src:. python scripts/goal2574_librts_external_runner.py parse-output --input scratch/librts_rtspatial_output.txt
```

## Authors-Code Pod Evidence

The authors code is available, so this benchmark uses the public
`RTSpatial/RTSpatial` implementation as the first serious paper-code baseline,
not a proxy baseline. The first pod evidence is recorded in:

- `docs/reports/goal2575_librts_rtspatial_authors_pod_evidence_2026-05-24.md`
- `docs/reports/goal2575_librts_rtspatial_authors_pod_evidence_2026-05-24.json`
- `docs/reports/librts_pod_raw/`

That evidence built `rtspatial_exec` on an NVIDIA RTX A5000 pod with OptiX 8.1
and CUDA 12.6 after CUDA 12.8 hit a driver/PTX-version mismatch. It recorded
same-fixture authors-code timings for uniform 10k, 100k, and 1M indexed boxes
with 1k queries for all three operations. The 10k row also matched the RTDL CPU
oracle exactly.

The authors' GTest suite was also built on the same pod/toolchain for mutation
coverage. `EnvelopeQueries.fp32_intersects_envelope_batch_update`,
`EnvelopeQueries.fp32_test_delete`, and
`EnvelopeQueries.fp32_test_delete_compact` all passed. This is authors-code
mutation correctness evidence only; it is not an RTDL native mutation primitive.

Goal2578 adds a paper-like small-box uniform slice using max indexed/query box
width/height `0.005`, matching the authors artifact's default scale more
closely than Goal2575. On the same pod, authors-code 1M boxes x 1k queries ran
in `0.099 ms` for point contains, `0.106 ms` for range contains, and `0.620 ms`
for range intersects. This is still RTDL-generated WKT, not exact paper artifact
dataset reproduction.

Goal2580 and Goal2581 add the generic RTDL OptiX `AABB_INDEX_QUERY_2D` path.
On the same paper-like fixtures, prepared-query RTDL OptiX counts matched the
authors-code counts for all three operations. The 1M x 1k warm median query rows
were `0.0983 ms` for point contains, `0.0889 ms` for range contains, and
`0.4049 ms` for range intersects. These are internal count-only benchmark
numbers, not public speedup wording.

To reproduce or extend those rows on an NVIDIA pod, build `RTSpatial/RTSpatial`
with:

- Linux
- CMake 3.27+
- CUDA 12+
- NVIDIA driver 535+
- NVIDIA OptiX 8.0
- `gflags` for examples

Then run the emitted WKT fixtures through the authors `rtspatial_exec` for all
three operations and compare:

- result counts against this CPU oracle;
- load/query timings against RTDL paths once those paths exist;
- paper-scale settings against the paper's stated point/range query claims.

## Claim Boundary

- This is a research benchmark / reconstruction instrument.
- It does not reproduce the full LibRTS paper yet.
- It has first authors-code pod timings, but they are not RTDL speedup claims.
- It does not add a native RTDL spatial-index ABI.
- It does not authorize public speedup wording.
- The `partner_grid_reference` mode is a benchmark-level call into generic CPU
  `AABB_INDEX_QUERY_2D`; it is not an RT-core path and not a paper baseline.
- The `optix_aabb_index` mode is a benchmark-level call into generic RTDL OptiX
  `AABB_INDEX_QUERY_2D`; it is not a `LibRTS` native symbol.
- Python owns the benchmark fixture, predicate orientation, mutation scenario,
  and authors-code command construction.
- Any future engine primitive must be app-name-free, e.g. a generic mutable
  spatial-index or prepared-AABB-query contract, not a `LibRTS` native symbol.
