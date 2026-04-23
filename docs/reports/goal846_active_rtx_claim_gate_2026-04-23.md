# Goal846 Active RTX Claim Gate

## Scope

Add a focused readiness gate for the active OptiX claim-review set without weakening the full baseline ledger.

## Problem

Goal836 is intentionally strict and currently counts every Goal835 baseline row:

- active rows
- deferred rows
- optional/reference rows

That is useful as a total ledger, but it obscures the state of the current NVIDIA RT work. After the Linux robot refresh, the remaining Goal836 misses are:

- 2 optional SciPy/reference rows for active fixed-radius apps
- 9 deferred rows for apps that are not active in the current OptiX claim batch

So Goal836 still reports `needs_baselines` even though the mandatory active same-semantics baselines are now complete.

## Decision

Keep Goal836 unchanged as the full ledger.

Add a second, narrower gate that:

- checks only active rows
- counts only manifest actions whose collection status is one of:
  - `local_command_ready`
  - `linux_postgresql_required`
  - `linux_preferred_for_large_exact_oracle`
- explicitly excludes:
  - `optional_dependency_or_reference_required`
  - `deferred_until_app_gate_active`

## Why This Is Correct

- It does not rewrite the underlying baseline contract.
- It does not silently ignore missing rows; the excluded rows are listed explicitly.
- It matches the current NVIDIA RT work focus: active prepared DB, fixed-radius summaries, and robot pose-count summaries.
- It preserves the full Goal836 ledger for total project accounting.

## What Changed

- Added:
  - `scripts/goal846_active_rtx_claim_gate.py`
  - `tests/goal846_active_rtx_claim_gate_test.py`
- Generated:
  - `docs/reports/goal846_active_rtx_claim_gate_2026-04-23.json`
  - `docs/reports/goal846_active_rtx_claim_gate_2026-04-23.generated.md`

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal846_active_rtx_claim_gate_test tests.goal836_rtx_baseline_readiness_gate_test tests.goal838_local_baseline_collection_manifest_test`
- `python3 scripts/goal846_active_rtx_claim_gate.py --output-json docs/reports/goal846_active_rtx_claim_gate_2026-04-23.json --output-md docs/reports/goal846_active_rtx_claim_gate_2026-04-23.generated.md`
- `python3 -m py_compile scripts/goal846_active_rtx_claim_gate.py tests/goal846_active_rtx_claim_gate_test.py`
- `git diff --check`

Result: all focused checks passed.

## Current Honest State

Goal846 reports:

- active rows checked: `5`
- mandatory active baseline artifacts: `12`
- valid mandatory artifacts: `12`
- missing mandatory artifacts: `0`
- invalid mandatory artifacts: `0`
- skipped optional/deferred artifacts: `2`

Those two skipped artifacts are the optional SciPy/reference rows for:

- `outlier_detection / prepared_fixed_radius_density_summary`
- `dbscan_clustering / prepared_fixed_radius_core_flags`

## Boundary

This goal improves active claim-review visibility for the NVIDIA RT work. It does not by itself authorize a public RTX speedup claim.
