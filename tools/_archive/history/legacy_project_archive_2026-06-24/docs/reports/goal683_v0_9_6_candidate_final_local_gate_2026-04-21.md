# Goal683: v0.9.6 Candidate Final Local Gate

Status: PASS

Date: 2026-04-21

## Scope

Goal683 records the final local gate after the `v0.9.6` release-candidate
package was added and linked from public docs.

This is still a release-candidate gate only. It is not a tag action.

## Full Local Test

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1271 tests in 116.304s
OK (skipped=187)
```

## Candidate Package Regression

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal682_v0_9_6_release_candidate_package_test -v
```

Result:

```text
Ran 3 tests in 0.000s
OK
```

## Public Command Truth Audit

Command:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py --write
```

Result:

```text
valid: true
command_count: 250
public_doc_count: 14
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

## Mechanical Check

Command:

```text
git diff --check
```

Result:

```text
clean
```

## Updated Candidate Docs

The `v0.9.6` release-candidate package now records the final candidate-state
full-suite result:

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/tag_preparation.md`

## Boundary

- Current public release remains `v0.9.5`.
- `v0.9.6` remains a release candidate and is not tagged.
- Tag/push commands remain held until explicit maintainer authorization.
- No broad DB, graph, full-row, one-shot, GTX 1070 RT-core, AMD GPU, or Apple
  RT full-row speedup claim is made.

## Verdict

PASS.

The `v0.9.6` candidate package has a final local release-gate result:
`1271` tests OK, `187` skips.
