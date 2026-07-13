# Review: Goal5082 ContinuationPayloadOpening Rope-Branch Hardening

Date: 2026-07-07

## Verdict

```text
approve_goal5082_continuation_payload_rope_branch_hardening
```

## Blocking Findings

None.

## Required Amendments

None.

## Non-Blocking Notes

The reviewer did not rerun the full local 76-test suite because the review sandbox shell was unstable. The conclusion is based on manual traversal of `_rope_distinguishing_hierarchy` and inspection of the executor's aggregate-acceptance and continuation branches. The result report records:

```text
Ran 76 tests in 30.944s
OK (skipped=1)
```

## Review Summary

Goal5082 directly addresses the non-blocking suggestion left by the Goal5081 review: add a behavior-level fixture in which an accepted aggregate must continue through `rope_index`, with `next_index != rope_index`.

The new fixture satisfies that condition:

```text
node_next_index[1] = 2
node_rope_index[1] = 3
```

For source `0`, traversal proceeds:

```text
0 -> 1
node 1 accepted as aggregate
continue via rope[1] = 3
skip node 2
visit node 3 exactly
```

This yields the asserted row:

```text
(0, 2.0, 3, 1, 1)
```

If the executor confused `rope_index` with `next_index`, it would visit node `2` instead and produce different projected rows. The test includes a deliberate confused-rope control fixture and asserts that the projections differ.

The fixture remains non-RT-BarnesHut:

- synthetic 3-point / 4-node hierarchy,
- `ContinuationPayloadOpening(max_ratio=1.0)`,
- `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- no author prepared-state arrays,
- no sentinel adapter,
- no force law,
- no paper comparator,
- app-identity scan remains present.

Optional Numba execution remains scoped as parity only.

## Answers To Review Questions

1. Yes. The fixture distinguishes `rope_index` from `next_index` through both explicit index assertions and a confused-rope negative/control run.
2. Yes. Sources `0` and `1` have `aggregate_contribution_count = 1`; the fixture exercises accepted aggregate traversal, not only leaf traversal.
3. Yes. The test is non-RT-BarnesHut and contains no author prepared-state, sentinel, force-law, or comparator logic.
4. Yes. It asserts concrete projected rows including visited, aggregate, and exact contribution counts.
5. Yes. The confused-rope fixture is useful negative/control evidence that the test would fail if rope and next were conflated.
6. Yes. Numba remains optional parity through `skipUnless`, not backend completion.
7. Yes. The full local suite result recorded in the report supports closing this hardening goal.
8. No additional required amendments are needed before bounded same-input closeout.

## Thread Conclusion

Goals5079-5080's BF-1 and RA-1/RA-2/RA-3 were substantively addressed by Goal5081. Goal5082 closes the only remaining non-blocking behavior-coverage suggestion from that review by adding a discriminating rope-branch fixture.

Goals5079-5082 may now close under the following boundary:

- bounded same-input correctness closed,
- narrow resident-kernel phase still pending/limited unless separately accepted,
- broader reported envelope remains unfavorable to RTDL,
- full paper reproduction remains not closed,
- independent tree construction remains not claimed.
