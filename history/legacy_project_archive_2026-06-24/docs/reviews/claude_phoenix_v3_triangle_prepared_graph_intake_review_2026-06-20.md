Now I have everything I need. Let me deliver the full review.

---

## Review: Phoenix V3 Triangle Prepared-Graph Candidate Intake

**Verdict: approve-with-required-fixes (P1-level fixes only; no P0 blockers found)**

---

### Fact Verification

All stated facts in the call-for-review check out against the artifacts:

| Fact | Verified |
|---|---|
| 4 rows extracted from 2 comparison groups | JSON `comparison.row_count=4`, `group_count=2` |
| Groups are `cliques_20000` and `cliques_80000` | Both present in `pairs[]` and `rows[]` |
| Same contract `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit` | `same_contract: true`; verified per-row in JSON |
| Same primary metric `timing_ms.query_median_ms converted-ms-to-sec` | `same_metric_source: true`; per-row `primary_metric_source` matches |
| All rows match triangle-count oracle | 20k: 80,000 ✓; 80k: 320,000 ✓ (4 triangles per K4 clique) |
| Phase timing validates under `rtdl.partner.v2.4` | `all_phase_timing_accept: true`; per-row `phase_contract_version` matches |
| Embree non-RT-core, OptiX RT-core | `embree_rt_core_accelerated: false`, `optix_rt_core_accelerated: true` per pair |
| All claim flags blocked | `all_claim_flags_blocked: true`; `release_authorized: false`, `m7_qualified: false` |
| 20k ratio 116.060x | 0.14156 / 0.001220 = 116.060 ✓ |
| 80k ratio 347.232x | 0.54789 / 0.001578 = 347.232 ✓ |
| Status `internal_triangle_prepared_graph_candidate_not_m7` | Top-level `status` field ✓ |
| Synthetic K4 clique ladder, not paper datasets, not M7-qualified | MD report, JSON `synthetic_fixture_boundary`, `m7_blockers` ✓ |

---

### Q1: Does the intake honestly classify Triangle as internal candidate evidence, not closure?

**Yes, without reservation.** The MD report leads with the status line; the JSON has five distinct `false` claim boundary flags; the status string itself includes `_not_m7`; `m7_qualified: false` appears in both `comparison` and per-pair `claim_status`; the report's "What This Evidence Does Not Mean" section is explicit. The wording gate script (`v3_release_wording_gate.py`) requires the string `internal_triangle_prepared_graph_candidate_not_m7` to appear in the scanned corpus. The MD file is in the scanned set (`DEFAULT_FILES` line 37). Classification is honest.

---

### Q2: Is `prepared_graph_chunk` the right generic capability label?

**Partially correct as a taxonomy label; it carries an unresolved ambiguity.**

The field is named `generic_capability`, not `proven_capability`, and the top-level `status` field already contains `_candidate_not_m7`. The label correctly identifies what Phoenix domain this intake belongs to. However:

- The `m7_blockers` list includes `"prepared_graph_chunk_executor_linkage_not_closed"` — meaning the route has not been closed against the actual M113/M120 V3 prepared-graph chunk executor. The label asserts the taxonomy without asserting the linkage.
- `run_test_matrix.py` groups `v3_current` include both `goal4509_v3_0_m113_prepared_graph_chunk_executor_test` and `goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_test`. These are distinct gates. An agent reading only `generic_capability: prepared_graph_chunk` without reading `m7_blockers` could incorrectly conclude the M113/M120 linkage is closed.

**Recommendation (P1):** Add a companion field to the payload:

```json
"generic_capability_status": "candidate_executor_linkage_not_closed"
```

This makes the label unambiguous without changing its taxonomy role. Alternatively, rename the value to `prepared_graph_chunk_candidate` to embed the qualifier directly. Either fix prevents label-creep into future agent summaries.

---

### Q3: Are the M7 blockers complete enough?

**Mostly yes, but one material gap.**

The five listed blockers correctly cover: fixture type, workload scope, author/paper comparison, executor linkage, and public review. What is missing:

**The wall-timing vs. hot-query disparity is not a named blocker.**

Looking at the raw data in the intake JSON:

| Group | Embree wall | OptiX wall | End-to-end ratio |
|---|---:|---:|---:|
| 20k cliques | 4185ms | 2496ms | **1.68x** |
| 80k cliques | 15792ms | 2490ms | **6.34x** |

The hot-query ratios are 116x and 347x; the wall-timing ratios are 1.68x and 6.34x. This is a 69–55x compression of the apparent speedup depending on scale point. For the 20k case, OptiX takes significantly longer on scene build (919ms vs 474ms Embree) — nearly 2x longer on preparation — but wins decisively on the query itself.

The report does say "It is a hot-query metric, not end-to-end suite timing" — which is correct — but the M7 blockers don't name "end-to-end wall-timing ratio not characterized for release" as an explicit gate. If this intake is ever promoted, a reviewer reading only the blockers list would not know to investigate the wall-time gap.

**Required addition (P1):**

```json
"hot_query_vs_wall_timing_ratio_not_characterized_for_release"
```

to `m7_blockers`.

---

### Q4: Does the report make hot-query vs. end-to-end timing clear enough?

**Partially.** The prose says "hot-query metric, not end-to-end suite timing" — which is correct. But:

1. The single sentence appears after the ratio table, not as a table footnote. A reader skimming to the table sees 116x and 347x without the qualifier.
2. Neither the markdown table nor the `pairs[]` JSON objects include the wall-timing ratio. The `wall_median_sec` is present in `rows[]` but is not carried into `pairs[]`, so the aggregated view loses the end-to-end signal entirely.
3. For the 20k case, the end-to-end OptiX win is only 1.68x, which would be a significant correction to the 116x hot-query headline. This deserves explicit visibility, not a footnote.

**P1 fix:** Add `embree_wall_median_sec`, `optix_wall_median_sec`, and `optix_wall_speedup_vs_embree` to each `pairs[]` entry, and add a second row to the markdown table showing wall-timing ratios. No new data collection required — the values are already in `rows[]`.

---

### Q5: Does the test enforce the right facts without overfitting?

**The tests are well-structured and appropriately loose.** Specific observations:

**Strengths:**
- Threshold checks (`> 100.0`, `> 300.0`) correctly capture the data's character without pinning to exact floats.
- `test_script_rebuilds_intake_summary` is a genuine integration test — it re-runs the builder against the real calibrated source file and checks the pairs output matches.
- `test_report_keeps_release_boundary_visible` guards the exact wording that must appear for a reader to see the boundaries; this is appropriate here because the strings are normative, not incidental.

**Gaps:**

1. **No test for `m7_blockers` completeness.** If a blocker is silently dropped from `build_payload()` in the script, nothing in the test suite would catch it. Example of what's missing:
   ```python
   self.assertIn("prepared_graph_chunk_executor_linkage_not_closed", payload["m7_blockers"])
   ```

2. **`test_script_rebuilds_intake_summary` only compares `pairs`.** It does not compare `rows` or `claim_boundary`. If the builder changes to omit claim boundary flags from `rows[]`, this test would pass. Consider also asserting `rebuilt["claim_boundary"] == self.load()["claim_boundary"]`.

3. **No test for wall-timing presence in rows.** Given the hot-query/wall gap identified in Q4, a test that `row["wall_median_sec"] > row["primary_metric_sec"]` for all rows would document the expected timing structure in code. This is P2 since the data is present; it's a documentation test, not a safety test.

---

### P0 Findings

**None.** The intake is structurally sound as internal candidate evidence. All claim flags are blocked in both the JSON payload and the report. The status string is unambiguous. The builder hard-codes `"release_authorized": False` and `"m7_qualified": False` rather than computing them from row state — this is the correct conservative choice for an intake script that should never auto-authorize.

---

### P1 Findings

**P1-A: Wall-timing ratios missing from `pairs[]` and from the markdown table.**

The 20k end-to-end win is only 1.68x despite a 116x hot-query win. This must be visible to any reviewer reading the intake without needing to manually compute from `rows[]`. Fix: add `embree_wall_median_sec`, `optix_wall_median_sec`, `optix_wall_speedup_vs_embree` to `_pair_summary()` in the builder and expose them in the MD table.

**P1-B: `m7_blockers` missing the wall-timing gap blocker.**

Add `"hot_query_vs_wall_timing_ratio_not_characterized_for_release"` to the blockers tuple in `build_payload()`. Without this, a promoter reading the blocker list would not know to investigate the end-to-end speedup regression.

**P1-C: No test guards `m7_blockers` list completeness.**

The test suite should assert that all expected blocker strings are present in `payload["m7_blockers"]`. A dropped blocker after a script edit would be silent. Add this to `test_intake_passes_as_internal_candidate_not_m7`.

**P1-D: `generic_capability` label ambiguity with respect to M113/M120 executor linkage.**

Add `"generic_capability_status": "candidate_executor_linkage_not_closed"` to the payload, or rename `prepared_graph_chunk` → `prepared_graph_chunk_candidate`. The current setup relies on a future agent reading both `generic_capability` and `m7_blockers` together; the label alone is overclaimable in isolation.

---

### P2 Suggestions

1. The markdown table would benefit from a footnote in the `Embree query median` / `OptiX query median` column headers: `(hot-query median, warmup=2, repeat=12; not end-to-end)`. This makes the caveat in-table rather than post-table.

2. `test_script_rebuilds_intake_summary` currently asserts `rebuilt["pairs"] == self.load()["pairs"]`. Consider also asserting `rebuilt["claim_boundary"] == self.load()["claim_boundary"]` to catch accidental loosening of the claim gate during rebuild.

3. The `goal_level_decision_audit` block uses prose strings for boolean-adjacent answers. A `"foolish": false` field would help if the audit block is ever machine-read for compliance checks.

4. The intake covers only two scale points (20k, 80k). Adding a note that "scaling behavior at intermediate or larger clique counts has not been tested" would prevent later readers from extrapolating the 347x ratio as a general rule.

---

### Final Recommendation

**Accept as internal candidate evidence after P1-A through P1-D are resolved.**

The intake is doing exactly what it claims to do: it extracts the Triangle RT-Graph 2A1 rows from the calibrated all-app artifact, verifies oracle match and phase timing, blocks all claim flags, names all M7 blockers, and preserves the synthetic-fixture boundary. The ratios are correctly computed and the builder is honest. No false claim is currently possible given the status field, the `m7_qualified: false` flag, and the wording gate enforcement.

The P1 fixes close a specific disclosure gap (wall vs. hot-query) and a guard gap (m7_blockers not tested for completeness) before Codex closes this bounded intake packet. They are not correctness bugs — they are clarity and guard bugs. The packet should not be promoted to any user-facing surface or cited in external performance discussions until M7 qualification work is complete, regardless of P1 resolution.
