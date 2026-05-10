# Goal1647 v1.6.x OptiX Collect-K Cooperative Merge-Chain Prep 3-AI Consensus

## Verdict

`cooperative_merge_chain_capability_probe_ready_for_pod`

Codex, Claude, and Gemini agree that the local Goal1647 preparation is a safe no-pod step before attempting an OptiX `COLLECT_K_BOUNDED` cooperative merge-chain performance diagnostic.

## Consensus

The accepted interpretation is:

- The native entry point is capability-only: it queries CUDA device attributes and launches no kernels.
- The Python script records readiness artifacts and does not produce performance evidence.
- The next pod run should stop early if `cooperative_launch_supported` is false.
- If cooperative launch is supported, the next implementation must remain opt-in diagnostic work and must not be enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- Exact parity, merge-event timing, wrapper median, profile total time, and transfer counts are required before any performance conclusion.
- A first probe below `1.15x` should not be treated as a good-win candidate.

## Review Notes

Claude approved the approach with no blockers and suggested three cleanups: zero native outputs before CUDA calls, document that the first probe is device-0-specific, and treat cooperative multi-device launch as informational only. The local files were updated for those points.

Gemini found the native capability probe, ctypes script, report, and static tests technically sound and procedurally compliant. The Gemini CLI command timed out after emitting its review text, so this consensus only relies on the explicit verdict and review content saved in `docs/reviews/gemini_goal1647_collect_k_cooperative_merge_chain_prep_review_2026-05-09.md`; it does not infer additional unrecorded approval.

## Claim Boundary

This consensus does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
