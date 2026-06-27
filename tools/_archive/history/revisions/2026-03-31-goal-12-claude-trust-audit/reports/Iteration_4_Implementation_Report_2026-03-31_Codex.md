# Goal 12 Implementation Report

Date: 2026-03-31
Author: Codex
Round: Goal 12 Claude trust audit closure

## Scope

This revision round addresses the discrepancies reported in:

- `external_reports/trust_audit_2026-03-31.md`

and follows the Claude revision plan archived in:

- `external_reports/Iteration_3_Revision_Plan_2026-03-31_Claude.md`

## Original Audit Items

1. `boundary_mode` for PIP was accepted by the DSL surface but silently ignored in execution.
2. Goal 10 workloads were labeled as BVH-style even though their local runtime path did not use an Embree BVH traversal.
3. LSI all-hits behavior was suspected to be incomplete because the native code used `rtcIntersect1`.
4. Goal 10 workloads were missing from the frozen baseline/evaluation runners and artifacts.

## Revision Outcome

### 1. PIP `boundary_mode` is now explicit and enforced

Revised files:

- `src/rtdsl/reference.py`
- `src/rtdsl/runtime.py`
- `src/rtdsl/embree_runtime.py`
- `src/native/rtdl_embree.cpp`

What changed:

- CPU PIP now accepts `boundary_mode` explicitly and rejects anything except `"inclusive"`.
- CPU semantics now perform explicit boundary-inclusive edge checks.
- The Embree runtime now rejects unsupported boundary modes before native execution.
- The native C++ PIP implementation now uses an explicit inclusive containment loop, so the audited runtime semantics match the DSL contract.

Net effect:

- `point_in_polygon(..., boundary_mode="inclusive")` is explicitly supported.
- Unsupported boundary modes fail loudly instead of being silently ignored.

### 2. Goal 10 workload labels are now honest

Revised files:

- `src/rtdsl/lowering.py`
- `schemas/rayjoin_plan.schema.json`
- `src/rtdsl/baseline_contracts.py`
- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/embree_baseline_contracts.md`
- `docs/embree_evaluation_matrix.md`

What changed:

- `segment_polygon_hitcount` lowering now reports `accel_kind="native_loop"`.
- `point_nearest_segment` continues to report `accel_kind="native_loop"`.
- Schema validation now accepts both `bvh` and `native_loop`.
- Docs explain that these two workloads remain part of the supported RTDL surface, but the current local backend executes them via audited native-loop paths rather than BVH traversal.

Net effect:

- The Goal 10 runtime claims are now aligned with the actual local execution strategy.

### 3. LSI audit concern was rebutted and protected by regression coverage

Revised files:

- `tests/rtdsl_embree_test.py`
- `src/native/rtdl_embree.cpp`

What changed:

- Added `test_run_embree_lsi_collects_multiple_hits_for_one_probe`.
- The new test uses one probe segment intersecting three build segments and checks CPU-vs-Embree parity with float tolerance.
- Added a clarifying comment in the native LSI callback explaining that the current callback collects all matching build segments directly and is not restricted to a single closest-hit output row.

Evidence:

- Manual spot-check before the regression test showed CPU and Embree both returned three rows for the same probe/build setup.
- The new regression test passes in the final suite.

Net effect:

- The original audit suspicion was not confirmed by runtime evidence.
- The project now has explicit regression protection for that behavior.

### 4. Goal 10 workloads are now part of the frozen baseline/evaluation surface

Revised files:

- `src/rtdsl/baseline_contracts.py`
- `src/rtdsl/baseline_runner.py`
- `src/rtdsl/baseline_benchmark.py`
- `src/rtdsl/evaluation_matrix.py`
- `src/rtdsl/evaluation_report.py`
- `tests/baseline_contracts_test.py`
- `tests/baseline_integration_test.py`
- `tests/evaluation_test.py`
- `docs/embree_evaluation_matrix.md`
- `docs/reports/embree_evaluation_summary_2026-03-30.md`
- `docs/reports/embree_gap_analysis_2026-03-30.md`
- `docs/reports/embree_evaluation_report_2026-03-30.pdf`

What changed:

- `BASELINE_WORKLOAD_ORDER` now contains six workloads.
- Baseline contracts include `segment_polygon_hitcount` and `point_nearest_segment`.
- Baseline runner and benchmark kernel dispatch now recognize the Goal 10 workloads.
- The frozen evaluation matrix now contains Goal 10 authored and fixture cases.
- The evaluation report code and generated snapshots now reflect the six-workload matrix.

Net effect:

- The audited baseline/evaluation surface is now internally consistent with the supported RTDL workloads.

## Verification

Commands executed successfully:

```sh
make build
python3 -m unittest discover -s tests -p '*_test.py'
make eval-rtdsl-embree
```

Observed results:

- `make build`: passed
- full test suite: `Ran 50 tests ... OK`
- evaluation pipeline: regenerated JSON, Markdown summary, CSV, SVG figures, PDF report, and gap analysis

## Requested Final Review Focus

For final closure, Claude should re-check:

1. whether the four original audit items are now resolved or properly rebutted,
2. whether the revised docs, code, and generated report artifacts are mutually consistent,
3. whether the repository can now be described as an audited version for this round.
