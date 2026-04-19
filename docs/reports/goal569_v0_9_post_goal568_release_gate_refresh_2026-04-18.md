# Goal 569: v0.9 Post-Goal568 Release-Gate Refresh

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Status: accepted by Codex, Claude, and Gemini Flash.

## Purpose

Goal 568 changed the v0.9 release-candidate state by adding prepared HIPRT DB
table reuse for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

That means the earlier Goal 562/563/564 pre-release trail is still valid as a
historical gate, but it is no longer sufficient as the latest release gate by
itself. Goal 569 refreshes the release evidence after Goal 568 without rewriting
the earlier reports.

## Code/Test Gate

### Local Full Test

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 64.168s
OK
```

### Linux Backend-Capable Full Test

Linux checkout:

`/tmp/rtdl_goal568`

Runtime environment:

```bash
cd /tmp/rtdl_goal568
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
```

Command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 147.598s
OK
```

### Goal 568 Focused Linux Test

Goal 568 also ran the affected HIPRT DB suites directly:

```bash
PYTHONPATH=src python3 -m unittest tests.goal568_hiprt_prepared_db_test tests.goal559_hiprt_db_workloads_test
```

Result:

```text
Ran 14 tests in 6.873s
OK
```

## Performance Gate

Goal 568 Linux performance artifact:

`/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_linux_2026-04-18.json`

Summary on 100k rows, 3 median iterations:

| Workload | HIPRT one-shot | HIPRT prepared query | HIPRT prepare | PostgreSQL setup/index | PostgreSQL indexed query | Parity |
|---|---:|---:|---:|---:|---:|---|
| `conjunctive_scan` | 1.910673s | 0.001839s | 1.825620s | 5.734930s | 0.003271s | all matched CPU |
| `grouped_count` | 1.833957s | 0.002289s | 1.819266s | 5.644232s | 0.010592s | all matched CPU |
| `grouped_sum` | 1.822728s | 0.002445s | 1.790839s | 5.117464s | 0.011181s | all matched CPU |

Interpretation boundary:

- This supports repeated-query HIPRT DB table reuse.
- This does not claim RTDL is a DBMS.
- PostgreSQL remains the external database baseline for SQL semantics,
  indexing, persistence, concurrency, joins, and unbounded table behavior.
- The Linux GPU in this evidence is a GTX 1070 path with no RT cores, so no
  RT-core speedup claim is made.

## Documentation Gate

Audited files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_2026-04-18.md`

Stale wording check:

```bash
rg -n "prepare_hiprt.*currently limited|DB table reuse|future work|graph CSR, or DB table reuse|does not yet cover.*DB|broader prepared HIPRT reuse remains future|pending external review" ...
```

Result:

- No stale "DB reuse future work" statements found in the audited public docs.
- Matches were current positive statements saying prepared bounded DB table
  reuse is now supported.

Local Markdown link check:

```text
checked 12 files
bad_links 0
```

Documentation updates made after Goal 568:

- `README.md` now says `prepare_hiprt` includes prepared bounded DB table reuse.
- `docs/quick_tutorial.md` now mentions repeated prepared DB query support.
- `docs/current_architecture.md` now includes prepared DB reuse in the HIPRT
  candidate architecture.
- `docs/rtdl_feature_guide.md` now lists prepared bounded DB table reuse.
- `docs/capability_boundaries.md` now updates the remaining HIPRT prepared
  boundary.
- `docs/release_reports/v0_9/support_matrix.md` now cites Goal 568 evidence
  and summarizes the PostgreSQL comparison.

## Flow Gate

Goal 568 has 3-AI consensus:

- Codex report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_2026-04-18.md`
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal568_external_review_2026-04-18.md`
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal568_gemini_flash_review_2026-04-18.md`

The earlier v0.9 release-candidate gate remains part of the evidence chain:

- Goal 562: pre-release test gate
- Goal 563: documentation audit
- Goal 564: release-candidate flow audit

Goal 569 supersedes those as the latest post-568 release-gate refresh.

## Current Known Errors

Known code errors: none release-blocking after this gate. Local and Linux full
test discovery pass, and the affected HIPRT DB prepared/one-shot suites pass.

Known documentation errors: none release-blocking in the audited public docs.
The stale prepared-HIPRT boundary was refreshed to include DB table reuse.

Known flow errors: none release-blocking. Goal 568 has Codex, Claude, and Gemini
Flash acceptance, and Goal 569 preserves the post-568 gate rather than silently
rewriting the older reports.

## Codex Verdict

ACCEPT. The v0.9 release candidate is again internally coherent after Goal 568,
subject to final user-controlled release action.

## External Consensus

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal569_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal569_gemini_flash_review_2026-04-18.md`

Consensus verdict: ACCEPT, no blockers.
