# Goal958: Public App Native-Continuation Schema Gate

Date: 2026-04-25

## Verdict

Local implementation complete; peer review pending at the time this report was written.

Goal958 adds a regression gate after Goals 952-957 so future app changes cannot
reintroduce app payloads that mention `rt_core_accelerated` without also
exposing the native-continuation schema.

## Scope

New test:

- `tests/goal958_public_app_native_continuation_schema_test.py`

The test is intentionally static and lightweight:

- scans public `examples/rtdl_*.py`
- if an app exposes `rt_core_accelerated`, it must also expose both
  `native_continuation_active` and `native_continuation_backend`
- checks that key public docs mention native continuation boundaries
- blocks a small set of known overclaim phrase shapes in the public app/docs surface

## Verification

Focused gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal958_public_app_native_continuation_schema_test \
  tests.goal956_segment_polygon_native_continuation_metadata_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test

Ran 13 tests in 0.022s
OK
```

Syntax gate:

```text
python3 -m py_compile tests/goal958_public_app_native_continuation_schema_test.py
```

Whitespace gate:

```text
git diff --check -- tests/goal958_public_app_native_continuation_schema_test.py
```

Syntax and whitespace gates passed with no output.

## Boundary

This goal adds a regression test only. It does not add backend functionality,
new cloud evidence, or public performance claims.
