# Goal 561: v0.9 Public Docs Refresh

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

## Verdict

ACCEPT for first-pass public documentation synchronization after the v0.9 HIPRT
matrix reached full `run_hiprt` coverage.

The public docs no longer describe HIPRT as only a one-workload 3D
ray/triangle preview. They now describe the current honest state:

- active `v0.9` HIPRT candidate
- `run_hiprt` Linux parity coverage for the 18-workload matrix
- `prepare_hiprt` still limited to the prepared 3D `ray_triangle_hit_count`
  path
- no AMD GPU validation
- no RT-core speedup claim from the tested GTX 1070 path
- no HIPRT CPU fallback
- no released `v0.9.0` claim before final test/doc/audit gates

## Files Refreshed

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

## New v0.9 Candidate Package

Added:

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

This package is intentionally named as a candidate package, not a release
package. It points to the accepted Goal 560 evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_external_review_2026-04-18.md`

## Checks

Stale public-doc string scan:

```bash
rg -n 'experimental post|narrow Linux|3D `ray_triangle_hit_count` only|only one workload shape|HIPRT preview|Experimental HIPRT' \
  README.md \
  docs/README.md \
  docs/current_architecture.md \
  docs/quick_tutorial.md \
  docs/release_facing_examples.md \
  docs/rtdl_feature_guide.md \
  docs/tutorials/README.md \
  docs/capability_boundaries.md \
  examples/README.md
```

Result: no matches.

Focused unittest:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal560_hiprt_backend_perf_compare_test
```

Result:

```text
Ran 3 tests in 0.104s
OK
```

## Honesty Boundary

Allowed public statement:

HIPRT is an active v0.9 candidate backend with Linux `run_hiprt` parity coverage
for 18 workloads, backed by Goal 560 cross-backend parity/timing evidence.

Disallowed public statement:

HIPRT is not yet released as `v0.9.0`, not AMD-validated, not a CPU fallback,
and not performance-leading on the current one-repeat small-fixture smoke
comparison.

## Remaining Release Work

This goal refreshes public docs after the matrix changed. It does not replace
the final v0.9 full pre-release gate. The remaining release-critical work is a
full v0.9 test pass, release-document audit, and final flow audit.
