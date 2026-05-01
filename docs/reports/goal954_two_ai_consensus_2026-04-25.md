# Goal 954 Two-AI Consensus

Date: 2026-04-25

Status: ACCEPTED

## Consensus

Codex and the Euler peer reviewer agree Goal954 is complete after fixing the
initial `rt_core_accelerated` contract blocker.

The accepted change is:

- Regional DB and sales-risk compact summary paths report native continuation
  only when they avoid row/group materialization.
- The unified database app propagates native-continuation metadata only when
  all selected sections are materialization-free.
- `rt_core_accelerated` is true only for OptiX compact summaries whose native
  continuation backend is `optix_db_compact_summary`.
- Full output, summary output, and materializing compact fallbacks report no
  native continuation and no RT-core acceleration.

## Verification

Focused local gate:

```text
Ran 24 tests in 0.356s
OK
```

Additional checks:

- `py_compile` passed for touched Python files.
- `git diff --check` passed for touched files.

## Boundaries

Goal954 does not claim:

- SQL engine behavior.
- DBMS behavior.
- Query optimizer, transaction, or index behavior.
- Full dashboard speedup.
- Row-materializing DB speedup.
- New public RTX speedup evidence.
