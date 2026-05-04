# Gemini Review Request: Goal1254 v1.0 Post-Release Sanity Fix

Please review this narrow post-release public-doc correction.

Files to inspect:

- `README.md`
- `tests/goal646_public_front_page_doc_consistency_test.py`
- `docs/reports/goal1254_v1_0_post_release_sanity_fix_2026-05-04.md`

Context:

- `main` and annotated tag `v1.0` were pushed.
- A fresh checkout of remote tag `v1.0` confirmed `VERSION=v1.0`, source-tree
  import with `PYTHONPATH=src:.`, hello-world execution, and focused release
  tests.
- The sanity pass found one public-doc defect: root `README.md` said
  `python3 -m pip install -e .`, but v1.0 has no `setup.py` or `pyproject.toml`.
- The fix removes that unsupported install command and states the supported
  contract: use RTDL v1.0 directly from the source tree with `PYTHONPATH=src:.`.
- A regression test now prevents reintroducing the unsupported editable-install
  command before packaging metadata exists.

Verification already run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1217_version_marker_current_release_sync_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal1250_v1_0_release_surface_doc_audit_test
```

Result:

```text
Ran 14 tests in 0.115s
OK
```

Review questions:

1. Is this correction technically accurate for the current v1.0 repo state?
2. Does it preserve the v1.0 release/public-claim boundaries?
3. Is it acceptable to commit and push this as a post-release documentation fix
   on `main` without changing the existing `v1.0` tag?

Expected verdict format:

```text
VERDICT: ACCEPT or REJECT

Reasons:
- ...

Required fixes:
- ...
```
