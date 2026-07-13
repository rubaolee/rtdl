# Call For Review — Goal5414 Synthetic Payload-Transition Trace Fixture

Please strictly review Goal5414:

```text
Goal5414 — Synthetic non-app payload-transition trace fixture
```

Files to inspect:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5414_synthetic_payload_transition_trace_fixture_test.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5414_synthetic_payload_transition_trace_fixture.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5414_synthetic_payload_transition_trace_fixture.json
history/internal_docs/goal5414_xhd_synthetic_payload_transition_trace_fixture_result_2026-07-10.md
```

Context:

- Goal5412 fail-closed the current X-HD `-lb` line and authorized only a
  design-level generic native payload-transition trace direction.
- Goal5413 introduced a design-only generic payload-transition trace contract.
- Goal5414 is the first behavior proof on that evidence ladder: a synthetic
  non-X-HD consumer plus a generic summary helper.

Review questions:

1. Does `payload_transition_trace_summary_numpy_columns(...)` remain
   app-neutral, with no X-HD / paper / author / Figure identity in the core
   helper?
2. Does the synthetic fixture truly avoid X-HD semantics and exercise only a
   generic active-query / spatial-bin trace shape?
3. Does the result artifact show behavior, not just a paper contract assertion
   (`matched=true`, status counts, deterministic samples, overflow rejection)?
4. Are fail-closed paths adequate for this stage: row-capacity overflow,
   explicit overflow flag, unknown status codes, negative namespace / event
   ordinals, shape mismatch, and bad sample indices?
5. Is the helper correctly framed as CPU-reference / summary-only rather than
   native backend completion?
6. Do the tests sufficiently protect the claim boundary and public export?
7. Does this goal avoid reauthorizing X-HD `-lb`, Goal5387 row identity,
   Figure 7, Figure 11, author parity, performance ratio, exact dataset
   reproduction, or full paper reproduction?
8. Should Goal5414 close as a synthetic non-app proof, and should Goal5415 be
   limited to a decision on whether to stop or attempt one bounded X-HD
   sample-row gate?

Expected answer shape:

```text
Verdict: approve / approve_with_required_amendments / reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5414_synthetic_non_app_payload_transition_trace_fixture
```
