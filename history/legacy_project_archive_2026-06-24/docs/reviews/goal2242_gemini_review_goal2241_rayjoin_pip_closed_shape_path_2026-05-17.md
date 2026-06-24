# Independent Gemini Review: Goal2241 RayJoin PIP Closed-Shape Path

This is an independent Gemini review, distinct from any Codex review.

## Review of Goal2241

**Context:** This goal wires the RayJoin same-query PIP runner to use the newly introduced generic `closed_shape_membership_2d_optix` primitive, replacing the older compiled RTDL kernel path for PIP workloads on the OptiX backend. It aims to keep the native surface app-agnostic while preserving the RayJoin-facing output contract.

## Questions and Answers:

### 1. Does the runner correctly route only PIP/OptiX through the generic `closed_shape_membership_2d_optix` primitive?

**Yes.** The `scripts/goal2192_rayjoin_same_query_stream_runner.py` clearly defines a conditional routing within its `_run_backend` function. Specifically, `if backend == "optix"` and `if workload == "pip"`, the execution path is directed to `_run_pip_optix_closed_shape`, which in turn calls `rt.closed_shape_membership_2d_optix`. This selective routing is further confirmed by the metadata (`implementation_path` and `uses_generic_closed_shape_membership`) recorded in the output, which explicitly states when this new path is used. The `tests/goal2241_rayjoin_same_query_pip_closed_shape_path_test.py` unit test explicitly validates this routing logic.

### 2. Does the Python mapping preserve the RayJoin same-query output contract (`point_id`, `polygon_id`, `contains`) without putting app vocabulary into the native engine?

**Yes.** The Python-side mapping, implemented in the `_run_pip_optix_closed_shape` function within `scripts/goal2192_rayjoin_same_query_stream_runner.py`, translates the generic primitive's output (`point_id`, `shape_id`, `membership`) into the RayJoin-specific contract (`point_id`, `polygon_id`, `contains`). The report `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md` explicitly states that this mapping is performed in Python because `polygon_id` is RayJoin application vocabulary, thus ensuring the native engine remains app-agnostic. The `tests/goal2192_rayjoin_same_query_stream_adapter_test.py` includes a mock test (`test_pip_optix_backend_uses_generic_closed_shape_membership_path`) that directly verifies this translation.

### 3. Does the report keep the claim boundary narrow and avoid implying full RayJoin reproduction, v2.0 release readiness, or paper-scale speedup?

**Yes.** All relevant documentation, including `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md`, `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`, and `docs/reports/goal2240_closed_shape_membership_2ai_consensus_2026-05-17.md`, consistently and explicitly define a narrow claim boundary. These documents and the `claim_boundary` dictionary within the runner script itself disclaim any implications of full RayJoin reproduction, v2.0 release readiness, or broad paper-scale speedup. The tests also verify the presence of these boundary disclaimers.

### 4. Are the tests sufficient for this wiring change before pod timing?

**Yes.** The provided unit tests, particularly `tests/goal2241_rayjoin_same_query_pip_closed_shape_path_test.py` and the mock test in `tests/goal2192_rayjoin_same_query_stream_adapter_test.py` (`test_pip_optix_backend_uses_generic_closed_shape_membership_path`), thoroughly cover the critical aspects of this wiring change. They confirm the correct conditional routing, the precise Python-side mapping of data, and the adherence to reporting standards. For a "wiring change" that precedes full pod timing, these tests provide adequate confidence in the correctness of the integration.

## Verdict: `accept`
