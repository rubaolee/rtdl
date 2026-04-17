# Codex Consensus: Goal509 Robot/Barnes-Hut Linux Performance

Date: 2026-04-17

Verdict: ACCEPT

Reviewed artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal509_app_perf_linux_raw_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal509_app_perf_smoke_raw_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal509_claude_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal509_gemini_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal509_app_perf_linux.py`
- `/Users/rl2025/rtdl_python_only/tests/goal509_app_perf_harness_test.py`

Consensus:

- The robot collision benchmark is fair for CPU, Embree, and OptiX because all accepted backends run the same RTDL hit-count kernel on identical inputs and match the independent CPU oracle.
- Robot Vulkan is correctly rejected as performance evidence because it fails per-edge hit-count parity, even though it preserves the colliding pose count in the tested cases.
- The public robot demo CLI correctly excludes Vulkan until that correctness defect is fixed.
- The Barnes-Hut benchmark is fair because candidate generation is timed separately from full application execution, making clear that RTDL owns spatial candidate selection while Python owns opening-rule and force-reduction logic.
- The report correctly avoids RT-core claims because the Linux host GPU is a GTX 1070 with no RT cores.

No blockers remain for using Goal509 as bounded v0.8 app performance evidence.
