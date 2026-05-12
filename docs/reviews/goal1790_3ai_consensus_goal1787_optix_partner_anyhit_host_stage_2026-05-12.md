# Goal1790: 3-AI Consensus for Goal1787 OptiX Partner Any-Hit Host-Stage Execution

Status: `accept-with-boundary`

Date: 2026-05-12

## Scope

Goal1787 is the first narrow v2.0 execution bridge from partner-owned columns to
the RTDL OptiX runtime:

```text
NumPy CPU / PyTorch CUDA / CuPy CUDA columns
  -> RtdlTensorDescriptor validation
  -> explicit host staging
  -> existing app-agnostic OptiX 2-D ray/triangle any-hit packets
  -> prepared OptiX any-hit count
```

The consensus question is whether this bridge is architecturally valid while
preserving the app-agnostic native engine boundary and avoiding zero-copy,
RT-core speedup, or v2.0 release overclaims.

## Inputs

- [Goal1787 report](../reports/goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1788 Claude review](goal1788_claude_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1789 Gemini review](goal1789_gemini_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md)

Codex, Claude, and Gemini are three distinct AI systems for this consensus.
Codex+Codex does not count as independent consensus.

## Review Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Implemented and validated the host-stage bridge. Current Windows slice passes with expected local skips; Linux OptiX/PyTorch/CuPy slice passes `27/27` with no skips on `192.168.1.20`. |
| Claude | `accept-with-boundary` | Confirmed descriptor validation, explicit host staging, unchanged app-agnostic OptiX ABI, no partner-specific native symbols, bounded claims, and appropriate phase-timing next step. Claude cited the earlier `25/25` Linux run; a later Codex rerun widened the same slice to `27/27` after including the current local module set. |
| Gemini | `accept-with-boundary` | Confirmed direct file-grounded review after retry, including host staging, app-agnostic packet routing, bounded validation evidence, and no zero-copy or RT-core speedup overclaim. |

## Consensus

All three reviewers accept Goal1787 with boundary.

The accepted claim is narrow:

- partner-owned NumPy CPU, PyTorch CUDA, and CuPy CUDA columns can enter a
  first-wave OptiX execution path through `RtdlTensorDescriptor` validation;
- the transfer mode is explicit `host_stage`;
- packed data is routed through the existing app-agnostic OptiX ray/triangle
  any-hit ABI;
- no native engine code or exported native symbol becomes PyTorch-, CuPy-,
  NumPy-, or app-specific;
- the returned metadata correctly blocks true-zero-copy and RT-core speedup
  claims.

The non-claims remain binding:

- no true zero-copy;
- no direct device-pointer partner ABI;
- no broad PyTorch/CuPy acceleration claim;
- no RT-core speedup claim from the tiny fixture;
- no final v2.0 release readiness.

## Next Gate

The next v2.0 engineering slice should add phase timing around:

- descriptor validation;
- framework-to-host staging;
- packet packing;
- OptiX build/traversal;
- result copyback.

That evidence is required before deciding whether a direct device-pointer
partner path belongs in v2.0 or should remain post-v2.0 optimization work.
