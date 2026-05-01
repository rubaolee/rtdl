# Goal958 Peer Review: Public App Native-Continuation Schema Gate

Date: 2026-04-25

## Verdict

ACCEPT

## Findings

No blockers found.

The regression test correctly enforces the intended static schema rule for
public top-level examples: every `examples/rtdl_*.py` file that contains
`rt_core_accelerated` must also contain both `native_continuation_active` and
`native_continuation_backend`. I checked the current top-level example inventory
and did not find an obvious public app file with `rt_core_accelerated` outside
that scan pattern.

The documentation check covers the key public native-continuation surfaces named
by the gate: `examples/README.md`, `docs/application_catalog.md`, and
`docs/app_engine_support_matrix.md`. The forbidden-phrase check is intentionally
small and exact; it blocks the listed overclaim phrases without trying to become
a broad semantic claim detector.

The static approach is not too brittle for this regression-gate scope. Its main
limitation is that it is file-level token coverage: it can prove the schema
fields are present in the same public app file, but it does not prove every
runtime branch returns both fields. Existing focused runtime tests remain
necessary for branch-level metadata correctness.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal958_public_app_native_continuation_schema_test -v

Ran 3 tests in 0.002s
OK
```

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal958_public_app_native_continuation_schema_test \
  tests.goal956_segment_polygon_native_continuation_metadata_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test

Ran 13 tests in 0.014s
OK
```

```text
python3 -m py_compile tests/goal958_public_app_native_continuation_schema_test.py
git diff --check -- \
  tests/goal958_public_app_native_continuation_schema_test.py \
  docs/reports/goal958_public_app_native_continuation_schema_gate_2026-04-25.md
```

Syntax and whitespace checks passed with no output.

## Residual Risk

This is a lightweight static regression gate. It is not a substitute for
runtime payload tests, command-truth audit coverage, or public-claim semantic
review beyond the small forbidden phrase list.
