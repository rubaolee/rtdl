# Goal2791 Consensus - Thresholded Partner-Selection Guidance

Date: 2026-05-31

## Inputs

- Codex implementation/report:
  `docs/reports/goal2791_thresholded_partner_selection_guidance_2026-05-31.md`
- Goal2790 pod timing artifact:
  `docs/reports/goal2790_pod_artifacts/goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json`
- Goal2791 32K pod artifact:
  `docs/reports/goal2791_pod_artifacts/goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json`
- Independent Gemini review:
  `docs/reviews/goal2791_gemini_review_thresholded_partner_selection_guidance_2026-05-31.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | The mixed Goal2790 crossover is now machine-readable; auto-selection and claims stay blocked. |
| Gemini | `accept-with-boundary` | The new row accurately records mixed evidence, the Hausdorff/X-HD migration plan preserves two negative rows plus one thresholded row, and the 32K artifact is bounded tiled-completion evidence only. |

## Consensus

`accept-with-boundary`

Goal2791 is accepted as thresholded guidance metadata, not as a promoted
performance path. The tiled Triton route may be explicitly selected by an app or
benchmark harness when shape and memory evidence justify it, but no planner may
silently auto-select it from preview availability alone.

The 32K pod probe is accepted only as bounded tiled-completion evidence. It does
not authorize a same-contract 32K Torch speedup claim because the dense Torch
baseline OOMed.

## Claim Boundary

Still blocked:

- public speedup claims;
- RT-core speedup claims;
- whole-app speedup claims;
- true zero-copy claims;
- v2.5 release readiness;
- hidden automatic partner dispatch.
