# Goal2323: v2.0 Release Action

Status: `v2_0_source_tree_python_partner_rtdl_release_action_authorized`

Date: 2026-05-18

## Decision

The user explicitly authorized the v2.0 release after the final cleanup packet,
current-head Claude review, current-head Gemini review, and Goal2322 3-AI
consensus were completed.

This goal performs the v2.0 release action:

- bump `VERSION` to `v2.0`;
- publish the v2.0 source-tree release package under
  `docs/release_reports/v2_0/`;
- update front-door docs from hold/candidate wording to released source-tree
  wording;
- preserve source-tree-only, evidence-only, app-agnostic-engine, and partner
  boundary caveats;
- tag the committed tree as `v2.0` after the final release gate passes.

## Release Boundary

v2.0 is the source-tree Python+partner+RTDL language release. Python remains
the application/control layer. Partner frameworks own tensor/column memory and
normal framework continuations. RTDL owns documented RT-shaped primitive calls,
backend dispatch, and the app-agnostic native release surface.

v2.0 does not claim package-install support, arbitrary PyTorch/CuPy
acceleration, broad RT-core speedup, whole-application speedup, arbitrary
polygon overlay, RayJoin paper reproduction, Triton/Numba integration, Embree
CPU partner completion, or v3.0 custom engine extensions.

## Consensus Basis

- Codex integration cleanup: `docs/reports/goal2319_v2_0_final_cleanup_release_candidate_2026-05-18.md`
- Claude final cleanup review: `docs/reviews/goal2320_claude_final_v2_0_release_cleanup_review_2026-05-18.md`
- Gemini final cleanup review: `docs/reviews/goal2321_gemini_final_v2_0_release_cleanup_review_2026-05-18.md`
- Final 3-AI consensus: `docs/reports/goal2322_final_v2_0_release_cleanup_3ai_consensus_2026-05-18.md`

## Protected Local Files

The release staging step must keep the known protected local artifacts out of
git:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`
- `Lib/`

## Validation Command

The release gate is the focused v2.0 release-action slice:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal2323_v2_0_release_action_test tests.goal2322_final_v2_release_cleanup_3ai_consensus_test tests.goal2319_v2_0_final_cleanup_release_candidate_test tests.goal2072_v2_0_final_readiness_aggregator_test tests.goal2093_v2_pre_release_public_docs_boundary_test tests.goal2094_v2_learner_doc_single_version_cleanup_test tests.goal1906_public_v2_claim_boundary_scan_test tests.goal1217_version_marker_current_release_sync_test
```

Observed result:

```text
Ran 43 tests in 0.377s

OK
```

Broader release slice:

```text
Ran 82 tests in 2.735s

OK
```

## Verdict

`accept`: v2.0 is ready to tag and push as the source-tree Python+partner+RTDL
language release, with the bounded public claims above.
