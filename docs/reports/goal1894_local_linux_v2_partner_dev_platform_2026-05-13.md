# Goal1894 - Local Linux v2 Partner Development Platform

Status: dev-platform-ready-with-boundary

Date: 2026-05-13

## Scope

Goal1894 records the local Linux development setup used while the RTX pod was
unavailable. This host is suitable for Linux/CUDA/OptiX/Torch/CuPy functional
smoke tests and harness development, but it does not replace RTX-class pod
performance evidence.

## Host

- Host: `192.168.1.20`
- User: `lestat`
- Disposable checkout: `/tmp/rtdl_goal1889_smoke`
- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- OptiX SDK: `/home/lestat/vendor/optix-dev`
- Partner dependency target: `/tmp/rtdl_v2_partner_pydeps`

## Setup Commands

OptiX build:

```bash
cd /tmp/rtdl_goal1889_smoke
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

Partner package setup:

```bash
mkdir -p /tmp/rtdl_v2_partner_pydeps
python3 -m pip install --target /tmp/rtdl_v2_partner_pydeps \
  --index-url https://download.pytorch.org/whl/cu121 torch
python3 -m pip install --target /tmp/rtdl_v2_partner_pydeps cupy-cuda12x
```

Run environment:

```bash
export PYTHONPATH=/tmp/rtdl_v2_partner_pydeps:src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
```

## Validated

- `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev` produced
  `build/librtdl_optix.so`.
- Torch imported from `/tmp/rtdl_v2_partner_pydeps` and reported CUDA available
  on `NVIDIA GeForce GTX 1070`.
- CuPy imported from `/tmp/rtdl_v2_partner_pydeps` and reported the same device.
- Goal1889/Goal1869 local test slice passed.
- Goal1889 local smoke artifacts were generated at counts 64 and 256.

## Boundary

This host is useful for:

- Linux import and packaging mechanics;
- OptiX build validation;
- CUDA/partner framework functional smoke;
- catching script, parity, and artifact schema errors before pod time.

This host is not sufficient for:

- RTX 3090 or RTX Ada performance claims;
- broad RT-core speedup claims;
- v2.0 release readiness;
- replacing pod artifacts required by performance reports.

Accepted performance wording still requires RTX-class pod artifacts and external
review.
