# Handoff: Claude Review Goal3362 Owner-Face CuPy Continuation

Please perform an independent review of Goal3362, the owner-face CuPy device-column continuation.

Expected output:

- `docs/reviews/goal3363_claude_review_owner_face_cupy_continuation_2026-06-04.md`

## Scope

Read:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3362_owner_face_cupy_filter_continuation_test.py`
- `docs/reports/goal3362_owner_face_cupy_filter_continuation_2026-06-04.md`
- Prior context: `docs/reviews/goal3360_claude_review_owner_face_columnar_closure_2026-06-04.md`

## What Changed

Goal3362 added:

- `filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(...)`
- export through `rtdsl`
- contract registration as an optional columnar pipeline helper
- local skip-aware tests
- live RTX A5000 pod evidence

This helper uses CuPy device arrays to:

- sort owner point ids and topology shape ids on device,
- use device `searchsorted`,
- drop missing-topology candidates,
- fail closed on missing owner rows by default,
- require unique owner point ids by default,
- return CuPy output arrays for point, shape, membership, and owner-face columns.

## Validation Already Run

Local:

```text
Ran 92 tests in 0.048s
OK (skipped=3)
```

Pod environment:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000`
- Driver: `580.126.09`
- CuPy: `14.1.1`

Pod pre-commit copied-file stack:

```text
Ran 15 tests in 8.593s
OK
```

Pod committed-code rerun at `ea7a247f`:

```text
Ran 5 tests in 0.657s
OK
```

Current pushed commit after evidence refresh:

- `4a007cea`

## Review Questions

1. Is the CuPy continuation app-agnostic and compatible with the owner-face contract?
2. Does it preserve the important fail-closed semantics from the Python columnar reference?
3. Is the pod evidence sufficient for this internal device-continuation step?
4. Are the boundary statements clear enough that this is not native RT traversal, not a release claim, and not RayJoin reproduction?
5. What must be fixed before any next device/native lowering step?

## Required Boundaries

- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
- Do not authorize release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy claims.
- Native engine must not infer ownership policy.
