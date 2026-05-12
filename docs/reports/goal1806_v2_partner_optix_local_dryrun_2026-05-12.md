# Goal1806: v2.0 Partner OptiX Local Dry Run

Status: `local-dev-pass`

Date: 2026-05-12

## Scope

Goal1806 records a no-pod mechanics dry run of the Goal1804 OptiX partner pod
packet on the local Linux development host.

This is not RTX-class pod evidence and does not authorize RT-core speedup,
true zero-copy, direct device-pointer handoff, whole-app acceleration, or v2.0
release readiness.

## Host

Host:

```text
lestat@192.168.1.20
```

Checkout:

```text
/home/lestat/work/rtdl_v2_partner_check
```

Commit:

```text
76582116e2544061a7f58368a17e472aecf2e6a7
```

GPU:

```text
NVIDIA GeForce GTX 1070
```

OptiX SDK path:

```text
/home/lestat/vendor/optix-dev
```

## Command

The dry run used the pre-seeded partner framework site directory instead of
system Python package installation:

```bash
cd /home/lestat/work/rtdl_v2_partner_check
PYTHONPATH=.partner_site:src:. \
OUT_DIR=docs/reports/goal1804_v2_partner_optix_local_dryrun \
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
PYTHON_BIN=python3 \
bash scripts/goal1804_v2_partner_optix_pod_runner.sh
```

## Result

The runner completed successfully.

Captured artifacts are stored in:

```text
docs/reports/goal1806_v2_partner_optix_local_dryrun/
```

Key results:

- framework probe passed with NumPy, PyTorch CUDA, and CuPy CUDA visible;
- OptiX build completed;
- focused partner test slice passed: `31` tests, `0` failures;
- public example passed through `backend=optix` for:
  - `numpy`;
  - `torch-cuda`;
  - `cupy-cuda`;
- every example returned `hit_count = 1`;
- every example preserved `transfer_mode = "host_stage"`;
- every example preserved `true_zero_copy_authorized = false`;
- every example preserved `rt_core_speedup_claim_authorized = false`.

## Runner Lesson

The first local attempt exposed a useful pre-pod issue: Ubuntu system Python is
PEP 668 externally managed, so the runner should not rely on writing packages
into system Python when a pre-seeded framework site directory exists.

The Goal1804 runner was updated to preserve caller `PYTHONPATH` before
appending `src:.`. This lets local dry runs use `.partner_site` and lets future
pods use either a prebuilt site directory or an explicit virtual environment.

## Boundary

This dry run proves the packet mechanics work on the local Linux development
host, including OptiX build, partner framework discovery, focused tests, and
example claim guards.

It does not replace the required RTX-class pod run. v2.0 remains blocked on
actual RTX-class pod execution evidence and release consensus.

## External Review

Gemini reviewed Goal1806 in Goal1807 and returned `accept-with-boundary`:
the local dry run is useful pre-pod evidence that the packet mechanics are
ready, but v2.0 remains blocked on actual RTX-class pod execution evidence and
later release consensus.

Review:
`docs/reviews/goal1807_gemini_review_goal1806_v2_partner_optix_local_dryrun_2026-05-12.md`
