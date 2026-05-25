# Goal2600: GPU-RMQ Common-Tool Baseline Probe

Status: diagnostic only; not claim-grade performance evidence.

This probe compares the current RTDL GPU-RMQ paper-style OptiX lowering against
a common available tool on the same pod. The pod had NumPy installed, but did
not have CuPy, DuckDB, or pandas installed.

## Environment

- Pod: `root@203.57.40.101 -p 10082`
- Key used from Mac: `~/.ssh/id_ed25519_rtdl_codex`
- GPU: NVIDIA RTX A5000
- Native RTDL OptiX library:
  `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- Baseline available: NumPy `2.1.2`
- Missing tools: CuPy, DuckDB, pandas

## Method

All rows were checked against the RTDL CPU oracle.

- `numpy_slice_argmin`: straightforward per-query NumPy slice plus `argmin`.
- `local_hierarchical`: RTDL app's dependency-light block-summary/sparse-table
  CPU path.
- `rtdl_optix_paper_lowering`: RTDL app's paper-style ray/triangle lowering
  through generic OptiX `ray_triangle_closest_hit`.

Median of three repeats is reported. Timings are end-to-end for each path and
include Python scheduling and setup costs.

## Results

| Case | Values | Queries | NumPy slice argmin | Local hierarchical | RTDL OptiX RT lowering | RTDL / NumPy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `default_repeated` | 4,096 | 1,024 | 0.00257s | 0.00490s | 0.05028s | 19.5x slower |
| `random_mid` | 16,384 | 4,096 | 0.00999s | 0.02844s | 0.23676s | 23.7x slower |
| `large_repeated` | 65,536 | 8,192 | 0.02321s | 0.06454s | 0.87061s | 37.5x slower |

Correctness:

- NumPy: matches CPU oracle in all cases.
- Local hierarchical: matches CPU oracle in all cases.
- RTDL OptiX RT lowering: matches CPU oracle in all cases.

## Interpretation

The current GPU-RMQ RTDL OptiX path is a correctness-ready RT lowering, not a
performance-ready RMQ implementation. It rebuilds/repacks ray and triangle
geometry through Python for each phase, rebuilds acceleration structures, and
returns rows through host memory. Those costs dominate at the tested sizes.

Compared with NumPy's direct slice+argmin baseline, the current RTDL OptiX path
is 19.5x to 37.5x slower. This is expected for the current implementation
because it validates language/runtime expressiveness and generic closest-hit
correctness, not a prepared, partner-resident, throughput-optimized RMQ engine.

Next performance-relevant work would require prepared/static triangle scenes,
partner-resident query/ray generation, persistent device buffers, and separate
timing for build, transfer, traversal, and decode.
