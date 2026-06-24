# Goal4286: Remote Pod Validation Driver

Date: 2026-06-11

## Purpose

Reduce pod waste and long silent waits by adding a single SSH-controlled driver
for the v2.10 validation flow.

The driver prepares the next NVIDIA pod run without requiring a manual,
stateful shell session. It prints visible progress markers, uses a fresh remote
checkout, and runs the existing bootstrap probe and validation bundle.

## Added

- `scripts/rtdl_remote_pod_validation_driver.py`
- `docs/audit/runbooks/v2_10_remote_pod_validation_driver.md`
- A link from `docs/audit/runbooks/v2_10_pod_validation_bundle.md`
- `tests/goal4286_remote_pod_validation_driver_test.py`

## Behavior

Default mode is dry-run:

```powershell
py -3 scripts/rtdl_remote_pod_validation_driver.py `
  --target root@POD_HOST `
  --port POD_PORT `
  --identity-file ~/.ssh/id_ed25519 `
  --build-optix `
  --run-hardware `
  --json
```

Execution requires `--execute`. On the pod, the generated remote script:

1. Creates a fresh `mktemp` directory under `/root`.
2. Clones `https://github.com/rubaolee/rtdl.git`.
3. Runs `scripts/rtdl_pod_bootstrap_probe.py`.
4. Optionally runs `make build-optix`.
5. Runs the bootstrap probe again.
6. Runs `scripts/rtdl_v2_10_pod_validation_bundle.py`.
7. Prints the remote artifact directory.

## Boundary

The driver does not install CUDA, CuPy, Numba, or OptiX. It does not mutate
release tags, does not use destructive checkout operations, and does not
authorize package-install, broad RT-core, whole-application speedup, or release
claims.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4286_remote_pod_validation_driver_test
```

The broader v2.10 release-hardening gate includes the driver test plus the
source-tree doctor, pod probe, pod bundle, benchmark evidence index, current
claim scan, tutorial organization, and v2.10 consensus tests.

## Verdict

`accept`: the project now has a safe default remote pod driver for the next
hardware-validation pass.
