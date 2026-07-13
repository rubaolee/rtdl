# Call For Review — Goal4972 Bounded Single-Pass Exact LSI Producer Result

Please review:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_result_2026-07-04.md`

Artifacts:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_artifacts_2026-07-04/`

## Requested Verdict

`approve_goal4972_bounded_single_pass_exact_lsi_no_go`

## Review Questions

1. Did the implementation remain generic planar-map LSI pair-id output rather than a RayJoin-specific
   native kernel?
2. Is the bounded-capacity/overflow contract correct and fail-closed?
3. Do the correctness gates on the top4 representative pass for the bounded route?
4. Is the performance interpretation correct: bounded exact LSI does not improve the LSI stage versus
   exact pair-id device columns?
5. Does the report correctly identify the deleted count pass as too small to be the bottleneck?
6. Does the report avoid overclaiming the lower full writer-free hot time as an LSI-producer win?
7. Is it acceptable to record the POD environment fixes (`RTDL_OPTIX_PTX_COMPILER=nvcc`, explicit
   PATH/LD_LIBRARY_PATH) as measurement-environment fixes rather than algorithmic changes?
8. Should Goal4972 close as no-go and authorize the next goal to target the exact LSI producer itself
   instead of more row-wrapper/count-pass work?

## Boundary To Check

The new route must not authorize:

- broad RayJoin speedup claims
- author-performance headlines
- Layer 4 fusion/callback claims
- public release wording changes
- RayJoin-specific core semantics
