# External Review Request: Goal1255 v1.1 through v1.5 Roadmap

Please review the proposed RTDL post-v1.0 roadmap.

Primary file:

- `docs/reports/goal1255_codex_v1_1_to_v1_5_roadmap_and_scope_2026-05-04.md`

Reference files:

- `docs/reports/goal1042_primary_architecture_feedback_v1_5_primitives_2026-04-27.md`
- `docs/reports/goal1227_formal_v1_0_v1_5_v2_0_roadmap_design_2026-05-01.md`
- `docs/reports/goal1227_two_ai_consensus_2026-05-01.md`
- `docs/v1_0_app_acceleration_inventory.md`
- `docs/release_reports/v1_0/README.md`

Review context:

- RTDL `v1.0` is released as the app-shaped proof release.
- v1.5 has prior accepted direction: replace app-specific native continuations
  with reviewed generic traversal-plus-reduction primitives.
- The proposed new decision is the v1.1-v1.4 ladder:
  v1.1 post-release hardening and OptiX/Embree triage;
  v1.2 NVIDIA OptiX performance push;
  v1.3 primitive ABI and per-app lowering matrix;
  v1.4 compatibility-wrapper first migration slice;
  v1.5 generic primitive release.
- The proposed backend scope is strict: before v2.1, do not spend new
  implementation effort on Vulkan, HIPRT, or Apple RT. Preserve their existing
  proof surfaces, but focus active engineering on Embree and OptiX.
- NVIDIA RT performance is the top priority. Embree remains the CPU RT
  fallback and same-contract comparison baseline.

Review questions:

1. Is the v1.1-v1.4 sequencing technically sound as a path toward v1.5?
2. Is the pre-v2.1 freeze on Vulkan, HIPRT, and Apple RT justified, given that
   v1.0 already proved selected paths can work there?
3. Does the roadmap correctly prioritize NVIDIA OptiX/RTX performance while
   preserving Embree as the comparison baseline?
4. Does the v1.5 primitive target still match Goal1042 and Goal1227?
5. Are any statements overclaiming public speedup, whole-app acceleration,
   backend maturity, or v1.5 readiness?
6. What required fixes, if any, are needed before this can become a 3-AI
   consensus input?

Expected response format:

```text
VERDICT: ACCEPT or REQUEST_CHANGES

Reasons:
- ...

Required fixes:
- ...

Notes for 3-AI consensus:
- ...
```
