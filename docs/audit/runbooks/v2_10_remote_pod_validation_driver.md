# v2.10 Remote Pod Validation Driver

Use this when a fresh NVIDIA pod is available and you want a single SSH command
path with visible progress instead of a long manual session.

The driver is conservative by default:

- dry-run unless `--execute` is passed;
- uses a fresh `mktemp` checkout on the pod;
- prints progress markers before each major step;
- does not move tags, modify releases, or authorize performance claims;
- does not install CUDA, CuPy, Numba, or OptiX.

## Dry Run

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts/rtdl_remote_pod_validation_driver.py `
  --target root@POD_HOST `
  --port POD_PORT `
  --identity-file ~/.ssh/id_ed25519 `
  --build-optix `
  --run-hardware `
  --json
```

Inspect the generated `remote_script` first. The script clones the current
public repository into a fresh remote directory, runs
`scripts/rtdl_pod_bootstrap_probe.py`, optionally builds OptiX, then runs
`scripts/rtdl_v2_10_pod_validation_bundle.py`.

## Execute

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts/rtdl_remote_pod_validation_driver.py `
  --target root@POD_HOST `
  --port POD_PORT `
  --identity-file ~/.ssh/id_ed25519 `
  --build-optix `
  --run-hardware `
  --execute
```

Add `--run-partner-comparison` only when there is enough pod time for the
large-scale CuPy/Numba comparison packet.

## Expected Progress Lines

The remote script prints lines such as:

```text
[rtdl-remote-pod] start ...
[rtdl-remote-pod] workdir /root/rtdl_v2_10_validation....
[rtdl-remote-pod] bootstrap probe before build
[rtdl-remote-pod] build OptiX library
[rtdl-remote-pod] bootstrap probe after setup
[rtdl-remote-pod] run validation bundle flags=...
[rtdl-remote-pod] artifacts /root/rtdl_v2_10_validation....
[rtdl-remote-pod] done ...
```

The final artifact directory remains on the pod. Copy it back manually if you
want to preserve the hardware evidence in `docs/reports/`.

## Boundary

This runbook is an execution helper. It does not claim package-install support,
whole-app speedup, broad RT-core acceleration, automatic partner selection, AMD
support, or release authorization.
