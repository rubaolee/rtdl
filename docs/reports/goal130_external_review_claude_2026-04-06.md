# Claude External Review: Goal 130 v0.2 Test Plan and Execution Package

**Date reviewed:** 2026-04-06
**Reviewer:** Claude (Sonnet 4.6)
**Source handoff:** docs/handoff/GOAL130_EXTERNAL_REVIEW_HANDOFF.md

---

## Verdict

**Accepted.** The package is technically honest, the repairs are real and verified, and the Linux/PostGIS evidence is internally consistent with the saved artifacts. No overclaiming found. One structural transparency note and one runner scope note are worth carrying forward.

---

## Findings

**Artifact data is genuine and matches the report exactly.**
The hitcount and anyhit artifact JSONs were produced on host `lx1` (Linux-6.17.0-20-generic, same machine used throughout v0.2) at timestamps 2026-04-06T21:21:20 and 21:21:21. Every figure quoted in the execution report — PostGIS timings, backend timings, parity booleans — was confirmed against the raw JSON to six decimal places. No fabrication found.

**The n/a rendering fix is real and tested.**
The markdown output for both workload families shows `n/a` for cpu and vulkan prepared-path columns. `goal118_segment_polygon_linux_large_perf_test.py` explicitly asserts the `n/a` string in the rendered output. Before this fix, those cells showed `0.000000`, which would have been misleading. The fix is correct.

**The run_test_matrix.py repair is a real improvement.**
The `v0_2_local`, `v0_2_linux`, and `v0_2_full` groups now exist in the runner. `test_matrix_runner_test.py` has 7 tests covering: group disjointness, module existence, group union correctness for both `full` and `v0_2_full`, CLI execution, and a full end-to-end `v0_2_local` run that asserts `ok: true`. All 7 pass locally (confirmed, ran in 53s). The `test_group_modules_exist` test independently verifies that every named module in every group is importable — this is the right test to catch plan-accuracy drift like the original `plan_schema_test` reference.

**The `plan_schema_test` removal was handled correctly.**
The accepted plan and runner contain no reference to that nonexistent module. The repair is clean.

**Honesty boundaries are maintained throughout.**
Environment-gated rows (Vulkan native, Linux-only PostGIS runs) are explicitly labeled as not required for local Mac execution. The Vulkan performance expectation is stated correctly as "must work, must not be very slow" rather than "performance flagship." The `v0_2_linux` group is correctly documented as environment-gated.

**One transparency note on the execution report timings.**
The execution report presents figures for x64, x256, x512, x1024 scale levels as a unified table. In reality, x64 and x256 current-run means come from 3-iteration isolated perf measurements (mean_sec: x64 cpu 0.001937s, x256 cpu 0.007633s), while the figures cited in the execution report for all scale levels (x64 cpu 0.010713s, x256 cpu 0.008556s) come from single-shot PostGIS validation runs measured within the validation script. The PostGIS validation timings are the right comparison basis for the parity check — both RTDL and PostGIS are measured in the same script run — but they carry Python/script overhead not present in isolated perf measurements. This explains why x64 cpu appears 5.5× slower in the execution report than in the perf artifact (0.010713s vs 0.001937s). The report does not misrepresent correctness, and the PostGIS comparison is fair. But a reader who treats the execution report figures as isolated perf benchmarks will misread them.

**One runner scope note.**
The `v0_2_linux` group contains only two unittest modules: `goal110_segment_polygon_hitcount_closure_test` and `goal114_segment_polygon_postgis_test`. The large-scale Goal 118 and Goal 128 perf scripts are not unittest modules and therefore do not appear in `--group v0_2_linux` or `--group v0_2_full`. This is a structural gap between what the runner claims as the "v0.2 full" matrix and what was actually executed for the performance evidence. This is acceptable given the environment-gated nature of those scripts, but it means `--group v0_2_full` is not sufficient to reproduce the performance results in the execution report.

---

## Summary

The Goal 130 package closes what it claims to close. The three repairs (plan accuracy, stale runner, n/a rendering) are real, verified, and tested. The Linux/PostGIS evidence is traceable to the artifact JSONs with no discrepancies. Honesty boundaries around environment-gated Vulkan and Linux-only rows are maintained throughout.

The two items to carry forward: the execution report timing figures are from PostGIS validation single-shots, not isolated perf means, which matters if those figures are reused in performance comparisons downstream; and the `v0_2_full` runner group does not include the large-scale perf scripts, so it does not constitute a full reproduction of the Linux evidence. Neither of these is a reason to reject the package. They are documentation gaps that should inform how the Goal 130 results are cited in future work.
