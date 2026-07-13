# Call For Review: Goal5386 X-HD Author Trace V2 Patch Plan

Date: 2026-07-10

Please strictly review Goal5386.

## Files Under Review

Result report:

```text
history/internal_docs/goal5386_xhd_author_trace_v2_patch_plan_result_2026-07-10.md
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5386_author_trace_v2_patch_plan.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
```

Tests:

```text
tests/goal5386_author_trace_v2_patch_plan_test.py
```

Context:

```text
history/internal_docs/goal5385_xhd_author_trace_v2_spec_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5385_author_trace_v2_spec.json
```

## Review Questions

1. Does Goal5386 correctly validate concrete hook anchors in the current author
   source tree rather than merely restating the Goal5385 desired fields?

2. Are the three patch targets correctly limited to author source files?

```text
src/hd_impl/hausdorff_distance_rt.h
src/rt/launch_parameters.h
src/rt/shaders/shaders_nn_uniform_grid.cu
```

3. Does the field coverage matrix cover every Goal5385 required batch field?

4. Are the selected hooks plausible and sufficient for the v2 oracle categories:
   cmax2 before/after, cmin2 hashes/samples, raw offload row hash/sample,
   status counts, miss/completed counts, and loadBalanceProcessing feedback?

5. Does the artifact correctly remain a dry-run patch plan?

Required false flags:

```text
author_v2_trace_implemented = false
author_v2_trace_executed_on_pod = false
patch_applied_to_author_tree = false
rtdl_core_patched = false
```

6. Does the report avoid claiming explicit `-lb`, row parity, Figure 7/11
   reproduction, author RT-core parity, performance ratio, exact dataset
   reproduction, or full X-HD paper reproduction?

7. Are the tests strong enough to prevent silent drift in hook coverage and
   claim boundaries?

8. Is the proposed next step, Goal5387 author v2 patch implementation and POD
   run, the correct next concrete move?

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5386_author_trace_v2_patch_plan
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```
