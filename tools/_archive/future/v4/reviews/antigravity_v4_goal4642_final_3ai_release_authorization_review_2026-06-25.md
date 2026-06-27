# RTDL V4 Goal4642 Final 3-AI Release Authorization External Review Report

**Date of Review:** 2026-06-25  
**Reviewer:** Antigravity (External Reviewer)  
**Status:** Completed  

---

## Verdict

`authorize_formal_v4_0_high_performance_operator_release`

---

## Findings by Severity

### Critical / Blocker
- **None.** All validation tests passed (`171 tests OK`). There are no correctness regressions or blocking defects.

### Major
- **None.**

### Minor / Informational
- **Narrow Component-Union Performance Margin:** The fixed-radius graph component union (`v4_fixed_radius_graph_component_union_3d_device_arrays`) cleared the runner-vs-legacy OptiX wall-clock floor of `>=0.98x` with `1.208x`, and the runner-vs-Embree hot/wall floors of `>=1.20x` with `1.393x` and `1.600x` respectively, but the actual margin for component-union on large cluster sizes remains hardware-sensitive. Wording must stay strictly bound to this measured surface only.
- **Narrow Weighted-Sum Performance Margin:** Ray/triangle any-hit weighted sum ratio of `1.2011x` at the largest shape size (`524288`) narrowly cleared the `1.20x` floor. The geomean is strong (`1.5457x`), but the largest workload represents a tight boundary.
- **Missing Dependency Catch in Goal4641:** The clean-tree validation caught a missing dependency (`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`) in the committed package, which was subsequently committed and resolved. This verifies the integrity of the reproducibility gate.

---

## Answers to Call-for-Review Questions

### 1. Does the requested label accurately match the evidence?
**Yes.** The requested label—`RTDL v4.0.0 formal high-performance generic RT-core operator release`—accurately matches the evidence. It explicitly constrains the release scope to generic RT-core operators, rather than claiming broad application-level speedups. The evidence packet contains POD timing gates and unit tests for exactly eight generic operator surfaces, validated on Ampere class hardware.

### 2. Are the eight measured operator surfaces and the `4/4` strong-family scorecard sufficient for the requested narrow formal release?
**Yes.** The scorecard covers the 4 strong families in scope (`rt_dbscan`, `raydb_style`, `triangle_counting`, and `librts_spatial_index`) using 8 distinct measured operator surfaces. All 8 surfaces met their frozen performance floors, and the 4 families were verified as fully functional and performance-validated on the target POD. The geomean speedup of `5.185x` is mathematically solid and limited strictly to these operator surfaces.

### 3. Are deferred rows (`spatial_rayjoin`, `barnes_hut`) and partial controls handled honestly?
**Yes.** Deferred rows (`spatial_rayjoin` and `barnes_hut`) are explicitly listed as excluded from V4.0 in all status pages, READMEs, catalogs, and code decision parameters. The codebase rejects these requests or fails closed. Partial controls (`hausdorff_xhd`, `robot_collision`, `contact_manifold`, and `rtnn`) are run for correctness only and are strictly excluded from the geomean speedup aggregation.

### 4. Are public docs and examples clean enough for release without misleading users?
**Yes.** The public docs cleanups in Goal4640 successfully archived the legacy V3 files, updated `README.md` to reference V4 as the current user surface, and documented the exact claim boundaries of V4.0.0. The `examples/v4` quickstart and dry-run scripts are runnable, valid, and pass successfully.

### 5. Does the clean-tree evidence close the reproducibility blocker?
**Yes.** Under Goal4641, a detached clone at commit `35d04dbf0b1734e7c1fc323c366a046de51edee8` in a clean worktree folder successfully built, ran, and passed the full V4 test suite and catalog dry-runs. The catch of a missing dependency (`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`) proves the gate was robust and successfully closed the reproducibility blocker.

### 6. Which open review debts are closed, waived for this narrow release, or still release-blocking?
All 7 open review debts from the V4.0 release prep trajectory are explicitly closed as of this report. None are waived or carried forward:
- `external_review_debt_remains_for_antigravity_goal4633_backfill` is **closed**.
- `external_review_debt_remains_for_goal4635_component_union_completion` is **closed**.
- `external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion` is **closed**.
- `external_review_debt_antigravity_goal4638_formal_scorecard_freeze` is **closed**.
- `external_review_debt_antigravity_goal4639_serious_release_scorecard` is **closed**.
- `external_review_debt_goal4640_public_docs_cleanup` is **closed**.
- `external_review_debt_goal4641_clean_tree_reproducibility` is **closed**.

### 7. Are any forbidden claims still present in public-facing docs or machine status?
**No.** All public docs, tutorials, catalogs, and code status parameters (`V4ReleaseGate` objects in `src/rtdsl/v4_release_decision.py`) enforce the forbidden claims boundaries. The `forbidden_claims` tuple is verified by unittest assertions, and all corresponding boolean authorization flags in code are strictly set to `False`.

### 8. Final answer: authorize, authorize with amendments, or no-go?
**Authorize.** The release is authorized under the narrow label `RTDL v4.0.0 formal high-performance generic RT-core operator release` without amendments. All engineering gates, clean-tree reproducibility tests, public documentation cleanups, and performance floors are fully verified and closed.

---

## Explicit Debt Disposition

The following historical debts are officially **Closed**:

1. **Goal4633 Backfill (`external_review_debt_remains_for_antigravity_goal4633_backfill`):** Checked. The weighted-sum promotion gate meets the frozen floors (min shape ratio `1.2011x` >= `1.20x`, geomean `1.5457x` >= `1.50x`), parity is correct, and hot-path host materialization remains absent.
2. **Goal4635 Component-Union (`external_review_debt_remains_for_goal4635_component_union_completion`):** Checked. Component-union POD gate results (vs Embree wall `1.600x` >= `1.20x`, vs legacy OptiX wall `1.208x` >= `0.98x`) meet the floors, signatures match, and Numba scope limits are correctly documented.
3. **Goal4637 AABB Catalog (`external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion`):** Checked. The AABB Prepared Runner is integrated as `rtdl_native` operator coverage, and tests verify dry-run regression behavior.
4. **Goal4638 Scorecard Freeze (`external_review_debt_antigravity_goal4638_formal_scorecard_freeze`):** Checked. The formal freeze successfully integrated the Performance Floor Reference Table and locked families/surfaces.
5. **Goal4639 Serious Scorecard Run (`external_review_debt_antigravity_goal4639_serious_release_scorecard`):** Checked. RTX A5000 POD gate results (8/8 surfaces passed, geomean speedup `5.185x`, 4/4 strong families passed) are validated.
6. **Goal4640 Public Docs Cleanup (`external_review_debt_goal4640_public_docs_cleanup`):** Checked. Archive of V3 files is complete. README.md, current_v4_status.md, examples, and tutorials present V4 only and maintain strict boundaries.
7. **Goal4641 Clean-Tree (`external_review_debt_goal4641_clean_tree_reproducibility`):** Checked. Detached worktree tests and dry-runs pass cleanly, and the missing dependency check was verified and integrated.

---

## Explicit Non-Authorization Block

> [!WARNING]
> **This review does NOT authorize final release, publication, or public performance claims for any of the following scopes:**
> - **broad V4 speedup** or **whole-application / all-benchmark speedups**;
> - **public true-zero-copy** (data structures are bound to Torch CUDA memory contexts);
> - **Tier-3 callback support** or **raw OptiX callback support** (which remain spike-only/deferred);
> - **CuPy performance** (unmeasured);
> - **C ABI / embedding / non-Python host bindings**;
> - **app-specific native kernels** (only generic catalog operators are supported);
> - **Barnes-Hut** covered by V4.0 (deferred);
> - **Spatial RayJoin** covered by V4.0 (deferred);
> - **LibRTS paper reproduction** or code comparisons.
> 
> Claims must be limited strictly to the 8 measured generic Tier-2 operators under their documented hardware and partner configurations.
