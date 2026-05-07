# Goal1450 RTX 2000 Ada Pod Required Parity

## Verdict

Accepted as required Embree+OptiX prepared host-output parity evidence on an
RTX-capable NVIDIA pod. This is not a performance claim, not true zero-copy
evidence, not public speedup wording, not stable primitive promotion, and not a
release action.

## Run Scope

- Pod SSH target: `root@157.157.221.29 -p 57142`
- Key source used: `Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Git HEAD: `2bbcc621678c88601ed8a1f0e3a72d7f7bf8c93f`
- GPU: NVIDIA RTX 2000 Ada Generation, 16 GB
- Driver: `570.195.03`
- CUDA driver capability reported by `nvidia-smi`: `12.8`
- CUDA compiler used: `/usr/local/cuda-12.4/bin/nvcc`
- OptiX headers: `/root/vendor/optix-dev`
- Artifact directory:
  `docs/reports/goal1450_rtx2000ada_pod_required_final_2026-05-07`

## Setup Fixes

The first pod attempt built OptiX and passed OptiX `4/4`, but Embree failed
because Embree was not installed. The second attempt found Embree but skipped it
because `libgeos-dev` was missing for the native wrapper link. The final
accepted run installed:

- `libembree-dev`
- `libtbb-dev`
- `libgeos-dev`
- `pkg-config`

## Outcome

- `make build-optix`: passed
- Required prepared host-output parity: accepted
- Embree: `pass=4, fail=0, skipped=0`
- OptiX: `pass=4, fail=0, skipped=0`
- Required backend skips: none

## Boundary

This evidence supports the narrow same-contract prepared host-output parity
gate for `COLLECT_K_BOUNDED` on Embree and OptiX. It does not measure speed,
does not prove true zero-copy, does not authorize whole-app claims, does not
promote the primitive to stable, and does not publish or release anything.
External claim review remains the next gate item.
