# Goal1453 RTX 2000 Ada Latest-Main Validation

## Verdict

Accepted as latest-main RTX environment validation for the v1.5.2 prepared
host-output evidence path. This is not a performance claim, not true zero-copy
evidence, not public speedup wording, not stable primitive promotion, and not a
release action.

## Run Scope

- Pod SSH target: `root@157.157.221.29 -p 57142`
- Key source used: `Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Git HEAD: `3a6dd3fbf2265b4ed83add1b1bb9bd2345dd25a8`
- GPU: NVIDIA RTX 2000 Ada Generation, 16 GB
- Driver: `570.195.03`
- CUDA driver capability reported by `nvidia-smi`: `12.8`
- CUDA compiler used: `/usr/local/cuda-12.4/bin/nvcc`
- OptiX headers: `/root/vendor/optix-dev`

## Validation

- Focused/latest collect slice:
  `docs/reports/goal1453_rtx2000ada_validation_2026-05-07/goal1453_collect_slice.log`
- Result: `Ran 92 tests ... OK`
- Required prepared host-output parity:
  `docs/reports/goal1453_rtx2000ada_latest_main_required_2026-05-07/goal1450_prepared_host_output_parity_pod_required_2026-05-07.md`
- Embree: `pass=4, fail=0, skipped=0`
- OptiX: `pass=4, fail=0, skipped=0`
- Required backend skips: none

## Boundary

This latest-main rerun confirms the committed evidence path remains reproducible
on the RTX pod after the artifact commit. It does not measure speed, does not
prove true zero-copy, does not authorize whole-app claims, does not promote the
primitive to stable, and does not publish or release anything. External claim
review remains the next gate item.
