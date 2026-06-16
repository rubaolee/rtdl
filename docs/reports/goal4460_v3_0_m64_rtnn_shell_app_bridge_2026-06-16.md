# Goal4460 / V3.0 M64 - RTNN Shell App-Bridge Evidence

Status: complete internal V3 evidence.

M64 closes the distribution gap in the current RTNN resident app-front-door
bridge. The app CLI already exposed `--distribution shell`, but the underlying
generic M19 ranked-summary graph bridge only accepted `uniform` and `clustered`.
M64 adds `shell` to that generic point generator and records a large pod row
under the same prepared graph plus same-stream CuPy/Numba partner contract.

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m25_rtnn_app_bridge_measure.py \
  --point-count 1048576 \
  --query-count 65536 \
  --distribution shell \
  --warmups 2 \
  --repeats 1000 \
  --numba-cuda-home /usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc \
  --output docs/reports/goal4460_v3_0_m64_rtnn_app_bridge_shell_1048576q65536_r1000_2026-06-16.json
```

Hardware: NVIDIA RTX 4000 Ada Generation pod, driver 550.127.08.

## Result

Both partner rows validate the same compact signature, use CUDA graph replay,
run the partner reduction on the same stream, and keep device-result
materialization after the hot window.

| Distribution | Resident search points | Query batch | Partner | Hot median per batch | 1000-repeat hot total | Estimated 1M-query total by 16 batches | Signature |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| shell | 1,048,576 | 65,536 | CuPy | 38.588 ms | 38.588 s | 0.617 s | matched |
| shell | 1,048,576 | 65,536 | Numba | 39.267 ms | 39.267 s | 0.628 s | matched |

The partner ratio remains near parity:

| Comparison | Ratio |
| --- | ---: |
| Numba / CuPy hot median | 1.018x slower |

## Distribution Reading

The resident graph-bridge route now has three large repeat-1000 distribution
rows under the same 1,048,576-point / 65,536-query app-bridge contract:

| Distribution | CuPy hot median per batch | Numba hot median per batch | Reading |
| --- | ---: | ---: | --- |
| uniform | 4.988 ms | 5.020 ms | lightest M47 row |
| shell | 38.588 ms | 39.267 ms | medium surface-like stress row |
| clustered | 130.079 ms | 131.442 ms | heaviest M63 clustered row |

This is better than a single pretty number. It shows the same RTDL app bridge is
distribution-sensitive while preserving signature parity, CUDA graph replay,
same-stream partner continuation, and no-hidden-column-copy hot-window gates.

## Claim Boundary

What M64 can say:

- RTNN app-front-door graph bridge now has large uniform, shell, and clustered
  distribution evidence.
- Shell support is in the generic M19 ranked-summary graph bridge, not in an
  RTNN-specific native ABI.
- CuPy and Numba both pass signature parity on shell 1M/65K repeat-1000.
- The hot path uses CUDA graph replay and same-stream partner reduction.
- The result is decision-grade partner evidence, not a sub-millisecond smoke.

What M64 cannot say:

- It is not full RTNN paper reproduction.
- It is not an official RTNN authors-code comparison.
- It is not exact float64 OptiX-vs-Embree wording.
- It does not authorize arbitrary ANN-index speedup wording.
- It does not authorize automatic partner or exact-vs-float32 route selection.
- It does not claim the synthetic shell row is a paper dataset.

## Artifacts

- `docs/reports/goal4460_v3_0_m64_rtnn_app_bridge_shell_1048576q65536_r1000_2026-06-16.json`
- `tests/goal4460_v3_0_m64_rtnn_shell_app_bridge_test.py`
