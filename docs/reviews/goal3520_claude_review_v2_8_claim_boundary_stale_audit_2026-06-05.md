# Claude Review: Goal3520 v2.8 Claim-Boundary and Stale-Doc Audit

Date: 2026-06-05

Reviewer: Claude (independent read-only review)

Verdict: **accept-with-boundary**

---

## Scope

Files reviewed:

- `docs/reports/goal3520_v2_8_claim_boundary_and_stale_doc_audit_2026-06-05.md`
- `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py`
- `docs/research/future_version_to_do_list.md`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- Active learner Markdown surface (root README, docs/README, docs/learn, docs/tutorials, research_benchmark READMEs)

Independent scans performed:

- Ripgrep sweep for stale version wording in docs/learn, docs/tutorials, and research_benchmark README files: zero matches
- Root README sweep: only matches in History and Audit Trail section (lines 200–201) — allowed by test logic
- Ripgrep sweep for positive authorization phrases across all .md files: no matches in the active learner surface
- Grep for `v2_[56]` or `v2\.(?:5|6|x)` in examples/v2_0/research_benchmarks/**/*.py: 4 files, all in ALLOWED_VERSIONED_PYTHON_FILES

---

## Question-by-Question Findings

### Q1: Does Goal3520 correctly close stale user-facing v2.x/v2.5 wording without renaming compatibility helpers unsafely?

**Yes, correctly scoped.**

All five modified Python files show v2.8 in user-facing CLI/argparse descriptions:

- `rtdl_hausdorff_v2_user_benchmark.py` line 877–880: "User-level v2.8 Hausdorff benchmark..."
- `rtdl_hausdorff_v2_language_lab.py` line 326: "RTDL v2.8 Hausdorff language-level comparison lab."
- `rtdl_rt_dbscan_benchmark_app.py` line 1488: "RT-DBSCAN-inspired RTDL v2.8 benchmark app."
- `rtdl_rayjoin_v2_spatial_join_app.py` line 462: "...the serious v2.8 benchmark route..."
- `rtdl_hausdorff_v2_function.py` line 187: "Return the current warmed default for adaptive grouped RT traversal." (no stale version label)

Internal helper names were correctly left untouched. The most notable is `RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION = "rtdl.rayjoin.v2_6.numba_compact_mask_preview.v1"` at line 47 of the rayjoin app — this is a protocol schema string identifier used in artifact tagging, not a user-facing label. Renaming it would break artifact compatibility. The decision to quarantine rather than rename is sound.

### Q2: Is the active learner Markdown surface v2.8-current and free of overclaims?

**Yes, cleanly bounded.**

Independent ripgrep scans confirm:

- `docs/learn/*.md`: zero stale version matches
- `docs/tutorials/*.md`: zero stale version matches
- `examples/v2_0/research_benchmarks/**/*.md` (research benchmark READMEs): zero stale version matches
- `docs/README.md`: refers to v2.8 throughout; no stale version wording
- `README.md`: v2.x appears only in the History And Audit Trail section (lines 200–201, historical links), which is explicitly allowed

No positive authorization phrases (`v2.8 release authorized`, `public speedup claim authorized`, `true zero-copy authorized`, `full rayjoin reproduction is authorized`, `rtdl beats rayjoin is authorized`, `automatic partner selection is enabled`, `pip install -e .`) appear anywhere in the active learner Markdown surface.

Negative boundary language is preserved and intact. The root README (line 17–19) explicitly states: "do not read any current doc as a package-install promise, automatic partner-selection promise, general device-residency/zero-copy product claim, or broad speedup claim."

### Q3: Are remaining v2_5/v2_6 Python names legitimately quarantined as compatibility/protocol debt with adequate future-work documentation?

**Yes, with a minor note.**

The independent grep found exactly 4 Python files containing `v2_[56]` patterns:

1. `rtdl_rayjoin_v2_spatial_join_app.py` — in allowed list ✓
2. `rtdl_triangle_counting_benchmark_app.py` — in allowed list ✓
3. `rtdl_raydb_style_benchmark_app.py` — in allowed list ✓
4. `rtdl_hausdorff_distance_app.py` — in allowed list ✓

`rtdl_librts_spatial_index_benchmark_app.py` is in the ALLOWED_VERSIONED_PYTHON_FILES set but contains no v2_5/v2_6 patterns. This is a conservative allowlist entry — harmless.

`docs/research/future_version_to_do_list.md` now contains the "Legacy Versioned Helper Names" section with explicit mention of `v2_5` and `v2_6` names, rationale, and a clear non-blocking boundary statement. The deferral reasoning is sound: these are protocol/compatibility identifiers embedded in artifact schemas, not user-facing APIs that would mislead learners.

**Minor note**: The future-work entry says "Boundary: do not rename public or semi-public helper functions casually. Add aliases and migration tests first." This is adequate guidance for the future migration goal.

### Q4: Is tests/goal3520_v2_8_claim_boundary_stale_audit_test.py a meaningful fail-closed guard?

**Yes, with two minor coverage gaps.**

The four test cases cover the primary risk vectors:

- `test_active_markdown_keeps_old_versions_outside_history`: Blocks v2.3, v2.5, v2.6, v2.7, v2.x, and "release package" from the active Markdown surface. The history-section carve-out is logic-correct (checks for `"History And Audit Trail"` in text before the match).
- `test_positive_overclaim_phrases_are_absent`: Blocks 7 specific positive authorization phrases in active Markdown.
- `test_versioned_python_residuals_are_quarantined`: Enforces that only the 5 known files can contain v2_5/v2_6 Python patterns. Fail-closed: any new file with those patterns will fail immediately.
- `test_future_work_records_legacy_helper_names`: Ensures the migration debt is documented.

**Gap 1 (low risk)**: The `_active_markdown_files()` function uses `directory.glob("*.md")` and `directory.glob("*/README.md")`, not `directory.rglob("*.md")`. Files nested more than two levels deep (e.g., `docs/learn/subdir/file.md`) would not be scanned. Based on the flat structure of docs/learn and docs/tutorials, this gap appears low-risk in practice, but a future recursive scan would be more defensive.

**Gap 2 (low risk)**: The forbidden-phrase list is enforced only against Markdown, not Python source. However, the Python files themselves carry explicit `claim_boundary` dicts with `False` values at every route, so the risk of an unguarded positive claim slipping through Python is low.

Neither gap is material enough to block acceptance of this goal.

### Q5: Does this goal authorize release or public claims in any way?

**No. It does not.**

The goal report header explicitly states: "Status: internal closeout audit; not release authorization."

Every claim_boundary dict in the Python benchmark files explicitly records:

- `release_authorized: False` (or `v2_0_release_authorized: False`, `v2_8_release_authorized: False`)
- `public_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False` (or `full_rayjoin_reproduction: False`)
- `rtdl_beats_rayjoin_claim_authorized: False` (or `rtdl_beats_rayjoin_claim_authorized: False`)
- `true_zero_copy_claim_authorized: False`

The goal's self-verdict is `accept-with-boundary`, which this review confirms.

---

## Summary

Goal3520 correctly closes stale user-facing version wording in visible CLI/docstring paths across five benchmark Python files without touching compatibility protocol names. The active learner Markdown surface is v2.8-current and free of release-package, broad-speedup, true-zero-copy, full-RayJoin-reproduction, hidden-partner-selection, and app-specific-native-engine overclaims. Legacy versioned helper names are properly quarantined with documented future migration debt. The test is a meaningful fail-closed guard with two minor coverage gaps that do not constitute material risk at this stage.

The remaining boundary is unchanged from the goal's own assessment: legacy versioned helper names in Python source are compatibility/protocol debt deferred to a later alias/migration goal.

**Verdict: `accept-with-boundary`**

The boundary: this is an internal closeout audit only. It does not authorize release, public speedup wording, broad RT-core wording, true-zero-copy claims, package-install promises, paper-reproduction claims, hidden partner selection, or app-specific native-engine behavior. That authorization decision requires a separate and distinct gate.
