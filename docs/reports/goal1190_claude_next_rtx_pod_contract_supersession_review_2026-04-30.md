# Goal1190 Claude Review: Next RTX Pod Contract Manifest Supersession

Date: 2026-04-30

Reviewer: Claude (external review of Goal1190 supersession of Goal1189)

## VERDICT: ACCEPT

The supersession is legitimate, internally consistent, and correctly scoped. All six rows are command-complete, all remain gated behind local dry-run, and the authorization boundary is fully preserved.

---

## Review Question 1: Legitimacy of Superseding Goal1189 Blocked Rows

**Finding: Legitimate.**

Goal1189 blocked graph, polygon pair, and polygon Jaccard rows for a specific reason: no Embree/CPU baseline existed that was scoped to the same contract (candidate-discovery only, not exact-area or exact-Jaccard continuation). Goal1190 resolves exactly this gap by providing public-app Embree summary commands for each blocked row:

| App | Baseline command | Resolution |
| --- | --- | --- |
| `graph_analytics` | `rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 30000 --output-mode summary` | Provides `graph_phase_totals_sec.query_visibility_pair_rows_sec` for phase comparison |
| `polygon_pair_overlap_area_rows` | `rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary` | Provides `run_phases.rt_candidate_discovery_sec` for phase comparison |
| `polygon_set_jaccard` | `rtdl_polygon_set_jaccard.py --backend embree --copies 8192 --output-mode summary` | Provides `run_phases.rt_candidate_discovery_sec` for phase comparison |

This approach is valid: there is no requirement that the baseline be a special harness rather than the public app, provided the comparison is restricted to the correct phase field. The previously missing piece was a concrete baseline command — Goal1190 supplies one for each row. The key remaining unknown — whether the public app summary output actually emits the expected phase fields as parseable JSON — is correctly gated behind the local dry-run ("JSON schemas and comparable phase fields are verified").

The supersession does not change what is being claimed or tested; it only provides the missing Embree baseline commands.

---

## Review Question 2: All Six Rows Command-Complete, `local_dry_run_required`, `pod_ready_now: false`

**Finding: Correct and enforced.**

| App | `optix_command` present | `baseline_command` present | Status | pod_ready_now |
| --- | --- | --- | --- | --- |
| `database_analytics` | Yes | Yes | `local_dry_run_required` | false |
| `graph_analytics` | Yes | Yes | `local_dry_run_required` | false |
| `road_hazard_screening` | Yes | Yes | `local_dry_run_required` | false |
| `polygon_pair_overlap_area_rows` | Yes | Yes | `local_dry_run_required` | false |
| `polygon_set_jaccard` | Yes | Yes | `local_dry_run_required` | false |
| `hausdorff_distance` | Yes | Yes | `local_dry_run_required` | false |

The script's `build_manifest()` validator enforces all three invariants:
- Any row not carrying `"local_dry_run_required"` becomes a blocker (`valid=false`).
- Any row with an empty `optix_command` or `baseline_command` becomes a blocker.
- `pod_ready_now` is hardcoded `False` — not derived from row state, cannot drift.

`local_dry_run_required_count: 6` matches `row_count: 6`, confirming no row escaped the gate.

---

## Review Question 3: Honesty of Phase-to-Compare Fields

**Finding: Honest and appropriately narrow.**

The three newly-unblocked rows are the critical ones to evaluate:

**`graph_analytics`**: Phase is `"Embree graph_phase_totals_sec.query_visibility_pair_rows_sec versus OptiX prepared visibility count/query phase"`. This correctly identifies a sub-phase within the Embree summary rather than overall app latency. The claim contract is "visibility_edges prepared any-hit summary only" and the boundary explicitly excludes BFS orchestration, triangle set-intersection, shortest-path, and distributed graph — all computation outside the query_visibility phase.

**`polygon_pair_overlap_area_rows`**: Phase is `"run_phases.rt_candidate_discovery_sec; exact area continuation excluded"`. The explicit exclusion of exact area continuation is present in both the `phase_to_compare` field and the `boundary` field ("no whole-app speedup claim, exact area, overlay matrix, or monolithic polygon-area claim"). The claim contract reads "native-assisted LSI/PIP candidate discovery only". The test directly asserts `assertIn("rt_candidate_discovery_sec", ...)`. Consistent and honest.

**`polygon_set_jaccard`**: Phase is `"run_phases.rt_candidate_discovery_sec; exact set-area/Jaccard continuation excluded"`. Same structure as polygon pair. The boundary excludes "exact Jaccard, exact set-area, or whole polygon-set app claim". The claim contract reads "safe-chunk native-assisted LSI/PIP candidate discovery only". Consistent and honest.

No row claims a whole-app speedup. All three polygon/graph rows scope the comparison to a single sub-phase. The exclusion language in `phase_to_compare` and `boundary` is redundant (both say it) — this is the correct direction.

**One note on output format**: The three newly-unblocked rows redirect baseline output via `>` to a JSON path, while the OptiX commands use `--output-json`. If the public apps don't emit JSON to stdout, the redirected baseline files will not be parseable JSON, and the phase field extraction will fail. This is a real risk — but it is exactly what the local dry-run is designed to catch. It is not a blocker for accepting this manifest; it is the reason `local_dry_run_required` is the correct status.

---

## Review Question 4: Authorization Boundary Preserved

**Finding: Fully preserved, in three independent locations.**

1. **Markdown preamble**: "This supersession changes planning status only. It does not authorize public RTX speedup wording, release, tagging, or cloud execution by itself."
2. **JSON `boundary` field**: Identical text.
3. **`pod_recommendation` field**: "Do not use a paid pod yet. The manifest is now command-complete, but local dry-runs and schema checks must pass before cloud execution."

The script hardcodes `"pod_ready_now": False` — there is no code path that sets it true. The validator enforces that every row boundary contains `"whole-app speedup claim"` or marks the manifest invalid.

The Hausdorff `watch_item` ("may still be below timing floor; local dry-run must adjust if needed") from the Goal1189 review is preserved verbatim in the `scale_choice` field. This is the correct carry-forward of the one non-blocking risk identified previously.

---

## Test Coverage Assessment

Four tests, all passing the relevant invariants:

- `test_manifest_is_command_complete_but_not_pod_ready`: valid=True, row counts, pod_ready_now=False, supersedes Goal1189.
- `test_all_rows_have_baseline_and_optix_commands`: per-row structural checks including status, commands, phase_to_compare, boundary phrase.
- `test_graph_and_polygon_baselines_use_public_apps`: explicitly asserts the public app filenames and `rt_candidate_discovery_sec` phase field in the three newly-unblocked rows.
- `test_cli_writes_outputs`: end-to-end CLI smoke test.

Coverage is adequate. The test for public app baselines (`test_graph_and_polygon_baselines_use_public_apps`) is the critical new addition that locks in the supersession's key claim.

---

## Summary of Findings

| Question | Finding |
| --- | --- |
| Supersession of Goal1189 blocked rows is legitimate | Yes — public app Embree summary commands are valid baselines when phase comparison is correctly scoped |
| All 6 rows command-complete, `local_dry_run_required`, `pod_ready_now: false` | Yes — enforced by validator and hardcoded |
| Phase-to-compare fields honest; polygon area/Jaccard continuation excluded | Yes — exclusions present in both phase_to_compare and boundary fields; test locks it |
| No-release/no-public-speedup/no-cloud-run boundary preserved | Yes — three independent locations, hardcoded pod_ready_now, validator boundary check |

## VERDICT: ACCEPT

Goal1190 correctly resolves the three rows that Goal1189 blocked for missing baseline harnesses. The resolution — using public app Embree summary output scoped to the relevant phase field — is legitimate, honest about what it compares, and does not expand any claim boundary. All six rows are command-complete, all remain `local_dry_run_required`, and `pod_ready_now` is false. The authorization boundary is preserved identically to prior goals.

Proceed to: local command-shape dry-runs for all six rows, verifying that the public app Embree outputs emit the expected phase fields as parseable JSON. Verify Hausdorff timing floor. Do not package a pod batch until local dry-runs pass and schema checks confirm comparable phase fields.
