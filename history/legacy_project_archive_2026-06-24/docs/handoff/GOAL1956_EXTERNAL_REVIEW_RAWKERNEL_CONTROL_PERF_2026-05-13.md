# Goal1956 External Review Request - RawKernel Control-App Perf Path

Please perform an independent read-only review of the v2.0 RawKernel control-app work after commits `06316813` and `32a9aadd`.

## Review Scope

Review these files:

- `examples/rtdl_control_apps_cupy_rawkernel.py`
- `scripts/goal1955_rawkernel_control_app_perf.py`
- `scripts/goal1956_rawkernel_control_app_pod_runner.sh`
- `docs/reports/goal1955_rawkernel_control_app_local_linux_perf_2026-05-13.md`
- `docs/reports/goal1955_local_linux_database_100k_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_graph_1k_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_graph_1m_v2_only_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_polygon_pair_256_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_polygon_jaccard_256_cupy_rawkernel_2026-05-13.json`
- `tests/goal1953_control_apps_cupy_rawkernel_v2_test.py`
- `tests/goal1955_rawkernel_control_app_perf_test.py`
- `tests/goal1956_rawkernel_control_app_pod_runner_test.py`

## Questions

1. Does Goal1955 correctly preserve the user decision that the four former-control rows count as v2.0 app versions when written as Python+CuPy RawKernel+RTDL, while still declaring that the comparison is not absolutely fair against v1.8 Python+RTDL?
2. Does the graph RawKernel correction properly remove artificial global-atomic contention without changing the authored graph summary semantics?
3. Does the local Linux GTX 1070 report avoid overclaiming release-grade evidence?
4. Does Goal1956 provide a sufficiently controlled pod runner for the next evidence step: progress logging, timeouts, CuPy probe, OptiX build, source label propagation, per-app artifacts, and a bounded summary?
5. Are any public or report statements accidentally authorizing v2.0 release, broad RT-core speedup, whole-app acceleration, arbitrary CuPy acceleration, or package-install claims?

## Expected Verdict Format

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Recommended boundary unless you find a bug: `accept-with-boundary`, because local Linux evidence is useful but pod evidence for polygon rows with OptiX candidate discovery is still required before release-grade whole-app performance claims.

Save the review as:

`docs/reviews/goal1956_external_review_rawkernel_control_perf_2026-05-13.md`
