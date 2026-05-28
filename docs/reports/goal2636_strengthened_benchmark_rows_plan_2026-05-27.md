# Goal2636 Strengthened Benchmark Rows Plan

Date: 2026-05-27

Status: pod-ready benchmark-evidence hardening plan. This is not public
speedup wording and does not replace actual native timing artifacts.

## Purpose

Goal2635 found that five promoted benchmark rows were correct at their exact
subpath boundary but still too small or too scoped for broad "RT beats Embree"
performance conclusions:

- Hausdorff / X-HD-style
- Spatial RayJoin-style
- RTNN neighbor search
- Barnes-Hut / RT-BarnesHut-style
- Triangle counting

Goal2636 adds an explicit runner for those rows so future pod runs strengthen
the weak evidence instead of repeating the same short Goal2634 matrix. The
runner is:

```text
scripts/goal2636_strengthen_benchmark_rows.py
```

## Runner Design

The runner reuses the Goal2626 matrix machinery for environment capture,
case execution, primary metric extraction, ratio calculation, and markdown/json
artifact writing. It adds only the case definitions needed to strengthen weak
rows.

Supported tiers:

| Tier | Purpose |
| --- | --- |
| `smoke` | Local/dry-run sanity and small fixture validation. |
| `standard` | First pod timing target for stronger but bounded evidence. |
| `stress` | Larger pressure run when the pod can be kept alive long enough. |

The default artifact directory is:

```text
docs/reports/goal2636_strengthened_rows_pod/
```

## App Coverage

| App | Strengthening action | Boundary |
| --- | --- | --- |
| Hausdorff / X-HD-style | Adds prepared threshold-decision copy ladders and separate OptiX exact grouped seeded/pruned witness ladders. | Exact witness rows are OptiX-only and are not ratioed against Embree unless a same-contract Embree route is added. |
| Spatial RayJoin-style | Replaces tiny/zero-risk fixtures with authored nonzero tiled PIP, LSI, and overlay-seed fixtures. | Still not full polygon overlay materialization or full RayJoin paper reproduction. |
| RTNN neighbor search | Adds uniform, clustered, and shell distribution ladders for the prepared 3-D ranked-summary contract. | Still not a full RTNN paper reproduction; clustered rows are the density-risk signal. |
| Barnes-Hut / RT-BarnesHut-style | Adds same-contract node-coverage prepared threshold-decision scale ladder. | Still not full force aggregation or app-specific native inverse-square force math. |
| Triangle counting | Adds synthetic K4 RT-Graph 2A1 backend-query scale ladder. | Still not the large paper dataset path; segmented/streamed lowering remains the paper-scale blocker. |

## RayJoin Fixture Fix

The previous all-route Spatial RayJoin row was valid but too weak because the
fixture was tiny and some routes could be zero-row. Goal2636 adds authored
tiled fixtures in `src/rtdsl/baseline_runner.py`:

| Dataset | Workload | Smoke size check |
| --- | --- | --- |
| `derived/authored_pip_square_tiled_x64` | PIP | 128 points, 64 polygons, 64 positive assignments. |
| `derived/authored_lsi_crossing_tiled_x64` | LSI | 64 left segments, 64 right segments, 64 intersections. |
| `derived/authored_overlay_squares_tiled_x64` | overlay-seed | 64 left polygons, 64 right polygons, 4096 candidate pair rows, 64 active dependencies. |

The standard pod tier uses the corresponding `x512` versions. The stress tier
uses `x2048` versions so Spatial RayJoin stress actually increases work instead
of rerunning the standard fixture.

## Pod Commands

First set the pod environment. On the RTX A5000 pod used for Goal2636, the
following environment was required to avoid CUDA/PTX toolchain mismatch and to
make CuPy-backed triangle counting available:

```bash
source /root/rtdl_goal2627/venv/bin/activate
export LD_LIBRARY_PATH=/root/rtdl_goal2627/rtdl/build:/usr/local/cuda-12.6/compat:/usr/local/cuda-12.6/lib64:/usr/local/cuda-12.6/targets/x86_64-linux/lib:$LD_LIBRARY_PATH
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_NVCC=/usr/local/cuda-12.6/bin/nvcc
export RTDL_OPTIX_PTX_ARCH=compute_86
```

Then run the standard tier:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --artifact-dir docs/reports/goal2636_strengthened_rows_pod \
  --timeout-sec 1800 \
  --build-native
```

If the standard tier is stable and the pod has enough time, run stress:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier stress \
  --artifact-dir docs/reports/goal2636_strengthened_rows_stress_pod \
  --timeout-sec 3600 \
  --build-native
```

To isolate one app:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --only-app spatial_rayjoin \
  --artifact-dir docs/reports/goal2636_strengthened_rows_pod \
  --timeout-sec 1800 \
  --build-native
```

## Local Validation Performed

The following local checks passed on the Mac:

```bash
python3 -m py_compile \
  scripts/goal2636_strengthen_benchmark_rows.py \
  tests/goal2636_strengthen_benchmark_rows_test.py \
  src/rtdsl/baseline_runner.py
```

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2626_benchmark_embree_optix_baseline_test \
  tests.goal2636_strengthen_benchmark_rows_test
```

The combined unittest run executed 15 tests successfully.

The RayJoin authored smoke fixtures were also checked through the CPU reference
front door:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload pip \
  --backend cpu_python_reference \
  --dataset derived/authored_pip_square_tiled_x64 \
  --no-rows
```

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload lsi \
  --backend cpu_python_reference \
  --dataset derived/authored_lsi_crossing_tiled_x64 \
  --no-rows
```

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload overlay_seed \
  --backend cpu_python_reference \
  --dataset derived/authored_overlay_squares_tiled_x64 \
  --no-rows
```

Observed smoke fixture counts:

| Workload | Row signal |
| --- | ---: |
| PIP positive assignments | 64 |
| LSI intersections | 64 |
| Overlay candidate dependency rows | 4096 |
| Overlay active dependencies | 64 |

## Required Interpretation

This work strengthens the measurement harness and workload coverage. It does
not yet prove new Embree-vs-OptiX speedups, because the current Mac session did
not run native pod timings for these rows.

Once pod artifacts exist, update the Goal2635 audit conclusion with:

- exact commit hash;
- hardware and driver probe;
- standard and any stress artifact paths;
- per-app ratios;
- any row where OptiX loses or fails, with a concrete cause.
