# Goal1813: 3-AI Consensus for v2.0 Release Readiness

Date: 2026-05-13

Verdict: `accept-with-boundary`

## Scope

This consensus evaluates whether RTDL v2.0 is release-ready as the first
Python+partner+RTDL release candidate, with the bounded claim surface defined
in Goal1810.

This consensus does not tag, publish, or move a release. Release publication
still requires explicit user authorization.

## Consensus Inputs

Codex authored the Goal1810 release-readiness audit after implementing and
validating the v2.0 evidence chain.

External reviews:

- Claude:
  `docs/reviews/goal1811_claude_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md`
- Gemini:
  `docs/reviews/goal1812_gemini_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md`

Both external systems are distinct from Codex and from each other. This satisfies
the project rule for key release decisions: Codex plus two independent external
AI systems. Codex+Codex is not counted.

## Evidence Accepted

The consensus accepts the following as sufficient for the first v2.0 release
candidate:

- protocol-first v2.0 partner contract;
- PyTorch as the primary/reference partner;
- CuPy as the lightweight conformance partner;
- NumPy as the CPU/Embree partner path;
- real-framework validation for NumPy, PyTorch CUDA, and CuPy CUDA;
- Embree partner any-hit host-stage execution evidence;
- OptiX partner any-hit host-stage execution evidence;
- public Python dispatch for `backend="embree"` and `backend="optix"`;
- learner-facing partner any-hit example and tutorial;
- RTX-class OptiX pod evidence for NumPy, PyTorch CUDA, and CuPy CUDA sources;
- machine-readable claim guards in the pod artifacts:

```text
transfer_mode = "host_stage"
true_zero_copy_authorized = false
rt_core_speedup_claim_authorized = false
```

## Allowed v2.0 Claim

The accepted release claim is:

```text
RTDL v2.0 introduces the first Python+partner+RTDL path: partner-owned NumPy,
PyTorch CUDA, and CuPy CUDA columns can be passed through a public Python API
to the RTDL any-hit primitive path, with Embree as the CPU RT fallback and
OptiX validated on RTX-class hardware through the current host-stage bridge.
```

## Blocked Claims

The following remain blocked after v2.0:

- true zero-copy;
- direct device-pointer handoff;
- arbitrary PyTorch/CuPy program acceleration;
- RTDL optimizing partner code;
- broad RT-core speedup;
- whole-application acceleration;
- identical partner performance;
- packaging/install support beyond source-tree execution.

## Boundary Notes

Goal1808's two focused-test skips remain visible in the evidence chain. They do
not block v2.0 because the three public OptiX partner examples executed and
passed as separately captured JSON artifacts.

OptiX phase timings for the tiny first-wave fixture are not performance
evidence. v2.0 does not claim performance speedup.

The v2.0 partner path is host-stage. It is a real Python+partner+RTDL bridge,
not a true zero-copy bridge.

## Final Decision

`accept-with-boundary`: v2.0 is release-ready as the first bounded
Python+partner+RTDL release candidate.

The release may proceed only with the allowed claim surface above and only after
explicit user authorization to tag or publish.
