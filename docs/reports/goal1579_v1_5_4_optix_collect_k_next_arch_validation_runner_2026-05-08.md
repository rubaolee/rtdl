# Goal 1579: OptiX COLLECT_K_BOUNDED Next-Architecture Validation Runner

## Verdict

Goal1579 adds `scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py`, a reusable runner for the Goal1578 second-NVIDIA-architecture validation gate.

The runner does not promote the derived carry alias and does not authorize claims. It packages the evidence suite so the next pod can run the same validation consistently.

## What It Runs

- Focused static tests for Goals1570-1573.
- Baseline bounded even/odd sweep.
- Alias bounded even/odd sweep with `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1`.
- Optional targeted reruns for `49153`, `65536`, and `65537`.
- Summary JSON and Markdown with baseline/alias deltas and `carry_payload_copies`.

## Usage

From a Linux NVIDIA pod checkout:

```bash
cd /root/rtdl_goal1545_pod
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. python3 scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py \
  --build \
  --optix-prefix /root/vendor/optix-sdk \
  --library build/librtdl_optix.so \
  --output-prefix /tmp/goal1579_next_arch \
  --ld-library-path /usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64
```

If the pod CUDA runtime path differs, change `--ld-library-path` to match that pod.

## Smoke Validation

The runner was smoke-tested on the existing RTX 4000 Ada pod with `--repeats 1 --targeted-repeats 1`.

Artifacts:

- `docs/reports/goal1579_v1_5_4_optix_collect_k_next_arch_runner_smoke_summary_2026-05-08.json`
- `docs/reports/goal1579_v1_5_4_optix_collect_k_next_arch_runner_smoke_summary_2026-05-08.md`

The smoke run executed the focused tests, baseline profile, alias profile, targeted baseline profile, targeted alias profile, and summary generation successfully.

## Claim Boundary

This runner records validation evidence only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
