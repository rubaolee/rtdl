# Goal1797: 3-AI Consensus for Goal1795 Embree Partner Any-Hit Host-Stage Execution

Status: `accept-with-boundary`

Date: 2026-05-12

## Scope

Goal1795 adds the Embree CPU RT fallback for the same first-wave Python+partner
2-D ray/triangle any-hit column contract established by Goal1787 for OptiX.

The consensus question is whether the Embree bridge accepts NumPy CPU, PyTorch
CUDA, and CuPy CUDA columns through explicit host staging while preserving the
app-agnostic native ABI and avoiding zero-copy, RT-core speedup, performance, or
v2.0 release overclaims.

## Inputs

- [Goal1795 report](../reports/goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1796 Claude review](goal1796_claude_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1798 Gemini review](goal1798_gemini_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)

Codex, Claude, and Gemini are three distinct AI systems for this consensus.
Codex+Codex does not count as independent consensus.

## Review Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Implemented the Embree host-stage bridge and validated Windows plus Linux. Linux passes `14/14` with NumPy, PyTorch CUDA, CuPy CUDA, Embree, and the companion OptiX partner tests. |
| Claude | `accept-with-boundary` | Confirmed descriptor validation, explicit host staging, unchanged Embree native ABI, bounded timing evidence, and parity with Goal1787. |
| Gemini | `accept` | Confirmed CPU RT fallback parity, Python-only partner logic, host-stage metadata, no zero-copy/performance overclaim, and Linux/Windows validation evidence. |

## Consensus

All reviewers accept Goal1795. The consensus verdict remains
`accept-with-boundary` because the broader v2.0 release is still gated by larger
scale phase timing, hardware coverage, the device-pointer ABI decision, and final
release consensus.

Accepted narrow claim:

- Embree can consume NumPy CPU, PyTorch CUDA, and CuPy CUDA partner columns for
  2-D ray/triangle any-hit count through explicit host staging.
- The native engine ABI remains unchanged and app-agnostic.
- Metadata keeps `transfer_mode = "host_stage"`,
  `true_zero_copy_authorized = False`, and
  `rt_core_speedup_claim_authorized = False`.

Non-claims:

- no true zero-copy;
- no direct device-pointer partner ABI;
- no Embree speedup or RT-core claim;
- no final v2.0 release readiness.
