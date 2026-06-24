# Goal 645: v0.9.5 Public Release Docs And Package

Date: 2026-04-19

## Scope

Public release-facing documentation and package refresh for the v0.9.5
bounded any-hit / visibility-row / emitted-row reduction surface.

This goal checks that the front page, docs index, tutorials, examples, feature
guide, architecture page, capability boundaries, backend maturity page, and
release package describe the same state.

## Public Surface

The public v0.9.5 surface is:

- `rt.ray_triangle_any_hit(exact=False)` emits `{ray_id, any_hit}` rows.
- `rt.visibility_rows_cpu(...)` and `rt.visibility_rows(..., backend=...)`
  emit `{observer_id, target_id, visible}` rows.
- `rt.reduce_rows(...)` reduces emitted rows in Python with `any`, `count`,
  `sum`, `min`, or `max`.

Backend boundary:

- OptiX, Embree, and HIPRT have native early-exit any-hit implementations.
- Vulkan and Apple RT remain compatibility any-hit paths through hit-count
  projection.
- `reduce_rows` is a Python standard-library helper, not a native RT backend
  reduction.

## Files Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal410_tutorial_example_check.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal515_public_command_truth_audit.py`
- `/Users/rl2025/rtdl_python_only/tests/goal511_feature_guide_v08_refresh_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal513_public_example_smoke_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal532_v0_8_release_authorization_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal645_v0_9_5_release_package_test.py`

Release package files created:

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/tag_preparation.md`

## Validation

Focused public release-doc and example tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test tests.goal532_v0_8_release_authorization_test tests.goal645_v0_9_5_release_package_test tests.goal513_public_example_smoke_test tests.goal515_public_command_truth_audit_test -v

Ran 14 tests in 2.679s
OK
```

Public command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```text
valid: true
command_count: 248
public_doc_count: 14
```

Tutorial/example harness:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py --machine local-goal645 --output docs/reports/goal645_tutorial_example_check_2026-04-19.json
```

Result:

```text
65 passed
0 failed
26 skipped
91 total
```

Whitespace audit:

```text
git diff --check
```

Result:

```text
no output
```

Full local release gate after Goal645:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v

Ran 1211 tests in 111.506s
OK (skipped=179)
```

Stale public wording check:

```text
rg -n 'v0\.9\.5 candidate|active v0\.9\.5 candidate|v0\.9\.5 candidate surface|current released version: `v0\.9\.4`|current released version is `v0\.9\.4`' \
  README.md docs/README.md docs/rtdl_feature_guide.md docs/current_architecture.md docs/capability_boundaries.md docs/release_facing_examples.md docs/tutorials/README.md docs/backend_maturity.md docs/features/README.md examples/README.md tests
```

Result:

```text
no stale public-doc matches; only the regression test strings themselves match
inside tests/goal645_v0_9_5_release_package_test.py
```

## Verdict

Codex verdict: ACCEPT.

The public release-facing docs, tutorials, examples, and package now describe a
single consistent v0.9.5 state. No code/doc/flow blocker was found in this
goal. The user subsequently authorized release/tag/push.

## External Reviews

Claude review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal645_claude_review_2026-04-19.md`
- Verdict: ACCEPT.
- Finding: no release-blocking documentation, test, or honesty-boundary issue.

Gemini Flash review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal645_gemini_flash_review_2026-04-19.md`
- Verdict: ACCEPT.
- Finding: reviewed the Goal645 report and public docs; no release-blocking
  doc, test, or honesty-boundary issue.

Final consensus:

- Codex: ACCEPT.
- Claude: ACCEPT.
- Gemini Flash: ACCEPT.
