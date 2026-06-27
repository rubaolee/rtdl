# Codex Consensus: Goal 467 v0.7 External Test Report Response

Date: 2026-04-16

## Verdict

ACCEPT.

## Basis

Goal 467 read and triaged the two newer external report families:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_user_correctness_test_report_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md`

The macOS correctness report is accepted as positive evidence. The Windows
report exposed real stale-snapshot blockers: missing/stale Embree DLL exports
and stale public API exports. Current branch changes address those blockers by:

- adding `EMBREE_REQUIRED_SYMBOLS`
- rejecting stale/incomplete Embree libraries with a clear rebuild message
- adding `RTDL_FORCE_EMBREE_REBUILD`
- adding `make build-embree`
- documenting the Windows binary snapshot boundary
- adding regression coverage for `csr_graph`, `validate_csr_graph`, and the
  required Embree symbol list

## Validation

Local macOS validation:

- `python3 -m unittest tests.goal467_external_report_response_test`
- `PYTHONPATH=src:. python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test`
- `make build-embree`
- `PYTHONPATH=src:. python3 examples/rtdl_graph_bfs.py --backend embree`
- `PYTHONPATH=src:. python3 examples/rtdl_graph_triangle_count.py --backend embree`
- final focused sweep:
  `PYTHONPATH=src:. python3 -m unittest tests.goal467_external_report_response_test tests.rtdsl_embree_test tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test`

Fresh Windows current-branch validation:

- synced to `C:\Users\Lestat\work\rtdl_goal467_current`
- `py -3 -m unittest tests.goal467_external_report_response_test`
- `rt.csr_graph(...)` returned expected vertex count
- `rt.embree_version()` returned `4.4.0`
- `build\librtdl_embree.dll` was built and present
- all 22 required Embree symbols were present
- `py -3 examples/rtdl_graph_bfs.py --backend embree` passed
- `py -3 examples/rtdl_graph_triangle_count.py --backend embree` passed

## External Review

Claude external review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal467_external_review_2026-04-16.md`
- verdict: ACCEPT

Gemini Flash was attempted first and produced a useful intermediate objection
that the Windows retest was missing, but it could not write the review file due
to plan-mode write denial and repeated model-capacity 429s. After the Windows
retest was completed, Claude accepted the updated evidence package.

## Boundary

This closes the external-report response for the bounded graph/API/Embree
deployment issue found on Windows. It does not move Windows into the canonical
v0.7 PostgreSQL/GPU performance-validation role; Linux remains canonical for
that line.
