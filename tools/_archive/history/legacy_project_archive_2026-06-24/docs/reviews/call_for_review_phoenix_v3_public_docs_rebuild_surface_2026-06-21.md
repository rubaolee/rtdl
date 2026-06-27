# Call For Review: Phoenix V3 Public Docs Rebuild Surface

Please critically review this Phoenix V3 public-doc rebuild pass.

Files under review:

```text
docs/application_catalog.md
docs/backend_maturity.md
docs/performance_model.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
scripts/v3_release_wording_gate.py
tests/v3_public_docs_rebuild_surface_test.py
```

Current verification:

```text
py -3 -m unittest tests.v3_public_docs_rebuild_surface_test tests.v3_release_wording_gate_test
result: 7 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
result: pass, missing_required_strings=[], violations=[]

py -3 scripts/run_test_matrix.py --group v3_rebuild
result: 41 modules, 190 tests OK
```

Question:

Did this pass correctly move the public V3 docs from older
release-candidate-style wording to Phoenix boundary wording, while preserving
the hard current truth?

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Please check especially:

- whether `docs/application_catalog.md` clearly tells users what each app can
  teach today without implying any row is M7-qualified;
- whether `docs/backend_maturity.md` prevents backend-name overclaim and makes
  maturity row-scoped;
- whether `docs/performance_model.md` correctly separates hot/query/wall/end-to-end
  timing and avoids broad V3-over-V2 wording;
- whether the new test and wording-gate strings are strong enough to prevent
  regression;
- whether any wording still sounds like release authorization, broad speedup,
  paper reproduction, or automatic backend choice.

Needed verdict:

```text
approve_as_rebuild_docs
approve_with_p0_fixes
reject_as_misleading
```
