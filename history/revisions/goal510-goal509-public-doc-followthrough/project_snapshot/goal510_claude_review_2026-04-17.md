# Goal510 External AI Review

Date: 2026-04-17

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **PASS — public docs now honestly reflect Goal509's robot/Barnes-Hut
performance evidence without overclaiming**

## Scope Checked

- `README.md` (front page)
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/release_facing_examples.md`
- `docs/tutorials/v0_8_app_building.md`
- `docs/tutorials/feature_quickstart_cookbook.md`
- `examples/README.md`
- `tests/goal510_app_perf_doc_refresh_test.py`

## Findings By Doc

### Front Page (README.md)

Links Goal509 directly in the primary front-door link list and in the v0.8
version status block. Claims are bounded:

- robot has accepted CPU/Embree/OptiX; Vulkan is explicitly rejected for
  hit-count parity
- Barnes-Hut separates RTDL candidate generation from Python force reduction
- v0.8 is framed as accepted app-building work, not a new released language line

No overclaiming found.

### docs/README.md

Live-state summary correctly carries the Goal507/Goal509 evidence boundary and
the robot Vulkan rejection. Consistent with front page.

### docs/current_architecture.md

Performance evidence described as intentionally phase-specific. Robot accepts
CPU/Embree/OptiX and rejects Vulkan for hit-count mismatch. Barnes-Hut separates
RTDL candidate-generation timing from Python opening-rule and force-reduction
timing. No full N-body or RT-core claims.

### docs/capability_boundaries.md

Most precise treatment of the limits. Explicitly calls out:

- robot screening is bounded discrete case; CPU/Embree/OptiX are
  correctness-gated; Vulkan is not exposed until per-edge hit-count mismatch
  is fixed
- Barnes-Hut measures candidate-row generation, not full N-body solver
  acceleration; Python still owns opening rule and force reduction
- no RT-core performance claim (GTX 1070 evidence)

No overclaiming found.

### docs/release_facing_examples.md

Robot CLI examples include `cpu_python_reference`, `embree`, `optix` only —
Vulkan correctly omitted. Barnes-Hut CLI examples include `embree`, `optix`,
`vulkan`. Goal509 summary paragraph correctly explains the candidate-generation
vs. force-reduction split. Explicit caution not to read Barnes-Hut timing as
full N-body acceleration. Consistent backend CLI boundary also expressed in the
"Public CLI Backend Selection" section.

### docs/tutorials/v0_8_app_building.md

Links Goal509. Robot bounded readout names Embree as the strongest measured
backend and explicitly states Vulkan is not exposed due to hit-count parity.
Barnes-Hut bounded readout states candidate timing is reported separately
because Python still owns opening-rule and force reduction. Language-gap section
correctly notes missing tree-node types, opening predicate, and vector
reductions.

### docs/tutorials/feature_quickstart_cookbook.md

Robot recipe: "Goal509 accepts CPU, Embree, and OptiX for this app and rejects
Vulkan until per-edge hit-count parity is fixed." Barnes-Hut recipe: "Goal509
accepts CPU, Embree, OptiX, and Vulkan for candidate generation, but full-app
timing remains dominated by Python opening-rule and force-reduction work." Both
accurate and consistent.

### examples/README.md

v0.8 app boundary section correctly states robot does not expose Vulkan due to
Goal509 parity mismatch, and Barnes-Hut records candidate-generation timing
separately from Python force-reduction timing. Consistent with all other docs.

### Test Suite

`tests/goal510_app_perf_doc_refresh_test.py` checks all required strings. All
assertions verified against the actual file contents during this review. The
internal validation report states 10 tests passed. No gap found between test
assertions and actual doc content.

## Cross-Cutting Assessment

The following non-claims are preserved consistently across all eight docs:

| Non-claim | Preserved? |
| --- | --- |
| v0.8 is not a released language line | Yes, uniform across all docs |
| Robot Vulkan is not supported | Yes, explicit in every doc that mentions the app |
| Barnes-Hut is not faithful N-body acceleration | Yes, explicit boundary in every relevant doc |
| Full-app Barnes-Hut timing != RTDL candidate timing | Yes, explicit split stated every time timing is mentioned |
| No RT-core performance claim | Yes, no such claim appears anywhere |

## Summary

Goal510 is complete. All eight public doc surfaces now carry the Goal509
robot/Barnes-Hut evidence accurately, with the robot Vulkan rejection and
Barnes-Hut candidate-generation scope stated consistently and without
overclaiming. The test suite covers the critical assertion surface. No
corrections required.
