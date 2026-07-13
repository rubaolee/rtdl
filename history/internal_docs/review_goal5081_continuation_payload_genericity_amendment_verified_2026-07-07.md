# Review: Goal5081 ContinuationPayloadOpening Genericity Amendment Verified

Date: 2026-07-07

## Verdict

```text
approve_goal5081_continuation_payload_genericity_amendment_and_non_rtbh_consumer
```

BF-1 and RA-1 / RA-2 / RA-3 from the strict Goals5079-5080 review are resolved.

Goals5079-5080 can be marked as having their required amendments completed under their bounded claims.

## Blocking Findings

None.

## Required Amendments

None.

## Verified Evidence

The review verified the actual files rather than relying on report prose.

### Independent Non-RT-BarnesHut Consumer

File:

```text
tests/goal5081_continuation_payload_genericity_proof_test.py
```

The test builds a synthetic hierarchy with:

- three points,
- three nodes,
- `ContinuationPayloadOpening(max_ratio=0.5)`,
- `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- no author prepared arrays,
- no sentinel adapter,
- no force scaling,
- no paper comparator.

This is a true non-RT-BarnesHut consumer.

### Behavioral Coverage

The test asserts concrete output rows:

```text
(0, 2.0, 3, 0, 2)
(1, 2.0, 3, 0, 2)
(2, 2.0, 3, 0, 2)
```

It therefore runs the execution path rather than only checking metadata.

The test also includes:

- reference executor coverage,
- optional Numba parity coverage,
- fail-closed coverage when continuation columns are missing,
- app-identity scans for core and test text.

### Wording Amendments

The review confirmed that:

- Goal5079 and Goal5080 now describe `ContinuationPayloadOpening` as provisional/app-neutral at the Goal5079-5080 boundary and point to Goal5081 for the non-RT-BarnesHut proof.
- Goal5080 says correctness is same-prepared-state plus payload-matched reproduction, not independent tree construction.
- Goal5080 says the narrow timing comparison is pending external phase-boundary acceptance.
- The README marks the narrow phase as pending explicit phase-boundary acceptance.
- The unfavorable broader envelope remains visible.
- The review register records the amendment state and carry-forward rules.

## Non-Blocking Note

The synthetic fixture proves an independent consumer, different reducer, concrete execution rows, and fail-closed behavior. It does not strongly distinguish the `rope` branch because the fixture has `aggregate_contribution_count = 0` and the relevant `next_index` and `rope_index` successor coincide.

This is not blocking for the project-defined genericity gate. A future strengthening test could add a fixture where an aggregate node is accepted and `next_index != rope_index`, so a next/rope confusion would change the result.

## Review Question Answers

1. Yes. The new Goal5081 test provides a legitimate non-RT-BarnesHut consumer.
2. Yes. It is structurally different enough: aggregate count, no inverse-square force, no author prepared arrays.
3. Mostly yes. It checks concrete output rows, although the rope-branch distinction could be strengthened later.
4. Yes. Optional Numba parity is useful and does not imply native/CUDA/backend completion.
5. Yes. Goal5079 and Goal5080 wording amendments address the original overclaim.
6. Yes. The README no longer presents the narrow kernel comparison as accepted whole-program speedup.
7. Yes. The broader unfavorable envelope remains visible.
8. Yes. The review register records amendment state and carry-forward rules.
9. Yes. BF-1 / RA-1 / RA-2 / RA-3 can be marked completed.
10. No additional required amendments are needed before Goals5079-5080 close under bounded claims.
