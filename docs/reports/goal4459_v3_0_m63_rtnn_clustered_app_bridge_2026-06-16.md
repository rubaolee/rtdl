# Goal4459 / V3.0 M63 - RTNN Clustered App-Bridge Evidence

Status: complete internal V3 evidence.

M63 extends the current RTNN resident app-front-door bridge beyond the uniform
large row. It runs the same prepared graph plus same-stream partner continuation
contract on a clustered 1,048,576-point resident search scene with 65,536-query
batches and 1,000 measured repeats.

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m25_rtnn_app_bridge_measure.py \
  --point-count 1048576 \
  --query-count 65536 \
  --distribution clustered \
  --warmups 2 \
  --repeats 1000 \
  --numba-cuda-home /usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc \
  --output docs/reports/goal4459_v3_0_m63_rtnn_app_bridge_clustered_1048576q65536_r1000_2026-06-16.json
```

Hardware: NVIDIA RTX 4000 Ada Generation pod, driver 550.127.08.

## Result

Both partner rows validate the same compact signature, use CUDA graph replay,
run the partner reduction on the same stream, and keep device-result
materialization after the hot window.

| Distribution | Resident search points | Query batch | Partner | Hot median per batch | 1000-repeat hot total | Estimated 1M-query total by 16 batches | Signature |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| clustered | 1,048,576 | 65,536 | CuPy | 130.079 ms | 130.079 s | 2.081 s | matched |
| clustered | 1,048,576 | 65,536 | Numba | 131.442 ms | 131.442 s | 2.103 s | matched |

The partner ratio is near parity:

| Comparison | Ratio |
| --- | ---: |
| Numba / CuPy hot median | 1.010x slower |

## Reading

This is not a toy row. The hot batch time is about 26x heavier than the M47
uniform app bridge row, while preserving the same app-front-door contract and
the same no-hidden-copy gates. The result says the resident graph bridge works
on a dense clustered distribution, not just the uniform happy path.

The result should not be collapsed into Goal4381 exact aggregate rows. Goal4381
is exact float64 aggregate evidence for OptiX-vs-Embree. M63 is the resident
float32 app bridge with explicit CuPy and Numba partner reductions. Keep those
contracts separate.

## Claim Boundary

What M63 can say:

- RTNN app-front-door graph bridge now has large uniform and clustered evidence.
- CuPy and Numba both pass signature parity on clustered 1M/65K repeat-1000.
- The hot path uses CUDA graph replay and same-stream partner reduction.
- The result is decision-grade partner evidence, not a sub-millisecond smoke.

What M63 cannot say:

- It is not full RTNN paper reproduction.
- It is not an official RTNN authors-code comparison.
- It is not exact float64 OptiX-vs-Embree wording.
- It does not authorize arbitrary ANN-index speedup wording.
- It does not authorize automatic partner or exact-vs-float32 route selection.

## Artifacts

- `docs/reports/goal4459_v3_0_m63_rtnn_app_bridge_clustered_1048576q65536_r1000_2026-06-16.json`
- `tests/goal4459_v3_0_m63_rtnn_clustered_app_bridge_test.py`
