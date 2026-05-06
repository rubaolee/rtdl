# 3-AI Consensus: v1.5.1 Collect Primitives, Zero-Copy, and Data Movement - 2026-05-06

## Verdict

Consensus is reached.

The architecture report is accepted as v1.5.1 guidance:

```text
COLLECT_K_BOUNDED is the semantic primitive for bounded row output.
Zero-copy/reduced-copy is the memory architecture for moving that output cheaply.
The shared foundation is an explicit app-generic buffer contract.
```

This consensus does not claim public promotion, native parity completion,
performance speedup, true zero-copy, or partner implementation.

## Reviewed Artifacts

- Architecture report:
  `docs/reports/v1_5_1_collect_primitives_zero_copy_data_movement_architecture_2026-05-06.md`
- Claude initial review:
  `docs/reports/claude_v1_5_1_collect_primitives_zero_copy_architecture_review_2026-05-06.md`
- Claude rereview:
  `docs/reports/claude_v1_5_1_collect_primitives_zero_copy_architecture_rereview_2026-05-06.md`
- Gemini initial review:
  `docs/reports/gemini_v1_5_1_collect_primitives_zero_copy_architecture_review_2026-05-06.md`
- Gemini rereview:
  `docs/reports/gemini_v1_5_1_collect_primitives_zero_copy_architecture_rereview_2026-05-06.md`

## Consensus Position

Codex accepts the report because it preserves the current roadmap: finish
Python+RTDL first, then build Python+partner+RTDL. It keeps the native Embree and
OptiX direction app-generic and separates primitive semantics from data movement
mechanisms.

Claude accepts the revised report as v1.5.1 architecture guidance. Claude
confirmed that the final version satisfies the required clarifications for `K`
ownership, ordering semantics, duplicate semantics, `row_width`, and the
DLPack/v1.7 capability caveat.

Gemini accepts the revised report as v1.5.1 architecture guidance. Gemini
confirmed that the report correctly separates `COLLECT_K_BOUNDED` semantics
from zero-copy/reduced-copy mechanisms and keeps zero-copy and partner claims
properly bounded.

## Implementation Guidance

- `K` is selected by the caller-facing Python+RTDL invocation and passed
  explicitly to native backends.
- `row_width` is fixed per result buffer and per native call.
- Public result ordering is stable lexicographic ordering by the complete
  candidate-id row after discovery.
- Duplicate candidate-id rows are deduplicated before capacity checking.
- Overflow fails closed before partial semantic result materialization.
- Embree and OptiX should converge on the same app-generic row-buffer metadata
  before public promotion or benchmark claims.
- True zero-copy wording requires a measured GPU-resident or externally
  shareable device-memory path. Pinned/staging reuse is reduced-copy or
  reduced-transfer wording only.
- DLPack/PyTorch/CuPy is a v1.7 partner-track direction, not an implemented
  v1.5.1 capability.

## Decision

Use the architecture report as the conceptual foundation for v1.5.1
`COLLECT_K_BOUNDED` work. Continue implementation through the existing
Python+RTDL track, and defer partner integration semantics to v1.7-v2.0.
