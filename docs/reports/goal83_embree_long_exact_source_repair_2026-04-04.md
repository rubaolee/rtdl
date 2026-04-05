# Goal 83: Embree Long Exact-Source Repair

## Objective

Repair the RTDL Embree positive-hit `pip` path on the exact-source long
`county_zipcode` surface, restore exact parity against PostGIS, and determine
whether Embree has a defensible performance story on the same surface used for
the OptiX long-workload package.

## Why Goal 83 existed

The first exact-source Embree measurement on Linux failed badly:

- PostGIS row count: `39073`
- Embree row count: `39215`
- parity: `false`
- Embree runtime: about `45-48 s`

That established a real correctness defect, not just a slow benchmark.

The diagnosis package for that failure was reviewed and accepted separately:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_diagnosis_and_proposal_2026-04-04.md`

## Repair

The native Embree positive-hit path in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

was reworked so that positive-hit `pip` no longer tries to finalize truth inside
the Embree callback path.

The accepted repair shape is:

1. conservative candidate generation using Embree point-query callbacks over
   polygon bounds
2. deterministic candidate collection per probe point
3. host exact finalize on those candidates
4. GEOS-backed exact finalize when available

This preserves the project rule:

- traversal narrows the search space
- exact finalize owns truth

## Validation

Focused validation after the repair:

- local Mac:
  - `tests.rtdsl_embree_test`
  - `tests.goal80_runtime_identity_fastpath_test`
  - `tests.goal76_runtime_prepared_cache_test`
  - `tests.goal69_pip_positive_hit_performance_test`
  - result: `OK` with one expected local Embree/GEOS skip
- clean Linux clone:
  - same focused suite
  - result: `19` tests, `OK`

Clean Linux clone used for the final exact-source reruns:

- `/home/lestat/work/rtdl_goal83`
- head: `209db71` plus the Goal 83 native Embree patch copied into that clean
  clone before rerun

Exact-source directories:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

## Accepted exact-source results

### Prepared exact-source boundary

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json`

Result:

- Embree: `1.773865199 s`
- PostGIS: `3.402695205 s`
- row count: `39073`
- sha256:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`
- parity: `true`

### Repeated raw-input exact-source boundary

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json`

Results:

- Embree first run: `1.959970190 s`
- Embree repeated run: `1.092190547 s`
- PostGIS comparison runs:
  - `3.583030458 s`
  - `3.188612651 s`
- row count: `39073`
- sha256:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`
- parity: `true` on all runs

## Outcome

Goal 83 closes the Embree exact-source long `county_zipcode` positive-hit `pip`
repair successfully.

Accepted claims:

- Embree is now parity-clean on the exact-source long `county_zipcode`
  positive-hit `pip` surface.
- Embree beats PostGIS on the prepared exact-source boundary.
- Embree also beats PostGIS on the repeated raw-input exact-source boundary.

Non-claims:

- this does not claim a cold first-call general end-to-end win for every surface
- this does not claim every Embree workload family is now equally optimized
- this does not change Vulkan or oracle status

## Conclusion

After the Goal 83 repair, Embree joins OptiX in having a credible long-workload
performance story on the accepted RayJoin-style exact-source `county_zipcode`
positive-hit `pip` surface:

- exact parity preserved
- prepared exact-source win
- repeated raw-input exact-source win
