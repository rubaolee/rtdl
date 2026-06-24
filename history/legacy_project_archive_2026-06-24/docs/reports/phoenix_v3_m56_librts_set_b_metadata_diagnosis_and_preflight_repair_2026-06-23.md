# Phoenix V3 M56 LibRTS Set-B Metadata Diagnosis And Preflight Repair

Date: 2026-06-23

Status: `m56_local_diagnosis_complete_preflight_repair_ready_for_review`

## Scope

M56 locally diagnosed the M55 LibRTS failure:

```text
set_b_control_candidate_missing
```

No POD rerun was performed. No V3 release, all-app benchmark, public claim, or
watch-row closure is authorized by this report.

## Evidence Read

Copied M55 execution evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/optix_cold_single_shot_current_s01.stdout.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/embree_32768_stress_current_s01.stdout.json`

The sampled current payloads show that the productized runner did execute:

| Scenario | Productized runner used | Productized path | Primitive contract | Metadata failure |
| --- | --- | --- | --- | --- |
| `optix_cold_single_shot` | true | `prepared_execution_session_runner` | `generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count` | `set_b_control_candidate_missing` |
| `embree_32768_stress` | true | `prepared_execution_session_runner` | `generic_prepared_aabb_index_query_2d_count` | `set_b_control_candidate_missing` |

The M55 failure is therefore not evidence that the LibRTS/AABB path skipped the
prepared execution session runner. The observed failure is narrower: the current
payload's `prepared_execution_session_runner_metadata` did not expose
`set_b_control_candidate=true`.

## Diagnosis

Current local source already contains the intended Set-B markings:

- `src/rtdsl/prepared_execution.py` marks the three AABB helper paths with
  `set_a_probe_candidate=false` and `set_b_control_candidate=true`.
- `src/rtdsl/prepared_execution.py` marks the OptiX prepared-query-set helper
  with `prepared_query_mode="optix_prepared_query_set"`.
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
  exposes `set_b_control_candidate` in both top-level payload metadata and
  nested `prepared_execution_session_runner_metadata`.

Inference from copied evidence: the M55 target current root was either stale for
this metadata contract or insufficiently source-signed before execution. The
M47 preflight ran named unittest modules, but it did not prove that the target
root contained the new Set-B metadata code. A stale test module can pass while
the benchmark app still emits old metadata.

## Repair

M56 adds a required current-source signature preflight to the M47 protocol:

- file: `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- new required preflight row:
  `current_librts_set_b_source_signature`
- check type: target current root source inspection before any measured sample
  executes
- required markers:
  - AABB Embree count helper present;
  - AABB OptiX prepared-query-set helper present;
  - AABB helpers mark `set_b_control_candidate=true`;
  - AABB helpers mark `set_a_probe_candidate=false`;
  - OptiX helper marks `prepared_query_mode="optix_prepared_query_set"`;
  - LibRTS app exposes `set_b_control_candidate` into payload metadata;
  - LibRTS app exposes OptiX `prepared_query_mode` into runner metadata.

This repair prevents the exact M55 failure mode from consuming another POD run
before the target current root proves it has the required metadata contract.

## Tests Added

- `tests/v3_phoenix_m56_librts_set_b_metadata_diagnosis_test.py`

The test preserves three boundaries:

- M55 historical copied evidence remains red and is not rewritten.
- The local source now exposes the Set-B metadata contract.
- Future M47 runs require the new source-signature preflight row.

The M47 protocol test was also extended to require and execute the local source
signature script:

- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`

`scripts/run_test_matrix.py` now includes the M56 gate in `v3_rebuild`.

## Validation

Focused validation:

```text
py -3 -m unittest tests.v3_phoenix_m47_librts_stability_protocol_test tests.v3_phoenix_m56_librts_set_b_metadata_diagnosis_test
Ran 13 tests
OK
```

The command stderr contained only the known local Python warning:

```text
Could not find platform independent libraries <prefix>
```

Full local V3 rebuild:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 129
Ran 656 tests in 75.648s
OK
```

Captured output:

- `docs/reports/phoenix_v3_m56_v3_rebuild_after_preflight_repair_2026-06-23.combined.txt`

The rebuild stderr stream in the combined capture contains only the known local
Python warning `Could not find platform independent libraries <prefix>`. The
test matrix return code was 0.

Post-review final validation after adding external-review completion gates:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 129
Ran 657 tests in 76.102s
OK
```

Captured output:

- `docs/reports/phoenix_v3_m56_v3_rebuild_after_3ai_completion_2026-06-23.combined.txt`

## What This Does Not Do

This does not close either LibRTS watch row. M55 remains:

- `optix_cold_single_shot`: `red_failure_watch_row_open`
- `embree_32768_stress`: `red_failure_watch_row_open`

This does not authorize a new M47 run. A future rerun needs a separate reviewed
authorization packet after this local repair is accepted.

This does not change performance numbers, benchmark data, or M55 copied
evidence.

## Non-Authorization

This report does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure

## Goal-Level Decision Audit

Decision: repair the M47 protocol so future LibRTS focused runs must verify the
target current root's Set-B metadata contract before any paid sample executes.

1. Was I foolish? Partly, in the earlier M54/M55 flow.
2. If yes, what actions made the decision foolish? I treated named preflight
   unittest modules as sufficient proof that the target current root carried the
   latest metadata contract. That let a stale or insufficiently signed target
   tree consume one authorized run before the missing metadata surfaced.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Add a source-signature preflight to the harness itself before execution,
   so the target root proves the exact contract fields it must emit.
4. Can I now try a different path that actually solves the problem? Yes. Keep
   M55 as valid red evidence, add the preflight repair locally, request external
   review, and require a separate authorization before any future POD rerun.
