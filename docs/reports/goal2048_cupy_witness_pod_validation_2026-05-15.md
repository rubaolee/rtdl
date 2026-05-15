# Goal2048 CuPy Witness Pod Validation

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2046 added a CuPy-facing generic witness-continuation surface. Goal2048 validates that surface on an NVIDIA pod and records the first bounded scaling evidence for exact Hausdorff-with-witness.

This is not v2.0 release authorization. It is partner-continuation evidence only.

## Pod

- Host: `66.92.198.234`
- SSH port: `11830`
- Key used from Windows repo: `.\id_ed25519_rtdl_codex`
- GPU: NVIDIA L4
- Driver: `570.195.03`
- Python: `3.12.3`
- Runtime environment: `/root/rtdl_goal2046_venv`
- Installed packages: `numpy 2.4.4`, `cupy-cuda12x 14.0.1`
- Repo snapshot: local archive of commit `bc7d2e6e`

## Validation Commands

```bash
PYTHONPATH=src:. timeout 300 /root/rtdl_goal2046_venv/bin/python -m unittest \
  tests.goal2046_cupy_witness_continuation_surface_test \
  tests.goal2044_partner_continuation_numpy_reference_test
```

Result: `9` tests passed.

After wiring the explicit app backend:

```bash
PYTHONPATH=src:. timeout 300 /root/rtdl_goal2046_venv/bin/python -m unittest \
  tests.goal2046_cupy_witness_continuation_surface_test
```

Result: `3` tests passed.

Explicit app smoke:

```bash
PYTHONPATH=src:. timeout 300 /root/rtdl_goal2046_venv/bin/python \
  examples/rtdl_hausdorff_distance_app.py \
  --backend partner_cupy_witness_exact \
  --copies 64
```

Result: oracle match, `generic_group_argmin_then_global_argmax_with_witness`.

## Scaling Artifact

Artifact:

- `docs/reports/goal2048_cupy_witness_scaling.json`

| Backend | Points A | Points B | Median-like single run | Correct |
| --- | ---: | ---: | ---: | --- |
| `partner_numpy_exact` | 256 | 256 | 0.029746s | yes |
| `partner_cupy_witness_exact` | 256 | 256 | 0.880048s | yes |
| `partner_numpy_exact` | 1024 | 1024 | 1.365389s | yes |
| `partner_cupy_witness_exact` | 1024 | 1024 | 1.171543s | yes |
| `partner_numpy_exact` | 2048 | 2048 | 15.393135s | yes |
| `partner_cupy_witness_exact` | 2048 | 2048 | 2.010746s | yes |

## Interpretation

The result is exactly the kind of behavior expected from a partner GPU continuation:

- at small sizes, CuPy loses because device setup, allocation, and kernel launch overhead dominate;
- around 1024 x 1024 points, CuPy reaches parity;
- at 2048 x 2048 points, CuPy is about `7.65x` faster than the NumPy reference for the exact witness continuation.

This validates the design direction: rich exact continuations should be generic partner primitives, and GPU partners can become useful once the continuation has enough arithmetic intensity.

## Boundary

Allowed claim:

- The generic CuPy witness continuation works on an NVIDIA L4 pod and matches the NumPy/oracle semantics for exact Hausdorff witness extraction.
- For this bounded exact witness continuation, CuPy shows a large-size speedup over the NumPy reference at 2048 x 2048 points.

Not allowed:

- v2.0 release readiness.
- OptiX zero-copy candidate-row handoff.
- RT-core acceleration for exact Hausdorff witness extraction.
- broad all-app speedup.
- broad claim that exact Hausdorff is solved for all large-scale datasets.

The current path constructs partner point columns from Python rows. It does not yet consume OptiX-written candidate rows in device memory.

## Next Step

The next engineering step is an OptiX/partner same-contract bridge for exact candidate rows:

1. have OptiX emit generic candidate/witness rows into partner-owned device columns;
2. feed those rows into the generic CuPy continuation primitives;
3. compare against the current all-pairs CuPy witness continuation and the threshold RT-core decision path;
4. record separate timings for RT traversal, partner continuation, and total app time.

## Verdict

`accept-with-boundary`
