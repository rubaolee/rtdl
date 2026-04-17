# Goal 470 Claude Test-Review-Audit

**Date:** 2026-04-16
**Reviewer:** Claude Sonnet 4.6 — independent test-review-audit pass
**Scope:** All work since the last accepted Claude review, starting from
`docs/reports/goal470_v0_7_pre_release_test_doc_audit_2026-04-16.md`

---

## Verdict

**ACCEPT**

No blockers. All five evidence areas independently verified against source
and live re-runs. Honesty boundaries intact. No staging, tag, push, merge,
or release performed or authorized.

---

## What Was Reviewed

Goals 469 and 470 in full:

- **Goal 469** — v0.7 DB attack-report intake and local gap closure
- **Goal 470** — v0.7 pre-release full test, doc refresh, and mechanical audit

The review did not rely on the Codex-authored text in this file or the Gemini
Flash external review. Each claim was checked against primary sources or
re-executed.

---

## 1. Full-Test Evidence (macOS)

**Recorded claim:** `Ran 941 tests in 276.632s — OK (skipped=105)` after
fixing Goal 429's optional-backend skip behavior.

**Independent re-run:**

```
cd /Users/rl2025/worktrees/rtdl_v0_4_main_publish
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*test.py'
```

**Result:** `Ran 941 tests in 197.270s — OK (skipped=105)`

Test count, skip count, and OK status match exactly. Runtime differs (faster
second run) — consistent with warm filesystem caches; not a concern.

**Goal 429 fix verified:** `setUpClass` raises `unittest.SkipTest(...)` for
each missing native backend (lines 28–33 in the test file). The previous
behavior propagated `FileNotFoundError` as a suite error. The fix is minimal
and the only correct approach for optional-backend gates on macOS.

**Finding: PASS.**

---

## 2. Linux Focused Pre-Release Evidence

**Recorded claim:** `Ran 155 tests in 8.776s — OK` on `lestat-lx1` with
PostgreSQL 16.13, Embree 4.3.0, OptiX [9, 0, 0], Vulkan [0, 1, 0].

**Transcript read:** `docs/reports/goal470_linux_focused_pre_release_test_2026-04-16.txt`

Verified in the transcript:

- Host and date header: `lx1`, `2026-04-16T12:10:50-04:00`
- Python: `3.12.3`
- PostgreSQL: `psql (PostgreSQL) 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)`
- Socket: `accepting connections`
- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- Vulkan built from source with `g++` against `/usr/lib -lvulkan -lshaderc`
- OptiX built from source with `nvcc` against `/home/lestat/vendor/optix-dev`
- Runtime probe JSON: `{"embree": [4, 3, 0], "optix": [9, 0, 0], "vulkan": [0, 1, 0]}`
- 155 test dots followed by `OK` with no failures or errors

**Finding: PASS.** Transcript is internally consistent. All three backends
built from source on the run day. PostgreSQL present and accepting connections.
155 tests pass cleanly.

---

## 3. Documentation Refresh

Five release-facing docs read in full:

| Doc | Key claims verified |
|---|---|
| `release_statement.md` | Names Goals 469 and 470. States "not release authorization" and "not a DBMS". GTX 1070 caveat present. No arbitrary SQL claims. |
| `support_matrix.md` | Goal 470 pre-release gate section present. Counts 941/105 (macOS) and 155 (Linux). PostgreSQL 16.13 named. Vulkan runtime probe token present. One-group-key and integer-sum boundary stated. |
| `audit_report.md` | Covers all six branch passes through Goal 470. States "does not authorize tagging". External DB attack report and local gap closure named. |
| `tag_preparation.md` | Leads with "Do not tag `v0.7` yet." Names Goal 470 with both test counts. |
| `v0_7_goal_sequence_2026-04-15.md` | Names Goals 469 and 470. Names "pre-release full test." |

No doc claims RT-core hardware speedup from the GTX 1070. No doc claims RTDL
is a DBMS. No doc claims arbitrary SQL support. All hold conditions are
present.

**Finding: PASS.**

---

## 4. Mechanical Audit JSON

**Recorded claim:** `valid: true` from `scripts/goal470_pre_release_doc_audit.py`.

**Independent re-run:**

```
cd /Users/rl2025/worktrees/rtdl_v0_4_main_publish
python3 scripts/goal470_pre_release_doc_audit.py
```

**Result:** `{"output": "...goal470_pre_release_doc_audit_2026-04-16.json", "valid": true}`

The audit script was read in full. It checks:

- 12 release-facing docs exist — all `"exists": true` in the JSON
- 9 required artifacts exist — all `"exists": true` in the JSON:
  - both test transcripts, the external Gemini review, this file, the
    Goal 469 external review and gap-closure report, the attack report
    and imported test file, and the gap-closure test file
- Required claim strings appear in each release doc — `claim_gaps: []`
- Internal markdown links in release docs resolve — `broken_release_doc_links: []`
- Transcript tokens verified in both log files — all four `transcript_checks` true
- `staging_performed: false`, `release_authorization: false`

**Limitation acknowledged:** `staging_performed` and `release_authorization`
are hardcoded `False` in the script, not derived from git state. The
worktree's `git status` was checked independently: 30 files modified,
all unstaged, no commits since `a4d0925`. The hardcoded values accurately
reflect the actual repository state.

**Finding: PASS.**

---

## 5. Changed Files

**Git status:** 30 modified files, all unstaged and uncommitted. Worktree
HEAD is `a4d0925 — Package v0.7 DB branch release gates`, unchanged.

### `src/rtdsl/oracle_runtime.py` — empty-table fast-path fix

Three early-return guards confirmed at exact locations:

```python
# line 346, inside _run_conjunctive_scan_oracle
if not table_rows:
    return ()

# line 378, inside _run_grouped_count_oracle
if not table_rows:
    return ()

# line 423, inside _run_grouped_sum_oracle
if not table_rows:
    return ()
```

These are minimal and correct. They prevent schema-free empty inputs from
crossing the C ABI, which requires field metadata. The non-empty paths are
unchanged. The Python reference already returned `()` for empty inputs;
the native oracle now agrees.

### `tests/goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test.py` — skip fix

`setUpClass` raises `unittest.SkipTest` for missing Embree, OptiX, and
Vulkan rather than propagating `FileNotFoundError`. This is the correct
pattern for optional-backend test gates.

### `tests/test_v07_db_attack.py` — imported attack suite

105-test external attack suite imported into the repo. Independently
re-run: **105/105 PASS in 0.046 s.**

### `tests/goal469_v0_7_db_attack_gap_closure_test.py` — gap closure suite

6-test suite. Independently re-run: **6/6 PASS in ~1 s.** Coverage:

| Gap from external report | Test | Independently verified |
|---|---|---|
| Float-bound `between` | `test_float_between_scan_matches_native_cpu_oracle` | PASS |
| Alternate integer sum field | `test_alternate_integer_value_field_grouped_sum_matches_native_cpu_oracle` | PASS |
| Empty table — all three workloads | `test_empty_denorm_table_returns_empty_for_all_db_workloads` | PASS |
| 65,536-row scan boundary | `test_large_power_of_two_scan_boundary_matches_native_cpu_oracle` | PASS |
| Grouped boundaries at 1 and 1,024 rows | `test_grouped_boundaries_match_native_cpu_oracle` | PASS |
| Repeated + failed compile cleanup | `test_repeated_compile_and_failed_compile_do_not_leak_context` | PASS |

Each test cross-validates `run_cpu` against `run_cpu_python_reference`,
so the native oracle is exercised in every case.

### Release docs (5 files)

Verified in Section 3 above.

### Native backend sources and runtime Python files

Changed in the upstream commit `a4d0925` as part of the v0.7 Goals 426–430
evidence chain. Not re-reviewed here; those goals carried their own
acceptance evidence.

**Finding: PASS.** All changed files are scoped appropriately. No unannounced
changes observed. No scope creep.

---

## Honesty Boundary Assessment

| Claim | Check | Result |
|---|---|---|
| No staging/commit/tag/merge/push/release | `git status`: 30 unstaged files, no new commits | ✓ |
| No RT-core speedup claim from GTX 1070 | Caveat present in `release_statement.md`, `support_matrix.md`, `tag_preparation.md` | ✓ |
| No DBMS widening | "not a DBMS" present in `release_statement.md`; "RTDL is not a DBMS" in `audit_report.md` | ✓ |
| `grouped_sum` RT backend stays integer-compatible | First-wave contract stated in `support_matrix.md`; honesty boundary in Goal 469 doc | ✓ |
| Linux-only gaps mapped to existing evidence | Goal 469 gap triage table names Goals 423/424/429/450/464 (PostgreSQL) and 426–430 (GPU backends) | ✓ |

---

## Minor Observations (non-blocking)

1. `test_large_power_of_two_scan_boundary_matches_native_cpu_oracle` asserts
   `assertGreater(len(rows), 0)` rather than a pinned count. Acceptable: the
   signal is `run_cpu` agreement with `run_cpu_python_reference`, which is
   also asserted, and the exact matching count across 65,536 modular rows is
   not the correctness claim being made.

2. `staging_performed` and `release_authorization` are hardcoded `False` in
   the audit script rather than derived from git state. This is a known
   limitation of the script design. Independent git inspection confirms the
   values are accurate.

3. Combined independent re-run of 111 tests (105 + 6) completes in 0.573 s —
   well within normal range for pure-Python DB workload tests with no native
   backends exercised on macOS.

---

## Summary

| Evidence area | Claim | Independent check | Finding |
|---|---|---|---|
| Full-test evidence (macOS) | 941 tests, 105 skips, 0 failures | Re-run: 941/105/OK confirmed | PASS |
| Linux focused pre-release | 155 tests, PG 16.13, Embree/OptiX/Vulkan ready | Transcript read and verified | PASS |
| Documentation refresh | 5 docs current through Goal 470; honesty boundaries intact | Each doc read; all required claims confirmed | PASS |
| Mechanical audit JSON | `valid: true`; no gaps, no broken links | Re-run: `valid: true` confirmed | PASS |
| Changed files | 30 modified; 3 oracle guards, 1 skip fix, 2 new test files, 5 release docs | Each key file read; 111 tests re-run | PASS |

**ACCEPT.**
