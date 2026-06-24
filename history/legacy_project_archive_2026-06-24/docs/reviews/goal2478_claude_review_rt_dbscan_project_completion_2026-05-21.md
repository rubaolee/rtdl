## Goal2478 RT-DBSCAN Project-Close Review

---

### Verdict: Approved

No blocking issues. All evidence checks pass and claim boundaries are consistently maintained across all six artifacts.

---

### Blocking Issues

None.

---

### Non-Blocking Issues

1. **`source_commit: null` / `source_tree_is_git_checkout: false`** — the pod ran from an rsync copy. This is documented in the report, expected for pod runs, and the test explicitly asserts `assertFalse(summary["source_tree_is_git_checkout"])`. No traceability gap beyond what is documented, but future pods should consider a `git bundle` approach if commit-level reproducibility is wanted.

2. **"Grouped native, sec" column label** in the report table is ambiguous without context — it refers to the RTDL native grouped-stream kernel time only, not total elapsed. The total column is correctly labeled. Not wrong, but could confuse a first-time reader of the report in isolation.

3. **`_tail_median` with `repeat_count=3`** drops exactly one row and takes the median of two remaining values, which is a single value. The label "median" is technically correct but the reader should know this is equivalent to the min of the two tail runs. No impact on validity.

---

### Evidence Checks

**Q1 — Numbers consistent with summary.json?** Yes, fully.

| Points | CuPy (report/JSON) | RT-count (report/JSON) | RT speedup | Grouped total | Grouped native | Grouped speedup |
|---:|---|---|---|---|---|---|
| 32,768 | 0.1597758988 / 0.1597758987… ✓ | 0.1429276895 / 0.14292768947… ✓ | 1.1179x / 1.117879… ✓ | 0.0408550138 / 0.04085501376… ✓ | 0.0224657068 / 0.022465706… ✓ | 3.9108x / 3.91080… ✓ |
| 65,536 | 0.4676661789 / 0.4676661789… ✓ | 0.3734569130 / 0.37345691304… ✓ | 1.2523x / 1.25226… ✓ | 0.0990382954 / 0.09903829544… ✓ | 0.0674216980 / 0.06742169801… ✓ | 4.7221x / 4.72207… ✓ |
| 131,072 | 1.5541055435 / 1.5541055435… ✓ | 1.0094030295 / 1.0094030294… ✓ | 1.5396x / 1.53962… ✓ | 0.3172265468 / 0.31722654681… ✓ | 0.2537486283 / 0.25374862831… ✓ | 4.8990x / 4.89904… ✓ |

All 18 figures match to 10 significant digits. Speedup computations match `cupy_tail_median / grouped_tail_median` per runner.py:133.

**Q2 — Claim boundaries correctly avoided?** Yes.

- Report explicitly states: "This is not a paper-reproduction claim and not a public broad DBSCAN speedup claim."
- `summary.json.claim_boundary`: `paper_dataset_reproduction: false`, `paper_speedup_claim_authorized: false`, `whole_app_speedup_claim_authorized: false`.
- The benchmark app emits `native_dbscan_abi_added: false` and `paper_speedup_claim_authorized: false` in every return payload.
- Both planners (`plan_rt_dbscan_execution`, `plan_rt_dbscan_continuation_execution`) carry `release_claim_authorized: False` and `paper_reproduction_claim_authorized: False`.
- README Claim Boundary section explicitly lists all three prohibited claim types.
- No comparison to authors' implementation or authors' datasets appears anywhere.

**Q3 — Close conclusion reasonable for generic-primitive implementation?** Yes.

The native engine surfaces are verified generic: fixed-radius geometry, caller-owned count/flag/parent/adjacency columns. The engine has no DBSCAN vocabulary (`cluster`, `label`, `min_neighbors`). App semantics live entirely in Python. Planner is transparent (emits `execution_plan` in metadata, `not_hidden_dispatcher: True`). Deferred items (paper reproduction, Vulkan/HIPRT, public speedup wording, intersection-direct promotion) are all correctly scoped out with explicit reasons. The 3.9x–4.9x grouped-stream benefit and 1.1x–1.5x RT-count benefit are internally consistent with a generic primitive — not inflated by DBSCAN-specific engine knowledge.

**Q4 — Test suite consistent?** Yes. All six test assertions are satisfiable from the artifact:
- Speedup floor `> 3.9` passes (min observed: 3.9108x).
- Speedup floor `> 1.5` at 131k passes (1.5396x).
- All `signatures_match_probe` fields are `true` in summary.json.
- Planner selections match expected modes at all three sizes.

---

### Claim Boundary

| Claim | Status |
|---|---|
| Paper dataset reproduction | Explicitly false — not authorized, not attempted |
| Paper-level speedup | Explicitly false — `paper_speedup_claim_authorized: false` in every artifact layer |
| Broad DBSCAN acceleration | Explicitly false — `whole_app_speedup_claim_authorized: false` |
| Authors' implementation comparison | Not attempted — report explicitly notes paper authors' implementation and datasets not used |
| Internal project-close evidence | True — `project_close_internal_evidence: true`, consistent numbers, matching signatures |
