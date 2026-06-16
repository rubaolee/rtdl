# Goal4424: V3.0 M27 Triangle Counting Partner Dual-Path Closure

## Status

M27 makes the triangle-counting benchmark's advertised `--partner numba`
summary route executable for both RT-Graph mappings:

- `rt_graph_2a1_generic_rt`
- `rt_graph_1a2_generic_rt`

CuPy remains the high-performance GPU graph-contract builder.
The new Numba route is deliberately bounded: it builds the RT-Graph summary
contract with the existing Python/NumPy contract builder, uploads the compact
summary columns to Numba CUDA device arrays, then uses the same app-agnostic
OptiX device-column summary primitive as CuPy.

## What Changed

- Added `build_rt_graph_triangle_summary_contract_numba_binary(...)`.
- Generalized the triangle-counting partner summary validator from CuPy-only to
  CuPy-or-Numba.
- Added Numba device-column geometry builders for both RT-2A1 and RT-1A2.
- Fixed prepared-session metadata so Numba device-column paths say
  `numba_device_columns`, not `cupy_device_columns`.
- Added `scripts/v3_0_m27_triangle_partner_dual_measure.py` for CuPy-vs-Numba
  evidence on the same binary K4-clique graph.
- The measurement runner prewarms both partner routes on a small K4-clique graph
  before recording the formal rows, so cold CUDA/CuPy/OptiX initialization is
  not misreported as graph-contract cost.

## Contract Boundary

| Question | M27 answer |
| --- | --- |
| Does CuPy remain the best current Python GPU graph-contract builder? | Yes. |
| Does Numba now work from the app front door? | Yes. |
| Is the Numba route a fully fused GPU graph-construction implementation? | No. |
| Does either route add app-specific native OptiX code? | No. |
| Does either route authorize public whole-app speedup wording? | No. |

## Pod Evidence

The M27 runner writes compact evidence to:

- `docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques5000_2026-06-15.json`
- `docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques50000_2026-06-15.json`
- `docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques200000_2026-06-15.json`

Expected evidence fields:

- both RT-2A1 and RT-1A2 modes are present;
- both `cupy` and `numba` partners are present;
- `parameters.prewarm.enabled: true`;
- `comparison.all_triangle_counts_match_oracle: true`;
- `comparison.signature_match_by_mode.*: true`;
- CuPy rows use `partner_construction_mode: null` because the CuPy builder is
  already the native summary-contract builder;
- Numba rows use
  `partner_construction_mode: cpu_contract_then_numba_device_upload`;
- Numba rows expose `numba_device_columns` in `v2_4_input_source_protocols`.

## Measured Matrix

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB.
All rows are prewarmed. `total` is the app route wall time in milliseconds;
`partner` is the graph-contract construction/upload portion; `query median` is
the repeated OptiX summary query median after scene preparation.

| Cliques | Mapping | Partner | Triangles | Primitives | Rays | Total ms | Partner ms | Prepare ms | Query median ms |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5,000 | RT-2A1 | CuPy | 20,000 | 30,000 | 15,000 | 42.959 | 24.436 | 1.908 | 0.391 |
| 5,000 | RT-2A1 | Numba | 20,000 | 30,000 | 15,000 | 219.420 | 205.604 | 2.148 | 0.373 |
| 5,000 | RT-1A2 | CuPy | 20,000 | 20,000 | 30,000 | 14.390 | 7.979 | 1.556 | 0.367 |
| 5,000 | RT-1A2 | Numba | 20,000 | 20,000 | 30,000 | 215.188 | 198.914 | 1.961 | 0.841 |
| 50,000 | RT-2A1 | CuPy | 200,000 | 300,000 | 150,000 | 84.709 | 58.119 | 3.762 | 1.104 |
| 50,000 | RT-2A1 | Numba | 200,000 | 300,000 | 150,000 | 1,904.068 | 1,816.284 | 3.580 | 1.109 |
| 50,000 | RT-1A2 | CuPy | 200,000 | 200,000 | 300,000 | 34.792 | 21.348 | 3.314 | 1.377 |
| 50,000 | RT-1A2 | Numba | 200,000 | 200,000 | 300,000 | 1,951.729 | 1,836.982 | 6.821 | 2.391 |
| 200,000 | RT-2A1 | CuPy | 800,000 | 1,200,000 | 600,000 | 416.645 | 376.237 | 10.636 | 2.694 |
| 200,000 | RT-2A1 | Numba | 800,000 | 1,200,000 | 600,000 | 8,139.455 | 7,808.690 | 7.291 | 1.955 |
| 200,000 | RT-1A2 | CuPy | 800,000 | 800,000 | 1,200,000 | 76.348 | 51.020 | 5.799 | 3.275 |
| 200,000 | RT-1A2 | Numba | 800,000 | 800,000 | 1,200,000 | 7,932.472 | 7,540.007 | 5.974 | 3.267 |

## Interpretation

This closes a front-door honesty gap: the CLI offered `--partner numba`, but the
summary route previously rejected non-CuPy partners. After M27, users can run a
no-C++ Numba reference through the same RTDL/OptiX generic primitive, while the
report makes clear that CuPy remains the optimized graph-contract construction
path.

The measured lesson is sharper than a yes/no partner checkbox:

- The RTDL/OptiX device-column primitive is shared by both partners and remains
  fast once geometry is prepared: the 200,000-clique runs query 0.6M to 1.2M
  rays in roughly 2-3 ms.
- CuPy is the right current high-performance partner for this app because it
  builds the compact graph contract on the GPU-side array path; at 200,000
  cliques it is roughly 19.5x faster than Numba on RT-2A1 total wall time and
  roughly 104x faster on RT-1A2 total wall time.
- The Numba route is still useful because it is now a real no-C++ front-door
  route through the same RTDL primitive, but its current implementation is
  intentionally not the optimized route: Python/NumPy graph-contract
  construction dominates the 7.5-7.8 s partner time at 200,000 cliques.
- Therefore M27 authorizes "RTDL supports CuPy and Numba partner routes for the
  triangle-counting RT-Graph summary contract." It does not authorize public
  whole-app speedup wording against external C++/CUDA/OptiX baselines.

## Verification

```bash
PYTHONPATH=src:. python -m unittest tests.goal4424_v3_0_m27_triangle_partner_dual_test
PYTHONPATH=src:. python scripts/v3_0_m27_triangle_partner_dual_measure.py \
  --cliques 5000 \
  --warmup 1 \
  --repeat 3 \
  --partners cupy,numba \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques5000_2026-06-15.json
```
