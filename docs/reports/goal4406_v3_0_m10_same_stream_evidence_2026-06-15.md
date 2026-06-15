# Goal4406 V3.0 M10 Same-Stream Evidence Closeout

Date: 2026-06-15

Commit under test: `455219ba`

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Native build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc`

## Conclusion

M10 is complete for same-stream evidence. RTDL now has an app-agnostic native OptiX grouped-union self-query entrypoint that queues on a caller-supplied CUDA stream and returns without an internal stream synchronize. Both CuPy and Numba partner rows prove the exact native producer to partner consumer handoff with CUDA event pairs.

This does not promote true-zero-copy wording. The rows intentionally keep `true_zero_copy_ready=false` because M10 does not attach CUDA transfer-counter or equivalent no-hidden-copy evidence. Same-stream ordering is proven; no-hidden-copy remains a separate gate.

## Results

| Point count | Partner | Host median ms | Native event ms | Partner event ms | Total event ms | Same-stream ready | True-zero-copy ready |
|---:|---|---:|---:|---:|---:|---|---|
| 8,192 | CuPy | 0.421 | 0.292 | 0.005 | 0.297 | true | false |
| 8,192 | Numba | 0.731 | 0.295 | 0.006 | 0.301 | true | false |
| 65,536 | CuPy | 0.889 | 0.761 | 0.005 | 0.766 | true | false |
| 65,536 | Numba | 1.202 | 0.762 | 0.007 | 0.769 | true | false |

The CuPy and Numba validation signatures match for both sizes. The total event-time ratio is effectively parity: CuPy/Numba = `0.989x` at 8,192 points and `0.997x` at 65,536 points.

## Evidence Checks

For each measured row:

- `same_stream_ready=true`
- `native_synchronized_before_return=false`
- CUDA stream pointer in the partner event evidence equals the native metadata stream pointer.
- Event scope names the exact handoff: `prepared_native_optix_launch_to_{cupy,numba}_label_kernel_on_same_stream`
- Validation materialization happens after the measured native-plus-partner event window.
- `public_claim_authorized=false`
- `rt_core_speedup_claim_authorized=false`
- `true_zero_copy_ready=false`

## Artifacts

- 8,192-point JSON: `docs/reports/goal4406_v3_0_m10_same_stream_evidence_8192_2026-06-15.json`
- 65,536-point JSON: `docs/reports/goal4406_v3_0_m10_same_stream_evidence_65536_2026-06-15.json`
- Runner: `scripts/v3_0_m10_same_stream_evidence_measure.py`
- Validator/test: `tests/goal4406_v3_0_m10_same_stream_evidence_test.py`

## Scope Boundary

This is an evidence gate, not a benchmark-app speedup claim. It proves RTDL can hand native OptiX RT work to a Python partner continuation on the same CUDA stream without the previous default-stream synchronize. It does not prove that a benchmark app is faster end to end, and it does not prove true zero copy without transfer counters.
