# Third-AI Review Request: Goal1255 v1.1 through v1.5 Roadmap

Please independently review the RTDL post-v1.0 roadmap so we can complete a
3-AI consensus.

Primary file:

- `docs/reports/goal1255_codex_v1_1_to_v1_5_roadmap_and_scope_2026-05-04.md`

Existing review input:

- `docs/reports/goal1255_gemini_external_review_v1_1_to_v1_5_roadmap_2026-05-04.md`

Reference files:

- `docs/reports/goal1042_primary_architecture_feedback_v1_5_primitives_2026-04-27.md`
- `docs/reports/goal1227_formal_v1_0_v1_5_v2_0_roadmap_design_2026-05-01.md`
- `docs/reports/goal1227_two_ai_consensus_2026-05-01.md`
- `docs/v1_0_app_acceleration_inventory.md`
- `docs/release_reports/v1_0/README.md`

Review context:

- RTDL `v1.0` is released as the app-shaped proof release.
- The proposed v1.1-v1.5 roadmap is:
  v1.1 post-release hardening and Embree/OptiX triage;
  v1.2 NVIDIA OptiX performance push;
  v1.3 primitive ABI and per-app lowering matrix;
  v1.4 compatibility-wrapper first migration slice;
  v1.5 generic traversal-plus-reduction primitive release.
- Before v2.1, the proposal freezes new Vulkan, HIPRT, and Apple RT
  implementation work. Their existing proof surfaces remain documented, but
  active engineering focuses on Embree and OptiX.
- NVIDIA RT performance is the top priority. Embree remains the CPU RT fallback
  and same-contract comparison baseline.
- Gemini already returned `VERDICT: ACCEPT` with no required fixes. This review
  should still be independent and should not rubber-stamp Gemini.

Review questions:

1. Is the v1.1-v1.4 ladder the right path into v1.5?
2. Is the pre-v2.1 freeze on Vulkan, HIPRT, and Apple RT justified?
3. Does the roadmap correctly prioritize NVIDIA OptiX/RTX performance while
   preserving Embree as baseline and fallback?
4. Does the v1.5 primitive set match the Goal1042/Goal1227 contract?
5. Does the roadmap avoid public speedup, whole-app, backend-maturity, or
   v1.5-readiness overclaims?
6. Are there any required fixes before this can become final 3-AI consensus?

Expected response format:

```text
VERDICT: ACCEPT or REQUEST_CHANGES

Reasons:
- ...

Required fixes:
- ...

Notes for final 3-AI consensus:
- ...
```
