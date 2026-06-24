# Kepler Review: Phoenix V3 RTNN Step-2 Prepared-Execution Runner

Date: 2026-06-22

Verdict: `accept_for_pod`

Scope: focused RTNN Step-2 pod evidence only. This does not authorize V3 release, all-app benchmark runs, public speedup wording, broad V3-over-V2 wording, or V4/zero-copy/embedding claims.

## Reviewed Files

- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/__init__.py`
- `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_rtnn_prepared_execution_runner_wiring_test.py`
- `docs/reviews/codex_kepler_phoenix_v3_next_set_a_family_rtnn_consensus_2026-06-22.md`

## Review History

Initial verdict: `accept_with_required_fixes`.

Finding: the helper could overstate V3 residency because `prepared_queries_resident` was inferred from requested `optix` + `prepared_query_points`, even when the returned runtime aggregate did not report `query_resident`. That could incorrectly set `internal_device_residency_between_rtdl_phases`, `runtime_trunk_executes_end_to_end`, and `repeat50_material_probe_candidate`.

Fix applied: `prepared_queries_resident` is now taken only from returned `query_resident`. A negative unit test covers the exact overclaim case: complete aggregate signatures without `query_resident` must keep residency, runtime-trunk, and material-candidate flags false.

Final verdict after fix: `accept_for_pod`.

## Verified Gates

Kepler accepted the following local gates:

```text
py -3 -m py_compile scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py
py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test
```

Result: `29 tests OK`.

## POD Authorization Boundary

Approved next action:

- Run the focused RTNN repeat50 script at serious scale.
- Keep CuPy enabled.
- Do not expand to all-app.
- Treat the result as focused evidence only.

Not authorized:

- V3 release.
- all-app rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- true zero-copy wording.
- external device-buffer interop or embedding claims.

## Goal-Level Decision Audit

1. Was I foolish? No. The blocking review finding was accepted and fixed before pod.
2. If yes, what actions made it foolish? The risky action would have been running pod evidence with inferred residency instead of runtime-proven residency.
3. Was there another path? Yes: ignore the review and run anyway. That would have produced untrustworthy evidence.
4. Can I now try a different path that actually solves the problem? Yes. Run a focused pod smoke first, then serious repeat50 only if smoke proves the productized runner metadata is correct.
