# Goal635: v0.9.5 Pre-Release Test, Doc, And Audit Gate

Date: 2026-04-19

## Verdict

PASS for the bounded `v0.9.5` any-hit / visibility-row slice.

This is not a final tag authorization. It is the local pre-release gate for the
implemented Goal631-Goal634 work.

## Implemented Scope

Included:

- `rt.ray_triangle_any_hit(exact=False)`
- `rt.ray_triangle_any_hit_cpu(...)`
- `rt.visibility_rows_cpu(...)`
- lowering metadata for `ray_tri_anyhit`
- `run_cpu_python_reference` support
- `run_cpu` oracle fallback support
- public examples:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_ray_triangle_any_hit.py`
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_visibility_rows.py`
- public docs:
  - `/Users/rl2025/rtdl_python_only/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
  - `/Users/rl2025/rtdl_python_only/docs/features/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/features/ray_tri_anyhit/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
  - `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
  - `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
  - `/Users/rl2025/rtdl_python_only/examples/README.md`

Excluded:

- multi-hop graph traversal
- hierarchical candidate filtering
- rendering hooks or shader callback APIs
- native backend-specific any-hit kernels
- performance/speedup claims for any-hit or visibility rows

## Local Full Test

Command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1187 tests in 114.108s
OK (skipped=171)
```

This full-suite result was rerun after the final feature-cookbook update.

Focused command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal632_ray_triangle_any_hit_test tests.goal633_visibility_rows_test tests.rtdsl_ray_query_test tests.rtdsl_simulator_test -v
```

Focused result:

```text
Ran 22 tests in 0.019s
OK
```

Example smoke commands:

```bash
PYTHONPATH=src:. python3 examples/rtdl_ray_triangle_any_hit.py
PYTHONPATH=src:. python3 examples/rtdl_visibility_rows.py
```

Both commands completed successfully and emitted deterministic JSON.

Feature cookbook smoke:

```bash
PYTHONPATH=src:. python3 examples/rtdl_feature_quickstart_cookbook.py
```

Result summary:

- `feature_count: 24`
- includes `ray_tri_anyhit`
- includes `visibility_rows`

## Public Doc Command Audits

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Result:

```json
{"goal": 497, "valid": true}
```

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{"command_count": 244, "public_doc_count": 14, "valid": true}
```

## 2+ AI Consensus

Codex conclusion: ACCEPT.

Claude review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal632_633_claude_review_2026-04-19.md`
- Verdict: ACCEPT
- Notes: confirms early-exit `break`, correct `tmax=1.0` finite visibility
  construction, docs/examples accuracy, and no blocking issues.

Gemini Flash review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal632_633_gemini_flash_review_2026-04-19.md`
- Verdict: ACCEPT
- Notes: confirms API/reference/runtime/oracle/lowering wiring, tests, examples,
  and scope honesty.

## Audit Findings

No blockers found in the v0.9.5 slice.

Non-blocking observations:

- `oracle_runtime.py` follows the existing ray-query convention that rays are
  the left/probe input and triangles are the right/build input. Future cleanup
  can resolve by role rather than side.
- `ray_triangle_any_hit_cpu` inherits mixed 2D/3D validation from the shared
  ray-triangle intersection helper, matching the existing hit-count and
  closest-hit pattern.

## Honesty Boundary

The docs explicitly state that `v0.9.5` is a language/reference/oracle contract
slice. It does not claim native backend-specific any-hit kernels or performance
speedups. Visibility rows are documented as a CPU standard-library helper, not
a renderer, path tracer, scene graph, or dynamic occlusion system.
