# Goal3565 RayDB Sum Fast Path A5000 Evidence

Date: 2026-06-06

## Purpose

Goal3563 closed the measurement-advisory debt from Goal3560 but showed that
RayDB `sum` was no longer just one-run noise: over five alternating trials it
measured `0.956948x` against the v2.3 overlay.

Goal3564 added a generic native fast path for dense small-group grouped-i64
`sum` and `sum_count`: for `group_capacity <= 1024`, the generated CUDA kernel
accumulates per-block counts and sums in shared memory, then emits one global
atomic per group per block. This reduces global atomic contention for small
dense group-key workloads without adding any RayDB-specific ABI or engine logic.

Goal3565 validates that fast path on the A5000 pod.

## Pod Evidence

Artifact directory:

`docs/reports/goal3565_raydb_sum_fastpath_a5000/`

Pod:

- SSH target: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- v2.3 overlay root: `/root/rtdl_goal3556_v23_overlay`
- v2.9 root: `/root/rtdl_goal3556_current`
- v2.3 source commit: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.9 source commit: `bdcf53b313a4782bef38856703a2707d673b00e7`

## Results

Protocol:

- copies: `120000`
- warmup: `2`
- repeat: `20000`
- primary scalar: `metadata.timings.query_median_sec`
- sum trials: 5 alternating trials per lane
- count sanity trials: 3 alternating trials per lane

| Mode | v2.3 median sec | v2.9 median sec | v2.9 speedup |
| --- | ---: | ---: | ---: |
| sum | 0.000751490 | 0.000473938 | 1.585627x |
| count | 0.000588950 | 0.000583647 | 1.009085x |

Per-trial scalar values:

| Mode | Lane | Trial values |
| --- | --- | --- |
| sum | v2.3 | 0.000738876, 0.000793541, 0.000751490, 0.000789295, 0.000746052 |
| sum | v2.9 | 0.000454409, 0.000493076, 0.000473938, 0.000453945, 0.000493784 |
| count | v2.3 | 0.000589445, 0.000588950, 0.000587152 |
| count | v2.9 | 0.000552943, 0.000583647, 0.000590804 |

## Interpretation

The RayDB `sum` weak row is repaired for this internal A5000 same-contract
probe. The improvement comes from a generic runtime technique: replacing
row-level global atomics into a tiny dense group array with block-local shared
memory accumulation, then a much smaller number of global atomics.

The fast path is intentionally generic:

- native kernel name: `device_column_grouped_i64_small_group_kernel`
- operations: `sum`, `sum_count`
- threshold: `group_capacity <= 1024`
- app-specific native logic: `False`

Count remains near parity-positive (`1.009x`) in the sanity probe. The fast path
does not alter the count operation selector.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3565_raydb_sum_fastpath_a5000_test tests.goal3564_grouped_i64_small_group_sum_fastpath_test tests.goal3563_raydb_5trial_and_rtdbscan_advisory_cleanup_test
```

Pod validation:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
RayDB sum 5 alternating trials: 1.585627x
RayDB count 3 alternating sanity trials: 1.009085x
```

## Next Step

Refresh the v2.9 full packet or a compact updated summary so the v2.9 table no
longer carries the stale Goal3558 RayDB sum value.
