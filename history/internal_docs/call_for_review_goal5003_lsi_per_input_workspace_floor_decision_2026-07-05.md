# Call For Review: Goal5003 LSI Per-Input Workspace Floor Decision

Please review:

```text
history/internal_docs/goal5003_lsi_per_input_workspace_floor_decision_2026-07-05.md
history/internal_docs/goal5003_lsi_workspace_floor_probe.py
history/internal_docs/goal5003_lsi_workspace_floor_artifacts_2026-07-05/lsi_workspace_floor_probe_top4.json
```

## Requested Verdict Label

```text
approve_goal5003_accept_fresh_lsi_workspace_floor_for_v2_14_3
```

or:

```text
revise_goal5003_before_goal5004_matrix
```

## Review Questions

1. Does the source audit correctly explain that `scaled_cache_ensure` depends
   on the combined base/query scale domain, while `grouped_range_ensure`
   builds right-side grouped AABB acceleration for that scaled domain?

2. Does the POD probe correctly distinguish:

   ```text
   same prepared query replay
   same base + new query + same input
   same base + changed query scale domain
   ```

3. Does the evidence support the claim that same prepared-query replay is fast
   (`~0.003s`) but is not fresh one-shot and not true query-many?

4. Does the evidence support the claim that same base plus same scale domain
   can reuse most right-side workspace (`~0.142s`), but that changing the scale
   domain rebuilds the expensive workspace (`~1.47-1.57s`)?

5. Is it correct for v2.14.3 to accept the current fresh LSI workspace floor
   rather than hide it behind prewarm/replay language?

6. Is the proposed future direction correct and generic?

   ```text
   generic fixed-domain / resident planar-map LSI workspace API
   ```

7. Does Goal5003 avoid adding or recommending hidden RayJoin-specific RTDL core
   state?

8. Is the recommended next goal correct?

   ```text
   Goal5004: v2.14.3 Updated Fresh Matrix After Goal5002/5003
   ```

## Non-Authorization Boundary

This review should not approve:

- using same-input replay as a fresh headline;
- true query-many claims;
- excluding per-input workspace from fresh one-shot timing;
- author-performance parity claims;
- top4 author ratios without top4 AuthorOfficial timing;
- RayJoin-specific workspace state in RTDL core.
