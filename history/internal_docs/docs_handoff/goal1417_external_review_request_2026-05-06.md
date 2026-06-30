# Goal1417 External Review Request: v1.5.1 COLLECT_K_BOUNDED Benchmark

Please review the Goal1417 v1.5.1 `COLLECT_K_BOUNDED` benchmark package in this repository.

## Files To Inspect

- `scripts/goal1417_v1_5_1_collect_k_benchmark.py`
- `tests/goal1417_v1_5_1_collect_k_benchmark_test.py`
- `docs/reports/goal1417_v1_5_1_collect_k_benchmark_multi_env_2026-05-06.md`
- `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
- `docs/reports/goal1417_v1_5_1_collect_k_benchmark_linux_embree_2026-05-06.md`
- `docs/reports/goal1417_v1_5_1_collect_k_benchmark_nvidia_pod_optix_2026-05-06.md`
- `docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md`
- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`

## Review Questions

1. Does this package honestly provide bounded collection benchmark evidence for the measured scope?
2. Does it preserve same-contract parity checks while recording timings?
3. Are Windows, Linux Embree, and NVIDIA pod OptiX results represented without over-claiming?
4. Does the report avoid public primitive promotion, speedup wording, and zero-copy wording?
5. Are there blockers before using this as benchmark evidence for the v1.5.1 `COLLECT_K_BOUNDED` promotion track?

## Required Output

Write a concise Markdown review with sections:

- Verdict
- Accepted Evidence
- Blockers
- Notes

Use `ACCEPT` only if the package is suitable as benchmark evidence for this measured scope. Use `BLOCK` if any issue invalidates the evidence. Do not authorize public promotion or speedup wording.
