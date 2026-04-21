# Goal 742: LSI/PIP Root Workload Refresh

## Scope

This report gives VIP treatment to RTDL's original root workloads: line-segment intersection (`lsi`) and point-in-polygon (`pip`). It separates standalone primitive behavior from later composed polygon apps.

- host: `Rs-MacBook-Air.local`
- platform: `macOS-26.3-arm64-arm-64bit-Mach-O`
- scale: `standard`
- repeats: `5`
- Embree thread config: `{'requested': 'auto', 'effective_threads': 10, 'source': 'api', 'auto': True}`

## Results

| Case | Inputs | Rows | CPU ref s | Embree 1T s | Embree auto s | Prepared raw median s | Auto vs CPU | Auto vs 1T | Raw vs dict | Parity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| lsi_sparse | left=5000, right=5000 | 5000 | 5.380152 | 0.034887 | 0.006341 | 0.001946 | 848.43x | 5.50x | 3.26x | True |
| lsi_dense | left=350, right=350 | 122500 | 0.090317 | 0.069314 | 0.061724 | 0.001352 | 1.46x | 1.12x | 45.64x | True |
| pip_positive | points=10000, polygons=5000 | 10000 | 1.656962 | 0.019332 | 0.009800 | 0.005375 | 169.08x | 1.97x | 1.82x | True |

## Interpretation

- `lsi_sparse` is the traversal-friendly root case: many build segments, each probe expected to emit a small number of rows.
- `lsi_dense` is intentionally output-heavy. If this case is slower, the bottleneck is row emission/materialization, not absence of ray traversal.
- `pip_positive` is the historical positive-hit PIP shape: Embree performs native BVH/point-query candidate discovery and emits only accepted containment rows.
- Prepared raw mode measures the low-overhead native result path before Python dict materialization.

## Boundaries

- This is an Embree CPU ray-tracing/root-workload closure, not an NVIDIA RT-core claim.
- LSI/PIP remain float-approximate RTDL primitives; exact GIS semantics still require external exact validation when users need it.
- Composed polygon applications should cite these root workloads when they use LSI/PIP for candidate discovery.

## Independent Review Status

- Gemini Flash review was requested on 2026-04-21, but the service returned repeated model-capacity 429 responses. The local evidence above is therefore Codex-verified only until a later external review retry succeeds.
