# Codex Review: Goal4405 V3.0 M10 Same-Stream Evidence Plan

Date: 2026-06-15

Reviewer: Codex

Reviewed artifact: `docs/reports/goal4405_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`

VERDICT: ACCEPT_WITH_GATES

## Top Findings

1. The plan is the right next step after M9. M9 already proved device-resident grouped-stream partner rows for CuPy and Numba, and it correctly left `same_stream_ready=false` and `true_zero_copy_ready=false`.
2. The plan keeps the work in the evidence layer rather than pretending this is a benchmark speedup result.
3. The strictest part is also the most important part: same-stream readiness can only flip with observed CUDA event or Nsight stream-correlation evidence.
4. Pointer identity alone is correctly rejected as true-zero-copy evidence. The transfer-counter/no-hidden-copy requirement is necessary.
5. The fail-closed rule is correct. If the current native wrapper synchronizes internally or hides the stream, M10 should record a blocked result and leave readiness false.
6. The partner policy is correct: both CuPy and Numba rows are required, and there is no automatic partner selection.

## Required Gates

- Do not set `same_stream_ready=true` without an observed producer-to-consumer stream-ordering record.
- Do not set `true_zero_copy_ready=true` without transfer-counter or equivalent no-hidden-copy evidence.
- Do not use host materialization before the partner continuation.
- Do not introduce app-specific public Python names or native symbols.
- Do not convert M10 into a public performance claim.
- Keep CuPy and Numba in the same packet, same scale, same threshold, same contract.

## Risks

- Existing grouped-union wrappers may synchronize before returning to Python. If so, the correct M10 result is partial or blocked.
- CuPy and Numba stream APIs may not expose identical external-stream semantics on the pod. The plan correctly allows a partner-specific blocked row rather than forced promotion.
- The measured rows may remain sub-millisecond. That is acceptable for an evidence gate, but not for public speedup wording.

## Wording Boundary

Allowed wording after a full pass:

"M10 provides internal hardware-observed evidence that this grouped-stream OptiX plus explicit partner route can preserve stream-ordered device-resident handoff on the tested pod."

Allowed wording after a partial or blocked result:

"RTDL has device-resident grouped-stream partner evidence, but same-stream and true-zero-copy wording remain blocked until stream and transfer evidence are observable."

Not allowed:

- broad RTDL speedup claims;
- "zero-copy" from pointer identity alone;
- "same-stream" when the native wrapper synchronizes internally;
- claims that this M10 gate represents all RTDL partner paths.

## Final Recommendation

Proceed to M10 implementation only under these gates. The plan is acceptable because it makes false promotion harder than a blocked result.
