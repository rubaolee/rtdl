I have read all seven files. Here is the full review.

---

## Review: Phoenix V3 RTNN Ranked-Summary Candidate Intake

**Date:** 2026-06-20  
**Verdict:** approve-with-required-fixes

---

### Numerical fact check

Every stated number was verified against the JSON artifact:

| Distribution | Hot speedup (stated) | Hot speedup (JSON) | Wall speedup (stated) | Wall speedup (JSON) |
|---|---|---|---|---|
| clustered | 3.333x | 3.3328837… ✓ | 0.625x | 0.6250743… ✓ |
| shell | 1.182x | 1.1816254… ✓ | 0.316x | 0.3157743… ✓ |
| uniform | 1.084x | 1.0835478… ✓ | 0.303x | 0.3031316… ✓ |

Row count: 6, group count: 3, same contract per pair, aggregate summaries match per pair — all confirmed.

---

### Q1 — Does the intake honestly classify RTNN as internal candidate evidence, not closure?

**Yes.** The classification chain is airtight:
- Report header: *"not M7 release evidence"*
- Report body: *"does not authorize V3 release wording"*
- Report decision: *"This packet is useful, but it is not closure."*
- JSON `status`: `internal_rtnn_ranked_summary_candidate_not_m7`
- JSON `comparison.m7_qualified`: `false`, `release_authorized`: `false`, `public_speedup_claim_authorized`: `false`
- `claim_boundary.m7_qualified_release_rows`: `0`

No honest-classification defect found.

---

### Q2 — Are `ranked_summary` and `distribution_specific_candidate_wall_regression` the right labels?

**Yes.** `ranked_summary` correctly names the capability (fixed-radius neighbors producing a bounded-k aggregate summary, not materializing individual neighbor rows). `distribution_specific_candidate_wall_regression` captures both the scope limitation and the specific blocker in one label without overreaching. These are the right labels for this evidence tier.

---

### Q3 — Are the M7 blockers complete enough?

The seven blockers cover the essential gaps:

| Blocker | Assessment |
|---|---|
| `wall_timing_optix_slower_than_embree_for_all_three_distributions` | Primary gate — correct |
| `distribution_specific_not_universal_rtnn_acceleration` | Prevents overgeneralization — correct |
| `paper_equivalent_rtnn_row_false` | Correct |
| `summary_rows_materialized` | Correct |
| `no_author_code_or_external_ann_baseline_comparison` | Correct |
| `prepared_cuda_graph_replay_false` | Correct |
| `public_row_level_external_review_not_done` | Correct — this review satisfies the intent |

One notable absence: no `no_multi_run_variance_evidence` blocker. All timing evidence is from a single run. The hot elapsed values (0.175s clustered OptiX, 0.106s shell/uniform OptiX) are small enough that a second run could produce a materially different ratio — particularly for the shell (1.182x) and uniform (1.084x) rows, which are only marginally above 1.0 on the hot metric. This does not block the internal-candidate classification but should be added before any M7 row review (see P1-2 below).

---

### Q4 — Is the hot-metric win versus wall-timing loss clear enough?

Largely yes, but with one presentation gap in the markdown report:

The report table has columns "Hot OptiX / Embree" and "Wall OptiX / Embree" with values 3.333x and 0.625x for clustered. A reader scanning only the table will see two numbers both expressed as "Nx" ratios and may not immediately register that 0.625x means OptiX is **slower**. The table does not have a note indicating that values below 1.0 mean OptiX loses. The M7 blockers section later says "OptiX wall timing is slower than Embree for all three distributions" — but that requires reading past the table.

The JSON is unambiguous: `all_wall_optix_slower_than_embree: true` is a correctly-named boolean. The JSON carries the clearer version.

---

### Q5 — Does the test enforce the right facts without overfitting?

The five tests are well-structured:

- `test_intake_passes_as_internal_candidate_not_m7`: Uses `issubset` for blockers (non-brittle), checks all comparison booleans, claim boundary flags. Correct.
- `test_pairs_show_hot_signal_and_wall_blocker`: Clustered threshold `> 3.0` is loose enough to survive minor rerun variance (actual value is 3.333). Shell and uniform use `> 1.0`. Wall ratios use `< 1.0`. All correct.
- `test_rows_block_public_claims_and_preserve_summary_boundaries`: Checks all six rows on query_count, row_count, k_max, and all claim flags. Correct.
- `test_script_rebuilds_intake_summary`: Runs the builder script and checks `pairs` and `claim_boundary` equality. One fragility: float equality on `pairs` dict fields. Deterministic in practice, but could produce spurious failures on a platform with different float rounding. Not a correctness bug; a robustness note.
- `test_report_keeps_release_boundary_visible`: All seven required phrases are confirmed present in the report. Correct.

No meaningful overfitting found. The thresholds are appropriate given the actual signal values.

---

### P0 Findings

**None.** No factual error, no misclassification, no logic defect that would make the intake unsafe to record as internal candidate evidence.

---

### P1 Findings

**P1-1 — "boundary row" label is undefined and potentially misleading**
Location: `phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md`, line 59–61 (report table, Classification column).

Shell and uniform are labelled "boundary row" while clustered is "internal candidate only." The term "boundary row" does not appear anywhere else in the report or in the JSON. It is not defined. A downstream reader could interpret it as "closer to M7 qualification" (wrong — all three groups carry `claim_status: internal_candidate_not_m7`) or as purely descriptive of the hot ratio (shell 1.182x and uniform 1.084x are barely above 1.0). If the intended meaning is "hot speedup is small, near the 1.0 boundary," that should be stated explicitly or the label should be replaced with "internal candidate only" for consistency with the JSON and with clustered.

**Required fix:** Remove "boundary row" and replace with "internal candidate only" for all three rows, or add a footnote defining the term unambiguously.

**P1-2 — `claim_flags_blocked` silently passes for absent flags**
Location: `scripts/v3_phoenix_rtnn_ranked_summary_intake.py:195`.

```python
"claim_flags_blocked": all(not bool(claim_boundary.get(flag)) for flag in FALSE_CLAIM_FLAGS),
```

`FALSE_CLAIM_FLAGS` includes `broad_rt_core_speedup_claim_authorized`, `device_ranked_summary_aggregate`, `device_resident_query_points`, `embree_ranked_summary_aggregate`, `float32_precision`, and `same_stream_partner_consumer`. If any of these flags are absent from the source `claim_boundary` dict, `.get()` returns `None`, which is falsy, so `not bool(None)` evaluates to `True`. The check passes silently rather than asserting the flag is explicitly `False`.

For flags that are safety gates against overclaim, the difference between "flag is False" and "flag is absent" matters. If a future source artifact omits a flag rather than setting it False, `claim_flags_blocked` would report `True` while the claim boundary is unverified.

**Required fix:** Either (a) document that "absent = blocked" is an intentional design choice and add a comment to that effect, or (b) add an assertion that required claim boundary flags exist in the source data before evaluating them. Option (a) is lower effort; option (b) is safer long-term.

---

### P2 Suggestions

**P2-1 — Add table header annotation for wall ratio direction**

In the report table, append "(>1 = OptiX faster)" to both column headers, or add a single note below the table: "Wall ratios below 1.0 indicate OptiX is slower than Embree." This makes the inversion self-evident without requiring the reader to reach the M7 blockers section.

**P2-2 — Add `no_multi_run_variance_evidence` to M7 blockers**

The shell (1.182x) and uniform (1.084x) hot margins are small enough that run-to-run noise could plausibly reverse them. Adding this blocker would make the M7 qualification bar explicit for a future pod rerun packet, rather than leaving it implicit.

**P2-3 — Float equality in `test_script_rebuilds_intake_summary`**

`self.assertEqual(rebuilt["pairs"], self.load()["pairs"])` compares floating-point dict values for exact equality. This is deterministic only when the same Python version, same JSON parser, and same arithmetic path are used. Consider asserting the key boolean fields and using `assertAlmostEqual` for numeric fields, or at minimum document the assumption.

---

### Final Recommendation

**Approve with required fixes on P1-1 and P1-2 before 2-AI closure.**

The intake is factually honest, numerically accurate, and conservatively scoped. The hot-metric win (especially the 3.333x clustered result) is correctly preserved as a real signal while the wall-timing regression blocks all M7 promotion. The classification chain — report header, JSON status, comparison flags, claim boundary, and wording gate — is consistent throughout. The test suite enforces the right facts without overfitting.

The two P1 issues are about terminology consistency and a silent-pass edge case in the claim-flag guard, not about factual correctness or classification honesty. Fix those, and Codex can close this packet as reviewed internal candidate evidence.
