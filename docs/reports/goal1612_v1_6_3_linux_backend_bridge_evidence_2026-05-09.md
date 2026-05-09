# Goal1612 v1.6.3 Linux Backend Bridge Evidence

Date: 2026-05-09

## Verdict

ACCEPTED as Linux backend bridge evidence for the prepared host-output
measurement path.

This is not public performance evidence and does not authorize any speedup,
RTX, true zero-copy, stable primitive, partner handoff, package-install,
release-tag, or release-action claim.

## Environment

- Host: `192.168.1.20`
- Linux hostname: `lx1`
- Checkout: `/home/lestat/work/rtdl_codex_local_check`
- Git commit: `527d38e1a5fb0fb6d63015c0bbabdd7a7b15bf8c`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- CUDA compiler: `cuda_12.0`
- OptiX SDK: `/home/lestat/vendor/optix-dev`
- Native libraries observed before the run:
  `build/librtdl_embree.so` and `build/librtdl_optix.so`
- Runtime probes before the run reported Embree `(4, 3, 0)` and OptiX `(9, 0, 0)`.

## Command

```bash
PYTHONPATH=src:. python3 scripts/goal1612_v1_6_3_backend_prepared_host_output_bridge.py \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --unique-rows 64 \
  --repeats 4 \
  --iterations 5 \
  --json-out docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.json \
  --md-out docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.md
```

## Outcome

- `fake_native`: `pass`
- `embree`: `pass`
- `optix`: `pass`
- Required backend skips: none
- Failures: none
- Package status: `accepted_backend_bridge`

Each backend recorded:

- candidate rows: `256`
- iterations: `5`
- baseline input materializations: `5`
- prepared input materializations: `1`
- input materialization delta: `4`
- prepared host-output buffer reused: `true`
- timing recorded for diagnostics only: `true`

## Artifact Paths

- `docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.json`
- `docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.md`

## Boundary

This run shows that the backend bridge can execute the prepared host-output
measurement path on local Linux with fake-native, Embree, and OptiX all required
and passing. The GTX 1070 host is a smoke/behavior environment only; this run is
not RTX performance evidence and must not be used for public speedup wording.
