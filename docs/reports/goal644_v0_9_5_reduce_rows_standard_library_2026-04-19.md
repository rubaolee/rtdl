# Goal 644: v0.9.5 `reduce_rows` Standard-Library Helper

Date: 2026-04-19
Status: ACCEPTED by Codex + Claude consensus; Gemini Flash unavailable due tool quota

## Goal

Add the bounded emitted-row reduction helper proposed in Goals 534 and 536.
This is the generic `rt.reduce_rows(...)` surface discussed as the next useful
ITRE extension after bounded any-hit and visibility rows.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/reduction_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_reduce_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_feature_quickstart_cookbook.py`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/reduce_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal410_tutorial_example_check.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal515_public_command_truth_audit.py`
- `/Users/rl2025/rtdl_python_only/tests/goal513_public_example_smoke_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal644_reduce_rows_standard_library_test.py`

Public API:

```python
rt.reduce_rows(
    rows,
    group_by="pose_id",
    op="any",
    value="any_hit",
    output_field="pose_blocked",
)
```

Supported operations:

- `any`
- `count`
- `sum`
- `min`
- `max`

Semantics:

- accepts already-emitted row mappings
- emits deterministic grouped rows in first-seen group order
- supports one or more group fields
- has explicit empty-input identities for ungrouped `count`, `any`, and `sum`
- rejects empty ungrouped `min`/`max`
- raises explicit errors for missing required fields and invalid argument shapes

## Boundary

`reduce_rows` is a Python standard-library helper over materialized emitted
rows. It is not a native RT backend reduction and must not be represented as an
OptiX, Embree, Vulkan, HIPRT, or Apple RT speedup path.

The reason to add it now is ergonomic and architectural:

- it removes repeated app boilerplate
- it makes ITRE composition explicit as `input -> traverse -> refine -> emit -> reduce`
- it supports current apps such as Hausdorff, outlier detection, DBSCAN,
  visibility summaries, and robot collision screening
- it creates a stable future target if profiling later proves native reductions
  are worth implementing

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal644_reduce_rows_standard_library_test tests.goal513_public_example_smoke_test tests.goal515_public_command_truth_audit_test -v
```

Result:

- `Ran 10 tests`
- `OK`

Example smoke:

```bash
PYTHONPATH=src:. python3 examples/rtdl_reduce_rows.py
```

Result:

- emits `reduce_rows_demo` JSON
- reports the no-native-backend-reduction boundary
- returns pose collision flags, neighbor counts, and a Hausdorff-style max row

Public command truth audit:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

- `valid: true`
- public docs scanned: `14`
- runnable public commands found: `245`

Tutorial/example harness:

```bash
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py --machine local-goal644 --output docs/reports/goal644_tutorial_example_check_2026-04-19.json
```

Result:

- `63 passed`
- `0 failed`
- `26 skipped`
- `89 total`

Mechanical checks:

```bash
python3 -m py_compile src/rtdsl/reduction_runtime.py examples/rtdl_reduce_rows.py scripts/goal410_tutorial_example_check.py scripts/goal515_public_command_truth_audit.py
git diff --check
```

Result:

- no errors

Post-review cleanup:

- Claude noted one harmless unreachable grouped-output guard in
  `/Users/rl2025/rtdl_python_only/src/rtdsl/reduction_runtime.py`.
- Codex removed the dead branch.
- The focused suite and `py_compile` / `git diff --check` were rerun and passed.

## External Review

Claude:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal644_claude_review_2026-04-19.md`
- verdict: ACCEPT
- confirmed the post-cleanup implementation is bounded, correct, and does not
  overclaim native RT acceleration

Gemini Flash:

- attempted with `gemini --model gemini-2.5-flash -y`
- result: unavailable due `codebase_investigator` quota exhaustion; no Gemini
  verdict file was produced

## Current Verdict

Codex verdict: ACCEPT.

Consensus status: ACCEPT by two AIs (Codex + Claude). Gemini Flash did not
participate because the tool reported quota exhaustion.
