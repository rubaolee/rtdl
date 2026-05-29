# Goal2684 Post-Pod Consensus

Date: 2026-05-28

## Verdict

Goal2684 is accepted as an internal architecture and correctness milestone.

This consensus does not authorize public speedup wording.

## Inputs

- Codex implementation and pod validation report:
  `docs/reports/goal2684_generic_rt_hit_stream_handoff_2026-05-28.md`
- Pod artifacts:
  `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_small.json`
  and `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_100k.json`
- Pre-pod Claude review:
  `docs/reports/external_reviews/goal2684_v2_4_v2_5_claude_critical_review_2026-05-28.md`
- Codex response to pre-pod review:
  `docs/reports/goal2684_claude_review_response_2026-05-28.md`
- Post-pod Antigravity/Gemini review:
  `docs/reports/external_reviews/goal2684_gemini_post_pod_review_2026-05-28.md`
- Post-pod Claude critical review:
  `docs/reports/external_reviews/goal2684_claude_post_pod_critical_review_2026-05-28.md`
  and
  `docs/reports/external_reviews/goal2684_claude_post_pod_critical_review_2026-05-28.docx`

## Consensus Points

- `RAY_TRIANGLE_HIT_STREAM_3D` is a valid app-free primitive boundary for this
  goal. Native rows contain generic `(ray_id, primitive_id)` data only.
- Embree, OptiX, and Python reference paths implement fail-closed bounded-row
  overflow semantics.
- The OptiX path uses real RT traversal through GAS plus `optixTrace`; it is not
  a CUDA-only scan hidden behind an OptiX library entry point.
- RayDB predicate encoding, primitive-to-group/value mapping, and result
  formatting remain app-owned Python/partner work.
- The RayDB hit-stream path reaches Triton through public partner adapter entry
  points, not app-specific raw kernels.
- The L4 pod artifacts are credible internal evidence: all reported cases are
  correct against CPU reference, phase timings are recorded, and artifacts
  explicitly set `no_public_speedup_claim: true`.
- Claude and Antigravity/Gemini both return `Accept` after pod evidence. Claude
  additionally records that the 100k RT hit-stream+Triton path is within about
  5% of the native grouped-reduction path for count and sum, while still
  blocking public speedup wording.

## Blocked Claims

Public speedup wording remains blocked. The evidence supports internal
engineering conclusions only.

Reasons:

- The current hit-stream path has a large CPU/GPU materialization and mapping
  cost, especially for the 100k `sum` case.
- The review notes that Triton continuation kernels still need redesign before
  they can replace stronger GPU baselines as public-performance paths.
- A public claim would need exact wording, exact subpath scope, and a separate
  review against the final text.
- No external database/tool baseline is part of the Goal2684 pod artifacts.

## Next Engineering Target

The next runtime target is device-resident hit-stream handoff or typed primitive
payload columns, so Triton can consume RT-produced rows without the current
large host-side row presentation step. The companion continuation target is to
replace flat atomic grouped-reduction kernels with a more scalable reduction
strategy before any public performance positioning.
