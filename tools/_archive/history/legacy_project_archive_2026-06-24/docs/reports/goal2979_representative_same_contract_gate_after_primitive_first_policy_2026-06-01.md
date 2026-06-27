# Goal2979 Representative Same-Contract Gate After Primitive-First Policy

Date: 2026-06-01

Status: RTX 4000 Ada representative gate passed on current main

## Purpose

Goal2978 encoded the v2.5 closeout rule from the Claude roadmap: use a fused
app-agnostic RTDL primitive first when it exactly satisfies the requested
continuation, use partners only for unfused continuations or explicit app/user
choice, and never auto-select Triton simply because Triton is available.

Goal2979 runs the next C-2 check from that roadmap on three representative
shapes:

1. RayDB-style scalar grouped reductions, where the fused RTDL primitive should
   beat typed hit-stream plus Triton and remain the selected path.
2. RT-DBSCAN grouped-stream continuation, where RTDL should avoid materializing
   the full neighbor stream and hand the continuation to a partner path.
3. Barnes-Hut-style grouped vector reduction pressure, where partner choice is
   measured under the same contract instead of assumed.

## Pod Environment

Target: `root@157.157.221.29 -p 22722`

GPU: `NVIDIA RTX 4000 Ada Generation, 565.57.01`

Source commit: `6fd7be7c9ab20b2128634cfffb6e673caf2c8824`

Toolchain:

- CUDA: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk` pinned to OptiX 8.1 headers
- RTDL OptiX library: `/tmp/rtdl_goal2977_rtx4000ada/build/librtdl_optix.so`
- RTDL Embree library: `/tmp/rtdl_goal2977_rtx4000ada/build/librtdl_embree.so`

Artifacts:

- `docs/reports/goal2979_same_contract_representative_gate_pod/raydb_raw_current.json`
- `docs/reports/goal2979_same_contract_representative_gate_pod/raydb_current.json`
- `docs/reports/goal2979_same_contract_representative_gate_pod/rt_dbscan.json`
- `docs/reports/goal2979_same_contract_representative_gate_pod/vector_partner.json`

## Results

### RayDB Primitive-First Control

Fresh run command:

```text
python3 scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py \
  --row-counts 250000,1000000 \
  --group-count 256 \
  --modes count,sum \
  --backends paper_rt_optix,paper_rt_optix_v2_5_primitive_first,paper_rt_optix_device_hit_stream_triton_prepared \
  --repeats 3 \
  --warmup 1 \
  --output /tmp/goal2979_same_contract_gate/raydb_raw_current.json
python3 scripts/goal2896_raydb_same_contract_performance_decision_gate.py \
  --input /tmp/goal2979_same_contract_gate/raydb_raw_current.json \
  --output /tmp/goal2979_same_contract_gate/raydb_current.json
```

| Rows | Mode | Primitive-first sec | Typed hit-stream + Triton sec | Hit-stream slowdown |
| ---: | --- | ---: | ---: | ---: |
| 250000 | count | `0.000384` | `0.016848` | `43.850x` |
| 250000 | sum | `0.001984` | `0.347557` | `175.151x` |
| 1000000 | count | `0.000396` | `0.011308` | `28.533x` |
| 1000000 | sum | `0.002303` | `0.351926` | `152.819x` |

Interpretation: the primitive-first rule remains correct for this shape. The
typed hit-stream plus Triton path is real and hardware-proven, but this exact
continuation is already expressible by the fused generic RTDL primitive, so
forcing Triton would be the slower and less honest route.

### RT-DBSCAN Grouped-Stream Continuation

Fresh run command:

```text
python3 scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py \
  --point-count 32768 \
  --point-count 65536 \
  --point-count 131072 \
  --repeat-count 3 \
  --raw-output-dir /tmp/goal2979_same_contract_gate/raw_dbscan \
  --output /tmp/goal2979_same_contract_gate/rt_dbscan.json
```

| Points | Prepared CuPy grid sec | RT grouped-stream sec | Speedup vs prepared CuPy grid | Planned continuation |
| ---: | ---: | ---: | ---: | --- |
| 32768 | `0.164768` | `0.042738` | `3.855x` | `optix_rt_core_adjacency_cupy_components_3d` |
| 65536 | `0.529003` | `0.107296` | `4.930x` | `optix_rt_core_grouped_stream_cupy_components_3d` |
| 131072 | `1.628180` | `0.358402` | `4.543x` | `optix_rt_core_grouped_stream_cupy_components_3d` |

The artifact records:

- `grouped_stream_rt_core_accelerated: true`
- `grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream: true`
- `signatures_match: true`
- `source_dirty: []`

Interpretation: this is the representative case where partner continuation is
needed. The native side emits a grouped stream without materializing the large
neighbor rows/full directed adjacency stream, and the partner path handles the
component continuation.

### Grouped Vector-Sum Partner Choice

Fresh run command:

```text
python3 - <<'PY'
from pathlib import Path
from scripts.goal2932_cupy_presegmented_vector_sum_tuning import run_goal2932
run_goal2932(
    group_count=8192,
    rows_per_group=16,
    repeats=5,
    warmups=2,
    output=Path("/tmp/goal2979_same_contract_gate/vector_partner.json"),
)
PY
```

| Candidate | Median sec |
| --- | ---: |
| `cupy_add_at` | `0.000381` |
| `cupy_offsets_rawkernel` | `0.000474` |
| `torch_scatter_add` | `0.000759` |
| `triton_offsets` | `0.004901` |

The artifact records:

- all candidates match the Torch reference;
- `triton_over_torch: 6.458x`;
- `cupy_offsets_over_torch: 0.624x`;
- winner: `cupy_add_at`.

Interpretation: this confirms the policy shape. Partner selection is a
same-contract measurement, not a brand preference. For this small presegmented
vector-sum pressure point, CuPy wins; Triton remains a valid preview backend but
is not automatically selected.

## C-2 Verdict

The representative C-2 gate passes.

| Shape | Question | Result |
| --- | --- | --- |
| RayDB scalar grouped reductions | Does primitive-first remain the right fast path when a fused generic primitive exists? | Yes; typed hit-stream + Triton is `28.533x` to `175.151x` slower. |
| RT-DBSCAN grouped stream | Does a partner continuation still matter when the fused primitive does not express the full continuation? | Yes; grouped stream is `3.855x` to `4.930x` faster than prepared CuPy grid and avoids giant stream materialization. |
| Grouped vector sum | Can partner choice be evidence-driven rather than Triton-first? | Yes; CuPy wins this same-contract shape, while Triton remains available but not promoted. |

## Boundary

Goal2979 is internal v2.5 closeout evidence. It does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

The remaining closeout items from the Claude roadmap are C-3 neutral-seam
scope/closure decision and C-4 closeout report, followed by external review
before any user-requested release packet.
