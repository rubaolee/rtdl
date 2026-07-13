# Call For Review - Goal5278 Generic Heavy-Offload Worklist API Design

Please strictly review Goal5278.

## File Under Review

```text
history/internal_docs/goal5278_generic_heavy_offload_worklist_api_design_2026-07-09.md
```

## Context

Goal5277 decided that X-HD Figure 11 memory denominators are not aligned under
the current RTDL route:

```text
Author WL            = in_queue + miss_queue
Author WL Heavy Peak = peak heavy-cell offload queue
RTDL current WL      = generic frontier row-table capacity
RTDL Heavy Peak      = unavailable
```

Goal5278 proposes the next system API direction:

```text
generic heavy/offload worklist + peak telemetry
```

This is a design document only.  It does not implement the primitive.

## Review Questions

1. Is it correct that Figure 11 cannot be closed by JSON reshaping and instead
   needs a real generic heavy/offload worklist plus telemetry?
2. Is the proposed API generic enough, or does it still leak X-HD / Hausdorff /
   author-specific semantics?
3. Are the proposed row columns sufficient and appropriately app-neutral?
4. Is the proposed telemetry contract enough to map RTDL fields to author
   `WL` and `WL Heavy Peak` only after same-denominator evidence exists?
5. Are the four correctness gates in the right order?
6. Is the non-X-HD consumer gate necessary before using this for X-HD Figure 11?
7. Is the proposed implementation sequence realistic?
8. Should the project pursue this system API now, or stop Figure 11 as
   denominator-not-aligned under the current route?

## Expected Answer Shape

```text
Verdict: approve_goal5278_generic_heavy_offload_worklist_api_design |
         approve_with_required_amendments |
         reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Review question answers:
1. ...
...
8. ...
```

Requested approval label:

```text
approve_goal5278_generic_heavy_offload_worklist_api_design
```
