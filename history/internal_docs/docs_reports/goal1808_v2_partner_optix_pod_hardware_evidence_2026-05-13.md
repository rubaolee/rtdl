# Goal1808: v2.0 Partner OptiX Pod Hardware Evidence

Status: `accept-with-boundary`

Date: 2026-05-13

## Scope

Goal1808 records the first RTX-class pod execution of the Goal1804 v2.0
partner OptiX packet. This validates the public partner any-hit dispatch
through OptiX for:

- NumPy CPU columns;
- PyTorch CUDA columns;
- CuPy CUDA columns.

This is hardware execution evidence for the first v2.0 partner OptiX path. It
is still not a true zero-copy claim, direct device-pointer handoff claim,
RT-core speedup claim, whole-application acceleration claim, or v2.0 release
readiness claim.

## Pod

SSH command provided by the user:

```text
ssh root@213.173.108.27 -p 13381 -i ~/.ssh/id_ed25519
```

Windows OpenSSH rejected the key directly from `Z:\` due to open share
permissions, so the key was copied to:

```text
C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

with private ACLs for the run.

Pod GPU:

```text
NVIDIA RTX 4000 Ada Generation
```

Driver and CUDA runtime from `nvidia-smi`:

```text
Driver Version: 550.127.05
CUDA Version: 12.4
```

Repository checkout:

```text
/workspace/rtdl
```

Commit:

```text
573b18183cd33bed3512c3e49d5e64017ee167fc
```

OptiX SDK:

```text
/root/vendor/optix-dev
```

The SDK was populated from NVIDIA `optix-sdk` tag `v8.0.0`, matching the
driver-compatible lane used by earlier pod work.

## Artifacts

Captured artifacts are stored in:

```text
docs/reports/goal1808_v2_partner_optix_pod/
```

Files:

- `environment.txt`
- `partner_probe.json`
- `build_optix.log`
- `focused_unittest.log`
- `example_numpy_optix.json`
- `example_torch-cuda_optix.json`
- `example_cupy-cuda_optix.json`
- `summary.json`

## Framework Probe

The pod run reported:

```text
numpy = 2.4.4
torch = 2.5.1+cu121
torch_cuda_available = true
torch_cuda = 12.1
cupy = 14.0.1
cupy_device_count = 1
```

## Validation

The packet built OptiX:

```text
build/librtdl_optix.so
```

Focused tests:

```text
Ran 31 tests in 19.248s
OK (skipped=2)
```

The two skips are preserved from the existing focused slice and do not block
this packet result because the required public OptiX partner examples executed
and passed for all three source modes below.

## Example Results

All three public example runs succeeded through `backend=optix`:

| Partner input | Source device | Source protocol | Hit count | Transfer mode |
| --- | --- | --- | ---: | --- |
| `numpy` | `cpu:0` | `numpy` | 1 | `host_stage` |
| `torch-cuda` | `cuda:0` | `torch` | 1 | `host_stage` |
| `cupy-cuda` | `cuda:0` | `cupy` | 1 | `host_stage` |

Every artifact preserved:

```text
true_zero_copy_authorized = false
rt_core_speedup_claim_authorized = false
```

## Claim Boundary

Goal1808 proves that the first public Python+partner+RTDL any-hit dispatch can
execute through OptiX on RTX-class hardware for NumPy, PyTorch CUDA, and CuPy
CUDA sources while retaining the current host-stage boundary.

Goal1808 does not prove:

- true zero-copy;
- direct device-pointer handoff;
- RT-core speedup;
- arbitrary PyTorch/CuPy program acceleration;
- whole-application acceleration;
- v2.0 release readiness.

## Verdict

`accept-with-boundary`: the first v2.0 partner OptiX hardware packet passed on
an RTX 4000 Ada pod. v2.0 still needs final release-scope audit and required
external consensus before any release-ready claim.

## External Review

Gemini reviewed Goal1808 in Goal1809 and returned `accept-with-boundary`:
Goal1808 provides valid RTX-class hardware evidence for the first public
Python+partner+RTDL OptiX any-hit path, while v2.0 remains blocked on
release-scope audit and final required consensus.

Review:
`docs/reviews/goal1809_gemini_review_goal1808_v2_partner_optix_pod_hardware_evidence_2026-05-13.md`
