# Goal1008 Large-Repeat Artifact Intake Consensus

Date: 2026-04-26

Consensus: **ACCEPT**

Participants:

- Codex: implemented the intake gate, ran Goal1008 tests, and generated the report.
- Claude: external review verdict `ACCEPT`.
- Gemini: external review verdict `ACCEPT`.

Decision:

- `6/7` Goal1006 held rows now clear the 100 ms RTX query/native phase timing floor for separate 2-AI public-wording review.
- `robot_collision_screening / prepared_pose_flags` remains held because both large-repeat variants stay below the floor on median query time.
- Goal1008 authorizes zero public speedup claims. It only repairs the short-phase concern for eligible rows and keeps wording scoped to prepared RTX query/native sub-paths.
- A follow-up facility x4 repeat replaced the originally borderline facility x3 timing. The selected facility artifact is now `goal1007_facility_service_coverage_x4_large_rtx.json` with median RTX query time `0.157368` s.

Boundary:

- No front-page or release-note speedup wording is authorized by Goal1008.
- Any public wording still needs a separate wording review and must avoid whole-app speedup claims.
