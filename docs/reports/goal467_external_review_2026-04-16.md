# Review of Goal 467: v0.7 External Test Report Response

**Reviewer:** Second-AI (Claude Sonnet 4.6)
**Date:** 2026-04-16
**Verdict: ACCEPT**

---

## Summary

Goal 467 triages two external reports (macOS user correctness report and a Windows
v0.6 audit), applies fixes for the actionable Windows blockers, and provides
validation evidence on both platforms. All blockers identified by the prior REJECT
are now resolved. The goal is accepted.

---

## Evidence Evaluated

### 1. macOS User Correctness Report

`rtdl_user_correctness_test_report_2026-04-16.md` is a genuine user-perspective
independent report with no source access. 179/179 checks pass across
`cpu_python_reference`, `cpu`, and `embree` on macOS Darwin 25.3.0 arm64, Python
3.14.0. Coverage spans all 10 documented workloads from v0.2.0 through v0.6.1.
Cross-backend agreement is verified for every multi-backend workload. The five
behavioral findings (count vs. row-style empty-result contract, Jaccard zero-overlap
rows, BFS dedupe source, triangle deduplication) are correctly classified as
coherent design decisions, not bugs. This report is solid positive evidence.

### 2. Windows v0.6 Audit Report

`rtdl_v0_6_windows_audit_report_2026-04-16.md` identified two real release blockers
against an older v0.6 snapshot: (a) `librtdl_embree.dll` absent or stale, causing
raw `AttributeError` on missing symbols; (b) stale Python API exports missing
`rt.csr_graph`. PostgreSQL/PostGIS baselines on Windows are functional and accepted
as ground-truth scaffolding, not as RTDL Embree validation.

### 3. Code Changes — Verified

**`src/rtdsl/embree_runtime.py`**

- `EMBREE_REQUIRED_SYMBOLS` at lines 54–77: tuple of 22 symbols covering the full
  public Embree surface including the v0.6.1 graph additions
  (`rtdl_embree_run_bfs_expand`, `rtdl_embree_run_triangle_probe`) and the v0.7 DB
  additions (`rtdl_embree_db_dataset_create_columnar`, etc.).
- `_require_embree_symbols()` at lines 3004–3017: raises `RuntimeError` with an
  actionable rebuild message naming the missing symbols and giving the correct
  commands for both Unix (`make build-embree`) and Windows (RTDL_EMBREE_PREFIX +
  RTDL_VCVARS64 path). Does not silently fall through.
- `RTDL_FORCE_EMBREE_REBUILD` at line 3060: honoured before the mtime check,
  enabling explicit rebuilds without manual DLL deletion.

**`src/rtdsl/__init__.py`**

- `csr_graph` imported at line 279, listed in `__all__` at line 428.
- `validate_csr_graph` imported at line 311, listed in `__all__` at line 500.
  Both were already present; no regression possible on Windows API mismatch for
  these two names.

**`tests/goal467_external_report_response_test.py`**

- `test_public_graph_exports_include_csr_constructor`: constructs a CSR graph,
  checks `vertex_count`, asserts both names are in `rt.__all__`. Locks the export
  contract.
- `test_embree_required_symbols_cover_windows_audit_exports`: explicitly asserts
  the four symbols that were missing in the Windows audit (`rtdl_embree_run_fixed_radius_neighbors`,
  `rtdl_embree_run_bfs_expand`, `rtdl_embree_run_triangle_probe`,
  `rtdl_embree_db_dataset_create_columnar`). Correctly targets the audit's findings.

**`Makefile`**

- `build-embree` target present and listed under `make help` public targets. Verified
  in grep output.

### 4. Windows Fresh Current-Branch Retest

The response document's `Validation` section records the fresh Windows retest on
`C:\Users\Lestat\work\rtdl_goal467_current`:

- `py -3 -m unittest tests.goal467_external_report_response_test` → 2 tests, OK.
- `rt.csr_graph(...)` → correct `csr_graph 2` output.
- `build\librtdl_embree.dll` present, 372,224 bytes, dated 04/16/2026.
- `required_symbols 22`, `missing []` — loader gate would pass.
- `rtdl_graph_bfs.py --backend embree` → PASS (expected two BFS rows).
- `rtdl_graph_triangle_count.py --backend embree` → PASS (expected one triangle row).

The interpreter warning (`Could not find platform independent libraries <prefix>`)
is a Windows host environment noise unrelated to RTDL; commands exit successfully
and produce correct output. That classification is appropriate.

The prior REJECT was issued specifically because this retest was pending. It is now
complete and passes.

### 5. Documentation Changes

README, `docs/quick_tutorial.md`, `docs/release_facing_examples.md`, and
`docs/release_reports/v0_7/support_matrix.md` are listed as updated to document
the `build-embree` path and the Windows binary snapshot boundary. These are
scope-appropriate prose changes that communicate the deployment contract to users.

---

## Finding-by-Finding Response Assessment

| ID | Response | Assessment |
|----|----------|------------|
| R467-001 | macOS 179/179 accepted as positive evidence | Correct — no action required. |
| R467-002 | Behavioral semantics, not bugs; docs/familiarization points | Correct classification. All five findings are internally consistent and match the source report. |
| R467-003 | `EMBREE_REQUIRED_SYMBOLS` gate + `RTDL_FORCE_EMBREE_REBUILD` + `make build-embree` + Windows retest | Fix is code-verified and Windows-retested. Blocker resolved. |
| R467-004 | `csr_graph`/`validate_csr_graph` already in `__init__.py __all__`; regression test added | Fix is code-verified. Blocker resolved. |
| R467-005 | PostGIS SRID hygiene classified as external driver issue | Correct — this is a benchmark-driver concern, not an RTDL runtime defect. |
| R467-006 | PostgreSQL/PostGIS baselines accepted as ground-truth scaffolding only | Correct scoping. |

---

## Blockers

None.

---

## Scope Boundary (Not Blockers)

The following are correctly bounded out of this goal and do not prevent acceptance:

- Windows is not the primary v0.7 DB performance-validation platform; Linux remains
  canonical for PostgreSQL and GPU workloads.
- The Windows retest covers the graph/API/Embree deployment surface only; it does
  not validate DB workloads on Windows.
- `optix` and `vulkan` were not tested on the Windows host (Linux GPU only).

These are accurately stated in the "Remaining Boundary" section of the response
document.

---

## Conclusion

All actionable Windows blockers are fixed and retested on the current branch. The
macOS correctness report provides independent positive evidence for the full public
workload surface. Code changes are targeted and verifiable. Goal 467 is
**ACCEPTED**.
