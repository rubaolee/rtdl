# Goal 675 Consensus: Vulkan Prepared 2D Any-Hit With Packed Rays

Date: 2026-04-20

## Inputs

- Codex implementation/report: `docs/reports/goal675_vulkan_prepared_2d_anyhit_packed_optimization_2026-04-20.md`
- Gemini Flash review: `docs/reports/goal675_external_review_gemini_flash_2026-04-20.md`
- Claude review request: `docs/handoff/GOAL675_VULKAN_PREPARED_2D_ANYHIT_REVIEW_REQUEST_2026-04-20.md`

## Verdicts

- Codex: ACCEPT
- Gemini 2.5 Flash: ACCEPT
- Claude: unavailable for this goal in the automated call; the first CLI process stalled without output and was terminated, and the local shell lacks a `timeout` command for a bounded retry.

## Consensus

Goal 675 has 2-AI acceptance consensus from Codex and Gemini Flash.

The accepted claim is bounded:

- Vulkan now supports a prepared Ray2D/Triangle2D `ray_triangle_any_hit` handle.
- The prepared handle reuses the build-side triangle GPU buffer plus BLAS/TLAS.
- The prepared path accepts prepacked `PackedRays`.
- The measured speedup applies to prepared scene plus prepacked rays, not to tuple-ray prepared calls.

Linux evidence:

```text
Focused correctness:
  Ran 14 tests in 0.769s
  OK (skipped=4)

Repeated-query performance:
  4096 rays / 1024 triangles:
    direct median: 0.008035034 s
    prepared+packed median: 0.004496957 s
  8192 rays / 8192 triangles:
    direct median: 0.011363139 s
    prepared+packed median: 0.006903602 s
  32768 rays / 8192 triangles:
    direct median: 0.028801230 s
    prepared+packed median: 0.021956306 s
```

## Boundary

This goal does not claim prepared Vulkan 3D any-hit, scalar count-only any-hit, or DB/graph sparse output allocation changes.
