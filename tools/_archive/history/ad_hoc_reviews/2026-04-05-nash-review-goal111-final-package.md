Keep.

- The strengthened package now clears the main redundancy objection. In
  `src/rtdsl/generate_only.py`, the generated program owns all three accepted
  dataset builders directly, including fixture reconstruction and derived
  tiling, instead of punting to `baseline_runner`. That makes it a real
  single-file handoff artifact, not just an emitted wrapper around repo
  internals.
- The request contract is now honest and concrete.
  `docs/goal_111_v0_2_generate_only_mvp.md` and
  `docs/reports/goal111_v0_2_generate_only_mvp_2026-04-05.md` match the actual
  product shape: one family, accepted datasets, chosen backend, verify flag,
  and output mode. It no longer pretends to be broader than it is.
- The implementation is still narrow, but usefully narrow.
  `examples/rtdl_generated_segment_polygon_hitcount_cpu.py` is specific enough
  to be a real “give me one runnable file for this exact request” tool, which
  is more useful than sending a user to a generic example plus extra helper
  machinery for the stated scenario.
- The tests prove the right baseline for an MVP.
  `tests/goal111_generate_only_mvp_test.py` checks contract specialization and
  generated-program execution, and the final report states the generated `cpu`
  path also succeeded on Linux capable host. That is enough to keep the MVP.
- The right caution remains: keep it as a narrow second bet, not as evidence
  that RTDL should broadly pivot into code generation. If future expansion
  collapses back into thin template filling, it should be paused quickly.
