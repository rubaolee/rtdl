# Goal1451 Prepared Host-Output Linux GTX 1070 Compatibility Evidence

## Verdict

Accepted as Linux OptiX compatibility/parity evidence for the v1.5.2 prepared
host-output path. Not accepted as RT-core evidence, performance evidence, public
speedup wording, true zero-copy evidence, stable primitive promotion, or release
action.

## Run Scope

- Git HEAD: `fe9ac747a9fe7061f5d17a30a527ea1ca4226d5d`
- Host: `192.168.1.20`, Linux `lx1`
- GPU reported by `nvidia-smi`: NVIDIA GeForce GTX 1070
- Executor: `scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh`
- Artifact directory:
  `docs/reports/goal1451_prepared_host_output_linux_gtx1070_compat_2026-05-07`

## Outcome

- `make build-optix`: passed
- Required Embree+OptiX prepared host-output parity: passed
- Embree: `pass=4, fail=0, skipped=0`
- OptiX: `pass=4, fail=0, skipped=0`
- Required backend skips: none

## Boundary

This closes the previous local Linux blocker where `librtdl_optix` was missing.
It provides same-contract OptiX compatibility evidence for the prepared
host-output path on a non-RT-core NVIDIA GPU. It does not prove RTX/RT-core
execution, does not prove performance, does not prove true zero-copy, does not
authorize public speedup wording, and does not authorize release action.

For RT-priority evidence, still run the same executor on a real RTX-capable pod
and preserve the artifact directory with the pod host, GPU model, and Git HEAD.
