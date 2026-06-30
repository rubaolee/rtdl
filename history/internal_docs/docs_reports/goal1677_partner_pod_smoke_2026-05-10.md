# Goal1677 Partner Pod Smoke

Date: 2026-05-10

Status: pod evidence for the protocol-first Python+partner+RTDL substrate.

## Environment

Validated on the pod reached through the RTDL SSH key in `Z:\rtdl-dev`:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- Python: 3.11.10
- Staging directory: `/tmp/rtdl_goal167x_validate`

The staged source excluded the old untracked archive:

```text
docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
```

## Passing Pod Checks

The current source tree passed the targeted v1.8/v2.0 gate checks on the pod:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1669_python_partner_rtdl_partner_choice_architecture_test \
  tests.goal1670_all_external_partner_analysis_consensus_test \
  tests.goal1671_v1_8_v2_0_partner_gate_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1674_oracle_root_wrapper_quarantine_test \
  tests.goal1675_partner_protocol_substrate_test \
  tests.goal1676_native_leakage_delta_regression_test
```

Result:

```text
Ran 43 tests in 0.301s
OK (skipped=1)
```

The OptiX group-name compatibility cluster also passed:

```text
Ran 20 tests in 0.237s
OK (skipped=5)
```

The public Python+RTDL lowering target passed:

```text
make build
```

## Real Partner Smoke

PyTorch was already installed on the pod:

```text
torch 2.4.1+cu124
cuda_available True
```

The real PyTorch smoke confirmed:

- `rt.partner.auto()` selects `torch`;
- the descriptor reports `cuda:0`;
- a borrowed pointer is present;
- grad-enabled tensors are rejected before RTDL export.

CuPy was validated in an isolated temporary venv:

```text
/tmp/rtdl_goal167x_cupy_venv
cupy 14.0.1
```

The real CuPy smoke confirmed:

- `rt.partner.auto()` selects `cupy`;
- the descriptor reports `cuda:0`;
- a borrowed pointer is present;
- `ctx.empty()` returns a CuPy-owned CUDA output array.

## Native Backend Blockers

The pod initially missed native backend dependencies. Embree was then
provisioned and validated in:

- `docs/reports/goal1678_python_rtdl_pod_embree_build_2026-05-10.md`

Remaining native backend blocker:

- `make build-optix` is blocked because the OptiX SDK header is absent at
  `/opt/optix/include/optix.h`, and no `optix.h` was found in the searched
  pod paths.
- `nvcc` exists at `/usr/local/cuda-12.4/bin/nvcc`, but OptiX still needs the
  SDK headers.

## Claim Boundary

This evidence supports the current protocol-first partner substrate and real
PyTorch/CuPy adapter selection on CUDA tensors. It does not prove OptiX native
runtime correctness, true zero-copy execution, or a complete v1.8 app-agnostic
native-engine gate.

Blocked wording remains:

```text
RTDL native internals are fully app-agnostic.
```

```text
RTDL has general true zero-copy support.
```
