# Claude Review: Phoenix V3 M71 RTNN Local Harness Dry-Run Gate

Date: 2026-06-23 (backfilled 2026-06-24)

Reviewer: Claude (Anthropic claude-sonnet-4-6, external critical review seat)

Call for Review: `docs/reviews/call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`

Candidate Dry-Run JSON: `docs/rebuild/v3/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json`

Candidate Dry-Run Report: `docs/reports/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`

Gate Test Suite: `tests/v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test.py`

RTNN App: `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`

---

## Verdict

```
accept_m71_local_dry_run_gate_continue_no_execution_no_pod
```

M71 is accepted as a local dry-run gate only. The packet is dry-run throughout,
covers all 7 M70 shape groups and all 14 rows without generating commands,
exposes correctly separated telemetry fields in the RTNN app, and preserves
all non-authorization boundaries. No execution, no POD, no runbook, no
benchmark execution is authorized by this review.

---

## P0 / P1 / P2 Findings

### P0 Findings

None. The JSON packet, report, and call-for-review are internally consistent.
All 14 check flags in the JSON are true. `failed_checks` is empty. All
non-authorization flags are false. No command templates appear in the dry-run
packet or the RTNN app source. No authorization token is present.

### P1 Findings

**P1-A: M70 Claude review debt was open at time of M71; this review resolves
the M70 debt.** The provisional 2AI consensus correctly limited M71 to
local-only validation pending Claude backfill. The companion M70 Claude review
(also backfilled this session) now satisfies the M70 Claude seat requirement.
Both M70 and M71 may proceed to final 3AI consensus after this session.

**P1-B: App-win gap remains active.** 13 of 14 RTNN rows sit below the 1.05x
performance exit criterion. M71 acceptance does not close or narrow this gap.
Any future execution protocol must treat the frozen scorecard gap as its primary
risk.

### P2 Findings

**P2-A: Full-batch self-query constraint limits evaluation scope.** The
`ValueError` raised by `rtnn_prepared_execution_ranked_summary_payload` when
`query_batch_size != point_count` is load-bearing. This is correct behavior
under the current protocol; alternate batch configurations require separate
code-path review before any harness uses them.

**P2-B: Windows Python launcher requirement.** Running gate tests with `python`
fails on standard Windows without shell aliases; `py -3` is required. This is a
developer environment note, not a protocol defect.

---

## Direct Answers to Review Questions

### 1. Does M71 remain dry-run only with no execution path?

Yes. Verified at three levels:

- **JSON packet:** `dry_run_gate_only: true`, `benchmark_execution_authorized:
  false`, `commands_generated: false`, `authorization_token_present: false`.
  All 7 shape groups have `command_present: false` and `dry_run_only: true`.
  JSON check `no_command_templates: true`, `all_non_authorization_flags_false:
  true`.

- **Source code:** `rtdl_rtnn_benchmark_app.py` contains no `command_template`
  string. The `rtnn_prepared_execution_ranked_summary_payload` function computes
  telemetry and returns a dict; it does not generate execution commands or write
  runbook entries.

- **Non-authorization block:** All non-authorization flags in the JSON
  `non_authorization` object are false. The report and call-for-review carry the
  complete non-authorization block.

### 2. Does the telemetry-only RTNN app change correctly expose input_load, input_pack, input_load_pack, runner_after_input_load_pack, hot_query_median, and signature_match_status?

Yes. Verified directly in source at `rtnn_prepared_execution_ranked_summary_payload`:

- `input_load`: `input_load_sec` — wall time of `_load_rtnn_csv_xyz_records`
  call (CSV record loading duration).
- `input_pack`: `input_pack_sec` — wall time of `rt.pack_points` call (point
  column packing duration).
- `input_load_pack`: `input_load_pack_sec` — arithmetic sum of `input_load_sec`
  and `input_pack_sec`.
- `runner_after_input_load_pack`: `runner_sec` — wall time of
  `rt.run_fixed_radius_ranked_summary_3d_prepared_session` call (prepared
  session execution excluding input load/pack).
- `hot_query_median`: `float(metadata["measured_median_sec"])` — the per-query
  median from the prepared session, equivalent to steady-state hot-query time.
- `signature_match_status`: `runner_result.validation_output` — neighbor count
  and checksum verification output.

All six fields are present in the returned dict under `timing_sec` (for the
timing fields) and at the top level (for `signature_match_status`). They are
individually named and not merged.

The broader telemetry contract also includes `runner_wall`, `runner_measured_total`,
and `runner_measured_median`, which are present and separated. The required
metadata fields `prepared_execution_session_runner_used`,
`productized_execution_path`, `runtime_trunk_executes_end_to_end`,
`material_probe_candidate`, `release_authorized`,
`public_speedup_claim_authorized`, `broad_v3_faster_than_v2_claim_authorized`,
and `signature_match_status` are all present. No metadata field carries a
`true` value for any authorization or speedup flag.

### 3. Does the dry-run plan cover all 7 M70 shape groups and 14 rows?

Yes. The dry-run shape plan in the JSON packet is a strict reflection of the M70
frozen shapes table: exactly 7 shape groups across three distributions (uniform,
clustered, shell) and two point sizes (65536 and 262144), each with 2 backend
rows (embree and optix), totaling 14 rows. Point sizes and distributions match
the M70 frozen shapes one-for-one. JSON checks `all_7_shape_groups_planned:
true` and `all_14_rows_planned: true`.

### 4. Are source-surface route checks sufficient before any future harness execution is discussed?

Yes. The dry-run gate (via `v3_phoenix_m71_rtnn_local_harness_dry_run_gate.py`)
checks the following surface properties before any execution discussion:

- `rt.run_fixed_radius_ranked_summary_3d_prepared_session` is called (generic
  helper, not a route-specific shortcut). JSON check
  `source_generic_helper_call_present: true`.
- `prepared_execution_ranked_summary` mode is present and is the entry point
  for this protocol. JSON check `source_productized_mode_present: true`.
- Full-batch self-query `ValueError` assertion is present. JSON check
  `source_full_batch_constraint_present: true`.
- Telemetry split helper is present. JSON check
  `source_timing_fields_present: true`, `source_metadata_fields_present: true`.
- `"native_engine_customization": False` appears throughout the app at every
  mode boundary, confirming no route-specific tuning is active. JSON check
  `source_no_route_specific_tuning_marker: true`.

These checks are sufficient to confirm that the execution path is clean and
matches the M70 protocol contract before any execution conversation begins.

### 5. Are non-authorization boundaries preserved?

Yes. All non-authorization flags in the JSON `non_authorization` object are
false. The report and call-for-review carry the complete non-authorization block
in full. No unauthorized release label appears in any M71 file. The summary confirms
`release_authorized: false`, `benchmark_execution_authorized: false`,
`pod_authorized: false`.

---

## Carry-Forward Requirements

1. **No execution from M71:** M71 acceptance is strictly a dry-run gate
   acceptance. No execution protocol is unlocked. Any future execution proposal
   requires a new reviewed protocol with 3AI consensus.

2. **M70 final 3AI consensus required:** With both M70 and M71 Claude seats now
   backfilled, Codex must draft the final 3AI consensus for M70 and M71 and run
   the goal completion audit before either milestone can be declared
   goal-complete.

3. **Productized path constraint:** Future work must continue through
   `rt.run_fixed_radius_ranked_summary_3d_prepared_session` under the
   `prepared_execution_ranked_summary` app mode. No shortcut, route-specific
   tuning, or app-level customization.

4. **Per-distribution phase bounds remain unvalidated for clustered/shell:**
   The M71 dry-run plan correctly tags clustered and shell shapes with
   `phase_bound: true` (meaning per-distribution bounds are required). These
   bounds must be established before any phase-attribution claim in a future
   execution protocol.

5. **Hot-query boundary visibility:** The 0.988781x hot-query boundary from M69
   must remain visible in any future execution protocol.

6. **Full-batch self-query constraint:** Any relaxation of `query_batch_size ==
   point_count` requires separate code-path review before harness use.

7. **App-win gap is the primary risk:** 13 of 14 rows are below the 1.05x
   exit criterion. The execution protocol, when eventually proposed, must treat
   this gap as the primary risk and must not claim a whole-app or steady-state
   speedup.

---

## Explicit Non-Authorization Block

This review carries an explicit non-authorization block. No matter the verdict:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no runbook execution
- no benchmark execution
- no public speedup wording
- no broad V3-over-V2 wording
- no whole-app speedup wording
- no paper reproduction wording
- no RT-core speedup wording
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure
