# Goal 1593: OptiX Collect-K Gated Candidate Mode

## Verdict

Implemented `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` as an experimental opt-in mode for the OptiX `COLLECT_K_BOUNDED` path. The gated mode keeps the optimized baseline bundle active, then enables the fastest-candidate carry-alias behavior only when static topology prediction says it reduces carry payload copies.

RTX 3090 validation passed parity and topology checks. The result supports the gated direction, but it does not promote `COLLECT_K_BOUNDED`, does not change default behavior, and does not authorize public speedup wording.

## Implementation

- Native implementation: `src/native/optix/rtdl_optix_api.cpp`
- Probe model and expected topology: `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py`
- Tests: `tests/goal1593_v1_5_4_optix_collect_k_gated_candidate_test.py`

The first gated attempt was corrected after RTX 3090 validation showed that gate-off cases fell back to the raw default path. The corrected behavior is:

- `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` enables the optimized baseline bundle.
- The candidate carry-alias behavior is enabled only when predicted candidate carry payload copies are fewer than predicted baseline carry payload copies.
- Default behavior remains unchanged without the opt-in flag.

## Local Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1593_v1_5_4_optix_collect_k_gated_candidate_test tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test tests.goal1590_v1_5_4_optix_cuda_toolchain_diagnostics_test
```

Result:

- `Ran 26 tests`
- `OK`

## RTX 3090 Validation

Environment:

- Host: `root@213.192.2.74 -p 40053`
- Checkout: `/root/work/rtdl_rtx3090`
- Commit: `942970e16db8240c7f7af007ccf2a2e513a2c127`
- GPU: `NVIDIA GeForce RTX 3090`
- Driver: `580.126.20`
- CUDA toolkit: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Runtime library path: `/usr/local/cuda-12.4/lib64`
- Architecture override: `RTDL_OPTIX_PTX_ARCH=compute_86`

Pod validation:

- Rebuilt `build/librtdl_optix.so` from commit `942970e16db8240c7f7af007ccf2a2e513a2c127`.
- Focused tests: `Ran 26 tests`, `OK`.
- Three measured rounds compared optimized baseline versus gated mode on boundary counts.
- All baseline and gated profile artifacts reported accepted evidence, parity pass, and expected topology.

## RTX 3090 Boundary Results

Negative delta means gated mode is faster than the optimized baseline.

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change |
|---:|---:|---:|---|
| 49152 | -0.004263 | 3/3 | 1 -> 0 |
| 49153 | -0.005960 | 3/3 | 3 -> 1 |
| 49154 | -0.002050 | 1/3 | 3 -> 1 |
| 65535 | -0.000797 | 2/3 | 0 -> 0 |
| 65536 | 0.003477 | 0/3 | 0 -> 0 |
| 65537 | -0.014750 | 3/3 | 5 -> 0 |
| 65538 | -0.018233 | 3/3 | 5 -> 0 |
| 65552 | -0.011567 | 3/3 | 5 -> 0 |
| 69632 | -0.012066 | 3/3 | 4 -> 0 |
| 69633 | -0.007280 | 3/3 | 4 -> 1 |

## Interpretation

The corrected gated mode solves the previous broad-preset problem: it avoids falling back to the raw default path and focuses candidate behavior on predicted copy-reduction cases.

The strongest evidence remains around payload-copy reductions:

- `65537`, `65538`, `65552`: `5 -> 0` payload copies and 3/3 faster rounds.
- `69632`, `69633`: `4 -> 0` or `4 -> 1` payload copies and 3/3 faster rounds.
- `49152` and `49153`: smaller but consistent wins on this RTX 3090 run.

The weak evidence remains around no-copy-reduction cases:

- `65536` has `0 -> 0` payload-copy change and was slower in all three rounds.
- `65535` has `0 -> 0` payload-copy change and is effectively noise-scale.

## Next Hardware Need

RTX 3090 gives non-Ada evidence. Before considering any default behavior change, the corrected gated mode needs a same-contract Ada rerun, preferably RTX 4090 or RTX 4000 Ada, using the same counts and repeats. That Ada run should verify that `65536` does not regress materially and that the copy-reduction regions remain positive.

## Claim Boundary

This is internal v1.5.4 experimental evidence only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
