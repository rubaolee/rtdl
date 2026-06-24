# Goal1416 External Review Request: v1.5.1 COLLECT_K_BOUNDED Native Parity

Please review the Goal1416 v1.5.1 `COLLECT_K_BOUNDED` native parity package in this repository.

## Files To Inspect

- `scripts/goal1416_v1_5_1_collect_k_native_parity.py`
- `tests/goal1416_v1_5_1_collect_k_native_parity_test.py`
- `docs/reports/goal1416_v1_5_1_collect_k_native_parity_multi_env_2026-05-06.md`
- `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.md`
- `docs/reports/goal1416_v1_5_1_collect_k_native_parity_linux_embree_2026-05-06.md`
- `docs/reports/goal1416_v1_5_1_collect_k_native_parity_nvidia_pod_optix_2026-05-06.md`
- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`

## Review Questions

1. Does this package honestly prove same-contract bounded candidate-row parity for the measured scope?
2. Does it preserve fail-closed overflow semantics, exact capacity behavior, canonical ordering, and complete-coverage metadata?
3. Are the Windows, Linux Embree, and NVIDIA pod OptiX outcomes represented without over-claiming?
4. Does the report avoid public primitive promotion, speedup claims, and zero-copy claims?
5. Are there blockers before using this as accepted parity evidence for the v1.5.1 `COLLECT_K_BOUNDED` promotion track?

## Required Output

Write a concise Markdown review with sections:

- Verdict
- Accepted Evidence
- Blockers
- Notes

Use `ACCEPT` only if the package is suitable as bounded parity evidence for this measured scope. Use `BLOCK` if any issue invalidates the evidence. Do not authorize public promotion or speedup wording.
