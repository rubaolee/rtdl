# Goal2639 Aggregate-Frontier Native ABI Contract

Date: 2026-05-27

Status: local contract/specification complete; Embree native slice implemented;
OptiX native symbol implemented with pod parity evidence and host-side timing
baseline; RT-core speedup evidence remains future work.

## Purpose

Goal2638 accepted `AGGREGATE_FRONTIER_COLLECT_2D` as a CPU-reference and
partner-column candidate primitive. The next local step was to specify the
native C ABI target and implement the Embree side when local Embree was
available.

This document records that ABI boundary and the first local native backend
implementations. It is not RT-core speedup evidence, not an RT-core speedup
claim, and not a Barnes-Hut whole-app claim.

## Contract Name

`generic_aggregate_frontier_collect_2d_native_abi_v1`

Python API:

`rtdsl.aggregate_frontier_collect_native_abi_contract()`

Validation API:

`rtdsl.validate_aggregate_frontier_collect_native_abi_contract()`

Native symbols in this ABI family:

- `rtdl_embree_collect_aggregate_frontier_2d`
- `rtdl_optix_collect_aggregate_frontier_2d`

## ABI Shape

The ABI is app-name-free. It accepts source point rows, DFS-ordered aggregate
tree nodes, and CSR-style child/member arrays. It emits row-major int64
frontier rows plus per-source row offsets.

Source point fields:

- `id:int64`
- `x:float64`
- `y:float64`

Tree node fields:

- `id:int64`
- `cx:float64`
- `cy:float64`
- `half_size:float64`
- `depth:int32`
- `dfs_index:int64`
- `resume_index:int64_sentinel_minus_one`
- `is_leaf:uint8`

CSR inputs:

- `child_offsets:uint64[node_count+1]`
- `child_ids:int64[child_count]`
- `member_offsets:uint64[node_count+1]`
- `member_ids:int64[member_count]`

Output row schema:

`source_id, frontier_kind_code, item_id, owner_aggregate_id, dfs_index, resume_index, metadata_flags`

## Overflow Semantics

The ABI inherits the primitive's exact fail-closed policy:

- If `overflowed_out == 0`, `frontier_rows_out`, `row_offsets_out`, and
  `emitted_count_out` are valid.
- If `overflowed_out == 1`, `emitted_count_out` must be `0`.
- On overflow, `frontier_rows_out` and `row_offsets_out` are invalid partial
  workspace and must not be surfaced by Python.
- `attempted_count_out` is diagnostic only.

This keeps the native contract aligned with the Python reference: no
truncation, no partial result, and no downstream scoring after overflow.

## Explicit Non-Ownership

The native ABI does not own:

- force laws;
- scoring;
- app reductions;
- time integration;
- benchmark-specific logic;
- paper-specific shortcuts.

The engine may collect generic frontier IDs. App or partner code remains
responsible for any workload-specific computation over those IDs.

## Current Implementation Boundary

Local code now exposes and tests the ABI contract. The Embree lowering plan
reports:

`implemented_embree_native_symbol_optix_parity_validated_timing_baseline_recorded`

The OptiX lowering plan now reports:

`implemented_optix_native_symbol_pod_parity_validated_timing_baseline_recorded`

That is intentional. The native symbol is app-name-free and emits only generic
frontier rows. Pod parity and host-side timing evidence exist below, but RT-core
speedup evidence is still future work.

## Local Verification

Expected local check:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2639_aggregate_frontier_native_abi_contract_test
```

This test verifies the ABI is app-independent, fail-closed, linked from current
Embree/OptiX lowering plans, and that the local native symbols match the CPU
reference when the corresponding backend libraries are available. It does not
enable performance claims.

## Pod Verification

Pod access used for Goal2639 evidence:

```text
ssh root@66.92.198.226 -p 11132 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment summary:

- GPU: NVIDIA L4, driver 570.195.03
- CUDA: 12.8, `nvcc` at `/usr/local/cuda/bin/nvcc`
- OptiX SDK: `/root/optix-sdk-8.1`
- Embree installed from Ubuntu packages: `libembree-dev` 4.3.0

Evidence commands:

```bash
make build-optix OPTIX_PREFIX=/root/optix-sdk-8.1 CUDA_PREFIX=/usr/local/cuda -j1
nm -D build/librtdl_optix.so | grep rtdl_optix_collect_aggregate_frontier_2d
RTDL_FORCE_EMBREE_REBUILD=1 RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
  PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2639_aggregate_frontier_native_abi_contract_test
```

Observed result:

- `librtdl_optix.so` exports `rtdl_optix_collect_aggregate_frontier_2d`.
- `tests.goal2639_aggregate_frontier_native_abi_contract_test`: 8 tests OK.
- The pod run included Embree parity, Embree fail-closed overflow, OptiX parity,
  and OptiX fail-closed overflow checks.

This authorizes the narrow statement that the generic native row-collection ABI
has same-contract Embree/OptiX parity evidence for the tested fixtures. It does
not authorize RT-core speedup wording.

## Timing Baseline

Timing artifact:

`docs/reports/goal2639_aggregate_frontier_native_timing_2026-05-27.json`

The timing run measured only row collection for generated Barnes-Hut-style
inputs. It validated identical row outputs before recording times.

Summary:

| Bodies | Frontier rows | CPU reference median | Embree native median | OptiX native median |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 28,988 | 0.0682 s | 0.0654 s | 0.0624 s |
| 2,048 | 153,976 | 0.4081 s | 0.3723 s | 0.3502 s |
| 8,192 | 750,173 | 1.8777 s | 1.9935 s | 1.9128 s |

Interpretation: this timing establishes a baseline for the current host-side
native row collectors. It does not show RT-core acceleration, and it should not
be used as Barnes-Hut whole-app performance evidence.

## Larger Embree-vs-OptiX Row-Collector Run

Timing artifact:

`docs/reports/goal2639_aggregate_frontier_embree_optix_perf_pod_2026-05-27.json`

Command:

```bash
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so PYTHONPATH=src:. \
  python3 scripts/goal2639_aggregate_frontier_perf.py \
  --sizes 2048,8192,16384,32768 \
  --output docs/reports/goal2639_aggregate_frontier_embree_optix_perf_pod_2026-05-27.json
```

Summary:

| Bodies | Frontier rows | Embree median | OptiX median | OptiX/Embree |
| ---: | ---: | ---: | ---: | ---: |
| 2,048 | 153,976 | 0.3625 s | 0.3581 s | 1.01x |
| 8,192 | 750,173 | 1.9484 s | 1.8766 s | 1.04x |
| 16,384 | 2,182,950 | 5.7010 s | 5.6741 s | 1.00x |
| 32,768 | 3,577,098 | 9.9200 s | 9.8099 s | 1.01x |

Interpretation: OptiX-library row collection is consistently a little faster
than Embree row collection on this pod, but only by about 0.5-4%. That is useful
same-contract baseline data, not evidence that the RT cores are accelerating the
aggregate-frontier traversal. The next real performance step is a true RT-core
aggregate-frontier traversal/collection design; the current native symbol is
host-side generic traversal packaged in the OptiX backend library.
