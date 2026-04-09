**Verdict**

The reorganization is approved. The structural justification is sound, the code fixes are minimal and scope-clean, and the verification is adequate.

**Findings**

- The move from `examples/` to `examples/visual_demo/` is structurally justified: visual demos are application-style proofs, not release-facing workload examples, and the subdirectory accurately reflects that distinction.
- Code fixes are tight and on-scope: only `REPO_ROOT` path computation, cross-demo imports, test module paths, one stale URL, and one audit-script special case were touched — nothing beyond what the move required.
- Verification is sufficient for a path-reorganization slice: 52 tests across 8 test files, a `compileall` sweep of all moved/affected files, a repo-wide stale-reference scan, and a direct CLI smoke run of the moved smooth-camera demo.

**Summary**

Goal 190 is a clean, bounded reorganization. The 3D demos are now correctly scoped under `examples/visual_demo/`, the move propagated consistently through code, tests, and docs, and all bounded checks passed with no regressions.
