# v2.10 Pod Bootstrap Probe

Status: current pod setup preflight.

Run this before building OptiX or launching the v2.10 pod-validation bundle:

```bash
PYTHONPATH=src:. python scripts/rtdl_pod_bootstrap_probe.py
```

JSON form:

```bash
PYTHONPATH=src:. python scripts/rtdl_pod_bootstrap_probe.py --json
```

Strict form for automation:

```bash
PYTHONPATH=src:. python scripts/rtdl_pod_bootstrap_probe.py --json --strict
```

The probe checks:

- `nvidia-smi`;
- `nvcc`;
- `make` and `g++`/`c++`;
- Python modules `numpy`, `cupy`, and `numba`;
- OptiX headers under `OPTIX_PREFIX`, `/root/vendor/optix-sdk`,
  `/root/vendor/optix-dev`, `/workspace/vendor/optix-sdk`,
  `/workspace/vendor/optix-dev`, `/workspace/vendor/optix-dev-8.0.0`, or
  `$HOME/vendor/optix-dev`;
- `RTDL_OPTIX_LIBRARY`, `RTDL_OPTIX_LIB`, or a built `build/librtdl_optix.so`.

The probe does not install packages and does not authorize performance claims.
It only tells us whether the pod is ready or what needs to be installed/built
before running:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python scripts/rtdl_v2_10_pod_validation_bundle.py \
  --run-front-door \
  --run-scale-profile \
  --output-dir docs/reports/v2_10_pod_validation_bundle_pod
```
