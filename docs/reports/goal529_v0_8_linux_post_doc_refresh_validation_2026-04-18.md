# Goal 529: v0.8 Linux Post-Doc-Refresh Validation

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal528 closed the macOS-side post-doc-refresh audit after Goals 525-527. Since
Linux is the primary validation platform for RTDL, Goal529 repeats the critical
public command and full-test checks on `lestat-lx1` from a fresh synced
checkout at commit `10fd467`.

## Linux Host

Host:

- `lestat-lx1`
- checkout: `/home/lestat/work/rtdl_goal529_v08_post_doc`

Host probes:

```text
hostname: lx1
GPU: NVIDIA GeForce GTX 1070, driver 580.126.09
PostgreSQL: /var/run/postgresql:5432 - accepting connections
Python: 3.12.3
```

Fresh checkout setup:

```text
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
```

Runtime probes after build:

```text
embree (4, 3, 0)
optix (9, 0, 0)
vulkan (0, 1, 0)
```

## Public Command Harness

Command:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine linux-goal529-v08-post-doc-refresh \
  --output docs/reports/goal529_linux_public_command_check_2026-04-18.json
```

Artifact copied back to this repo:

- `docs/reports/goal529_linux_public_command_check_2026-04-18.json`

Summary:

```json
{
  "passed": 88,
  "failed": 0,
  "skipped": 0,
  "total": 88
}
```

Backend status:

```json
{
  "cpu_python_reference": true,
  "oracle": true,
  "cpu": true,
  "embree": true,
  "optix": true,
  "vulkan": true
}
```

## Full Linux Test Discovery

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 143.328s
OK
```

## Readout

Goal529 confirms that the current post-doc-refresh `main` state still runs on
the primary Linux host with:

- full public command coverage: 88 passed, 0 failed, 0 skipped
- all local RTDL backend probes available: CPU Python reference, oracle/CPU,
  Embree, OptiX, and Vulkan
- full unit discovery passing: 232 tests OK
- PostgreSQL host availability preserved

## Boundary

This validation confirms release-facing command/test health after documentation
refreshes. It does not create a new performance speedup claim. v0.8 remains
accepted app-building work on `main`, and performance interpretation remains
bounded by the Goal507, Goal509, and Goal524 reports.

## AI Consensus

- Claude review: `docs/reports/goal529_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal529_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The Linux validation is accurate, bounded, and
  sufficient as the primary-host post-doc-refresh follow-up to Goal528.
