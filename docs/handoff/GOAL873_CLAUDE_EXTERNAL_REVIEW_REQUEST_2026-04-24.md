# Goal873 Claude External Review Request

Please independently review Goal873, focusing on whether the new OptiX gate is
safe, honest, and sufficient as a pre-cloud strict gate for the native bounded
`segment_polygon_anyhit_rows` pair-row emitter.

Files to review:

- `src/rtdsl/optix_runtime.py`
- `scripts/goal873_native_pair_row_optix_gate.py`
- `tests/goal873_native_pair_row_optix_gate_test.py`
- `docs/reports/goal873_native_pair_row_optix_gate_2026-04-24.md`
- `docs/reports/goal873_native_pair_row_optix_gate_2026-04-24.json`
- `docs/reports/goal873_codex_review_2026-04-24.md`

Expected review questions:

- Does the optional `ctypes` binding match the C ABI for
  `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded`?
- Does the gate preserve honesty by avoiding promotion of the public rows path?
- Is non-strict local behavior acceptable when `librtdl_optix` is missing?
- Is strict mode sufficient for the next Linux/RTX run: native symbol must run,
  match CPU row digest, and report no overflow?
- Are there missing tests or failure modes that should block Goal873?

Return a concise markdown verdict: `ACCEPT`, `ACCEPT_WITH_CAVEATS`, or `BLOCK`,
with concrete reasons.
