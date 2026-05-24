# Goal2574 LibRTS Spatial-Index Benchmark Intake

## Scope

This goal starts the benchmark-app track for reproducing:

- Liang Geng, Rubao Lee, and Xiaodong Zhang, "LibRTS: A Spatial Indexing Library by Ray Tracing," PPoPP 2025.
- DOI: `10.1145/3710848.3710850`
- Authors code: `https://github.com/RTSpatial/RTSpatial`

The paper is directly relevant to RTDL because it treats ray tracing hardware as
a reusable spatial-index substrate rather than as a rendering-only accelerator.
The core workload slice for RTDL is:

| Paper workload | Local benchmark operation |
| --- | --- |
| point query | `point_contains`: indexed box contains query point |
| range-contains query | `range_contains`: indexed box contains query box |
| range-intersects query | `range_intersects`: indexed box intersects query box |
| mutability | delete/update/insert pressure in `mutation_cpu_reference` |

## Paper Claims To Reproduce

The reproduction target is the paper's spatial-index behavior and measured
claims, not just a similarly named app. The current target claims are:

| Paper claim family | Reported headline in paper | Current status |
| --- | ---: | --- |
| Point queries | up to `85.1x` speedup | Not reproduced yet; local oracle and WKT fixture generation added |
| Range-contains queries | up to `94.0x` speedup | Not reproduced yet; predicate orientation locked to authors shader |
| Range-intersects queries | up to `11.0x` speedup | Not reproduced yet; forward/backward query shape identified in authors code |
| Point-in-polygon application | up to `3.8x` over prior RT method | Future extension after spatial-index core is reproducible |

The paper mechanisms to check during reproduction are:

| Mechanism | LibRTS role | RTDL pressure |
| --- | --- | --- |
| Query translation | Convert point/range predicates into RT-compatible tests | generic prepared AABB query semantics |
| Rectangle diagonal / ray simulation | Use ray-box intersection for range predicates | exact predicate orientation and false-positive refinement |
| Ray Multicast | Split geometries into `k` subspaces and cast `k` rays | runtime-controlled load balancing without app-specific engine names |
| Instancing | Keep inserted geometries in separate BVHs under an IAS | mutable prepared spatial-index state |

## What Was Added

- `examples/v2_0/research_benchmarks/librts_spatial_index/`
- `rtdl_librts_spatial_index_benchmark_app.py`
- `scripts/goal2574_librts_external_runner.py`
- `tests/goal2574_librts_spatial_index_benchmark_app_test.py`

The local app provides:

- inclusive-boundary CPU predicate oracle;
- CPU partner-style uniform-grid broadphase with exact predicate refinement;
- deterministic tiny and uniform fixtures;
- WKT fixture emission compatible with the authors `RTSpatial` example loader;
- manifest and command helper for pod-side authors-code runs;
- parser for `rtspatial_exec` output lines of the form
  `RT, load ... ms, query ... ms, results: ...`.

## Predicate Orientation

The authors' range-contains shader calls `envelope.Contains(query)`, where
`envelope` is the indexed geometry and `query` is the range-query envelope.
Therefore this RTDL benchmark fixes the range-contains orientation as
indexed-box-contains-query-box.

This is a necessary correctness detail. Reversing the orientation would make
local counts pass for symmetric or random cases sometimes while being wrong for
the actual paper code path.

## Authors-Code Reproduction Plan

The authors code is available at `RTSpatial/RTSpatial`, so the benchmark should
use it when a CUDA/OptiX pod is available. The current local Mac step prepares
the input and parser only.

Required pod environment:

- Linux
- CMake 3.27+
- CUDA 12+
- NVIDIA driver 535+
- NVIDIA OptiX 8.0
- `gflags` for example binaries

Expected authors-code flow:

```bash
git clone https://github.com/RTSpatial/RTSpatial.git
mkdir -p RTSpatial/build
cd RTSpatial/build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=ON ..
make -j
```

Then emit fixtures from RTDL:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode emit_wkt --dataset uniform --box-count 100000 --query-count 1000 \
  --skip-counts --output-dir scratch/librts_uniform_100k_1k
```

Use the helper to construct commands:

```bash
PYTHONPATH=src:. python scripts/goal2574_librts_external_runner.py commands \
  --manifest scratch/librts_uniform_100k_1k/manifest.json \
  --rtspatial-exec /path/to/rtspatial_exec --load-factor 0.25
```

## RTDL Design Pressure

LibRTS is not merely another app. It is a direct pressure test for a generic
mutable spatial-index primitive family:

- prepared 2-D AABB geometry state;
- point and envelope query streams;
- query predicates that return counts or pairs;
- mutable insert/delete/update behavior;
- runtime-controlled load balancing and ray multicast;
- optional authors-code comparison through a shared WKT fixture.

The engine must not gain app-specific `LibRTS` symbols. If this track promotes
runtime work later, the primitive should be named by behavior, such as mutable
prepared AABB index query, not by paper or app name.

The local `partner_grid_reference` mode is intentionally benchmark-side code.
It helps quantify candidate pressure and validates a Python+partner shape, but
it is not an RTDL native engine primitive and not a substitute for authors-code
OptiX timing.

## Claim Boundary

This intake does not reproduce the full paper, does not time authors code, does
not compare RTDL performance to authors performance, does not add native RTDL
engine ABI, and does not authorize public speedup wording.

The current claim is only: RTDL has a local, test-backed benchmark-app harness
that preserves LibRTS predicate semantics and can generate shared input files
for future authors-code reproduction.
