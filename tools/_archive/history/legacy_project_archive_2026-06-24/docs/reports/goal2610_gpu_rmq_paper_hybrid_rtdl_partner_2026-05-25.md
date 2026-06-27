# Goal2610 GPU-RMQ Paper-Hybrid RTDL Partner Path

Date: 2026-05-25

## Purpose

The previous RTDL GPU-RMQ path was an RTXRMQ-style one-level RT lowering:
partition the array into fixed blocks, use RT for element/partial-block and
full-block candidates, and reduce candidates with generic grouped argmin.

The GPU-RMQ paper's stronger design is different. Its CL/interleaved family
builds a multi-level reduction hierarchy, scans edge fragments at lower levels,
and uses RT only for the coarsest fully-contained interval. This report records
the first RTDL implementation of that behavior.

## Implemented

Added app-level implementation in
`examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py`:

- `PaperHybridRmqHierarchy`: fixed-factor reduction hierarchy with value and
  original-index propagation.
- `build_paper_hybrid_hierarchy`: constructs the paper-style level structure.
- `_paper_hybrid_partner_scan_candidates`: scans lower-level edge fragments and
  final small ranges using app-side partner logic.
- `_paper_hybrid_top_rt_query`: computes the coarsest fully-contained RT
  interval using the author-code formula shape.
- `PreparedPaperHybridRtdlPartnerRmq`: reusable app-side handle that keeps the
  hierarchy and prepared top-level RTDL scene across repeated queries.
- `paper_hybrid_rtdl_partner_payload`: benchmark front door mode
  `paper_hybrid_rtdl_partner`.

The native RTDL engine remains app-agnostic. It sees only generic prepared
triangle scenes, ray batches, group maps, values, and tie-break indices.

## Current Partner Boundary

The lower-level edge/final segment work is implemented as an app-level partner
stage. It has a Python-loop fallback for portability, and a NumPy sparse-table
batch path on environments with NumPy. The latest prepared-batch form computes
the partner candidates during `prepare_query_batch` and reuses them across
query repetitions. This is correct for semantics and avoids the first obvious
Python scan bottleneck, but it is still not the final performance partner.
The intended next step is to replace host-side candidate merge/finalization
with a CuPy, Torch, or standalone CUDA partner kernel while keeping the same
app-level scheduler and native RTDL boundary.

This split matches the project rule:

- Python owns RMQ policy, hierarchy, and decomposition.
- Partner owns non-RT scan/reduction work.
- RTDL owns generic RT traversal and grouped argmin.
- Native engine must not contain RMQ-specific formulas.

## Validation

Local validation completed:

```text
PYTHONPATH=src:. python3 -m py_compile examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py scripts/goal2609_gpu_rmq_non_author_baselines.py
PYTHONPATH=src:. python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2598_optix_generic_closest_hit_contract_test
```

Result:

```text
Ran 24 tests in 0.158s
OK (skipped=1)
```

The local tests validate the hierarchy, no-RT-top fallback, scope exposure, the
top-level RT interval formula, and a block-size-1 partial-ray regression found
during pod validation.

## Pod Evidence

RunPod endpoint used:

```text
ssh b908xd2jqzcq9o-64412254@ssh.runpod.io -i ~/.ssh/id_ed25519
Jupyter: https://b908xd2jqzcq9o-8888.proxy.runpod.net/lab
```

The SSH proxy was not usable from this Mac because the local default key path
did not exist and the alternate RTDL key was rejected by the proxy. Files and
commands were executed through the Jupyter HTTP/kernel API instead.

Pod environment:

- GPU: NVIDIA RTX PRO 4000 Blackwell, compute capability 12.0.
- Driver: 580.159.04.
- CUDA compiler: `/usr/local/cuda/bin/nvcc`.
- OptiX SDK: installed from local
  `NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh` into
  `/workspace/optix8`.
- RTDL OptiX library: built with
  `make build-optix OPTIX_PREFIX=/workspace/optix8 CUDA_PREFIX=/usr/local/cuda`.
- Repo clone: `/workspace/rtdl_goal2610`, base commit
  `dc6b91d29a37ad335e2ebe0cf553cd01606530fc`, plus local overlay files from
  this goal.

Native OptiX validation:

```text
python3 scripts/goal2598_optix_closest_hit_validation.py --backend optix --skip-gpu-rmq
overall_matches_cpu_reference: true
```

RT-enabled hybrid smoke:

```text
mode: paper_hybrid_rtdl_partner
value_count: 4096
query_count: 1000
reduction_factor: 32
scan_threshold: 64
rt_top_block_size: 1
matches_cpu_reference: true
rt_used: true
partner_mode: numpy_level_sparse_table_batch_prepared
query_median_ms: 0.840
```

The smoke initially failed correctness because the app-side left-partial ray
formula used the cell midpoint instead of the same-block endpoint formula for
`[left, block_end]`. This was exposed by `block_size=1` top-level RT queries.
The fix updates both scalar and vectorized ray packers:

- left partial z: `(block_size - 1 - eps) / block_size`;
- right partial y: `eps / block_size`.

This is app-side lowering logic, not a native-engine RMQ customization.

After correctness was fixed, an app-level NumPy sparse-table partner was added
for lower-level edge/final segment minima. This keeps native RTDL unchanged and
replaces per-element Python scans with O(1) segment minima over the hierarchy
levels. A follow-up batched path answers segment candidates by level and reduces
by query with NumPy arrays. On the 4K/1K smoke case this reduced the hybrid
median from about 13.8 ms to about 3.0 ms. The latest prepared-batch path moves
the partner candidate arrays into `prepare_query_batch`, so repeated query
execution only merges already prepared partner candidates with the RT output.
That drops the same 4K/1K smoke query median to about 0.84 ms.

## Non-Author Baseline Matrix

Command:

```text
python3 scripts/goal2609_gpu_rmq_non_author_baselines.py \
  --repeats 12 \
  --threads 16 \
  --reduction-factor 32 \
  --scan-threshold 64 \
  --rt-top-block-size 1 \
  --out docs/reports/goal2610_gpu_rmq_paper_hybrid_non_author_baselines_2026-05-25.json
```

CUDA baseline compilation automatically detected Blackwell and used:

```text
-gencode arch=compute_120,code=sm_120
```

Query-only median times:

| Dataset | Values | Queries | CPU OpenMP Sparse | CUDA Sparse | RTDL One-Level Prepared | RTDL Paper-Hybrid |
|---|---:|---:|---:|---:|---:|---:|
| repeated | 4,096 | 1,000 | 0.0108 ms | 0.0090 ms | 0.2470 ms | 0.8046 ms |
| random | 16,384 | 4,000 | 0.0805 ms | 0.0252 ms | 0.4165 ms | 3.2135 ms |
| repeated | 65,536 | 8,000 | 0.2966 ms | 0.0479 ms | 0.8528 ms | 7.4846 ms |

All RTDL rows matched the CPU reference. The paper-hybrid rows used
`partner_mode = numpy_level_sparse_table_batch_prepared`.

## Performance Conclusion

The paper-hybrid implementation is now semantically correct and uses native
RTDL for the coarsest fully-contained interval, but it is not performance-ready.
The prepared NumPy sparse-table partner removed the obvious per-element Python
scan bottleneck and avoids rebuilding partner candidate arrays during repeated
query execution, but host-side partner/RT result merging and RT result download
still dominate runtime. `partner_candidate_count` was 3,374, 15,021, and 30,733
across the three workloads. The older one-level prepared RTDL path is still
about 3.3x to 8.8x faster than the paper-hybrid path on these fixtures, and
the standalone CUDA sparse-query baseline is still about 89x to 156x faster.

The next optimization is therefore app/partner/runtime boundary work: keep the
paper-style hierarchy scheduler and generic RTDL top-level boundary, but move
partner/RT merge and candidate finalization closer to device-resident data.
RT traversal is not the current bottleneck.

## Claim Boundary

This report authorizes only an internal correctness and non-author baseline
statement for the paper-hybrid RTDL path. It does not authorize a speedup claim,
a paper-code comparison claim, or a public GPU-RMQ reproduction claim. Those
still require author-code comparison on the special CUDA/OptiX pod.
