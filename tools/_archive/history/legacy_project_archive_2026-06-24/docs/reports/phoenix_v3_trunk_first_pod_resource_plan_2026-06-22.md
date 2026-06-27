# Phoenix V3 Trunk-First POD Resource Plan

Date: 2026-06-22
Status: `planning_for_non_release_phoenix_v3_engineering`

## Why This Plan Exists

The current Phoenix V3 correction addresses two specific failures:

1. The work order was reversed: leaf routes were optimized before the shared
   execution/runtime trunk was made to execute and carry wins.
2. The useful V3 residency lever was frozen by confusing internal RTDL
   device-residency with V4 external-buffer zero-copy.

The corrected boundary is:

- Internal RTDL residency between RTDL-owned phases is V3.
- Exposing caller-owned device buffers to external hosts is V4 and remains out.

## Current Evidence

The same-RT-hardware V2.14 vs Phoenix V3 all-app run remains the controlling
negative fact:

```text
same_metric_comparison_count: 52
geomean V3 speedup vs V2.14: 1.012x
release_authorized: false
all_app_rerun_authorized: false
```

Hausdorff M5 is now closed as valid negative evidence:

```text
runner route executed: true
runner vs legacy prepared OptiX: about 0.975x to 0.987x depending on metric/sample
classification: valid_negative_evidence_not_third_set_a_material_win
next: generic runner-overhead reduction
```

## Work Order And POD Budget

### Stage A: Close Hausdorff M5 Review

When: complete now.

Expected cost:

```text
local time: 0.25-0.5 h
pod time: none
pod cost at $1 / 4 h: $0
```

Exit:

- 2-AI consensus saved.
- No repeat Hausdorff run.

### Stage B: Generic Runner-Overhead Reduction

When: next immediate engineering stage.

Expected cost:

```text
local engineering: 4-8 h
local tests: 0.5-1 h
pod time: none until local no-overhead evidence exists
pod cost at $1 / 4 h: $0 before focused validation
```

Scope:

- Reduce overhead inside `prepared_execution_session_runner` and its generic
  helper paths.
- Do not add app-specific fast paths.
- Preserve explicit backend/partner/phase/residency metadata.
- Preserve claim-boundary flags as false.

Exit:

- Local tests show the same contracts.
- Micro/local evidence shows reduced runner wrapper/session overhead on generic
  helper calls.
- 2-AI review authorizes a focused pod rerun.

### Stage C: Focused POD No-Regression Validation

When: only after Stage B passes local gates and review.

Expected cost per focused run:

```text
pod wall time: 0.5-2 h including sync, remote tests, benchmark, copy-back, intake
pod benchmark hot time: usually minutes, but reserve setup/debug margin
pod cost at $1 / 4 h: about $0.125-$0.50 per focused run
recommended initial reserve: 2-4 focused runs, about $0.50-$2.00
```

Targets:

- First rerun the affected runner-vs-legacy no-regression rows.
- Prefer AABB / RTDBSCAN / Hausdorff style focused probes before any all-app
  suite.

Exit:

- Productized runner no longer loses to the relevant legacy prepared route.
- If it also shows material Set-A gain, count it as candidate evidence only
  after review.
- If it recovers only parity, record parity and choose the next Set-A family by
  2-AI consensus.

### Stage D: Third Set-A Runtime-Trunk Family

When: after runner overhead is bounded, or sooner only if 2-AI consensus rejects
overhead work as the critical path.

Expected cost:

```text
local route work: 3-8 h depending on family
local tests/report: 1-2 h
focused pod validation: 0.5-2 h
pod cost: about $0.125-$0.50 per focused validation
```

Exit:

- A third Set-A family flows through the same productized runner.
- Win is from the runtime path, not from a leaf cache.
- No app-specific optimization is counted as V3 core.

### Stage E: All-App Paired Run

When: not now.

Preconditions:

- At least three Set-A families route through the single runner.
- Productized runner evidence includes material Set-A wins sourced from the
  runtime path.
- Set-B parity risk is bounded.
- 2-AI review authorizes the spend.

Expected cost:

```text
pod wall time: 4-8 h initial reserve
pod cost at $1 / 4 h: about $1-$2
debug buffer if environment breaks: another 2-4 h, about $0.50-$1
```

Stop rule:

- Do not run all-app merely to check whether small patches helped. That would
  repeat the 1.012x failure mode.

## Near-Term Budget Recommendation

For the next Phoenix V3 push, reserve:

```text
local work: one focused 6-10 h block
pod time: 2-4 h
pod cost: about $0.50-$1.00
hard cap before new review: $2.00
```

This budget is enough to close the current negative evidence, implement one
generic overhead reduction, and run one or two focused validations. It is not a
budget for a full all-app release run.

## Goal-Level Decision Audit

Decision: spend the next POD budget only after generic runner-overhead local
evidence, not on another all-app run or repeated Hausdorff sampling.

1. Was I foolish?

   No for this decision. It follows the measured failure: the productized runner
   currently leaks enough overhead to erase old route wins.

2. If yes, what actions made the decision foolish?

   Not applicable. The earlier foolish pattern was paying for broad runs before
   the trunk had proved it could carry wins.

3. Was there another path that would have avoided getting stuck?

   Yes. The alternative is the current path: reduce shared runner overhead and
   validate focused probes before broad spending.

4. Can I now try a different path that actually solves the problem?

   Yes. Work on the shared execution runner can help every routed Set-A probe;
   a leaf-only patch cannot.
