# Goal977 OptiX-Only Artifact Intake — Claude Review

Date: 2026-04-26
Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

---

## Scope

This review covers the Goal977 intake script, its tests, the two source cloud artifacts, the four generated Goal835 baseline artifacts, and the downstream Goal836/Goal971 readiness state they produce.

---

## Source Artifact Verification

### goal889_graph_visibility_optix_gate_rtx.json (Runpod A5000, 2026-04-26T09:06:25)

- `strict_pass: true`, `strict_failures: []`
- `status: "pass"`
- Three OptiX records, each with `parity_vs_analytic_expected: true` and `status: "ok"`:
  - `optix_visibility_anyhit`: row_count=80000, sec=1.583, scenario=visibility_edges
  - `optix_native_graph_ray_bfs`: row_count=40000, sec=5.470, scenario=bfs
  - `optix_native_graph_ray_triangle_count`: row_count=20000, sec=1.197, scenario=triangle_count
- Each optix record's row_digest matches its corresponding `analytic_expected_*` record exactly.
- `copies: 20000`, `validation_mode: "analytic_summary"`, `output_mode: "summary"`
- `boundary` field correctly scopes to ray/triangle any-hit and native graph-ray candidate generation only.

### goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json (Runpod A5000, 2026-04-26T09:05:06)

- `strict_pass: true`, `strict_failures: []`
- `status: "pass"`
- `result.matches_oracle: true`, `result.overflowed: false`
- `actual_digest == expected_digest` across all five fields (row_count, polygon_id_sum, segment_id_sum, unique_polygon_count, unique_segment_count)
- `iterations: 5`, `output_capacity: 4096`, `emitted_count == copied_count == 2816`
- `boundary` field explicitly states it does not authorize public speedup claims.

Both source artifacts are genuine strict-pass cloud RTX runs. No fabrication, no partial pass.

---

## Intake Script Analysis (scripts/goal977_optix_only_artifact_intake.py)

### Correctness parity logic

**Graph baselines** (`_graph_artifact`): parity is set True only when all three conditions hold simultaneously:
- `graph_payload["strict_pass"] is True`
- `record["status"] == "ok"` (per-scenario record)
- `record["parity_vs_analytic_expected"] is True` (per-scenario parity)

All three conditions are satisfied for each scenario in the source artifact.

**Segment baseline** (`_segment_anyhit_artifact`): parity is set True only when:
- `payload["strict_pass"] is True`
- `result["matches_oracle"] is True`
- `result["overflowed"] is False`

All three conditions are satisfied in the source artifact.

Both parity chains are properly grounded in the source artifact's own validation results, not asserted independently.

### Target resolution

The four targets in GRAPH_BASELINES plus `optix_prepared_bounded_pair_rows` are verified against `scripts/goal759_rtx_cloud_benchmark_manifest.py` lines 164–170 and 232–234. These names appear verbatim in the manifest's `required_baselines` lists for `graph_analytics:graph_visibility_edges_gate` and `segment_polygon_anyhit_rows:segment_polygon_anyhit_rows_prepared_bounded_gate`. The intake is targeting the correct slots.

### No speedup authorization

Every generated artifact carries:
- `authorizes_public_speedup_claim: false`
- A note: "This artifact does not authorize public RTX speedup claims."
- `collect()` boundary: "This intake converts existing RTX artifacts into Goal835 baseline artifacts. It does not run cloud and does not authorize public RTX speedup claims."

No path in the script sets `authorizes_public_speedup_claim: true` or omits the boundary.

### Claim limits

All four artifacts inherit `claim_limit` from the Goal835 plan row via `load_goal835_row()`. The values are:
- Graph: "bounded graph RT sub-paths only: visibility any-hit plus BFS/triangle candidate generation; not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration"
- Segment: "experimental native bounded pair-row gate only; not default public app behavior and not unbounded row-volume performance"

These limits are correctly restrictive and prohibit whole-app or unbounded speedup claims.

### Benchmark scale honesty

Graph artifacts use `{copies: 20000, validation_mode: "analytic_summary"}` from the source artifact (the gate row has `scale: null` in the plan, so no plan-vs-artifact scale conflict). Segment artifact uses `{dataset: "derived/br_county_subset_segment_polygon_tiled_x256", iterations: 5, output_capacity: 4096}` directly from the source artifact. Both are accurately transcribed.

### Audit trail

Each artifact's `validation` field preserves the source artifact path, `strict_pass`, `strict_failures`, and per-artifact parity fields. The conversion is fully traceable.

---

## Generated Baseline Artifact Verification

All four artifacts were read directly:

| Artifact | status | correctness_parity | authorizes_public_speedup_claim | repeated_runs | phase coverage |
|---|---|---|---|---|---|
| optix_visibility_anyhit | ok | true | false | 3 | 5/5 required phases |
| optix_native_graph_ray_bfs | ok | true | false | 3 | 5/5 required phases |
| optix_native_graph_ray_triangle_count | ok | true | false | 3 | 5/5 required phases |
| optix_prepared_bounded_pair_rows | ok | true | false | 5 | 13/13 required phases |

Phase coverage for graph artifacts matches the plan's `required_phases: [records, row_digest, strict_pass, strict_failures, status]`. Phase coverage for segment matches the plan's 13-entry required_phases list exactly.

---

## Goal836 50/50 Readiness State

The Goal836 gate report (re-run after intake) shows:
- `required_artifact_count: 50`
- `valid_artifact_count: 50`
- `missing_artifact_count: 0`
- `invalid_artifact_count: 0`
- `status: "ok"`

All 17 rows pass with `row_status: "ok"`. The four new artifacts account for the transition from 46/50 to 50/50. The arithmetic is consistent: graph_analytics required 7 baselines (3 CPU + 3 OptiX + 1 Embree), the 3 OptiX ones were the remaining gap; segment required 3 (CPU + OptiX + PostGIS), the OptiX one was the remaining gap.

The readiness gate boundary is preserved: "This readiness gate only inspects local baseline evidence. It does not run benchmarks, start cloud resources, promote deferred apps, or authorize RTX speedup claims."

---

## Goal971 Conservative State

Goal971 report shows:
- 17/17 rows at `same_semantics_baselines_complete`
- `public_speedup_claim_authorized_count: 0`
- `baseline_pending_count: 0`

`same_semantics_baselines_complete` is correctly defined as "strict Goal836 required baseline set is present and valid; this still needs review before public speedup wording." No row is promoted to a public speedup claim.

---

## Test Verification

### goal977_optix_only_artifact_intake_test.py

- `test_targets_exact_remaining_optix_only_baselines`: Verifies GRAPH_BASELINES set is exactly the three expected names; for all four (app, path_name, baseline) triples, confirms the baseline name appears in `load_goal835_row()["required_baselines"]` and the artifact filename follows the correct convention. Valid and sufficient.
- `test_source_artifacts_are_strict_pass_before_intake`: Guards against re-running the intake on a source artifact that has since degraded. Checks strict_pass, empty strict_failures, matches_oracle, and overflowed. Valid pre-condition gate.

### goal974_remaining_local_baselines_test.py

- `test_remaining_baselines_are_valid_after_linux_postgis_collection`: `expected_remaining_missing` is `{}`, asserting 0 missing and 0 invalid across all rows. Consistent with the 50/50 state.
- `test_goal971_stays_conservative_after_partial_baseline_collection`: Asserts `same_semantics_baselines_complete_count==17`, `baseline_pending_count==0`, `public_speedup_claim_authorized_count==0`. Correctly enforces conservative claim boundary.

### goal836_rtx_baseline_readiness_gate_test.py

- `test_real_plan_currently_has_complete_baseline_artifacts_without_authorizing_claims`: Asserts status=="ok", missing==0, invalid==0. Passes with 50/50 state.
- Synthetic valid/invalid artifact tests correctly verify schema enforcement (correctness_parity, repeated_runs, phase coverage, benchmark scale matching).
- CLI test verifies exit code 0 and correct JSON output.

All tests are coherent with the documented state and do not over-claim.

---

## Minor Observations (Non-Blocking)

**Graph repeated_runs=3 interpretation**: The script hardcodes `repeated_runs=3` for graph baselines. The source gate is a single comprehensive run across 3 scenarios (not 3 independent timing repetitions of each scenario). This is consistent with the existing CPU baseline artifacts for graph_analytics (also showing repeated_runs=3 in the Goal836 JSON), so the pattern is established. The segment artifact correctly derives repeated_runs from `iterations=5`.

**Shared phase_seconds.records=6.0 across three graph baselines**: All three graph artifacts get `phase_seconds.records=6.0` (total record count across all scenarios in the gate). This is correct — the gate is a joint run — but it means per-baseline phase timing is the gate-level count, not an isolated per-scenario count. This is the appropriate representation for a chunked summary-mode gate and matches the plan's required_phases for this row.

---

## Verdict

**ACCEPT**

The intake is valid, bounded, honest, and does not authorize public speedup claims. Specifically:

1. **Valid**: Both source cloud artifacts are genuine strict-pass RTX runs with digit-exact parity verification (analytic summary match for graph; CPU oracle digest match for segment).
2. **Bounded**: All four artifacts carry correct claim_limits from the Goal835 plan, explicitly excluding whole-app, unbounded, and non-RT-sub-path claims.
3. **Honest**: Source artifact provenance is preserved in each artifact's `validation` field; notes describe the conversion; no independent performance claims are made.
4. **No public speedup authorization**: `authorizes_public_speedup_claim: false` is hardcoded in the schema builder and confirmed in all four artifacts; the intake boundary statement is explicit.
5. **50/50 readiness state is correct**: The four new artifacts complete the required set; arithmetic and gate validation are consistent.
6. **Tests are correct**: They verify source quality before intake, exact target matching against the plan, and conservative post-intake claim state.
