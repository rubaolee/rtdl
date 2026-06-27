# Three-AI Consensus: Goal1417 v1.5.1 COLLECT_K_BOUNDED Benchmark

## Verdict

ACCEPTED as same-contract bounded collection benchmark evidence for the measured Goal1417 scope.

This consensus does not authorize public primitive promotion, speedup wording, or zero-copy wording. `COLLECT_K_BOUNDED` remains a v1.5.1 promotion-track candidate until release-gate work authorizes any public surface change.

## Reviewed Evidence

- Benchmark harness: `scripts/goal1417_v1_5_1_collect_k_benchmark.py`
- Unit tests: `tests/goal1417_v1_5_1_collect_k_benchmark_test.py`
- Multi-environment report: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_multi_env_2026-05-06.md`
- Windows generated artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
- Linux Embree required-backend artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_linux_embree_2026-05-06.md`
- NVIDIA pod OptiX required-backend artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_nvidia_pod_optix_2026-05-06.md`
- Prior parity consensus: `docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md`
- External Claude review: `docs/reports/claude_goal1417_v1_5_1_collect_k_benchmark_review_2026-05-06.md`
- External Gemini review: `docs/reports/gemini_goal1417_v1_5_1_collect_k_benchmark_review_2026-05-06.md`

## Consensus

- Codex accepts the package as benchmark evidence because it measures the exact-capacity bounded candidate-row contract and checks parity metadata for every measured backend/scale.
- Claude returned `ACCEPT` with no blockers, confirming that Goal1417 builds on the accepted Goal1416 parity baseline and records timing data without weakening contract validation.
- Gemini returned `ACCEPT` with no blockers, confirming that the benchmark preserves parity checks and avoids unauthorized speedup or public-promotion wording.
- All reviewers agree that Windows OptiX skips are non-authoritative; required OptiX benchmark evidence comes from the NVIDIA pod run.
- Claude noted one cosmetic issue: the copied Linux Embree and NVIDIA OptiX artifact bodies retain the generic generated file names in their internal `Files` section. The multi-environment summary lists the correct environment-specific saved artifact paths, so this does not block acceptance.
- Claude also noted that OptiX is slower than the Python reference at the smallest measured scale, consistent with launch overhead. The report records this honestly and makes no speedup claim.

## Remaining Gates

- Keep public wording narrowed until a release-gate package explicitly authorizes promotion.
- Do not claim zero-copy from this evidence.
- Any future performance claim must identify exact scope, scale, environment, and reviewed timing basis.
