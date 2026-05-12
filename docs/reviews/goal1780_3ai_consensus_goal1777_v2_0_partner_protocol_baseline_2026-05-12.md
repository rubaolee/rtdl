# Goal1780: 3-AI Consensus for Goal1777 v2.0 Partner Protocol Baseline

Date: 2026-05-12

Status: `accept-with-boundary`

## Scope

This consensus covers Goal1777 only: the first v2.0 Python+partner+RTDL
protocol baseline.

Reviewed artifacts:

- `src/rtdsl/partner.py`
- `src/rtdsl/__init__.py`
- `tests/goal1777_v2_0_partner_protocol_baseline_test.py`
- `docs/reports/goal1777_v2_0_partner_protocol_baseline_2026-05-12.md`
- `docs/reports/goal1770_v2_0_roadmap_boundary_after_v1_8_release_2026-05-12.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

## Consensus Rule

Important architecture goals require 3-AI consensus. Routine goals may close
with 2-AI review. Goal1777 is an important v2.0 architecture boundary, so it
requires Codex implementation plus independent Claude and Gemini review.

Codex+Codex does not count as independent consensus.

## Independent Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | Goal1777 implementation and report | `accept-with-boundary` |
| Claude | `goal1778_claude_review_goal1777_v2_0_partner_protocol_baseline_2026-05-12.md` | `accept-with-boundary` |
| Gemini | `goal1779_gemini_review_goal1777_v2_0_partner_protocol_baseline_2026-05-12.md` | `accept` |

## Shared Findings

All three reviewers agree that Goal1777:

- keeps the partner protocol in Python adapter code;
- does not add PyTorch, CuPy, or application vocabulary to native engine
  internals;
- records PyTorch as the v2.0 reference partner;
- records CuPy as the v2.0 conformance partner;
- keeps `stream_handle` reserved at zero;
- blocks zero-copy and v2.0 release-readiness claims until measured evidence
  exists;
- is a protocol baseline, not a hardware-proven partner execution path.

## Follow-Up From Review

Claude requested stronger local baseline coverage before the first real
framework slice. The Goal1777 test was expanded to cover:

- PyTorch and CuPy export paths;
- grad-enabled PyTorch rejection;
- `RtdlTensorDescriptor` validation guards;
- `RtdlOutputSpec` validation guards;
- DLPack integer device normalization;
- `partner.auto()` framework-priority and generic-DLPack fallback behavior.

The focused partner gate now passes 24 tests.

## Release Boundary

This consensus accepts the Goal1777 baseline. It does not release v2.0.

v2.0 remains blocked until at least:

- real PyTorch CPU/CUDA tests pass;
- real CuPy CUDA conformance tests pass;
- a narrow OptiX partner-descriptor execution path is validated;
- phase timing separates device-resident handoff, fallback copy, and host
  staging;
- pod/hardware evidence exists;
- final v2.0 release consensus is written.

## Verdict

`accept-with-boundary`: Goal1777 has valid 3-AI consensus for the v2.0 partner
protocol baseline, while v2.0 release readiness remains `needs-more-evidence`.
