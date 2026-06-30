# Goal1138 Current RTX Status Evidence Sync

Date: 2026-04-29

## Scope

Refresh current RTX public-status documentation so it records the newer
Goal1135/Goal1136 changed-path RTX A5000 artifacts while preserving the
existing Goal1048/Goal1058 historical evidence and no-whole-app-speedup
boundary.

## Changes

- Updated `src/rtdsl/app_support_matrix.py` so the shared RT-core maturity
  cloud policy cites Goal1135/Goal1136 changed-path artifacts from source
  marker `21fa036881bf9a0c806f69c15727d87b482ccfcf`.
- Updated `scripts/goal947_v1_rtx_app_status_page.py` so generated
  `docs/v1_0_rtx_app_status.md` records Goal1135/Goal1136 artifact intake.
- Regenerated `docs/v1_0_rtx_app_status.md` and
  `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`.
- Updated `docs/app_engine_support_matrix.md` so the OptiX RTX benchmark policy
  and RT-core maturity table mention Goal1135/Goal1136 changed-path evidence.
- Updated `tests/goal1044_public_rtx_cloud_policy_sync_test.py` to guard the
  current evidence chain: Goal1048/Goal1058 plus Goal1135/Goal1136.

## Boundary

This is a documentation/status synchronization. It does not authorize a release,
new public speedup wording, broad whole-app acceleration claims, or treating
same-backend warm/prepared ratios as RTX-vs-baseline speedups.

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1044_public_rtx_cloud_policy_sync_test tests.goal947_v1_rtx_app_status_page_test tests.goal687_app_engine_support_matrix_test tests.goal803_rt_core_app_maturity_contract_test -v
```

Result:

```text
Ran 19 tests in 0.365s

OK
```

## Codex Verdict

`ACCEPT`.

The current public RTX status docs now point at the newest changed-path
evidence without weakening claim boundaries.
