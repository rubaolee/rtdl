# Goal 467: v0.7 External Test Report Response

Date: 2026-04-16

## Verdict

The two newer external reports have been triaged.

- The macOS user-perspective correctness report is accepted as positive
  evidence: 179/179 checks passed across the public workload surface on the
  available backends.
- The Windows report exposed a real release blocker in an older v0.6 snapshot:
  stale/missing Embree binary deployment and stale Python API exports.
- Current-branch code and docs now address the actionable current-worktree
  failures, and a fresh current-branch Windows sync was retested after the fix.

## Source Reports

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_user_correctness_test_report_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md`

The first report was copied into this repo from:

- `/Users/rl2025/claude-work/rtdl-2026-04-16/docs/reports/rtdl_user_correctness_test_report_2026-04-16.md`

## Finding Response Table

| ID | Source | Finding | Current response | Status |
|---|---|---|---|---|
| R467-001 | macOS correctness report | 179/179 public workload checks pass across `cpu_python_reference`, `cpu`, and `embree` where applicable. | Accepted as positive evidence. No code change required. | accepted |
| R467-002 | macOS correctness report | Count-style predicates emit zero-hit rows, while row-style predicates omit zero-hit rows; KNN emits `k`; Jaccard may emit zero-similarity candidate rows; BFS dedupe emits one source. | Classified as coherent user-visible semantics, not bugs. The response records these as documentation/familiarization points. | accepted, no blocker |
| R467-003 | Windows audit | `librtdl_embree.dll` missing or stale in an older snapshot; stale library could raise raw `AttributeError` for missing `rtdl_embree_run_fixed_radius_neighbors`. | Added `EMBREE_REQUIRED_SYMBOLS` and a loader gate that rejects stale/incomplete Embree libraries with an explicit rebuild message. Added `RTDL_FORCE_EMBREE_REBUILD` support and `make build-embree` as a public build/probe target. Fresh Windows sync built `build/librtdl_embree.dll`, exported all 22 required symbols, and ran graph Embree examples. | fixed and retested |
| R467-004 | Windows audit | Older snapshot lacked current public API exports, especially `rt.csr_graph`, breaking graph tutorials. | Current branch already exports `csr_graph` and `validate_csr_graph`; added regression test to lock this public API. | fixed |
| R467-005 | Windows audit | Windows PostGIS driver logic needed explicit `ST_SetSRID` for TIGER SRID 4269. | Classified as external benchmark-driver hygiene, not an RTDL runtime defect. If those Windows PostGIS scripts enter the repo, they must preserve explicit SRID construction. | recorded |
| R467-006 | Windows audit | Windows PostgreSQL/PostGIS baselines are functional and fast for indexed graph/PIP probes. | Accepted as baseline evidence only. RTDL Windows Embree deployment correctness is covered separately by the fresh current-branch retest in R467-003. | accepted as baseline evidence |

## Code And Documentation Changes

- `src/rtdsl/embree_runtime.py`
  - Adds `EMBREE_REQUIRED_SYMBOLS`.
  - Checks loaded Embree libraries for required exports before assigning ctypes
    signatures.
  - Emits a clear stale/incomplete-library rebuild message instead of allowing
    raw missing-symbol `AttributeError`.
  - Supports `RTDL_FORCE_EMBREE_REBUILD=1` for explicit rebuilds.
- `Makefile`
  - Adds public `make build-embree`.
  - Adds the target to `make help`.
- `README.md`, `docs/quick_tutorial.md`,
  `docs/release_facing_examples.md`, and
  `docs/release_reports/v0_7/support_matrix.md`
  - Document the Embree build/probe path.
  - Document the Windows Embree binary snapshot boundary: include a matching
    `build/librtdl_embree.dll` or allow first-use rebuild from source.
- `tests/goal467_external_report_response_test.py`
  - Locks public graph exports and the Embree required-symbol contract.
- `docs/reports/goal439_external_tester_report_intake_ledger_2026-04-16.md`
  - Adds rows for the two newer report families.

## Validation

Local validation completed on macOS:

```text
python3 -m unittest tests.goal467_external_report_response_test
Ran 2 tests in 0.000s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test
Ran 13 tests in 0.043s
OK

make help
Public targets include build-embree.

make build-embree
Embree 4.4.0

PYTHONPATH=src:. python3 examples/rtdl_graph_bfs.py --backend embree
PASS: emitted the expected two BFS rows.

PYTHONPATH=src:. python3 examples/rtdl_graph_triangle_count.py --backend embree
PASS: emitted the expected one triangle row.
```

Windows fresh current-branch retest:

```text
ssh lestat-win "hostname && cd C:\Users\Lestat && python --version"
host reachable, but default python is Microsoft Store shim.

ssh lestat-win "where python & where py & py -3 --version"
py -3 is available: Python 3.11.9.

Fresh sync path:
C:\Users\Lestat\work\rtdl_goal467_current

py -3 -m unittest tests.goal467_external_report_response_test
Ran 2 tests in 0.000s
OK

py -3 -c "import rtdsl as rt; ..."
csr_graph 2
embree 4.4.0

dir build\librtdl_embree.dll
04/16/2026  11:30 AM  372,224 librtdl_embree.dll

required_symbols 22
missing []

py -3 examples/rtdl_graph_bfs.py --backend embree
PASS: emitted the expected two BFS rows.

py -3 examples/rtdl_graph_triangle_count.py --backend embree
PASS: emitted the expected one triangle row.
```

The Windows `py -3` interpreter printed `Could not find platform independent
libraries <prefix>` before some commands, but the commands exited successfully
and produced correct RTDL output. That interpreter warning should be tracked as
host environment noise, not as an RTDL failure.

## Remaining Boundary

The Windows audit blocker is resolved for the current branch at the bounded
graph/API/Embree deployment surface tested here. This does not convert Windows
into the primary v0.7 DB performance-validation platform; Linux remains the
canonical PostgreSQL and GPU validation platform.

## Status

Goal 467 is accepted with 2-AI consensus:

- Codex implementation/validation consensus: ACCEPT.
- Claude external review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal467_external_review_2026-04-16.md`
  verdict: ACCEPT.

Gemini Flash was attempted first, but hit repeated model-capacity 429s and
could not write the requested review file. Its intermediate objection was the
missing Windows retest; that retest was subsequently completed and accepted by
Claude.
