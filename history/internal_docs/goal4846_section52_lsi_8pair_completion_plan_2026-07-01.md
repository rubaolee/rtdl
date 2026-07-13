# Goal4846 - RayJoin Section 5.2 LSI 8-Pair Completion Plan

Date: 2026-07-01

## Objective

Complete the RayJoin Section 5.2 LSI reproduction path by comparing AuthorPatch RayJoin and RTDL v2.14-line OptiX LSI on the eight paper CDB pairs where exact inputs are available.

This goal continues Goal4845. Goal4845 completed the first controlled pair:

| Pair | AuthorPatch LSI count | RTDL LSI count | Delta |
|---|---:|---:|---:|
| County x Zipcode | 961165 | 961165 | 0 |

Goal4846 must not use V3/V4 evidence, Embree, or broad performance wording. This is an RTDL v2.14-line plus AuthorPatch paper-reproduction goal.

## Scope

In scope:

- AuthorPatch `query_exec -query=lsi -mode=rt` as the baseline.
- RTDL OptiX LSI predicate route with exact predicate semantics.
- Eight paper CDB pairs, subject to exact-input availability.
- Correctness first: counts must match before timing is interpreted.
- Pair-diff debugging when a count mismatch occurs.
- Synthetic regression test when a mismatch exposes a generic RTDL candidate/predicate defect.

Out of scope:

- Section 5.7 polygon overlay correctness.
- PIP.
- Embree.
- V3/V4.
- Numba partner claims. Section 5.2 LSI is native RTDL/OptiX; Python should only orchestrate.
- Broad RayJoin or RTDL speedup claims before all available correctness gates pass.

## Eight-Pair Worklist

| # | Pair | Case id | Exact input status from old Goal4380 | Goal4846 action |
|---:|---|---|---|---|
| 1 | County x Zipcode | `county_zipcode` | available | Completed by Goal4845; keep as row 1. |
| 2 | Block x Water | `block_water` | available | Run next under current AuthorPatch + repaired RTDL. |
| 3 | LKAF x PKAF | `lkaf_pkaf` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |
| 4 | LKAS x PKAS | `lkas_pkas` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |
| 5 | LKAU x PKAU | `lkau_pkau` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |
| 6 | LKEU x PKEU | `lkeu_pkeu` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |
| 7 | LKNA x PKNA | `lkna_pkna` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |
| 8 | LKSA x PKSA | `lksa_pksa` | missing in Goal4380 | Check POD for exact CDBs; run only if found. |

## Execution Plan

### A. Freeze dataset and command inventory

Produce a compact inventory table from the POD:

- exact CDB path exists or does not exist;
- file sizes;
- AuthorPatch command;
- RTDL route/mapping;
- output artifact path;
- status: `ready`, `missing_exact_input`, `completed`, or `blocked_by_count_mismatch`.

Exit gate:

- No pair may be reported as attempted unless its exact CDB inputs are present.
- Same-source regenerated CDBs may be listed separately, but must not be called exact paper inputs.

### B. Run Block x Water correctness gate

For Block x Water:

1. Run AuthorPatch LSI and record count/timing categories.
2. Run RTDL LSI with the same direction and parameters.
3. Compare counts.
4. If counts match, record a bounded correctness row.
5. If counts mismatch, dump pair sets, compute missing/extra pairs, and reduce to the first discriminating pair.

Exit gate:

- `delta = 0`, or a documented pair-level mismatch diagnosis.

### C. Debug any mismatch with the Goal4845 method

When a mismatch occurs:

1. Do not keep rerunning full CDBs blindly.
2. Use pair-set diff.
3. Build a minimal synthetic reproduction.
4. Identify whether the defect is:
   - RTDL generic candidate generation,
   - RTDL exact predicate,
   - direction/parameter mapping,
   - AuthorPatch command mismatch,
   - data provenance mismatch.
5. Only a generic RTDL defect may justify a core fix.

Exit gate:

- A focused regression test exists before claiming the fix.
- Any core fix gets external review debt if Claude is unavailable; Antigravity may review immediately.

### D. Process remaining exact-input-ready pairs

For the six lakes/parks pairs:

- If exact CDBs are present on the POD, run the same AuthorPatch-vs-RTDL correctness gate.
- If exact CDBs are absent, record `missing_exact_input` and stop that pair.
- Do not use regenerated data as exact paper reproduction.

Exit gate:

- Each pair has one of:
  - `correctness_passed`;
  - `blocked_by_count_mismatch_with_pair_diff`;
  - `missing_exact_input`.

### E. Bounded performance table

Only after correctness:

- separate CDB load/prep/build/query/count timing;
- report AuthorPatch and RTDL on the same hardware;
- do not compare against paper's other systems;
- do not report a naked speedup without denominator and scale.

Exit gate:

- A table exists for completed pairs, with correctness status attached to every timing row.

## Estimated Time

| Work | Optimistic | Expected | Worst credible case |
|---|---:|---:|---:|
| Dataset existence inventory | 10 min | 20 min | 45 min |
| Block x Water if counts match | 30 min | 60 min | 90 min |
| Block x Water if mismatch | 2 h | 3-5 h | 8 h if a new numeric boundary bug appears |
| Each small lakes/parks pair if exact data exists | 10 min | 30 min | 2 h if mismatch |
| Each large lakes/parks pair if exact data exists | 30 min | 90 min | 4 h if mismatch |
| Six missing-data decisions if exact data absent | 15 min | 30 min | 1 h |

Expected total:

- If only the two known exact pairs are available and Block x Water matches: about 1-2 hours.
- If Block x Water exposes a new generic numeric defect: 4-8 hours.
- If all eight exact inputs are found and several mismatch: 1-2 days.

## Expected Trouble

1. Exact CDB availability: Goal4380 recorded six missing exact lakes/parks CDB pairs.
2. Direction mapping: County x Zipcode already proved `poly1/poly2` order changes the count.
3. Float candidate edge cases: Goal4845 exposed one collapsed-float candidate ray bug; other pairs may expose similar numeric boundaries.
4. Route robustness: Goal4845 recorded `count_prepared_left` as failing with `OptiX error: Invalid value` on the large route; direct/grouped route is currently the reliable path.
5. Timing fairness: current Python CDB load can dominate wall time. Correctness comes first; performance must separate load, prepare, and native query.
6. Process risk: repeating full CDB runs without pair-diff is the known stupid path. This goal forbids that.

## Goal-Level Decision Audit

1. Am I being stupid by starting with an all-pair goal?
   Not if the first step is inventory and the second step is one available pair. It would be stupid to claim 8/8 before exact CDB availability is proven.

2. What actions would make this decision stupid?
   Rerunning huge CDBs without pair diffs, mixing Section 5.7 overlay with Section 5.2 LSI, using V3/V4 evidence, or treating regenerated data as exact paper input.

3. Is there an alternative that avoids getting stuck?
   Yes: freeze inventory first, run Block x Water next, and stop each missing-data pair at `missing_exact_input` instead of chasing unavailable files.

4. Can I switch paths if the plan proves wrong?
   Yes. If Block x Water mismatches, switch immediately to pair-diff and synthetic reproduction. If six pairs are missing, close them as input gaps instead of wasting POD time.

## Completion Artifacts

- `history/internal_docs/goal4846_section52_lsi_8pair_completion_plan_2026-07-01.md`
- `history/internal_docs/goal4846_section52_lsi_dataset_inventory_2026-07-01.md`
- `history/internal_docs/goal4846_section52_lsi_results_2026-07-01.md`
- focused test file if a new generic defect is repaired
- call-for-review file before closing Goal4846
