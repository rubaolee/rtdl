# Phoenix V3 M36 Grouped Vector-Sum Prepared-Session Core Node

Date: 2026-06-23

Status: `m36_grouped_reduction_core_node_local_ready_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Purpose

M36 implements the M35/Codex+Claude consensus next step: promote grouped
reduction from row-scoped packet evidence into a generic runner-callable V3
prepared-session core node.

This is local contract work. It is not a benchmark result and not a release
claim.

## What Changed

Code:

- `src/rtdsl/prepared_execution.py`
  - added `run_grouped_vector_sum_2d_prepared_session`;
  - exported it through `prepared_execution.__all__`;
  - routes grouped vector-sum through `PreparedExecutionSessionTask`;
  - default replay path calls existing generic
    `run_grouped_vector_sum_2d_partner_columns_session`;
  - requires explicit `partner="numba"`;
  - records Step-3/Step-4 audit metadata and closed claim boundaries.

Tests:

- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
  - verifies successful grouped vector-sum runner execution;
  - verifies invalid partner/count inputs fail closed;
  - verifies weak output metadata does not become trunk success.

Ledger:

- `docs/reports/phoenix_v3_m36_prepared_session_step4_surface_ledger_2026-06-23.md`
- `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py`
- `tests/v3_phoenix_prepared_session_surface_ledger_gate_test.py`

The current prepared-session surface is now:

```text
public_helper_count: 12
ledger_row_count: 12
step4_ready: 8
blocked_set_a_seed: 1
blocked_set_b_control: 3
```

## Runtime Contract

`run_grouped_vector_sum_2d_prepared_session` is generic:

- primitive: `grouped_vector_sum_2d`;
- row contract: `generic_presegmented_grouped_vector_sum_2d`;
- continuation contract: `generic_grouped_vector_sum_f64x2`;
- runtime trunk family: `grouped_vector_sum_2d_partner_columns_session`;
- productized execution path: `prepared_execution_session_runner`;
- explicit partner: `numba`;
- app-specific native engine logic: false.

The helper marks itself as a Set-A probe candidate because grouped reduction is
a continuation-rich runtime family, but this does not make it material
performance evidence.

## Local Validation

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_release_wording_gate
Ran 42 tests
OK
```

Surface-ledger gate:

```text
PYTHONPATH=src;. py -3 scripts/v3_phoenix_prepared_session_surface_ledger_gate.py
status: pass
public_helper_count: 12
ledger_row_count: 12
step4_ready: 8
blocked_set_a_seed: 1
blocked_set_b_control: 3
missing_from_ledger: []
stale_ledger_rows: []
```

Full local V3 rebuild matrix after M36:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 115
Ran 600 tests in 73.275s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m36_20260623_132320.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m36_20260623_132320.stderr.txt
```

## Read

M36 closes the M35 structural gap for grouped reduction: there is now a
generic prepared-session helper in the productized runner surface. It does not
prove grouped reduction is a Phoenix V3 material performance win. That requires
focused same-contract evidence after external review accepts the local contract
shape.

M36 also does not revive the old all-app path. All-app remains blocked until
the focused Set-A and Set-B conditions are met and externally reviewed.

Claude external review accepted M36 with verdict
`accept_m36_grouped_reduction_core_node_continue`. Carry-forward observation:
before any focused grouped-reduction POD evidence, verify the real
`run_grouped_vector_sum_2d_partner_columns_session` adapter reports both
`row_count` and `group_count`; otherwise the helper will correctly fail closed
on `output_counts_match_requested=false`.

## Goal-Level Decision Audit

Decision: add a generic grouped vector-sum/reduction prepared-session helper
instead of continuing route-specific grouped-reduction packet work.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be treating old grouped-reduction row speedups as
   if they already lived in the current productized runtime surface.

3. Was there another path?

   Yes. M3.4 had suggested AABB runner generalization. Claude accepted M35's
   redirect to grouped reduction because grouped reduction had strong
   row-scoped evidence and lacked the generic runner node.

4. Can I now try a different path that actually solves the problem?

   Yes. The grouped-reduction runtime node now exists locally; next is external
   review, then focused evidence only if the contract shape is accepted.

## Non-Authorization

This report authorizes no V3 release, no all-app POD spend, no public speedup
claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no automatic
partner selection, no V4 work, no C ABI work, and no embedding work.
