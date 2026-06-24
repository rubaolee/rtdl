# Phoenix V3 M34 Prepared-Session Surface Ledger Gate

Date: 2026-06-23

Status: `surface_ledger_gate_pass_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
external_consensus_obtained: false
```

## Purpose

M34 adds a machine gate between the V3 prepared-session code surface and the
M33 promotion ledger. The gate prevents a repeat of the old failure mode where
code, docs, and review packets drift apart.

The gate checks that every public prepared-session helper exported by
`src/rtdsl/prepared_execution.py::__all__` appears exactly once in the M33
ledger, and that the M33 classification counts remain:

- seven Step-4-ready local-audit families;
- one blocked Set-A seed;
- three blocked Set-B controls.

## Finding And Fix

The first M34 run failed:

```text
status: fail
error: m33_ledger_rows_not_exported_public_helpers
stale_ledger_rows:
  - run_fixed_radius_threshold_reached_count_2d_prepared_session
```

This was a real public-surface drift. The M33 ledger classified
`run_fixed_radius_threshold_reached_count_2d_prepared_session` as Step-4 ready,
but `prepared_execution.__all__` did not export it.

Fix applied:

- add `run_fixed_radius_threshold_reached_count_2d_prepared_session` to
  `src/rtdsl/prepared_execution.py::__all__`.

## Current Gate Result

```text
PYTHONPATH=src;. py -3 scripts/v3_phoenix_prepared_session_surface_ledger_gate.py
status: pass
public_helper_count: 11
ledger_row_count: 11
step4_ready: 7
blocked_set_a_seed: 1
blocked_set_b_control: 3
missing_from_ledger: []
stale_ledger_rows: []
```

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 39 tests
OK
```

Full local V3 rebuild matrix after the M34 gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 113
Ran 590 tests in 73.107s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_20260623_130102.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_20260623_130102.stderr.txt
```

## Read

This is not a performance result. It is a surface-integrity fix: the public V3
prepared-session helper set now matches the M33 ledger, and future drift should
fail locally before reaching a review packet.

This does not authorize release, all-app POD spend, public speedup claims,
broad V3-over-V2 claims, true-zero-copy wording, automatic partner selection,
V4 work, C ABI work, or embedding work.

## Goal-Level Decision Audit

Decision: add a local machine gate for prepared-session helper surface versus
M33 ledger classification while Claude external review is running.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would have been waiting idle for Claude or leaving a
   code/doc surface mismatch because the prose looked right.

3. Was there another path?

   Yes: keep the ledger as prose only. That would allow future helpers to drift
   outside the classification gate.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep this machine gate in `v3_rebuild`, so helper-surface drift fails
   before release or review claims can form around stale docs.
