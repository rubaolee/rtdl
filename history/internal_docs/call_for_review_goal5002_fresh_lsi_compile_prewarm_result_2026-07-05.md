# Call For Review: Goal5002 Fresh LSI Compile / Pipeline Prewarm Probe

Please review:

```text
history/internal_docs/goal5002_fresh_lsi_compile_prewarm_result_2026-07-05.md
history/internal_docs/goal5002_lsi_compile_prewarm_probe.py
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/baseline_no_prewarm.json
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/tiny_lsi_prewarm_then_fresh.json
```

## Requested Verdict Label

```text
approve_goal5002_global_lsi_compile_prewarmable_workspace_still_dominates
```

or:

```text
revise_goal5002_before_goal5003
```

## Review Questions

1. Does the tiny generic LSI prewarm prove that the LSI
   `exact_pipeline_ensure + split_kernel_ensure` cost is globally reusable and
   prewarmable?

2. Is the prewarm route generic, rather than RayJoin-specific?

   Evidence to check:

   ```text
   base.prepare_planar_map_lsi_2d_optix(...)
   query.run_bounded_pair_id_device_columns(...)
   tiny synthetic crossing segment pair
   no rtdsl.rayjoin_overlay import
   no RayJoin CDB input
   ```

3. Are the top4 numbers interpreted correctly?

   ```text
   no-prewarm compile-like top4 cost: 0.988718s
   prewarmed compile-like top4 cost: 0.000000591s
   LSI phase reduction: 0.950458s
   remaining workspace-like LSI cost after prewarm: 1.746695s
   ```

4. Does the report avoid using the prewarmed result as an unfair fresh
   one-shot headline?

   In particular, does it correctly state that if the prewarm cost is counted
   inside the same one-shot command, the cost is moved earlier rather than
   eliminated?

5. Does the report correctly identify the next LSI target as the per-input
   workspace-like floor?

   ```text
   grouped_range_ensure + scaled_cache_ensure ~= 1.7s
   ```

6. Is the recommended next goal correct?

   ```text
   Goal5003: LSI Per-Input Workspace Floor Decision
   ```

7. Does Goal5002 preserve RTDL's generic-system boundary and avoid adding a
   hidden RayJoin-specific LSI producer optimization?

8. If RTDL later promotes a generic LSI runtime prewarm / precompile hook, what
   benchmark rules should be required so that prewarm time is only excluded
   when process/service startup precompile is a real product behavior?

## Non-Authorization Boundary

This review should not approve:

- author-performance parity claims;
- top4 author ratios without a measured top4 author baseline;
- true query-many claims;
- hiding prewarm time in one-shot CLI measurements;
- calling per-input workspace cost solved;
- RayJoin-specific LSI preloading in RTDL core;
- full device-resident overlay completion.
