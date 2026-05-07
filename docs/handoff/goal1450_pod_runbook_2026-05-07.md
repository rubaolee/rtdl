# Goal1450 Pod Runbook

## Purpose

Collect the remaining v1.5.2 prepared host-output evidence on real NVIDIA
hardware. Local Windows and Linux Embree runs are already green; the known
blocker is that the non-GPU Linux host does not have `librtdl_optix`.

## Source

Use current `main` from `https://github.com/rubaolee/rtdl`.

## Pod Commands

```bash
git clone https://github.com/rubaolee/rtdl rtdl_goal1450_pod
cd rtdl_goal1450_pod
git rev-parse HEAD
```

If the pod has OptiX headers in a standard location, run:

```bash
bash scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh
```

If OptiX headers are in a custom SDK checkout, run:

```bash
OPTIX_PREFIX=/path/to/optix-dev CUDA_PREFIX=/usr/local/cuda \
  bash scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh
```

## Expected Artifact Directory

`docs/reports/goal1450_v1_5_2_prepared_host_output_pod_results_2026-05-07`

Expected key files:

- `goal1450_pod_environment.log`
- `goal1450_make_build_optix.log`
- `goal1450_make_build_optix.status.json`
- `goal1450_prepared_host_output_parity_pod_required_2026-05-07.json`
- `goal1450_prepared_host_output_parity_pod_required_2026-05-07.md`
- `goal1450_prepared_host_output_parity_pod_required.status.json`
- `goal1450_pod_summary.json`

## Acceptance Boundary

The required parity package is accepted only if both Embree and OptiX have
`pass=4, fail=0, skipped=0` and `Required backend skips: none`.

This pod run does not authorize true zero-copy wording, public speedup wording,
whole-app claims, stable primitive wording, or release action. If accepted, it
only addresses the `embree_optix_same_contract_parity` evidence item in the
v1.5.2 prepared-buffer reuse gate; external claim review is still required.
