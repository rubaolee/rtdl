# Call For Review: Goal4863 Chain 41230 Midpoint Contract Repair

Date: 2026-07-02

Please critically review Goal4863.

## Files To Review

- `history/internal_docs/goal4863_chain41230_midpoint_contract_repair_result_2026-07-02.md`
- `history/internal_docs/goal4863_chain41230_midpoint_point_location_probe.py`
- `history/internal_docs/goal4863_chain41230_midpoint_point_location_probe_summary.json`
- `history/internal_docs/goal4863_chain41230_midpoint_point_location_after_fix_probe_summary.json`
- `history/internal_docs/goal4863_chain41230_face_assignment_after_fix_probe_summary.json`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`
- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`

## Context

Goal4862 localized the first Section 5.7 County x Zipcode fallback-helper
mismatch to midpoint face selection:

```text
author: 41230 2 42104 42105 280 290
rtdl:   41230 2 42104 42105 294 295
```

The raw key mismatch was:

- expected: `(5, 10950)` / `(22, 10950)`;
- generated: `(5, 10938)` / `(22, 10938)`.

Goal4863 repaired midpoint construction so output-chain midpoint query points
prefer materialized scaled intersection endpoints when available.

## Requested Verdict Labels

Choose one:

- `approve_goal4863_chain41230_midpoint_contract_repaired_authorize_streaming_compare`
- `approve_with_required_amendments_before_streaming_compare`
- `reject_goal4863_repair_as_overfit_or_insufficient`

## Questions

1. Does the evidence prove the defect was midpoint query-point construction,
   not LSI row materialization, vertex PIP, or final face-id renumbering?
2. Is preferring materialized scaled intersection endpoints for output-chain
   midpoint construction a valid contract repair rather than a RayJoin-only
   chain-41230 shortcut?
3. Do the local tests preserve the rational fallback for cases without
   materialized scaled endpoints?
4. Does the POD after-fix chain probe prove chain `41230` now matches the
   AuthorPatch header and raw face key?
5. Does the report honestly document the prior debugging inefficiency and the
   new small-synthetic-first discipline?
6. Are the claim boundaries correct: no full Section 5.7 correctness, no
   performance claim, no broad RayJoin claim?
7. Is a single Section 5.7 streaming compare the right next step?

## Non-Authorization

This review must not authorize:

- full Section 5.7 byte-equal correctness;
- full Section 5.7 performance;
- broad RayJoin paper reproduction;
- broad RTDL correctness or performance claims.
