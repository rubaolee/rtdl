# Goal 469: v0.7 DB Attack-Report Intake And Local Gap Closure

Date: 2026-04-16

## Verdict

`ACCEPT` with 2-AI consensus:

- Codex implementation and validation review
- Claude external-style review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal469_external_review_2026-04-16.md`

Goal 469 preserves the new external DB attack report, imports the 105-test
attack suite as a repo-local regression artifact, fixes the local native CPU
empty-table DB edge case, and adds targeted gap-closure tests for the
non-platform gaps identified by the report.

No staging, commit, tag, merge, push, or release action was performed.

## Preserved External Artifacts

- Report copied from `/Users/rl2025/claude-work/rtdl-2026-04-16b/docs/reports/test_v07_db_attack_report_2026-04-16.md` to `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/test_v07_db_attack_report_2026-04-16.md`
- Test artifact copied from `/Users/rl2025/claude-work/rtdl-2026-04-16b/tests/test_v07_db_attack.py` to `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/test_v07_db_attack.py`

The external report states:

- 105/105 tests passed
- 0 failures
- runtime 0.031 s in the external environment
- three initial failures were corrected expected-value mistakes, not library
  defects

## Code Response

The native CPU DB oracle path now returns an empty tuple for empty denormalized
DB inputs before crossing into the C ABI.

Affected file:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`

Rationale:

- the Python reference already has a meaningful empty-input result
- the native C DB ABI requires field/schema information that an empty
  schema-free `DenormTable` payload cannot provide
- returning no rows is the correct bounded workload result for scan,
  grouped-count, and grouped-sum when the input table is empty

## New Local Gap-Closure Tests

Added:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal469_v0_7_db_attack_gap_closure_test.py`

The suite covers:

- float-bound `between` for `conjunctive_scan`
- alternate integer `grouped_sum` value field via `quantity`
- empty denormalized table results for scan/count/sum
- large power-of-two scan boundary at 65,536 rows
- grouped boundary rows at 1 and 1,024 rows
- repeated kernel compilation and failed-compilation context cleanup

## Gap Triage

| External gap | Goal 469 decision |
|---|---|
| live PostgreSQL | Already covered by Linux-only Goals 423/424/429/450/464; not rerun in this local goal. |
| large-table behavior | Locally closed for native CPU oracle with 1, 1,024, and 65,536 row boundaries plus empty-input fast path. |
| float-bound `between` | Locally closed for Python reference and native CPU oracle. |
| native Embree/OptiX/Vulkan on Linux | Already covered by Linux-only Goals 426-430, 450, and 464; not a macOS blocker. |
| multi-field sum | Locally narrowed and closed for alternate integer value fields. Float `grouped_sum` remains outside the first-wave Goal 416 RT backend contract. |
| re-entrant/repeated kernel compilation | Locally closed for repeated successful compilation and failed-compilation context cleanup. |

## Validation

Commands run from `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`:

```text
PYTHONPATH=src:. python3 -m unittest tests.test_v07_db_attack
```

Result:

```text
Ran 105 tests in 0.046s
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal469_v0_7_db_attack_gap_closure_test
```

Result:

```text
Ran 6 tests in 1.139s
OK
```

Combined local regression:

```text
PYTHONPATH=src:. python3 -m unittest tests.test_v07_db_attack tests.goal469_v0_7_db_attack_gap_closure_test tests.goal467_external_report_response_test
Ran 113 tests in 1.078s
OK
```

External-style review:

```text
Claude external review: ACCEPT
No blockers or honesty-boundary concerns.
```

## Honesty Boundary

Goal 469 does not claim a new Linux PostgreSQL or GPU/native backend run. Those
are separate Linux-host gates already recorded in the v0.7 evidence chain.

Goal 469 also does not widen `grouped_sum` to arbitrary float-sum RT backend
support. The first-wave Goal 416 contract remains exactly one group key and one
integer sum field for RT backend grouped-sum lowering.
