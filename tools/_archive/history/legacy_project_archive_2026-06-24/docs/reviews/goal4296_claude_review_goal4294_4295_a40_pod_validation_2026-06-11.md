# Review: Goal4294/4295 A40 Pod Validation and NVCC Probe Fix

Date: 2026-06-11
Reviewer: Claude (claude-sonnet-4-6)
Scope: Read-only critical review per Goal4296 handoff.

---

## Verdict

**`accept-with-boundary`** — both goals pass on all substantive checks. Two
low-severity coverage gaps are noted below; neither invalidates the evidence or
the boundary.

---

## Findings (severity-ranked)

### F1 — Low: Partner-comparison absolute times in report are not directly
verifiable from the top-level artifact summary

**File**: `docs/reports/goal4294_a40_pod_validation_2026-06-11.md` (lines 95–97)
**Artifact**: `large_scale_partner_comparison.json`, `summary.cupy_speedup_vs_numba`

The report presents absolute hot-total seconds ("Grouped suite hot total: CuPy
5.551 s, Numba 11.538 s" / "Compact-mask suite hot total: CuPy 1.415 s, Numba
39.412 s"). The artifact top-level summary stores only the derived speedup
*ratios* — `grouped_suite_hot_total: 2.0784`, `compact_mask_hot_total: 27.845`
— not the raw per-partner totals.

Cross-check: 11.538 / 5.551 ≈ 2.079 ✓ and 39.412 / 1.415 ≈ 27.85 ✓. The
numbers are internally consistent with the artifact ratios. The values
themselves appear to come from the per-suite sub-objects (`grouped_suite`,
`compact_mask_suite`) which are present in the file (confirmed at lines 6546
and 13 of the artifact). However, the test suite
(`tests/goal4294_a40_pod_validation_test.py`, lines 71–73) only asserts that
the speedup ratios are greater than 1.0 — it does not pin the absolute
per-partner totals against the report's stated values. A future regression that
changes the timing numbers without updating the report would not be caught.

**Impact**: The current figures appear correct. The gap is in test coverage, not
claim accuracy.

### F2 — Low: Goal4295 test is a source-text grep, not a runtime assertion

**File**: `tests/goal4295_pod_probe_absolute_nvcc_execution_test.py` (lines
13–18)

`test_probe_executes_discovered_nvcc_path` checks that the source code of
`rtdl_pod_bootstrap_probe.py` contains the expected string literals. This
correctly guards against reintroduction of the old `_run(["nvcc",
"--version"])` pattern, but it does not verify that `probe()` actually passes
the discovered path at runtime (e.g., via `unittest.mock.patch` on
`subprocess.run`). A variable rename (`nvcc_path` → `compiler`) would break the
test even if the logic were correct; conversely, a whitespace/formatting change
that preserved the semantics might pass.

**Impact**: Acceptable for a probe-reporting fix of this scope; the source-text
guard is appropriate as a lightweight regression sentinel.

---

## Question-by-question answers

### Q1: Does the Goal4294 report accurately reflect the copied artifact JSONs?

**Yes.** Every claim in the report was verified against the artifacts:

| Claim | Report | Artifact value | Match? |
|---|---|---|---|
| `all_pass` (scale profile) | `true` | `scale_profile_summary_clean.json` line 2 | ✅ |
| `row_count` (scale profile) | 10 | `summary.row_count` = 10 | ✅ |
| `working_tree_clean` | `true` | `runtime_environment.working_tree_clean` = true | ✅ |
| `git_status_short` | clean | `runtime_environment.git_status_short` = `[]` | ✅ |
| `source_commit_short` | `6a556994` | `runtime_environment.source_commit_short` = `"6a556994"` | ✅ |
| `all_pass` (front door) | `true` | `front_door_hardware_summary.json` line 2 | ✅ |
| `row_count` (front door) | 10 | `summary.row_count` = 10 | ✅ |
| All release/speedup flags | false | All artifacts, every relevant field | ✅ |

Per-row elapsed times in the report table round correctly to the JSON float
values (e.g., hausdorff 1.502 s ↔ 1.5015054841060191 s; spatial_rayjoin 10.780
s ↔ 10.77977124392055 s).

### Q2: Does the accepted scale-profile artifact truly show `all_pass`, 10 rows,
source commit `6a556994`, and a clean remote working tree?

**Yes.** Confirmed in `scale_profile_summary_clean.json` at lines 2145–2160:

```json
"runtime_environment": {
  "git_status_short": [],
  "nvidia_smi": "NVIDIA A40, 565.57.01, 46068 MiB",
  "source_commit": "6a556994a5176a3acc8bad2557c0905caa893898",
  "source_commit_short": "6a556994",
  "working_tree_clean": true
}
```

`all_pass: true` is at line 2 of the same file. The `summary.row_count` is 10
(line 2202) and the `rows` array contains exactly 10 entries. All 10 have
`status: "pass"` and `returncode: 0`.

### Q3: Does the report keep the claim boundary narrow?

**Yes.** The report's Boundary section explicitly excludes all prohibited claim
categories:

> "does not authorize release action, package-install wording, public speedup
> wording, whole-app acceleration wording, broad RT-core wording, paper
> reproduction wording, true-zero-copy wording, AMD performance wording,
> automatic partner selection, or app-specific native-engine logic."

Every artifact JSON independently carries `release_authorized: false`,
`public_speedup_claim_authorized: false`, `broad_rt_core_claim_authorized:
false`, `paper_reproduction_claim_authorized: false`, and
`whole_app_speedup_claim_authorized: false` at all relevant levels. The
partner-comparison result section is correctly scoped to same-contract
partner-continuation evidence with no superiority claim.

The test `test_report_documents_boundary_and_environment` (lines 18–26) guards
all six boundary phrases in the report text via case-insensitive match.

### Q4: Does Goal4295 correctly fix the `nvcc` probe inconsistency?

**Yes.** `scripts/rtdl_pod_bootstrap_probe.py` (line 148) assigns:

```python
nvcc_path = _nvcc_path()
```

and (line 163) executes:

```python
"probe": _run([nvcc_path, "--version"], timeout=10) if nvcc_path else None,
```

`_nvcc_path()` (lines 94–104) first consults `shutil.which("nvcc")` and then
iterates `CUDA_PREFIX_CANDIDATES` checking `prefix / "bin" / "nvcc"` for
existence. The discovered absolute path is used consistently for both the
reported `path` field and the probe execution. The old pattern
`_run(["nvcc", "--version"])` is absent from the script.

The `None`-guard in `CUDA_PREFIX_CANDIDATES` is handled correctly via
`if prefix is None: continue` in `_nvcc_path()`.

### Q5: Are the tests sufficient to prevent report/artifact/probe behavior from
drifting?

**Mostly yes, with the two gaps identified above.**

`goal4294_a40_pod_validation_test.py` provides solid coverage:

- Reads live artifact files (not mocks), so drift in the artifacts would
  immediately fail the tests.
- `test_clean_scale_profile_passes_all_rows_on_clean_tree` pins
  `working_tree_clean`, `git_status_short`, `source_commit_short`, all four
  claim flags, 10-row count, rayjoin row presence, and per-row pass/returncode.
- `test_front_door_hardware_passes_all_rows` pins 10-row count, `all_pass`, and
  all four claim flags.
- `test_large_scale_partner_comparison_is_correctness_clean_and_bounded` checks
  oracle match, one-second floor, empty `subsecond_hot_total_rows`, speedup
  ratios >1.0, and boundary flags.
- `test_short_named_scale_row_artifacts_exist` guards all 10 row files.

The gaps (F1: absolute times not pinned in test; F2: probe test is source-level
grep) do not weaken the core evidence but leave two regression vectors
unguarded.

---

## Summary

Goal4294 produces a complete, accurate A40 validation packet with a properly
narrow claim boundary. Goal4295 correctly addresses the nvcc-path probe
inconsistency by executing the discovered absolute path rather than the bare
`nvcc` command. The test suites adequately guard both. This review does not
authorize a release.
