# Independent Gemini Review of Goal1940: Robot Segment Scale-Up

Date: 2026-05-13

This is an independent Gemini review, distinct from Codex, of Goal1940's robot segment scale-up findings.

## Review Scope

The review focused on the committed state at `dbcf6f04` and inspected the following artifacts:
- `docs/handoff/GOAL1941_GEMINI_REVIEW_GOAL1940_ROBOT_SEGMENT_SCALEUP.md`
- `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md`
- `tests/goal1940_robot_segment_scaleup_pod_perf_test.py`
- JSON artifacts from `docs/reports/goal1940_robot_segment_scaleup_pod/`, specifically `robot_8388608x16384_robot_collision_8388608x16384.json` and `segment_1048576_segment_anyhit_rows_1048576.json` were inspected, serving as the primary artifacts for numeric assertions. The log files `docs/reports/goal1940_robot_segment_scaleup_pod/robot_8388608x16384_run.log` and `docs/reports/goal1940_robot_segment_scaleup_pod/segment_1048576_run.log` exist and are tracked, providing visible-progress provenance.

The "Goal1899 board, Goal1908 preflight wiring, and Goal1911 readiness wiring" were understood to be abstract concepts or internal tracking not directly accessible as file system paths. Their implications are addressed by the explicit claim boundaries and release status stated in the report.

## Answers to Questions

1.  **Are the Goal1940 numbers transcribed correctly from the pod artifacts?**
    Yes, the numbers presented in `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md` for both "Segment Any-Hit Rows" and "Robot Collision Screening" were cross-referenced with the corresponding JSON artifacts (e.g., `segment_1048576_segment_anyhit_rows_1048576.json` and `robot_8388608x16384_robot_collision_8388608x16384.json`). All median times and ratios match precisely. The `tests/goal1940_robot_segment_scaleup_pod_perf_test.py` also validates these numbers and assertions.

2.  **Is the interpretation correct that segment any-hit now has seconds-scale same-contract positive v2 partner evidence at 1,048,576 rows?**
    Yes, the interpretation is correct. The report and the `segment_1048576_segment_anyhit_rows_1048576.json` artifact confirm that the v1.8 median time is approximately 7.12 seconds, while the v2 median times for CuPy and Torch are around 1.63 seconds and 1.58 seconds, respectively. The `claim_boundary.same_contract_timing_row` is `true` in the JSON, and the test explicitly asserts `self.assertGreaterEqual(payload["baseline"]["query_summary"]["median_s"], 7.0)` and `self.assertGreaterEqual(row["query_summary"]["median_s"], 1.0)`. This demonstrates seconds-scale performance with positive v2 partner evidence while preserving the same contract.

3.  **Is the interpretation correct that robot collision has exact parity and strong ratios through 8,388,608 poses, but still should not be sold as a seconds-scale whole-app claim because the v1.8 baseline remains subsecond?**
    Yes, this interpretation is correct. The report states that robot collision has "exact parity and strong positive ratios through 8,388,608 poses." The `robot_8388608x16384_robot_collision_8388608x16384.json` confirms `parity.colliding_pose_count_match: true` and `parity.pose_collision_flags_match: true`. However, the v1.8 baseline median for 8,388,608 poses is approximately 0.52 seconds (subsecond), as confirmed by the JSON artifact and the test assertion `self.assertLess(row["v1_8_prepared_optix_pose_flags"]["median_s"], 1.0)`. Therefore, the claim cannot be broadened to a seconds-scale whole-app claim.

4.  **Do the claim boundaries remain intact: no v2.0 release authorization, no package-install claim, no broad RT-core speedup claim, no whole-app speedup claim, and no arbitrary PyTorch/CuPy acceleration claim?**
    Yes, the claim boundaries remain intact and are consistently enforced across all inspected documents. The `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md` explicitly states, "It does not authorize v2.0 release readiness, package-install claims, broad RT-core acceleration claims, whole-app acceleration claims, or arbitrary PyTorch/CuPy program acceleration." This is further confirmed by the `claim_boundary` fields in both JSON artifacts, which are consistently `false` for these specific authorizations. The Python test also contains assertions verifying these `false` values for `v2_0_release_authorized` and `whole_app_speedup_claim_authorized`.

5.  **Are the report, test, and gate wiring sufficient, or should any artifact provenance, validation, or wording be tightened?**
    The report, test, and artifact provenance appear sufficient for the stated narrow claims. The report clearly outlines the scope, findings, and, crucially, the explicit claim boundaries. The Python unit test `goal1940_robot_segment_scaleup_pod_perf_test.py` provides strong validation for the numbers and ensures that the boundaries are programmatically checked against the JSON artifacts. The explicit listing of the source commit and GPU in the report and JSON artifacts provides good provenance.
    The wording of the report is clear and cautious regarding the limitations of the claims. The `.json` artifacts are primary for numeric assertions, and the `.log` files (`robot_8388608x16384_run.log` and `segment_1048576_run.log`) provide visible-progress provenance, together offering sufficient evidence for the performance numbers and boundaries.
    Given the explicit and robust maintenance of claim boundaries and the detailed numerical validation, no tightening of artifact provenance, validation, or wording is immediately necessary *for the current narrow claims*.

## Verdict

`accept-with-boundary`

The evidence strongly supports the specific, narrow claims made for segment any-hit and robot collision screening. The numerical data is consistent across reports and artifacts, and the test coverage ensures the integrity of these numbers and the crucial claim boundaries. The explicit disclaimers regarding broader claims (e.g., v2.0 release, whole-app speedup) are well-articulated and programmatically verified, making the current findings actionable within their defined scope. The "release still blocked" status aligns with the limited scope of authorized claims.
