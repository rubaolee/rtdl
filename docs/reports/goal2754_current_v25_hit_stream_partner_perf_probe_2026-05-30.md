# Goal2754 Current v2.5 Hit-Stream Partner Perf Probe

Date: 2026-05-30

Pod: `69.30.85.171`, NVIDIA RTX A5000, driver 570.211.01

Commit: `02c049fd809c2d8e1cad5c2a1de8d9b7024697da`

Artifact:
`docs/reports/goal2754_pod_artifacts/goal2754_current_v25_hit_stream_partner_perf_probe_69_30_85_171_2026-05-30.json`

## Purpose

After Goals2748, 2750, and 2752 hardened the v2.5 hit-stream/partner boundary,
we ran a current pod probe to check the steady-state cost of two OptiX paths:

- `paper_rt_optix_prepared_grouped_reduction`: fused prepared native grouped
  primitive;
- `paper_rt_optix_device_hit_stream_triton_prepared`: generic native
  hit-stream columns plus typed payload gather plus Triton continuation.

This probe is diagnostic. It does not authorize speedup or true-zero-copy
wording.

## Command

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so
timeout 1800 python3 scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py \
  --row-counts 10000,50000 \
  --group-count 128 \
  --modes count,sum,min,max,avg_as_sum_count \
  --backends paper_rt_optix_prepared_grouped_reduction,paper_rt_optix_device_hit_stream_triton_prepared \
  --repeats 3 \
  --warmup 1 \
  --output docs/reports/goal2754_pod_artifacts/goal2754_current_v25_hit_stream_partner_perf_probe_69_30_85_171_2026-05-30.json
```

All cases matched the CPU reference.

## Results

| Rows | Mode | Fused grouped primitive sec | Generic hit-stream + Triton sec | Generic-path slowdown | Hit rows | Same-pointer adapter evidence |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 10000 | count | 0.000184 | 0.005425 | 29.5x | 27 | true |
| 10000 | sum | 0.000289 | 0.023134 | 80.2x | 27 | true |
| 10000 | min | 0.000301 | 0.035742 | 118.8x | 27 | true |
| 10000 | max | 0.000290 | 0.026243 | 90.5x | 27 | true |
| 10000 | avg_as_sum_count | 0.000294 | 0.029102 | 99.0x | 27 | true |
| 50000 | count | 0.000237 | 0.007753 | 32.7x | 119 | true |
| 50000 | sum | 0.000652 | 0.096478 | 147.9x | 119 | true |
| 50000 | min | 0.000678 | 0.094830 | 139.9x | 119 | true |
| 50000 | max | 0.000650 | 0.095878 | 147.5x | 119 | true |
| 50000 | avg_as_sum_count | 0.000669 | 0.085693 | 128.1x | 119 | true |

## Interpretation

This is not a generic hit-stream failure. It confirms the v2.5 planner rule:
use fused generic primitives when the requested continuation is one of the
engine's native reductions, and reserve generic hit-stream + partner
continuation for cases where the continuation is not expressible as a fused
primitive.

The generated fixture has very few hit rows: 27 hit rows for 10000 input rows
and 119 hit rows for 50000 input rows. In that regime, the generic path pays
fixed overhead for native hit-stream column handoff, CUDA-array to Torch carrier
adaptation, typed payload gather, and Triton launch/continuation. The fused
primitive avoids that overhead by reducing during the RT traversal pipeline.

## Useful Positive Evidence

- `all_correct=true`.
- Native device hit-stream column path is used.
- Host row bridge is bypassed.
- Same-pointer Torch carrier evidence is observed for the adapter.
- Claim flags remain conservative:
  `true_zero_copy_authorized=false` and `no_public_speedup_claim=true`.

## Design Consequence

The next real performance leap for hit-stream + partner continuation is not
another app-shaped shortcut. It is either:

- a real unfused workload where the partner continuation does enough work to
  amortize hit-stream handoff overhead; or
- deeper runtime work: event/same-stream ordering, no host synchronization,
  fused gather+continuation, and device-resident row-count/overflow handling.

Until then, v2.5 should keep the primitive-first planner behavior for scalar
grouped reductions.
