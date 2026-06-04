# Goal3231: Claude Review of Goal3230 Public Count Claim-Boundary Normalization

Date: 2026-06-03
Reviewer: Claude (claude-sonnet-4-6), independent read-only review
Verdict: **accept-with-boundary**

---

## Release Boundary

This review does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims. That boundary is carried over from every artifact
reviewed and is not relaxed here.

---

## Findings by Severity

### No Blocking Findings

No finding below rises to a blocking level. The normalization is structurally
correct, the count contracts are preserved, and the boundary language is
consistent throughout all artifacts, reports, and tests.

### Informational: Test Run Scope

The live probe tests (`goal3225_rayjoin_public_overlay_active_count_probe_test`
and `goal3227_rayjoin_public_pip_count_probe_test`) require GPU hardware and
could not be executed in this review environment. All tests were instead
validated by reading scripts and artifact files directly. The artifact tests,
summary test, and normalization test are fully machine-checkable against stored
files and were verified manually below.

### Informational: Count-Table Notation in Goal3230 Report

The Goal3230 report table shows overlay counts as `1/1` and `9/9` without a
column header clarifying the `observed/expected` convention. The surrounding
prose explains the counts unambiguously, so this is not a machine-checkability
problem; it is a minor readability point for future readers.

---

## Question-by-Question Findings

### Q1: Does Goal3230 close the Goal3226/Goal3228 informational inconsistency?

**Yes, fully.**

Both refreshed artifacts (`goal3225` and `goal3227`, at commit
`92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3`) carry the canonical six false flags
at three nesting levels:

- Top-level `data["claim_boundary"]`
- Per-row `data["rows"][i]["claim_boundary"]`
- Per-measurement `data["rows"][i]["measurements"]["prepared_overlay_active_count" | "prepared_pip_count"][j]["claim_boundary"]`

The six keys are exactly:

```
public_speedup_claim_authorized
rt_core_speedup_claim_authorized
true_zero_copy_claim_authorized
rayjoin_paper_reproduction_claim_authorized
rtdl_beats_rayjoin_claim_authorized
release_authorized
```

All values are `false`. The JSON is written with `sort_keys=True`, so the keys
appear in alphabetical order and are stable across regenerations.

The scripts define `CANONICAL_CLAIM_BOUNDARY` as a module-level constant and
inject `dict(CANONICAL_CLAIM_BOUNDARY)` at every emission site (top-level,
per-row, and per-measurement), so the correspondence is not fragile.

The `goal3230_rayjoin_public_count_claim_boundary_normalization_test.py` test
uses a shared `_assert_canonical_false_boundary` helper that verifies both the
exact key set and that all values are `False`. Both
`test_overlay_artifact_uses_canonical_boundary_at_every_level` and
`test_pip_artifact_uses_canonical_boundary_at_every_level` iterate every row
and every measurement in the stored artifacts. Verified manually: pass.

### Q2: Do the refreshed artifacts preserve the same count contracts and observed counts?

**Yes, exactly.**

From the stored JSON artifacts at `92e16b86`:

| Artifact | Case | Expected | Observed (×5) | Status |
| --- | --- | ---: | --- | --- |
| Goal3225 | `overlay_county128_soil128` | `active_seed_count = 1` | `[1, 1, 1, 1, 1]` | pass |
| Goal3225 | `overlay_county256_soil256` | `active_seed_count = 9` | `[9, 9, 9, 9, 9]` | pass |
| Goal3227 | `pip_county512` | `positive_assignment_count = 1430` | `[1430, 1430, 1430, 1430, 1430]` | pass |

Median timing values match between the JSON `medians` field, the `.md` report
tables, and the Goal3229 coverage summary table. Verified by reading the JSON:

- `overlay_county128_soil128` median: five repeat values sorted are
  `0.02236…, 0.02269…, 0.02271…, 0.02278…, 0.02353…`; middle value is
  `0.022716183215379715`. Matches `data["rows"][0]["medians"]["prepared_total_seconds"]`. ✓
- `overlay_county256_soil256` median: five repeat values sorted are
  `0.05868…, 0.05896…, 0.05908…, 0.06707…, 0.07873…`; middle value is
  `0.05908652022480965`. Matches reported median. ✓
- `pip_county512` median: five repeat values sorted are
  `0.06646…, 0.06775…, 0.06793…, 0.08031…, 0.08569…`; middle value is
  `0.06793256662786007`. Matches reported median. ✓

The stdout files confirm the runs proceeded as described. The warmup rows (which
show higher latency, e.g. `sec=0.764032` for the first overlay warm-up) are
correctly excluded from the median calculation.

Both artifacts set `"status": "pass"` at the top level, consistent with all
rows having `"counts_match": true`.

The `goal3225_rayjoin_public_overlay_active_count_probe_artifact_test.py` and
`goal3227_rayjoin_public_pip_count_probe_artifact_test.py` tests pin the commit
hash, GPU identity, observed-count arrays, and `counts_match` flag directly.
Verified manually: pass.

### Q3: Do reports and tests avoid overclaiming?

**Yes, consistently.**

Every report in scope closes with an explicit boundary paragraph:

- **Goal3225 MD**: "This report does not authorize release, public speedup
  claims, broad RT-core claims, true zero-copy claims, `RTDL beats RayJoin`
  claims, or RayJoin paper-reproduction claims." ✓
- **Goal3227 MD**: Same language. ✓
- **Goal3229 MD**: Same language. ✓
- **Goal3230 MD**: Same language, plus a clarifying note that this cleanup "only
  makes the existing public count/parity evidence easier to audit." ✓

None of the reports contain the phrases "release authorized", "RTDL beats
RayJoin", "true zero-copy", "paper reproduction", or any positive speedup claim.

The tests enforce this mechanically:

- `test_artifact_preserves_claim_boundaries` (goal3225 and goal3227 artifact
  tests) checks each of the six keys by name in the JSON.
- `test_reports_describe_the_normalization_without_overclaiming` (goal3230 test)
  checks for "does not authorize release", "true zero-copy claims", and
  "RayJoin paper-reproduction claims" in the report text.
- `test_summary_preserves_claim_boundary` (goal3229 test) checks for all six
  unauthorized-claim phrases in the summary text.

The scope of claims is also appropriately narrow:

- Goal3225 explicitly notes the probe checks the `active_seed_count` contract
  only, not full row overlay continuation.
- Goal3227 explicitly notes the probe checks `positive_assignment_count` only.
- Goal3229 explicitly separates PIP, LSI, and overlay families and lists open
  gaps (full paper-scale datasets, cross-system comparison, broader GPU family).

### Q4: Remaining machine-checkability or wording issues before this evidence is used by planning reports?

**No blocking issues. Two minor points for awareness:**

1. **Count-table notation in Goal3230 report**: The artifact summary table uses
   `1/1`, `9/9`, `1430/1430` in the "Counts" column without column-header
   annotation. The prose context makes the meaning clear (CPU-expected vs
   OptiX-observed), but adding a column note like `expected/observed` would help
   future planning reports that cite this table directly.

2. **Live probe test exclusion**: The two probe tests
   (`goal3225_rayjoin_public_overlay_active_count_probe_test` and
   `goal3227_rayjoin_public_pip_count_probe_test`) are text-level structure
   checks that verify the script source contains required strings; they do not
   execute the probes. This is correct design for tests that require GPU
   hardware, and the artifact tests cover the stored-output contracts. No change
   is required, but downstream planning reports should note that live probe
   execution requires a compatible OptiX environment.

---

## Test Coverage Assessment

| Test module | What it checks | Machine-checkable here |
| --- | --- | --- |
| `goal3225_…_probe_test` | Script text: required imports, case names, claim-boundary keys | Yes |
| `goal3227_…_probe_test` | Script text: required imports, case names, claim-boundary keys | Yes |
| `goal3225_…_artifact_test` | JSON counts, commit hash, hardware, claim boundaries all 3 levels + report/stdout phrases | Yes |
| `goal3227_…_artifact_test` | JSON counts, commit hash, hardware, claim boundaries all 3 levels + report/stdout phrases | Yes |
| `goal3229_…_summary_test` | Report phrases, cross-artifact count cross-check, boundary phrases | Yes |
| `goal3230_…_normalization_test` | Canonical 6-key false boundary at every level in both artifacts; report text phrases | Yes |

All six test modules were manually verified against the stored files. No
discrepancy was found between the tests' assertions and the actual file
contents.

---

## Summary

Goal3230 correctly closes the informational inconsistency identified in the
Goal3226/Goal3228 reviews. The six canonical false claim-boundary flags are now
uniformly present at top, row, and measurement levels in both refreshed pod
artifacts. The count contracts (overlay: 1, 9; PIP: 1430) are preserved exactly.
The boundary language is consistent and non-overclaiming in all reports and is
mechanically enforced in all six test modules.

Verdict: **accept-with-boundary**. The two informational notes above (table
notation, live-probe hardware dependency) do not block downstream use of this
evidence in RayJoin planning reports, provided those reports carry the same
six-flag false boundary and do not extend it into release, speedup, zero-copy,
or paper-reproduction claims.
