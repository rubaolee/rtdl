# Call For Review: Goal5081 ContinuationPayloadOpening Genericity Amendment

Date: 2026-07-07

## Requested Verdict Label

`approve_goal5081_continuation_payload_genericity_amendment_and_non_rtbh_consumer`

## Review Scope

Please review:

- `history/internal_docs/review_goals5079_5080_rt_barneshut_strict_phase_and_genericity_2026-07-07.md`
- `history/internal_docs/goal5081_continuation_payload_genericity_amendment_result_2026-07-07.md`
- `tests/goal5081_continuation_payload_genericity_proof_test.py`
- `history/internal_docs/goal5079_rt_barneshut_live_pod_generic_force_gate_result_2026-07-07.md`
- `history/internal_docs/goal5080_rt_barneshut_phase_boundary_and_bounded_closeout_result_2026-07-07.md`
- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `history/internal_docs/rt_barneshut_review_opinions_register_2026-07-06.md`

## Context

The strict review of Goals5079-5080 approved bounded same-input correctness but required amendments.

The central finding was that `ContinuationPayloadOpening` was app-neutral in RTDL core but not yet independently genericity-proven because the only live consumer was RT-BarnesHut.

Goal5081 adds a non-RT-BarnesHut synthetic consumer that uses:

```text
ContinuationPayloadOpening(max_ratio=0.5)
AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT
reference executor
optional Numba executor
```

It does not use RT-BarnesHut prepared arrays, author sentinel adapters, force-output scaling, or paper comparator logic.

## Review Questions

1. Does the new Goal5081 test provide a legitimate non-RT-BarnesHut consumer of `ContinuationPayloadOpening`?
2. Is the consumer structurally different enough from RT-BarnesHut, given that it uses aggregate count rather than inverse-square force and does not use app prepared arrays?
3. Do the expected rows prove the continuation-payload execution path is actually exercised rather than merely checking metadata?
4. Does the optional Numba parity test add useful coverage without turning this into a native/CUDA/backend-complete claim?
5. Are the Goal5079 and Goal5080 wording amendments sufficient to address the original overclaim?
6. Does the README now avoid presenting the narrow kernel comparison as an accepted whole-program or whole-envelope speedup?
7. Does the broader unfavorable envelope remain visible?
8. Does the review register correctly record the amendment state and carry-forward rules?
9. Can the BF-1 / RA-1 / RA-2 / RA-3 findings from the Goals5079-5080 strict review be marked completed?
10. Are any additional amendments required before Goals5079-5080 can close under their bounded claims?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
