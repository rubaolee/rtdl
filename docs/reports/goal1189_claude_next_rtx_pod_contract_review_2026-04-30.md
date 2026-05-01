# Goal1189 Claude Review: Next RTX Pod Contract Manifest

Date: 2026-04-30

Reviewer: Claude (external review of Goal1189 manifest)

## VERDICT: ACCEPT

The manifest is internally consistent, correctly conservative, and safe to proceed with — subject to the local dry-run gate and baseline-harness prerequisite work called out in the manifest itself.

---

## Review Question 1: Alignment with Goal1188 Evidence Gaps

**Finding: Aligned exactly.**

Goal1188 two-AI consensus (accepted) identified exactly six apps needing public-wording evidence:
`database_analytics`, `graph_analytics`, `road_hazard_screening`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`, `hausdorff_distance`.

Goal1189 manifest contains exactly these six apps, in the same scope. No app is missing, none added beyond scope.

---

## Review Question 2: Correctness of the Three-Way Ready/Blocked Split

**Finding: Correct and well-justified.**

### Pod-ready after local dry-run (3 apps)

| App | Both commands present? | Same-contract baseline? |
| --- | --- | --- |
| `database_analytics` | Yes | Yes — same script, `--backend embree`, same copies/iterations/mode/strict |
| `road_hazard_screening` | Yes | Yes — example app `--backend embree`, same copies |
| `hausdorff_distance` | Yes | Yes — example app `--backend embree`, same copies/radius |

All three have symmetrical optix/baseline command pairs. The boundary field on each correctly excludes whole-app, SQL/DBMS, GIS/routing, and exact-Hausdorff claims respectively.

### Needs baseline harness before pod (3 apps)

| App | Why blocked | Missing work description |
| --- | --- | --- |
| `graph_analytics` | No CPU/Embree summary baseline for visibility_edges | Must emit comparable blocked/visible counts and timing without full row materialization |
| `polygon_pair_overlap_area_rows` | No candidate-discovery-only CPU/Embree baseline | Full exact-area continuation is not an acceptable baseline for the candidate-only claim |
| `polygon_set_jaccard` | No candidate-discovery-only CPU/Embree baseline | Exact set-area/Jaccard continuation is outside the claim boundary |

Each `missing_work` field is specific and actionable. The script enforces this: `pod_ready_after_local_dry_run` rows with empty `baseline_command` would set `valid=false`. The three blocked rows correctly have empty `baseline_command` strings.

---

## Review Question 3: Scale Choices and Command Shapes

**Finding: Reasonable and bounded, with one watch item.**

| App | Scale choice | Rationale grounded in prior data? | Command bounded? |
| --- | --- | --- | --- |
| `database_analytics` | copies=30000, iters=10 | Yes — Goal1184 copies=20000 was 0.09356s (below floor); 50% increase has margin | Yes — `compact_summary`, `sales_risk`, `--strict` |
| `graph_analytics` | copies=30000 | Yes — above prior 20000 while preserving summary semantics | Yes — `analytic_summary`, `--chunk-copies 0` |
| `road_hazard_screening` | copies=20000, iters=5 | Yes — Goal1184 already cleared floor at median 0.108167s | Yes — `road_hazard_prepared_summary` scenario |
| `polygon_pair_overlap_area_rows` | copies=20000, chunk_copies=100 | Yes — Goal1184 candidate-discovery phase 2.950786s was reviewable | Yes — `pair_overlap`, `analytic_summary` |
| `polygon_set_jaccard` | copies=8192, chunk_copies=512 | Yes — Goal1184 safe chunk cleared at 1.830098s; chunk=512 is known safe | Yes — `jaccard`, `analytic_summary` |
| `hausdorff_distance` | copies=200000, iters=10, radius=0.4 | Yes — 10x from 20000; prior was 0.001296s (far below floor) | Yes — `hausdorff_threshold` scenario |

**Watch item — Hausdorff timing floor:** Prior timing at copies=20000 was 0.001296s. Linear scaling to 200000 predicts ~0.013s, which is still well below a typical 0.1s reviewable floor. The manifest correctly gates this behind local dry-run rather than claiming it will clear the floor. The local dry-run must confirm reviewable timing before pod packaging proceeds. This is not a blocker — the dry-run is the right gate — but the Hausdorff row may require a further scale increase after the dry-run result is known.

Command shapes are consistent across all six rows: all use `--output-json` with scoped subdirectory paths, `--output-mode summary` or `compact_summary`, and no command claims whole-app, exact-computation, or release-grade output.

---

## Review Question 4: Manifest Does Not Self-Authorize Pod, Release, or Cloud Execution

**Finding: Correctly scoped and enforced.**

The manifest states its boundary in three places:
1. Top of the markdown document (above the summary table)
2. Trailing boundary section
3. JSON `boundary` field

The `pod_recommendation` field explicitly says: "Do not run the next public-wording pod batch yet."

The script's `build_manifest()` validator enforces that:
- Every row with `pod_ready_after_local_dry_run` status must have a non-empty `baseline_command` (or it becomes a blocker → `valid=false`)
- Every row's boundary must contain either `"whole-app speedup claim"` or `"whole app speedup claim"` (checked with both hyphenated forms)

All six rows pass both checks. The boundary phrase check correctly handles the `polygon_set_jaccard` row which uses the unhyphenated form.

---

## Test Coverage Assessment

Four tests cover the manifest correctly:
- `test_manifest_is_valid_but_not_pod_ready`: checks valid=True, counts, and recommendation wording
- `test_ready_and_needs_harness_apps_are_expected`: checks exact app-set membership
- `test_each_row_has_boundaries_and_commands`: checks structural invariants per-row, including that blocked rows have `missing_work`
- `test_cli_writes_outputs`: end-to-end CLI smoke test

Coverage is adequate for a contract manifest. No gaps observed.

---

## Summary of Findings

| Question | Finding |
| --- | --- |
| Six rows match Goal1188 gaps | Yes — exact match |
| Three-way ready/blocked split correct | Yes — all three blocked rows have specific actionable missing_work |
| Scale choices reasonable and bounded | Yes — all grounded in Goal1184 data; Hausdorff is a dry-run watch item, not a blocker |
| Manifest does not self-authorize pod/release/cloud | Yes — explicitly blocked in three locations and enforced by validator logic |

## VERDICT: ACCEPT

The manifest correctly captures the six evidence gaps from Goal1188, applies the right readiness split with specific blocking rationale for the three harness-incomplete rows, uses scale choices grounded in prior measured timing, and does not self-authorize any pod run, public-wording promotion, release, or cloud execution. Proceed to baseline harness work for graph, polygon pair, and polygon Jaccard, then run local dry-runs for all six rows before packaging the next pod batch. Verify Hausdorff timing floor after the dry-run.
