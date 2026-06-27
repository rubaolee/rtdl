# RTDL V4.0 M8 Internal 2-AI Critical Review

Date: 2026-06-19
Status: accepted review input; actions required before release-candidate readiness.

Reviewed packet:

`docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md`

Reviewers:

- Ampere: release-gate and claim-boundary review.
- Sartre: runtime/API usefulness and Python GPU ecosystem review.

## Shared Verdict

Both reviewers accept the M8 packet as a critical-review baseline for the
experimental V4.0 M1 route.

Both reviewers reject calling V4.0 release-candidate ready today.

`v4_release_candidate` must remain a non-authorizing review gate.

## Shared P0/P1 Findings

1. Release-candidate readiness remains false. The blocker manifest still has
   open gates for external review, package/runtime, front-door docs, public
   true-zero-copy, async, speed, full framework surfaces, and SDK/C ABI.
2. The M8 evidence coordinates must not be mistaken for final release-candidate
   coordinates. A final RC decision needs one explicit candidate commit and a
   fresh validation bundle.
3. `v4_release_candidate` currently runs the same module set as `v4_active`.
   That is acceptable only because the gate is non-authorizing.
4. The current runtime story is source-tree-only. A real V4.0 release decision
   must either close a clean install/package runtime story or explicitly exclude
   it from V4.0 scope.
5. CUDA device identity needs a clearer single-GPU/multi-GPU contract. The
   adapter should preserve explicit CUDA Array Interface device identity where
   available and fail closed on mixed-device route inputs.
6. Candidate wording should avoid implying RTX/RT-core speed authority before
   RTX-class evidence exists.

## Accepted Actions

- Keep `v4_release_candidate` non-authorizing.
- Refresh the blocker manifest status from pre-M8 to M8-review-baseline.
- Add explicit review baseline coordinates while leaving final RC coordinates
  unset until release approval.
- Add device-id preservation/fail-closed tests for CUDA Array Interface inputs.
- Tighten wording from public candidate "RT-core" claims toward the narrower
  validated "OptiX-backed Python GPU operator" evidence where the packet is
  describing current validated scope.
- Run the final validation bundle after the fixes.

## Non-Actions

The review does not authorize:

- V4.0 current-release/front-door promotion;
- package install, PyPI, wheel, or stable SDK claims;
- public true-zero-copy claims;
- async/nonblocking completion claims;
- public speedup, RTX speedup, or RT-core speedup claims;
- full PyTorch, full Numba, or full DLPack surface claims;
- public multi-language C ABI or non-Python host support.
