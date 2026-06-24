# Claude Review: Phoenix V3 M70 RTNN Focused Protocol Draft

Date: 2026-06-23 (backfilled 2026-06-24)

Reviewer: Claude (Anthropic claude-sonnet-4-6, external critical review seat)

Call for Review: `docs/reviews/call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`

Candidate Protocol Draft: `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`

Candidate Protocol JSON: `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json`

Report: `docs/reports/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`

Gate Test Suite: `tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py`

---

## Verdict

```
accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod
```

M70 is accepted as a protocol draft only. It correctly names all 7 frozen RTNN
shape groups and all 14 rows with exact same-contract incumbents, carries forward
every M69 boundary without weakening, keeps all phase metrics separated, and
defines fail-closed stop conditions. No execution, no POD, no release, no runbook
is authorized by this review.

---

## P0 / P1 / P2 Findings

### P0 Findings

None. The JSON packet, Markdown protocol draft, and report are internally
consistent. All 13 check flags in the JSON are true. `failed_checks` is empty.
Gate tests match JSON contents exactly. Non-authorization flags are all false.
No command templates, no authorization token.

### P1 Findings

**P1-A: App-win gap is fully active for 13 of 14 rows.** The frozen scorecard
shows that 13 of 14 RTNN rows sit below the 1.05x performance exit criterion
(the lone exception is `rtnn_embree_clustered_65536_ranked_summary` at 1.1491x).
The overall RTNN family geomean is approximately 1.003x. RTNN is data-compatible
but has not exited the performance gate. Any future execution protocol must treat
this gap as the primary risk, not a closed matter.

**P1-B: Hot-query boundary is a regression, not a speedup.** The M69
uniform-distribution repeat50 reference shows `hot_query_speedup_vs_legacy:
0.988781x` — a slight regression against the same-contract legacy path at steady
state. Runner-wall improvement is entirely from input-load/pack consolidation
(32.3%) and execution-prepare amortization (67.7% runner-after-pack share).
This boundary must remain visible and must not be presented as a hot-query
speedup in any future communication.

### P2 Findings

**P2-A: Full-batch self-query constraint is load-bearing.** The
`prepared_execution_ranked_summary` mode enforces `query_batch_size ==
point_count`. This limits evaluation scope by design. Any relaxation requires
separate code-path review; the stop conditions enforce this.

**P2-B: Clustered and shell phase splits are unvalidated.** The repeat50 phase
attribution (32.3% input-pack, 67.7% runner-after-pack) is validated for uniform
distribution only. Clustered and shell distributions require independent
per-distribution phase measurements before their phase bounds can be asserted.
The `per_distribution_phase_bound_required: true` flag on all clustered/shell
shapes correctly records this gap.

---

## Direct Answers to Review Questions

### 1. Does M70 name all exact frozen RTNN shapes and same-contract incumbents?

Yes. The JSON `frozen_shapes` array contains exactly 7 shape groups and 14 rows
(2 rows per group: one embree, one optix). The 7 groups span three distributions
(uniform, clustered, shell) and two point sizes (65536 and 262144):

- `clustered:262144:rtnn_clustered_262144_ranked_summary`
- `clustered:65536:rtnn_clustered_65536_ranked_summary`
- `shell:262144:rtnn_shell_262144_ranked_summary`
- `shell:65536:rtnn_shell_65536_ranked_summary`
- `uniform:262144:rtnn_uniform_262144_ranked_summary`
- `uniform:65536:prepared_3d_ranked_summary`
- `uniform:65536:rtnn_uniform_65536_ranked_summary`

Each row names its same-contract incumbent precisely:
- Embree rows: `frozen_v2_14_embree_ranked_summary_row` (same-contract embree
  fixed-radius ranked-summary aggregate incumbent)
- OptiX rows: `legacy_app_front_door_prepared_optix_ranked_summary`
  (`prepared_optix_ranked_summary` mode)

Each same-contract incumbent specifies identical contract terms: same
`point_count`, same distribution, same generated or frozen point file, same
radius and k from the frozen RTNN row config, `query_batch_size == point_count`,
ranked-summary aggregate output contract, and signature or aggregate checks must
match before timing is interpreted.

The JSON checks `all_14_rows_named: true`, `all_7_shape_groups_named: true`,
and `all_rows_have_same_contract_incumbents: true` are all present and true.

### 2. Does M70 preserve the M69 boundaries?

Yes. All six M69 carry-forward items are present verbatim in the JSON
`m69_carry_forward` array:

- **Uniform-only repeat50 phase evidence:** `"repeat50 phase attribution is
  uniform-distribution evidence only"` — explicit in carry-forward and
  in the phase metric contract (`scope: "uniform-distribution repeat50 reference
  only"`). Stop condition halts if clustered/shell reuse this split without
  per-distribution measurement.

- **Per-distribution phase bounds:** `"per-distribution phase bounds are
  required before clustered or shell protocol use"` — explicit in carry-forward
  and enforced by `per_distribution_phase_bound_required: true` on all four
  clustered/shell shape groups. JSON check `distribution_bounds_required: true`.

- **Full-batch self-query constraint:** `"prepared_execution_ranked_summary
  currently requires full-batch self-queries"` — explicit in carry-forward.
  All 7 shape groups have `query_role: "full_batch_self_query"` and
  `query_batch_size == point_count`. JSON check
  `full_batch_self_query_constraint_source_present: true`. Stop condition
  requires separate code-path review if non-self-query batches are proposed.

- **Exact frozen RTNN shapes and same-contract incumbents must be named:**
  See answer to Q1 above. JSON check `all_rows_have_same_contract_incumbents:
  true`.

- **0.988781x hot-query boundary must remain visible:** Present verbatim in
  `m69_carry_forward`. Phase metric contract records
  `hot_query_speedup_vs_legacy: 0.9887810047298636`. Stop condition halts
  any claim that hides or contradicts this boundary.

- **Exact aggregate, productized prepared-session runner, graph partner bridge,
  and diagnostic rows must not be merged:** Explicit in carry-forward and
  enforced by a dedicated stop condition.

### 3. Does M70 require per-distribution phase bounds before clustered or shell shapes are used?

Yes. The JSON tags all four clustered and shell shape groups with
`per_distribution_phase_bound_required: true`, while the three uniform groups
carry `false`. The M69 carry-forward list names this requirement explicitly.
The sixth stop condition halts the protocol if clustered or shell rows reuse the
uniform repeat50 phase split without per-distribution measurement. JSON check
`distribution_bounds_required: true`.

### 4. Does M70 preserve the full-batch self-query constraint?

Yes. All 7 shape groups carry `query_role: "full_batch_self_query"` and
`query_batch_size == point_count` (65536 or 262144 respectively). The M69
carry-forward names this constraint explicitly. The JSON check
`full_batch_self_query_constraint_source_present: true`. The fourth stop
condition halts the protocol if non-self-query batches are proposed without
separate code-path review.

### 5. Are hot-query, runner-wall, prepare, and input-loading/packing metrics separated strongly enough?

Yes. The phase metric contract defines 10 named metrics that must remain
separate: `input_load_sec`, `input_pack_sec`, `input_load_pack_sec`,
`execution_prepare_sec`, `runner_after_input_load_pack_sec`,
`hot_query_median_sec`, `runner_wall_sec`, `measured_total_sec`,
`measured_median_sec`, and `signature_match_status`. The field
`must_keep_separate: true` is explicit. The fifth stop condition halts the
protocol if any of these are merged. The M69 uniform repeat50 reference records
the exact split values (0.866893s total delta, 32.3% input-pack share, 67.7%
runner-after-pack share, 0.357405s execution-prepare delta). JSON check
`phase_metrics_separated: true`.

### 6. Are the stop conditions enough to prevent RTNN app tuning, repeat50 overclaiming, and contract mixing?

Yes. The nine stop conditions are collectively sufficient and fail-closed:

- **Against RTNN app tuning:** Stop if productized runner metadata does not show
  `prepared_execution_session_runner` and `runtime_trunk_executes_end_to_end=true`.
  Stop if any route-specific tuning wording appears.

- **Against repeat50 overclaiming:** Stop if the result is only
  input-loading/packing consolidation or repeat50 amortization with no
  runner-after-pack contribution.

- **Against contract mixing:** Stop if exact aggregate, productized
  prepared-session runner, graph partner bridge, raw rows, or paper diagnostic
  rows are merged into a single claim. Stop if any frozen RTNN shape lacks its
  exact same-contract incumbent row.

- **Against unauthorized scope:** Stop if any public, release, all-app, POD,
  V4, embedding, C ABI, true-zero-copy, route-specific tuning, or watch-row
  closure wording appears.

- **Against harness without prior review:** Stop if a future harness lacks a
  reviewed local dry-run gate (M71 addresses this).

### 7. Is M71 local harness design/dry-run gate the right next step?

Yes. M71 as a local dry-run gate — schema validation, source-surface routing
checks, telemetry field verification, and fail-closed behavior — is the correct
incremental step. It is scoped to local no-execution validation only. It does
not authorize benchmarks, POD, runbooks, or all-app runs. The M70 stop condition
"Stop if a future harness lacks a reviewed local dry-run gate" directly implies
M71 as the gating mechanism.

### 8. Are any non-authorization boundaries weakened?

No. All non-authorization flags in the JSON `non_authorization` object are
false. The protocol draft, report, and call-for-review all carry the complete
non-authorization block. Protocol scope flags `execution_authorized_now`,
`runbook_authorized_now`, `pod_authorized_now`, `all_app_authorized_now`, and
`release_authorized_now` are all false. The `future_harness_requirements.status`
is `requirements_only_no_execution`. No unauthorized release label appears anywhere.

---

## Carry-Forward Requirements for M71

1. **No execution boundary:** M71 is a local dry-run gate only. No live
   benchmark runs, no POD spend, no runbook execution, no all-app runs.

2. **Telemetry phase isolation:** The harness must expose and validate all 10
   separated phase metrics as named in the M70 phase metric contract, failing
   closed if any are missing or merged.

3. **Productized path verification:** Source-surface checks must confirm
   `rt.run_fixed_radius_ranked_summary_3d_prepared_session` through the
   `prepared_execution_ranked_summary` mode with
   `runtime_trunk_executes_end_to_end=true` and no route-specific tuning flags.

4. **Full-batch self-query enforcement:** The dry-run gate must fail if
   `query_batch_size != point_count`.

5. **Per-distribution shape coverage:** The dry-run plan must cover all 7 M70
   shape groups and all 14 rows.

6. **Hot-query boundary visibility:** The 0.988781x boundary must remain visible
   and must not be misrepresented as a speedup.

7. **M70 Claude review debt:** M70 is not goal-complete until this backfill
   review is recorded and a final 3AI consensus is written. This review
   satisfies the Claude seat requirement for M70. Codex must now draft the
   final 3AI consensus and goal completion audit.

8. **No execution protocol proposed from M71:** Any future execution protocol
   requires a new, separate review. M71 acceptance does not authorize execution.

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
