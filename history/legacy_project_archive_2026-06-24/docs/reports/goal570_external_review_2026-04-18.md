# Goal 570 External Review: v0.9 Final Pre-Release Gate

Date: 2026-04-18

Reviewer: Claude (Sonnet 4.6), external consensus role

Verdict: **ACCEPT**

Blockers: none

---

## What Was Reviewed

- `docs/reports/goal570_v0_9_final_pre_release_test_doc_audit_2026-04-18.md`
- `docs/reports/goal570_hiprt_correctness_matrix_linux_2026-04-18.json`
- `docs/reports/goal570_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/capability_boundaries.md`
- `docs/release_reports/v0_9/README.md`
- `docs/release_reports/v0_9/support_matrix.md`

---

## Findings

### JSON Artifacts

Both Goal 570 JSON files exist and match the summaries reported in the audit:

- HIPRT correctness matrix: 18 workloads, all `PASS`, 0 fail, 0 not_implemented,
  0 hiprt_unavailable. Every entry carries exact row-count parity against the
  cpu_python_reference. Workload list in the JSON matches the 18-workload matrix
  declared in the support matrix.
- Cross-backend parity/performance matrix: 18 workloads × 4 backends = 72 cells,
  all `PASS`, 0 fail, 0 backend_unavailable. The JSON carries a
  `honesty_boundary` field that correctly characterizes the timing as
  startup/JIT/build overhead suitable only for release-smoke availability and
  parity, not throughput.
- `repeats: 1` is recorded in the perf JSON. Min/median/max are therefore
  identical for every cell. This is consistent with the audit's explicit
  statement that the matrix is a one-repeat smoke comparison, not a production
  benchmark. No concern.

### Test Gate

232 tests passing on macOS and 232 passing on the fresh Linux checkout
(`lestat-lx1`). Count agreement across both environments is a clean signal.
Neither run produced skips or errors that would suggest an environment-specific
gap.

### Documentation Consistency

All reviewed public documents are consistent with each other and with the audit
report:

- `README.md`: correctly states `v0.8.0` as current released version; HIPRT is
  described as "active v0.9 backend candidate"; all HIPRT non-claims (no AMD GPU,
  no RT-core speedup, no CPU fallback) are present.
- `docs/rtdl_feature_guide.md`: the fix described in the audit is confirmed.
  The file now reads "The current released state is `v0.8.0`" with v0.9 as the
  active candidate, not as a released line. The stale v0.7.0 wording is gone.
- `docs/capability_boundaries.md`: HIPRT non-claims are explicit and match all
  other documents. Boundaries on DB, SQL, AMD GPU, and RT-core are all stated
  directly.
- `docs/release_reports/v0_9/support_matrix.md`: correctly reads "Status: active
  candidate, not released as `v0.9.0`"; performance boundary section names
  fixture size, host GPU, and overhead composition for every prepared-path
  milestone (Goal 565-568). No performance claim is presented as a throughput
  benchmark.
- `docs/release_reports/v0_9/README.md`: Goal 570 is listed as the final gate
  step, pending external review. The evidence chain is complete.

No stale v0.7.0 wording was found in any reviewed file. No broken internal
cross-references were observed.

### Flow Audit

The evidence chain from Goal 560 through Goal 570 is coherent and traceable:

- Goal 560: 18-workload HIPRT matrix baseline
- Goals 562–564: pre-release test gate, documentation audit, release-candidate
  flow audit (each with external review)
- Goals 565–568: prepared HIPRT performance rounds covering ray/triangle, 3D
  fixed-radius NN, graph CSR, and bounded DB table reuse
- Goal 569: post-Goal568 gate refresh
- Goal 570: final total test/doc/audit gate (this review closes it)

Goals 568 and 569 carry Codex, Claude, and Gemini Flash ACCEPT verdicts as
stated in the audit. The chain is complete.

### Honesty Boundaries

The audit's stated non-claims are all verified in the source documents:

- No AMD GPU validation claimed or implied.
- No RT-core speedup claim from the GTX 1070 CUDA path.
- No HIPRT CPU fallback claimed.
- Performance timing is explicitly bounded to startup/JIT/build overhead on
  small fixtures.
- DB results are bounded repeated-query results against a specific PostgreSQL
  configuration, not a general DBMS or arbitrary-SQL claim.
- `v0.9.0` is not asserted as released anywhere in the reviewed documents.

---

## Assessment

The Goal 570 audit is coherent, honest, and release-ready. All test gates pass.
All JSON artifacts exist and match reported summaries. The feature guide fix is
confirmed. No stale version wording remains in the reviewed public documents. The
evidence chain is complete and traceable from Goal 560 through Goal 570.

The v0.9 candidate is ready for the final user-controlled release action.

**ACCEPT**
