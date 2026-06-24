# Goal681: Post-History Current-Main Release Gate

Status: PASS

Date: 2026-04-20

## Scope

Goal681 reruns the local release-gate checks after Goal680 repaired and
extended the public history indexes for Goals650-656 and Goals658-679.

This gate validates the current worktree after:

- cross-engine prepared/prepacked visibility/count optimization closure;
- public documentation refresh;
- local and Linux backend release gates;
- public history catch-up and stale history database repair.

## Full Local Test

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1268 tests in 108.542s
OK (skipped=187)
```

## Public Command Truth Audit

Command:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py --write
```

Result:

```json
{
  "command_count": 250,
  "public_doc_count": 14,
  "valid": true
}
```

Classification counts:

```json
{
  "linux_gpu_backend_gated": 33,
  "linux_postgresql_gated": 1,
  "optional_native_backend_gated": 44,
  "portable_python_cpu": 165,
  "visual_demo_or_optional_artifact": 7
}
```

## Focused Public Documentation Tests

Command:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal515_public_command_truth_audit_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal655_tutorial_example_current_main_consistency_test -v
```

Result:

```text
Ran 8 tests in 0.013s
OK
```

## Public Entry Smoke

Command:

```text
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Result:

```text
valid: true
```

## History Regression

Command:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal657_history_current_main_catchup_test \
  tests.goal680_history_cross_engine_optimization_catchup_test -v
```

Result:

```text
Ran 4 tests in 0.002s
OK
```

## Mechanical Check

Command:

```text
git diff --check
```

Result:

```text
clean
```

## Boundary

This gate is for current-main release readiness after post-`v0.9.5`
optimization and history work. It does not itself create a new release tag.

The current claim boundary remains:

- prepared/prepacked repeated 2D visibility/any-hit/count is validated across
  the documented current-main backend paths;
- DB, graph, full-row, and one-shot broad speedup claims are not implied;
- GTX 1070 Linux evidence is not RT-core evidence;
- HIPRT/Orochi CUDA on NVIDIA is not AMD GPU validation;
- Apple RT scalar count speedup is not full emitted-row speedup.

## Verdict

PASS.

The current worktree passes the post-history local test, public-doc, public
entry, history-regression, and mechanical whitespace gates.
