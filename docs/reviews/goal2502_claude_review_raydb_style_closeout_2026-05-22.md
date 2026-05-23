Here is the technical review.

---

## Review: Goals 2497–2502 RayDB-Style Benchmark Slice Closeout

### Q1 — "Locally complete as reconstruction harness, OptiX pod parity pending"

**Accurate.** The CPU reference path is fully implemented in `columnar_aggregate_reference.py` (`evaluate_columnar_grouped_aggregate`, `plan_columnar_aggregate_lowering`). Embree count/sum is wired and claimed proven. The OptiX path exists in `rtdl_raydb_style_benchmark_app.py` as an app code path, but `goal2501` is explicitly a *preparation packet* — it lists required pod commands and acceptance fields without containing any actual pod execution output or pass/fail evidence. The closeout correctly distinguishes these two states.

One precision issue: the closeout calls the slice "locally complete" while the pod packet for OptiX has not been executed. The phrase is immediately qualified in the same document, but a reader skimming the heading could mistake "locally complete" for "fully complete." This is a presentation risk, not a correctness problem.

### Q2 — Overclaim blocking

All seven named overclaim categories are blocked consistently across all three layers:

| Claim | Doc block | `ColumnarAggregateLoweringPlan` field | Test assertion |
|---|---|---|---|
| RayDB reproduction | Yes | n/a | Yes |
| SQL/DBMS | Yes | n/a | Yes |
| Authors-code perf comparison | Yes | n/a | Yes |
| Public speedup | Yes | n/a | Yes |
| True zero-copy | Yes | `true_zero_copy_authorized: False` | Yes |
| Whole-app acceleration | Yes | n/a | Yes |
| New app-specific native ABI | Yes | `native_abi_added: false` in acceptance criteria | Yes |

The `columnar_record_set_to_row_mappings()` call in the benchmark app's native path materially supports the `true_zero_copy_authorized: False` claim — data is copied into row mappings before dispatch, so the wording is grounded in code behavior, not just asserted.

The test (`goal2502_raydb_style_benchmark_slice_closeout_test.py`) is a *document integrity test* that validates the closeout markdown contains the required claim-block phrases. This is appropriate scaffolding given the pod gap, but it does not exercise runtime correctness. That distinction is clear to a careful reader but should be noted.

### Q3 — Next target: `direct_columnar_record_set_preparation_without_row_mapping`

**Reasonable and app-agnostic.** The current native path in the benchmark app calls `columnar_record_set_to_row_mappings()` as a shim before invoking `grouped_count`/`grouped_sum`. Eliminating that conversion is a genuine engine-layer improvement. The target is named as a field in `ColumnarAggregateLoweringPlan` (`direct_columnar_record_set_api_exists: False`) rather than as a benchmark-app feature, which anchors it at the right abstraction level. Nothing about the definition ties it to RayDB or the synthetic fixture.

### Q4 — Blocking issues

No hard blockers. The single open item — fresh OptiX pod execution — is honestly declared as a gap in the closeout and structurally separated into `goal2501`. The local artifacts (CPU reference, Embree parity, lowering descriptor, app path, diagnostic matrix runner, test) are self-consistent.

**Non-blocking notes worth tracking:**
1. `goal2501` acceptance criteria require `all_match_cpu_reference: true` from the OptiX pod — until that runs, OptiX parity is asserted-pending, not proven. Make sure downstream references to Goals2497–2502 carry that qualifier.
2. The term "locally complete" in the closeout heading is accurate but could be tightened to "locally complete (CPU + Embree); OptiX pod parity pending" to remove ambiguity at a glance.
3. The closeout test validates document structure, not runtime behavior. This is appropriate now but should be supplemented by a runtime parity test once the pod executes.

---

**Verdict: `APPROVE_WITH_NON_BLOCKING_NOTES`**

The slice is internally consistent, overclaims are properly blocked at three independent layers (documentation, data-structure fields, and test assertions), the pod gap is honestly disclosed rather than hidden, and the next-target selection is app-agnostic and grounded in current code structure. The notes above are housekeeping items, not defects.
