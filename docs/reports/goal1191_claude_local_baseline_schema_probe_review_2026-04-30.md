# Goal1191 Claude Review: Local Baseline Schema Probe

Date: 2026-04-30

Reviewer: Claude (external review of Goal1191 local baseline schema probe)

## VERDICT: ACCEPT

All six probes pass. The probe set covers the six Goal1190 command-complete rows exactly, validates the required phase fields, and correctly holds the baseline/schema-only boundary. No blockers.

---

## Review Question 1: Do the six probes cover the six Goal1190 command-complete rows?

**Finding: Yes — exact one-to-one match.**

Goal1190 established six command-complete rows:

| App | Probe present |
| --- | --- |
| `database_analytics` | Yes |
| `graph_analytics` | Yes |
| `road_hazard_screening` | Yes |
| `polygon_pair_overlap_area_rows` | Yes |
| `polygon_set_jaccard` | Yes |
| `hausdorff_distance` | Yes |

The script's `PROBES` tuple contains exactly these six entries. The test `test_probe_definitions_cover_six_apps` asserts this set with an equality check (not a subset check), so no row can be added or dropped without breaking the test. The JSON report confirms `probe_count: 6`, `passing_probe_count: 6`, `failing_probe_count: 0`.

---

## Review Question 2: Do the probes validate the phase fields needed for same-contract comparison, especially graph visibility and polygon candidate-discovery?

**Finding: Yes — all critical phase paths are probed and confirmed present.**

The Goal1190 Claude review identified the phase fields that must survive local dry-run to support the same-contract OptiX comparison. All are present in `required_paths` and confirmed by the passing probe run:

| App | Critical path | Probed | Passed |
| --- | --- | --- | --- |
| `graph_analytics` | `graph_phase_totals_sec.query_visibility_pair_rows_sec` | Yes | Yes |
| `graph_analytics` | `sections.visibility_edges.summary.blocked_edge_count` | Yes | Yes |
| `polygon_pair_overlap_area_rows` | `run_phases.rt_candidate_discovery_sec` | Yes | Yes |
| `polygon_pair_overlap_area_rows` | `run_phases.native_exact_continuation_sec` | Yes | Yes |
| `polygon_pair_overlap_area_rows` | `candidate_row_count` | Yes | Yes |
| `polygon_set_jaccard` | `run_phases.rt_candidate_discovery_sec` | Yes | Yes |
| `polygon_set_jaccard` | `run_phases.native_exact_continuation_sec` | Yes | Yes |
| `polygon_set_jaccard` | `candidate_row_count` | Yes | Yes |
| `hausdorff_distance` | `run_phases.native_directed_summary_sec` | Yes | Yes |
| `hausdorff_distance` | `matches_oracle` | Yes | Yes |
| `database_analytics` | `results.0.prepared_session_warm_query_sec.median_sec` | Yes | Yes |
| `database_analytics` | `results.0.reported_run_phase_totals_sec.compact_summary_operation_count` | Yes | Yes |

The test `test_probe_definitions_include_required_phase_paths` locks in the four most critical paths (graph visibility, polygon candidate-discovery for both polygon apps, and hausdorff directed summary) with explicit `assertIn` checks. The running probe confirms these fields are emitted as parseable JSON by each public app — resolving the stdout-JSON risk flagged in the Goal1190 review.

---

## Review Question 3: Does the probe correctly remain baseline/schema-only?

**Finding: Yes — boundary is correct and tested.**

The probe's authorization boundary is stated in three independent locations:

1. **Script constant** (`scripts/goal1191_next_pod_local_baseline_schema_probe.py`, `run_probe()` return dict): `"This is a local baseline JSON/schema probe only. It does not run OptiX, does not authorize pod execution, and does not authorize public RTX speedup wording."`
2. **JSON output** (`goal1191_next_pod_local_baseline_schema_probe_2026-04-30.json`, `boundary` field): identical text.
3. **Markdown output** (`## Boundary` section): identical text.

The test `test_cli_probe_passes_in_current_environment` asserts `assertIn("does not authorize pod execution", markdown)` — the boundary cannot silently disappear from the rendered output without breaking the test.

All six commands use `--backend embree` only. No OptiX binary is invoked. `pod_ready_now` is not set anywhere in this probe; that field belongs to the upstream Goal1190 manifest, which hardcodes it `False`.

---

## Review Question 4: Are there any blockers before building the next local pod executor/schema intake?

**Finding: No blockers.**

The key open risk from Goal1190 was whether the three newly-unblocked apps (graph, polygon pair, polygon Jaccard) actually emit parseable JSON to stdout with the expected phase fields. Goal1191 resolves this: all three return code 0, no parse errors, no missing required paths. The concern is closed.

The Hausdorff timing-floor watch item from Goal1189/1190 ("may still be below timing floor") is a timing question, not a schema question. The probe correctly validates field presence only; timing adequacy is properly deferred to the pod executor. This is not a blocker at this stage.

No structural issues were found in the script. `_get_path` walks the payload correctly for both integer keys (used for the `results[0]` database path) and string keys. The `stdout_path` side-file for `output_json_arg` mode provides diagnostics without interfering with the JSON output path. Error accumulation (`missing_paths`, `parse_error`, `returncode`) is correct — `status: "ok"` requires all three to be clean.

---

## Summary

| Review question | Finding |
| --- | --- |
| Six probes cover six Goal1190 rows exactly | Yes — set equality enforced by test |
| Phase fields for same-contract comparison probed and confirmed present | Yes — all critical paths in `required_paths`, all passed |
| Probe stays baseline/schema-only; no OptiX/pod/release/speedup claim | Yes — boundary in three locations, tested |
| No blockers before pod executor/schema intake build | None — stdout-JSON risk closed, Hausdorff timing deferred appropriately |

## VERDICT: ACCEPT

The Goal1191 schema probe is correct, complete, and correctly scoped. The stdout-JSON risk from Goal1190 is now closed: all six public apps emit parseable JSON with the required phase fields on the Embree backend. Proceed to building the local pod executor and schema intake for the six row pairs.
