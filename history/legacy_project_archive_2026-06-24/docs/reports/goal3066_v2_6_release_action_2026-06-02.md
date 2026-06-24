# Goal3066: v2.6 Release Action

Status: `v2_6_source_tree_python_partner_rtdl_release_action_authorized`

Date: 2026-06-02

## Decision

The user explicitly authorized the v2.6 release after the v2.6 documentation
audit, native tutorial/example pod validation, and their 3-AI consensus gates
were completed.

This goal performs the v2.6 release action:

- bump `VERSION` to `v2.6`;
- publish the v2.6 source-tree release package under
  `docs/release_reports/v2_6/`;
- update front-door docs from release-candidate wording to released
  source-tree wording;
- preserve source-tree-only, evidence-only, app-agnostic-engine,
  user-chosen-partner, and claim-boundary caveats;
- tag the committed tree as `v2.6` after the final release gate passes.

## Release Boundary

v2.6 is the current source-tree Python+partner+RTDL language release. Python
remains the application/control layer. Partner frameworks own their normal
array/tensor/custom-kernel continuations. RTDL owns documented RT-shaped
primitive calls, backend dispatch, and the app-agnostic native release surface.

v2.6 does not claim package-install support, arbitrary PyTorch/CuPy/Numba/Triton
acceleration, broad RT-core speedup, whole-application speedup, automatic
partner selection, general zero-copy/device-residency, arbitrary polygon
overlay, full paper reproduction, or v3.0 user-defined shader injection.

In short, automatic partner selection remains outside the release claim.

## Consensus Basis

- Codex documentation audit: `docs/reports/goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md`
- Documentation 3-AI consensus: `docs/reports/goal3061_v2_6_doc_total_audit_3ai_consensus_2026-06-02.md`
- Native tutorial/example pod validation: `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md`
- Claude native validation review: `docs/reviews/goal3063_claude_review_goal3062_v2_6_native_tutorial_validation_2026-06-02.md`
- Gemini native validation review: `docs/reviews/goal3064_gemini_review_goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md`
- Goal3065 native tutorial/example 3-AI consensus: `docs/reports/goal3065_v2_6_native_tutorial_validation_3ai_consensus_2026-06-02.md`
- Claude final release review: `docs/reviews/goal3067_claude_final_v2_6_release_review_2026-06-02.md`
- Gemini final release review: `docs/reviews/goal3068_gemini_final_v2_6_release_review_2026-06-02.md`
- Final release 3-AI consensus: `docs/reports/goal3069_final_v2_6_release_3ai_consensus_2026-06-02.md`

## Protected Local Files

The release staging step must keep the known protected local artifacts out of
git:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`
- `Lib/`

## Validation Command

The release gate is the focused v2.6 release-action slice:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3066_v2_6_release_action_test tests.goal3065_v2_6_native_tutorial_validation_3ai_consensus_test tests.goal3062_v2_6_native_tutorial_example_pod_validation_test tests.goal3061_v2_6_doc_total_audit_3ai_consensus_test
```

Observed result before external final release review:

```text
Ran 18 tests in 0.733s

OK
```

## Verdict

`accept-with-boundary`: v2.6 is ready for final Claude and Gemini release review
before the `v2.6` tag is created and pushed.
