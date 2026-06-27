# Goal511 External AI Review

Date: 2026-04-17

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **PASS**

## Review Criteria

The review checks whether the feature guide:

1. Honestly reflects the accepted v0.8 app-building line
2. Preserves Goal507/Goal509 boundaries without overclaiming
3. Does not overclaim release status
4. Does not overclaim backend performance

## Findings

### v0.8 App-Building Line

The feature guide correctly frames `v0.8` as "accepted app-building work on `main` over the released `v0.7.0` surface, not a released support-matrix line yet." All three v0.8 app examples (Hausdorff, robot collision screening, Barnes-Hut) are listed with links. The "Practical Promise" section reinforces this by directing readers to release reports for measured performance claims rather than making open-ended speedup promises.

### Goal507/Goal509 Boundaries

All three boundaries are present and accurately stated:

- **Robot Vulkan**: "Vulkan is not exposed for that app until the per-edge hit-count mismatch found in Goal509 is fixed." The boundary is named with the specific defect cause.
- **Barnes-Hut**: "Python still owns the opening rule and force reduction. This is not a full N-body acceleration claim." The candidate-generation-only scope is explicit.
- **GTX 1070**: Listed under "What RTDL Cannot Yet Claim" as "RT-core hardware speedup from the GTX 1070 Linux app evidence." No hardware-speedup inference is invited.

Both Goal507 and Goal509 performance reports are linked as canonical references, keeping evidence traceable.

### Release Status

The guide is consistent: `v0.7.0` is the released version; `v0.8` is accepted, not released. The release layer table makes this unambiguous. The docs index `README.md` Live State Summary agrees, as does the "What RTDL Is Today" section. There is no path by which a reader could infer a new released support-matrix line.

### Backend Performance

Performance claims are bounded throughout. The Hausdorff note says "bounded Linux Embree/OptiX/Vulkan performance evidence against RTDL and mature nearest-neighbor baselines." The Barnes-Hut note restricts the claim to candidate generation. No claim implies Vulkan is the faster backend; the feature guide says elsewhere that "Vulkan [is] the slower portable backend."

### Test Alignment

All three test methods in `goal511_feature_guide_v08_refresh_test.py` are satisfied by the current docs:

- String assertions in `test_feature_guide_carries_v08_app_building_state` all match.
- String assertions in `test_feature_guide_preserves_goal507_goal509_boundaries` all match, including the exact newline-spanning assertion `"Vulkan\n  is not exposed for that app"`.
- The index ordering assertion in `test_docs_index_links_feature_guide_in_live_path` holds: Feature Guide appears at position 3 in the New User Path, Capability Boundaries at position 4.

### Docs Index Routing

`docs/README.md` places Feature Guide before Capability Boundaries in the New User Path (step 3 vs. step 4), satisfying the routing goal stated in the Goal511 scope.

## Summary

Goal511 is complete and correct. The feature guide now presents the same v0.8 app-building story as the rest of the public docs, with all Goal507/Goal509 boundaries intact and no overclaiming of release status or backend performance.
