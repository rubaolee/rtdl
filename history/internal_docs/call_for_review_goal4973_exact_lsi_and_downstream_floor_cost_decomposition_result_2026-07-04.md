# Call For Review — Goal4973 Exact LSI And Downstream Floor Cost Decomposition

Date: 2026-07-04

Please review:

```text
history/internal_docs/goal4973_exact_lsi_and_downstream_floor_cost_decomposition_result_2026-07-04.md
```

Artifacts:

```text
history/internal_docs/goal4973_exact_lsi_and_downstream_floor_cost_decomposition_artifacts_2026-07-04/
```

## Requested Verdict

`approve_goal4973_exact_lsi_setup_decomposed_and_authorize_downstream_floor_work`

## Context

The prior midcheck review warned that Goal4972 under-weighted an important arithmetic fact:

```text
fresh bounded   ~= LSI 2.69s + downstream 2.59s
prepared replay ~= LSI 0.009s + downstream 2.56s
```

Therefore Goal4973 was amended to decompose both:

1. the `~2.69s` fresh exact LSI cost, and
2. the persistent `~2.56s` downstream floor.

## What Changed

Instrumentation only:

- native optional extended segment-pair timing getter,
- Python runtime access to that getter,
- app-level `lsi_cost_decomposition`,
- app-level `downstream_floor_breakdown`,
- diagnostic-only bounded exact same-process repeat route.

No RayJoin-specific core primitive was added. Core output remains `{left_id, right_id}` device columns.

## Review Questions

1. Does the evidence support that fresh exact LSI cost is native setup/workspace dominated, not Python dominated?
2. Does the same-process repeat diagnostic support that bounded exact LSI becomes `~0.003s` after prepared state is warm?
3. Does the evidence support that the persistent writer-free binary operator floor is downstream, around `~2.54s`?
4. Are the downstream largest components identified correctly from the artifacts?
   - vertex PIP map1 in map0,
   - midpoint point generation on both sides,
   - reprojection,
   - carrier/sort as secondary costs.
5. Does the result avoid reintroducing the invalid `2x vs author` claim?
6. Does the implementation preserve generic RTDL boundaries?
   - no output-chain logic in core,
   - no author text formatting in core,
   - no Layer 4 fusion claim,
   - no RayJoin-specific core kernel.
7. Are the correctness gates sufficient for this measurement goal?
   - LSI rows `428322`,
   - xsect side0/side1 `428322 / 428322`,
   - vertex positives `812721 / 4527305`,
   - device order validation true.
8. Should Goal4973 close with labels:
   - `exact_lsi_cost_dominated_by_workspace_setup`,
   - `steady_state_cost_dominated_by_downstream_floor`?
9. Should the next goal target downstream floor rather than more LSI traversal?
10. If approved, which downstream target should be first:
    - point-location/PIP device-column handoff,
    - midpoint point generation as generic device-column map,
    - reprojection/sort/carrier follow-up?

## Proposed Next Authorization

Authorize a downstream-floor goal that keeps RTDL generic and starts with the largest persistent component:

```text
PIP result residency / device-column handoff + downstream phase remeasure
```

The goal should remain measurement-gated and must not claim author parity.
