# Goal 1444 External Review Request

Please review the v1.5.2 native prepared collect execution envelope.

## Scope

- `src/rtdsl/v1_5_2_collect_buffers.py`
- `src/rtdsl/__init__.py`
- `tests/goal1444_v1_5_2_native_prepared_collect_execution_envelope_test.py`
- `docs/reports/goal1444_v1_5_2_native_prepared_collect_execution_envelope_2026-05-07.md`

## Questions

1. Does `run_native_collect_k_bounded_rows_with_prepared_result_buffer(...)` correctly remain a Python wrapper around the existing native generic i64 symbol path, rather than claiming prepared-buffer reuse, native pointer handoff, or true zero-copy?
2. Does it use the prepared descriptor capacity and row width, enforce backend consistency, and bind completion through the Goal1442 compatibility function?
3. Does the returned envelope preserve access to actual native collect `candidate_id_rows` while also returning validated result-buffer metadata?
4. Do the tests cover success, CUDA metadata without zero-copy claims, missing/mismatched backend rejection, non-prepared descriptor rejection, and overflow fail-closed behavior?
5. Does the report clearly avoid public speedup, whole-app speedup, stable promotion, release, and true zero-copy claims?

Please return `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, with any blocking issues listed precisely.
