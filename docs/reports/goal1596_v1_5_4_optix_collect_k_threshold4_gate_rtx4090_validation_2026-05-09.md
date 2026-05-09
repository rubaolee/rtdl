# Goal 1596: Threshold-4 Gated Collect-K Validation

## Verdict

The experimental `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` policy was tightened to require at least four predicted carry payload-copy reductions before enabling the candidate carry-alias behavior. RTX 4090 validation supports this stricter threshold: the strongest copy-reduction cases remain consistently faster, while weaker or noisy cases are excluded from the candidate subpath.

This remains experimental. It does not promote `COLLECT_K_BOUNDED`, does not change default behavior, and does not authorize public speedup wording.

## Policy

The gated mode now activates the candidate carry-alias behavior only when:

```text
baseline_carry_payload_copies >= candidate_carry_payload_copies + 4
```

The opt-in flag still enables the optimized baseline bundle for the collect-k tiled path, but the candidate carry-alias behavior is restricted to the stronger predicted-copy-reduction cases.

## Environment

- Host: `root@103.196.86.82 -p 54445`
- Checkout: `/root/work/rtdl_rtx4090_gated`
- Commit: `9042a86ace691a5dedfdf37e29c5ffbb7f588baa`
- GPU: `NVIDIA GeForce RTX 4090`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Runtime library path: `/usr/local/cuda-12.4/lib64`
- Architecture override: `RTDL_OPTIX_PTX_ARCH=compute_89`

## Validation

Local focused tests:

- `Ran 26 tests`
- `OK`

RTX 4090 focused tests after rebuild:

- `Ran 26 tests`
- `OK`

RTX 4090 measurement:

- Five rounds.
- `31` repeats per case.
- Counts: `65536`, `65537`, `65538`, `65552`, `69632`, `69633`.
- All baseline and gated artifacts reported accepted Goal1506 evidence, parity pass, and expected topology.

## Results

Negative delta means gated mode is faster than the optimized baseline.

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change | Interpretation |
|---:|---:|---:|---|---|
| 65536 | 0.000796 | 4/5 | 0 -> 0 | gate-off, noise-scale |
| 65537 | -0.009974 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 65538 | -0.009972 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 65552 | -0.011182 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 69632 | -0.008774 | 5/5 | 4 -> 0 | gate-on, accepted strong region |
| 69633 | 0.000721 | 3/5 | 4 -> 4 | gate-off, noise-scale |

## Interpretation

The threshold-4 rule is more conservative and better aligned with the measured evidence than the earlier threshold-3 rule:

- It preserves the strongest RTX 4090 wins: `65537`, `65538`, `65552`, and `69632`.
- It excludes `69633`, which was mixed under threshold-3 and becomes a no-op/noise-scale case under threshold-4.
- It keeps `65536` gate-off, where there is no predicted payload-copy reduction.

The current rule is now clear enough for continued internal validation. Before any default behavior change, the same threshold-4 policy should be rerun on RTX 3090 and at least one Ada run should be independently reviewed.

## Claim Boundary

This is internal v1.5.4 experimental evidence only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
