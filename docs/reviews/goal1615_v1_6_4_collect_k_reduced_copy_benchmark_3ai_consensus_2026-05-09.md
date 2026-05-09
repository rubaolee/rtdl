# Goal1615 v1.6.4 COLLECT_K_BOUNDED Reduced-Copy Benchmark 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as copy/materialization-count benchmark evidence.

This consensus accepts Goal1615 only for the measured local same-contract
wrapper paths. Timing remains diagnostic only. This does not authorize public
speedup wording, true zero-copy wording, broad RTX/GPU wording, stable
`COLLECT_K_BOUNDED` promotion, release tags, or release action.

## Reviewed Files

- `scripts/goal1615_v1_6_4_collect_k_reduced_copy_benchmark.py`
- `tests/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_test.py`
- `docs/reports/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_2026-05-09.json`
- `docs/reports/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_2026-05-09.md`
- `docs/reviews/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_claude_review_2026-05-09.md`
- `docs/reviews/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_gemini_review_2026-05-09.md`

## Evidence

- Codex generated the local fake-native reduced-copy/prepared-output benchmark
  artifact and validated it with the v1.6.x regression slice: `Ran 52 tests`
  and `OK`.
- The accepted metric is `input_materialization_count_delta`.
- The generated package records three scales: `32`, `128`, and `512` unique
  rows.
- Each scale records baseline input materializations equal to `iterations`,
  prepared typed-input materializations equal to `1`, and delta equal to
  `iterations - 1`.
- Each scale records prepared host-output buffer reuse and stable typed-input
  buffer address.
- Claude returned `ACCEPTED` with no blockers.
- Gemini returned `ACCEPTED` with no blockers.

## Consensus

All three reviewers agree that Goal1615 is valid local evidence for reduced
Python wrapper materialization counts with prepared host output. It satisfies
the Goal1613 missing evidence item named
`v1_6_x_collect_k_prepared_output_reduced_copy_benchmark_package` for local
fake-native scope only.

## Next Step

Prepare the representative RTX collect-k required-backend packet. The packet
should reuse the Goal1614 bounds-stress and Goal1615 reduced-copy commands with
`embree` and `optix` required where available, record backend metadata, and keep
all performance and stable-promotion claims blocked until reviewed.
