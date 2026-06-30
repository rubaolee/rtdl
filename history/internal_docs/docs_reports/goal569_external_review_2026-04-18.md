# Goal 569 External Review: v0.9 Post-Goal568 Release-Gate Refresh

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6

**Verdict: ACCEPT**

**Blockers: None**

---

## Purpose Coherence

PASS.

Goal 569's stated purpose is correct and necessary: Goal 568 materially changed
the v0.9 candidate state (adding prepared HIPRT DB table reuse for
`conjunctive_scan`, `grouped_count`, `grouped_sum`), so the prior Goal 562/563/564
pre-release gate is no longer sufficient as the _latest_ gate. Goal 569 provides
a fresh gate document that incorporates Goal 568's evidence without silently
rewriting the earlier trail. That is the right approach.

---

## Test Gate

PASS.

Two full-suite test runs are cited with consistent counts:

- macOS local: 232 tests, 64.168s, OK
- Linux backend-capable (`/tmp/rtdl_goal568`): 232 tests, 147.598s, OK

The focused Goal 568 suite (`goal568_hiprt_prepared_db_test` +
`goal559_hiprt_db_workloads_test`) is cited separately: 14 tests, 6.873s, OK.
Test count consistency (232 in both discovery runs) confirms no silent drops. The
focused suite covers the new prepared paths plus the existing one-shot regression
guard, which is the correct scope for the change.

---

## Performance Gate

PASS — comparison is honest and correctly bounded.

Goal 569 references the Goal 568 Linux perf artifact
(`goal568_hiprt_prepared_db_perf_linux_2026-04-18.json`) and restates the table
accurately. The interpretation boundary in both the Goal 569 report and the
support matrix is sound:

- The claim is bounded to a 100k-row synthetic fixture with no RT cores.
- HIPRT prepared query medians (1.8–2.4ms) beat PostgreSQL indexed query medians
  (3.3–11.2ms) on this fixture; the comparison is fair because both sides have a
  separately measured one-time setup phase.
- No claim is made that RTDL is a DBMS or faster than PostgreSQL in general.
- PostgreSQL remains the stated baseline for SQL semantics, persistence,
  concurrency, joins, and unbounded tables.

No overclaiming detected.

---

## Documentation Gate

PASS.

The audited docs (README.md, docs/README.md, current_architecture.md,
capability_boundaries.md, quick_tutorial.md, release_facing_examples.md,
rtdl_feature_guide.md, tutorials/README.md, examples/README.md,
release_reports/v0_9/README.md, release_reports/v0_9/support_matrix.md) were
spot-checked. Key findings:

- `README.md` now includes "prepared bounded DB table reuse" under `prepare_hiprt`.
- `capability_boundaries.md` (line 111) correctly states: "prepared bounded DB
  table reuse" as a current positive, not future work.
- `docs/release_reports/v0_9/support_matrix.md` cites Goal 568 evidence and
  includes accurate per-workload timing numbers and interpretation limits.
- No stale "DB reuse is future work" or "does not yet cover DB" wording was found
  in the public-facing docs. The grep audit result in the Goal 569 report is
  consistent with what spot inspection confirms.
- Markdown link check: 12 files, 0 bad links.

The support matrix `Prepared API Status` section names all four prepared-path
families (ray/triangle, fixed-radius NN, graph CSR, bounded DB) correctly and
without overpromise.

---

## Flow Gate

PASS.

Goal 568 has documented 3-AI consensus: Codex ACCEPT (in the Goal 568 Codex
report), Claude ACCEPT (goal568_external_review_2026-04-18.md), and Gemini Flash
ACCEPT (goal568_gemini_flash_review_2026-04-18.md). All three files are present
on disk and their verdicts are unambiguous.

Goal 569 correctly positions itself as superseding Goals 562/563/564 as the
_latest_ gate while preserving the earlier trail as valid historical evidence.
This is honest bookkeeping — it does not erase the prior gate, it extends it.

The evidence chain from Goal 560 (18-workload parity matrix) through Goals
565/566/567 (prepared ray, NN, graph) through Goal 568 (prepared DB) through
Goal 569 (gate refresh) is continuous and traceable.

---

## Known Errors and Limits

Goal 569 correctly lists no release-blocking code, doc, or flow errors. The
non-blocking limits are accurately characterized:

- Host-side aggregation for grouped workloads.
- Fixed string domain encoding.
- Synthetic 100k-row fixture, not a general DB benchmark.
- No RT cores on the test GPU (GTX 1070).
- No AMD GPU validation, no HIPRT CPU fallback.

These are scoped disclosures, not omissions.

---

## Summary

The post-Goal568 v0.9 release gate is coherent and honest. The test evidence is
consistent across macOS and Linux, the focused regression suite covers the new
prepared DB paths, the performance comparison is correctly bounded and
non-overclaiming, the public docs have been updated to remove stale "future work"
language, and the 3-AI consensus on Goal 568 is documented and verifiable. Goal
569 adds no new code — it is a gate document — and it fulfills that role
correctly.

**ACCEPT. No blockers.**
