# Goal2589 RT-Graph Triangle-Counting Pod Evidence

Date: 2026-05-24

Status: same-input correctness evidence collected for RT-Graph authors code and
RTDL generic OptiX mappings. Generic 3-D prepared ray/triangle summary paths
were added after the first row-returning timing pass. A follow-up optimization
pass vectorized benchmark-owned 1A2 packed lowering and removed per-weight
Python tuple packing from the generic weighted-summary host path. A second
follow-up pass avoided building the id-ascending adapter in RT summary modes
that do not use it. This is internal benchmark evidence only; it does not
authorize public speedup wording.

## Environment

| Field | Value |
| --- | --- |
| Pod | `ssh root@203.57.40.104 -p 10001 -i ~/.ssh/id_ed25519` |
| Working key actually present on this Mac | `~/.ssh/id_ed25519_rtdl_codex` |
| Hostname | `fc75fca4648a` |
| GPU | NVIDIA RTX A5000 |
| Driver | 550.127.05 |
| NVIDIA-SMI CUDA version | 12.4 |
| CUDA compiler used | `/usr/local/cuda-12.8/bin/nvcc`, release 12.8 |
| OptiX SDK used | NVIDIA OptiX SDK 7.7.0 |
| RTDL OptiX backend | `librtdl_optix.so`, `rt.optix_version() == (7, 7, 0)` |
| Repo base commit before local/untracked goal work | `dc6b91d29a37ad335e2ebe0cf553cd01606530fc` |

The pod tree was synced from the local working tree, including uncommitted
Goal2586-2589 files. It is therefore not a clean Git checkout evidence row.

## Authors-Code Build Notes

The authors RT-Graph code in `scratch/external/RT-Graph` was built from the
studied snapshot with compatibility patches required by this pod:

- `rt_tc/rt_base.cpp`: fixed an OptiX 7.7 compile typo by changing
  `ptxCode` to `ptx_code`.
- `tc/graph/CMakeLists.txt`, `tc/bs_tc/CMakeLists.txt`,
  `tc/rt_tc/CMakeLists.txt`: changed hardcoded CUDA codegen from `sm_75` to
  `sm_86` for RTX A5000.
- CMake was run with `OptiX_INSTALL_DIR=/root/vendor/NVIDIA-OptiX-SDK-7.7.0-linux64-x86_64`,
  `CMAKE_CUDA_COMPILER=/usr/local/cuda-12.8/bin/nvcc`, and
  `BIN2C=/usr/local/cuda-12.8/bin/bin2c`.

These patches are build-environment compatibility patches, not algorithmic
changes to the triangle-counting method. The compile-time selector
`RTTC_METHOD` was rebuilt as `0` for 1A2 rows and `1` for 2A1 rows.

## Workloads

The evidence used RT-Graph binary edge-list files generated from deterministic
disjoint K4 cliques:

| Workload | Vertices | Edges | Expected triangles |
| --- | ---: | ---: | ---: |
| `degree_oriented_two_triangles.edge` | 4 | 5 | 2 |
| `k4_cliques_1000.edge` | 4,000 | 6,000 | 4,000 |
| `k4_cliques_10000.edge` | 40,000 | 60,000 | 40,000 |

The K4 workloads are not paper SNAP datasets. They are controlled correctness
and scaling probes that let authors code and RTDL consume the exact same input.

## Correctness

All measured paths returned the expected triangle count.

| Workload | Path | Method | Count |
| --- | --- | --- | ---: |
| two-triangle fixture | authors `bs_tc` | 2A1 | 2 |
| two-triangle fixture | authors `rt_tc` | 2A1 | 2 |
| two-triangle fixture | authors `bs_tc` | 1A2 | 2 |
| two-triangle fixture | authors `rt_tc` | 1A2 | 2 |
| two-triangle fixture | RTDL OptiX generic | RT-2A1 mapping | 2 |
| two-triangle fixture | RTDL OptiX generic | RT-1A2 mapping | 2 |
| K4 x 1,000 | authors `bs_tc` | 1A2 / 2A1 | 4,000 |
| K4 x 1,000 | authors `rt_tc` | 1A2 / 2A1 | 4,000 |
| K4 x 1,000 | RTDL OptiX generic | 1A2 / 2A1 | 4,000 |
| K4 x 10,000 | authors `bs_tc` | 1A2 / 2A1 | 40,000 |
| K4 x 10,000 | authors `rt_tc` | 1A2 / 2A1 | 40,000 |
| K4 x 10,000 | RTDL OptiX generic | 1A2 / 2A1 | 40,000 |

## Performance Rows

Authors rows report the program's own printed phase timings. RTDL rows report
the benchmark app's timed Python+RTDL phases. These are not identical timing
contracts: authors `Counting Time` is kernel/trace-oriented, while RTDL
`run_backend` includes generic OptiX scene preparation plus scalar summary
execution. RTDL `total` additionally includes Python graph contract and
geometry lowering.

The first RTDL pod pass used row-returning generic traversal and exposed a
large runtime limit: RT-1A2 on K4 x 10,000 spent `15320.019 ms` in
`run_backend`, and RT-2A1 spent `596.790 ms`. The current rows below use the
new app-agnostic summary primitives:

- `PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1`
- `PREPARED_TRIANGLE_SCENE_3D_RAY_HIT_COUNT_SUM_V1`

### K4 x 1,000

| Path | Method | Main timed row | Count |
| --- | --- | ---: | ---: |
| authors `bs_tc` | 1A2 | `counting time = 0.039840 ms` | 4,000 |
| authors `rt_tc` | 1A2 | `Trace time = 0.054656 ms`, `BVH Building Time = 0.137401 ms` | 4,000 |
| authors `bs_tc` | 2A1 | `counting time = 0.025216 ms`, 2-hop preprocessing `4.951006 ms` | 4,000 |
| authors `rt_tc` | 2A1 | `Trace time = 0.043392 ms`, `BVH Building Time = 0.087481 ms` | 4,000 |
| RTDL OptiX generic summary | 1A2 | cold `run_backend = 58.761 ms`, warm best `run_backend = 0.651 ms`, best total `43.247 ms`, native traversal best `0.060 ms` | 4,000 |
| RTDL OptiX generic summary | 2A1 | cold `run_backend = 331.648 ms`, warm best `run_backend = 1.312 ms`, best total `31.151 ms`, native traversal best `0.052 ms` | 4,000 |

### K4 x 10,000

| Path | Method | Main timed row | Count |
| --- | --- | ---: | ---: |
| authors `bs_tc` | 1A2 | `counting time = 0.314048 ms` | 40,000 |
| authors `rt_tc` | 1A2 | `Trace time = 0.063616 ms`, `BVH Building Time = 0.072841 ms` | 40,000 |
| authors `bs_tc` | 2A1 | `counting time = 0.032320 ms`, 2-hop preprocessing `205.059241 ms` | 40,000 |
| authors `rt_tc` | 2A1 | `Trace time = 0.059904 ms`, `BVH Building Time = 0.146881 ms` | 40,000 |
| RTDL OptiX generic summary | 1A2 | best `run_backend = 4.300 ms`, best total `457.276 ms`, native traversal best `0.092 ms` | 40,000 |
| RTDL OptiX generic summary | 2A1 | best `run_backend = 10.714 ms`, best total `407.565 ms`, native traversal best `0.083 ms` | 40,000 |

## Follow-Up Optimization Pass

After the first accepted summary-primitive implementation, two additional
non-native optimizations were tested on the same pod:

- The 2A1 weighted summary path now accepts NumPy/array-like `uint64` weights
  without converting every entry through a Python tuple before the native call.
- The 1A2 OptiX summary lowering now builds packed 3-D triangle columns from
  CSR arrays with vectorized NumPy operations instead of appending one Python
  primitive at a time.
- RT summary modes no longer materialize the id-ascending adapter, because that
  adapter is only needed by the CPU `rt_graph_rtdl_adapter` path and full
  contract payloads.

These changes do not add graph semantics to the native engine.

### K4 Follow-Up Rows

Best warm rows from five iterations per mode before the optional-adapter
optimization:

| Workload | Method | Count | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native prepare ms | Native query-pack ms | Native traversal ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K4 x 10,000 | RTDL 2A1 summary | 40,000 | 391.048 | 347.616 | 22.488 | 4.323 | 2.779 | 0.028 | 0.087 |
| K4 x 10,000 | RTDL 1A2 summary | 40,000 | 378.626 | 329.207 | 20.632 | 4.155 | 2.280 | 0.001 | 0.103 |
| K4 x 50,000 | RTDL 2A1 summary | 200,000 | 2201.996 | 1946.675 | 141.075 | 15.252 | 10.755 | 0.044 | 0.178 |
| K4 x 50,000 | RTDL 1A2 summary | 200,000 | 2188.777 | 1936.186 | 143.123 | 13.019 | 6.820 | 0.002 | 0.275 |
| K4 x 100,000 | RTDL 2A1 summary | 400,000 | 4751.351 | 4217.253 | 313.245 | 25.091 | 17.030 | 0.048 | 0.287 |
| K4 x 100,000 | RTDL 1A2 summary | 400,000 | 4715.561 | 4202.033 | 292.411 | 23.174 | 12.005 | 0.001 | 0.439 |

Compared with the earlier K4 x 50,000 probe, the 2A1 host query-pack phase
dropped from about `32 ms` to about `0.04 ms`, and the 1A2 build-geometry phase
dropped from about `613 ms` to about `143 ms`.

Best warm rows after also skipping unused id-ascending adapter construction in
RT summary modes:

| Workload | Method | Count | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native prepare ms | Native query-pack ms | Native traversal ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K4 x 10,000 | RTDL 2A1 summary | 40,000 | 276.231 | 231.896 | 23.322 | 4.247 | 2.668 | 0.033 | 0.083 |
| K4 x 10,000 | RTDL 1A2 summary | 40,000 | 259.736 | 220.995 | 18.612 | 4.016 | 2.246 | 0.001 | 0.090 |
| K4 x 50,000 | RTDL 2A1 summary | 200,000 | 1539.519 | 1281.455 | 138.000 | 23.746 | 18.749 | 0.045 | 0.191 |
| K4 x 50,000 | RTDL 1A2 summary | 200,000 | 1569.971 | 1317.578 | 143.316 | 13.643 | 8.107 | 0.002 | 0.270 |
| K4 x 100,000 | RTDL 2A1 summary | 400,000 | 3244.977 | 2707.374 | 304.524 | 26.569 | 19.444 | 0.047 | 0.284 |
| K4 x 100,000 | RTDL 1A2 summary | 400,000 | 3185.847 | 2678.135 | 281.342 | 21.991 | 11.485 | 0.002 | 0.441 |

### Random Graph Follow-Up Rows

Deterministic undirected random graphs were generated on the pod and consumed
through the same binary edge-list reader. Both methods matched the Python
contract oracle:

| Workload | Method | Oracle count | Primitive count | Ray count | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native traversal ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| random `n=200,m=1000` | RTDL 2A1 summary | 157 | 1,000 | 2,999 | 333.900 | 6.908 | 1.697 | 324.931 | 0.066 |
| random `n=200,m=1000` | RTDL 1A2 summary | 157 | 3,369 | 1,000 | 65.994 | 4.196 | 0.693 | 60.835 | 0.069 |
| random `n=1000,m=6000` | RTDL 2A1 summary | 289 | 6,000 | 23,039 | 54.722 | 36.025 | 15.867 | 1.432 | 0.079 |
| random `n=1000,m=6000` | RTDL 1A2 summary | 289 | 23,898 | 6,000 | 33.839 | 26.221 | 3.256 | 2.847 | 0.068 |
| random `n=2000,m=12000` | RTDL 2A1 summary | 314 | 12,000 | 46,520 | 88.738 | 65.510 | 18.079 | 2.209 | 0.073 |
| random `n=2000,m=12000` | RTDL 1A2 summary | 314 | 47,309 | 12,000 | 73.714 | 61.010 | 6.439 | 3.220 | 0.078 |

The first random `n=200,m=1000` rows include cold OptiX/JIT effects in
`run_backend`; later rows are more representative of warm execution.

## Interpretation

The main positive result is semantic: RTDL can express both paper
decompositions using app-agnostic ray/triangle primitives.

- RT-2A1 maps directed 1-hop edges to generic `Triangle3D` primitives and
  compacted 2-hop relations to weighted `ANY_HIT` rays.
- RT-1A2 maps compacted 2-hop relations to generic `Triangle3D` primitives and
  directed 1-hop edges to per-ray `HIT_COUNT` probes.

The summary primitive removes the row-materialization bottleneck. The follow-up
optimizations also remove most avoidable host query-pack overhead from the 2A1
weighted path, materially reduce 1A2 geometry lowering, and avoid an unused
adapter construction cost in RT summary modes. On K4 x 10,000, RTDL native
traversal remains in the same rough order as authors trace time (`0.08-0.12 ms`
versus authors `0.06 ms`). RTDL whole-app `total` is still not competitive with
authors code because Python graph contract construction now dominates even more
clearly.

A focused authors-code comparison was added in
`docs/reports/goal2589_authors_vs_rtdl_triangle_counting_comparison_2026-05-24.md`.
That comparison rebuilds authors `bs_tc` and `rt_tc` for both `RTTC_METHOD=0`
and `RTTC_METHOD=1`, confirms same-input counts, and shows that RTDL traversal
is close in order of magnitude while RTDL whole-app performance is still slower
at larger K4 scales.

## CuPy Partner Follow-Up

The app-owned graph contract construction was then moved from pure Python to an
optional CuPy partner path. This keeps the RTDL native engine app-agnostic: the
partner constructs the RT-Graph-oriented directed CSR, duplicate-aware 2-hop
summary rays, and oracle triangle count; RTDL still receives only generic
`Triangle3D`, `Ray3D`, optional ray weights, and scalar summary requests.

Pod setup:

- Python environment: `/root/rtdl_cupy_venv`
- CuPy package: `cupy-cuda12x`
- CuPy version: `14.1.0`
- Device: NVIDIA RTX A5000
- Command shape:
  `PYTHONPATH=src:. /root/rtdl_cupy_venv/bin/python ... --backend optix --detail summary --partner cupy`

Focused tests passed on the pod with no skips:

```text
PYTHONPATH=src:. /root/rtdl_cupy_venv/bin/python -m unittest \
  tests.goal2589_rt_graph_triangle_contract_test \
  tests.goal2586_triangle_counting_benchmark_boundary_test

Ran 15 tests in 4.042s
OK
```

The CuPy partner contract test compares GPU-built summary contracts against the
Python contract on both the clean two-triangle fixture and the
duplicate/self/leaf cleanup fixture.

### CuPy Partner K4 Rows

Rows below are medians of three warm app runs after one small warmup run. The
native traversal column is the OptiX traversal phase inside the generic summary
primitive.

| Workload | Method | Count | Primitive count | Ray count | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native prepare ms | Native traversal ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K4 x 10,000 | RTDL+CuPy 2A1 summary | 40,000 | 60,000 | 30,000 | 13.661 | 7.125 | 2.412 | 4.122 | 2.801 | 0.076 |
| K4 x 10,000 | RTDL+CuPy 1A2 summary | 40,000 | 40,000 | 60,000 | 19.421 | 6.765 | 6.240 | 4.372 | 2.508 | 0.094 |
| K4 x 50,000 | RTDL+CuPy 2A1 summary | 200,000 | 300,000 | 150,000 | 83.132 | 19.805 | 46.855 | 17.196 | 11.833 | 0.180 |
| K4 x 50,000 | RTDL+CuPy 1A2 summary | 200,000 | 200,000 | 300,000 | 91.623 | 20.018 | 51.256 | 15.586 | 7.880 | 0.272 |
| K4 x 100,000 | RTDL+CuPy 2A1 summary | 400,000 | 600,000 | 300,000 | 162.544 | 25.704 | 97.026 | 28.200 | 20.601 | 0.290 |
| K4 x 100,000 | RTDL+CuPy 1A2 summary | 400,000 | 400,000 | 600,000 | 171.575 | 24.726 | 119.204 | 27.641 | 14.900 | 0.439 |

For K4 x 100,000, the same pod had previously measured the pure-Python contract
path at `3244.977 ms` total for 2A1 and `3185.847 ms` total for 1A2 after
skipping the unused id-ascending adapter. A later one-pass no-partner rerun from
the same code measured `3466.177 ms` for 2A1 and `3553.406 ms` for 1A2. The
CuPy partner rows therefore reduce whole-app time by roughly `20x` at this
scale, and reduce the contract-construction phase by more than `100x`.

This does not change the native engine claim boundary. It is evidence that the
Python+partner+RTDL design is the right direction for app-owned preprocessing.
The next bottleneck after the CuPy partner path is benchmark-owned geometry
packing and host/device transfer into the generic OptiX scene, not graph
contract construction.

## Runtime Design Pressure

This app now gives a clear next engine/language target:

1. Keep triangle-counting app logic in Python.
2. Keep the new summary primitives app-agnostic: the engine sees rays,
   triangles, optional ray weights, and scalar reductions only.
3. Move the next optimization frontier to partner/lowering support: prepared
   query buffers, zero-copy or lower-copy column inputs, and partner-resident
   geometry packing.
4. Preserve a behavior-first primitive boundary: no triangle-counting native
   ABI and no graph vocabulary in the OptiX engine.

## Claim Boundary

Authorized now:

- Authors `bs_tc` and `rt_tc` can be built and run on the pod with documented
  compatibility patches.
- RTDL OptiX generic 1A2 and 2A1 mappings match authors/oracle counts on
  deterministic same-input fixtures.
- RTDL now has app-agnostic 3-D ray/triangle scalar summary paths that remove
  the worst row-returning performance failure.
- The current RTDL implementation is semantically faithful; its whole-app
  performance is still dominated by Python preprocessing and lowering.

Not authorized:

- Public speedup wording.
- Claiming paper SNAP dataset reproduction.
- Claiming RTDL beats RT-Graph authors code.
- Treating the compatibility-patched authors build as an unmodified artifact.
- Adding triangle-counting-specific native code to the RTDL engine.
