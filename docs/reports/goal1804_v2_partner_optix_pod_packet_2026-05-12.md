# Goal1804: v2.0 Partner OptiX Pod Packet

Status: `pre-pod-ready`

Date: 2026-05-12

## Scope

Goal1804 prepares the OptiX pod packet for the v2.0 Python+partner+RTDL lane.
No pod was started for this goal.

The packet is designed for one concentrated pod session after the user provides
an RTX-class NVIDIA host. It validates the first public partner any-hit dispatch
through OptiX for:

- NumPy CPU columns;
- PyTorch CUDA columns;
- CuPy CUDA columns.

## Runner

New runner:

```text
scripts/goal1804_v2_partner_optix_pod_runner.sh
```

Default behavior:

```text
OUT_DIR=docs/reports/goal1804_v2_partner_optix_pod
OPTIX_PREFIX=/root/vendor/optix-dev
PYTHON_BIN=python3
```

The runner records:

- git commit;
- Python version;
- caller `PYTHONPATH`, preserving preinstalled framework site directories before
  appending `src:.`;
- `nvidia-smi`;
- PyTorch/CuPy/NumPy versions and CUDA visibility;
- OptiX build log;
- focused unittest log;
- JSON output from `examples/rtdl_partner_anyhit.py` for NumPy, PyTorch CUDA,
  and CuPy CUDA through `backend=optix`;
- a checked `summary.json` with claim flags.

## Pod Command Shape

After SSH into a pod and checking out `origin/main`:

```bash
cd /workspace/rtdl
export PYTHONPATH=src:.
export OPTIX_PREFIX=/root/vendor/optix-dev
bash scripts/goal1804_v2_partner_optix_pod_runner.sh
```

If the host uses a pre-seeded framework directory, keep it in front:

```bash
export PYTHONPATH=.partner_site:src:.
```

If the pod has a different OptiX SDK path:

```bash
OPTIX_PREFIX=/workspace/vendor/optix-dev bash scripts/goal1804_v2_partner_optix_pod_runner.sh
```

## Claim Boundary

The packet still does not authorize:

- true zero-copy;
- direct device-pointer handoff;
- RT-core speedup;
- whole-app acceleration;
- v2.0 release readiness.

It only seeks hardware evidence that the first public partner any-hit dispatch
works through OptiX with NumPy, PyTorch CUDA, and CuPy CUDA while retaining:

```text
transfer_mode = "host_stage"
true_zero_copy_authorized = false
rt_core_speedup_claim_authorized = false
```

## External Review

Gemini reviewed the packet in Goal1805 and returned
`accept-with-boundary`: Goal1804 is ready to send to an RTX-class OptiX pod as
a bounded validation packet, but v2.0 remains blocked on actual pod execution
evidence and later release consensus.

Review:
`docs/reviews/goal1805_gemini_review_goal1804_v2_partner_optix_pod_packet_2026-05-12.md`

## Why This Is Pod-Ready

The no-pod prerequisites are already complete:

- Linux Embree partner closure exists at Goal1801.
- The learner example exists at Goal1802.
- Local Linux validates NumPy, PyTorch CUDA, and CuPy CUDA availability.
- Local Linux validates Embree plus OptiX builds and the first-wave partner
  tests on a GTX 1070 development host.

The remaining evidence requires an RTX-class pod because the local GTX 1070 can
test CUDA/OptiX behavior but cannot support RT-core performance claims.

## Validation Without Pod

Static validation should verify that the runner includes:

- environment capture;
- caller `PYTHONPATH` preservation;
- framework probe;
- OptiX build;
- focused partner tests;
- NumPy/PyTorch/CuPy example runs through OptiX;
- claim-flag checks.
