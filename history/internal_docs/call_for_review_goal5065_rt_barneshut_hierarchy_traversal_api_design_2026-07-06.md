# Call For Review - Goal5065 RT-BarnesHut Hierarchy Traversal API Design

Date: 2026-07-06

## Review Targets

Please review both documents:

1. `history/internal_docs/goal5064_rt_barneshut_current_implementation_report_2026-07-06.md`
2. `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`

Context source files:

- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

Primary evidence path:

- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/pod_57582_author_optix_payload_gate/pulled/_runs`

## Background

The RT-BarnesHut paper-reproduction app has closed a bounded same-input POD
gate:

```text
Input size: 32768 bodies
AuthorOfficial vs RTDL: matched = true
mismatch_count = 0
max_rel_error = 2.3653388501211796e-06
RTDL resident kernel min: 1.1904959678649902 ms
Author RT force phase: 5.579 ms
RTDL / Author narrow force-kernel ratio: 0.21338877359114364
```

The same timing artifact also reports the broader envelope around that narrow
phase: RTDL tree preparation, host-to-device tensor preparation, extension
compilation, and resident kernel total about `336.98 ms`; the author's reported
preprocessing plus execution total about `99.91 ms`. The narrow ratio is
therefore not a whole-program speedup claim and must be reviewed together with
that broader envelope. The `0.21338877359114364` ratio is RTDL
`resident_kernel_min` over the author's single reported `rt_core_force`; RTDL
`resident_kernel_mean` over that same author value is about `0.2221`.

The implementation did not reproduce the full paper Section 5 evaluation
matrix. It reproduced the same-input force-kernel phase using the author
binary's dumped prepared state and an `author-optix-payload` traversal policy.

The design question now is whether the reusable part should be extracted into
RTDL as a general hierarchy traversal / aggregate-frontier API, while keeping
AuthorOfficial and comparator machinery inside the paper app.

## Requested Verdict Labels

Use one of:

```text
approve_goal5065_hierarchy_api_design_and_authorize_goal5066
approve_with_required_amendments
block_as_app_specific_or_underdesigned
```

## Review Questions

1. Does the current implementation report correctly state what has and has
   not been reproduced?

2. Does it correctly distinguish bounded same-input force-kernel reproduction
   from full paper Section 5 evaluation reproduction?

3. Does it correctly classify the current RTDL route as primarily a
   diagnostic CUDA/Torch-extension path, not the v2.14.4 RayJoin
   device-columnar API path?

4. Does the report correctly preserve the general-system principle: RTDL core
   is not currently polluted by RT-BarnesHut/AuthorOfficial public APIs, while
   the paper app does contain app-specific comparator machinery?

5. Is the proposed hierarchy traversal / aggregate-frontier API the right
   system-level abstraction for this workload class?

6. Are the proposed public concepts generic enough:

   ```text
   AggregateHierarchy3D
   PreparedAggregateHierarchy3D
   aggregate_frontier_reduce_3d
   SizeDistanceOpening / opening policies
   reducers
   continuation columns
   ```

   Or do they still encode RT-BarnesHut identity too strongly?

7. Does the plan correctly keep the following out of RTDL core/public API?

   ```text
   AuthorOfficial
   Treelogy
   RTBH_FORCE_OUT
   RTBH_PREPARED_ARRAYS_OUT
   author-optix-payload exact comparator mode
   ```

8. Is it acceptable for the near-term API to start from externally prepared
   flat hierarchy arrays, rather than immediately supporting raw-body-to-tree
   construction inside RTDL?

9. Is the implementation sequence reasonable?

   ```text
   Goal5066 contract/schema
   Goal5067 reader/validator extraction
   Goal5068 generic CUDA backend extraction
   Goal5069 RT-BarnesHut app migration
   Goal5070 non-RT-BarnesHut genericity smoke
   Goal5071 POD gate
   Goal5072 docs/release boundary
   ```

10. Are the performance gates sufficient to prevent accidental regression of
    the completed 32,768-body same-input force-kernel result, including the
    concrete migration threshold `resident_kernel_mean <= 1.37 ms`?

11. Is one non-RT-BarnesHut smoke test enough for the next line if it uses a
    substantially different density/count reducer and opening configuration,
    or should the release require two independent consumers before claiming a
    public generic hierarchy traversal API?

12. Does the plan correctly avoid claiming:

    - full paper Section 5 reproduction;
    - whole-program speedup;
    - ChaNGa/Treelogy paper-scale parity;
    - raw-body-to-force RTDL parity?

13. Should Goal5066 be authorized as the next implementation goal?

## Specific Concerns For Reviewer To Check

Please be strict on these points:

- If the API still looks like RT-BarnesHut renamed, block it.
- If an app-identity opening name appears in the proposed public API, block it.
- If `author-optix-payload` is promoted as normal RTDL public API, block it.
- If the plan uses only RT-BarnesHut to prove genericity, require amendment.
- If the performance claim slips from force-kernel phase to whole-program
  runtime, block it.
- If the plan ignores current 32,768-body correctness evidence, require a
  better migration gate.

## Expected Output Format

Please return:

```text
Verdict: <one requested verdict label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
13. ...
```

## Desired Outcome

If the design is sound, authorize Goal5066 as a contract/schema goal only. It
should not yet implement a large backend rewrite. The first implementation step
should prove the generic API boundary before moving code out of the diagnostic
script.
