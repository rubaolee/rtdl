# V4 Public Language And Top-Level Cleanup - 2026-06-27

## Purpose

After the advanced tutorial surface pass, the remaining cleanup target was the
first impression of the current V4 repository:

- user-facing documentation should avoid maintainer-only wording;
- paper-reproduction wrappers should be clearly V4-related but separate from
  the 10 benchmark apps;
- local top-level generated debris should not distract from the real source
  tree while preparing the release state.

## Public Files Updated

| File | Action |
| --- | --- |
| `docs/current_v4_status.md` | Replaced maintainer-style release-boundary wording with user-facing package, source-tree, and performance-table wording. |
| `docs/v4_engineering_summary.md` | Replaced installed-wheel smoke wording with installed-package import checks. |
| `examples/paper_reproduction/README.md` | Clarified that paper-oriented entrypoints are V4 work, added Linux/macOS commands, and kept them separate from the standard benchmark suite. |
| `examples/paper_reproduction/rt_barneshut.py` | Made the wrapper runnable directly from a fresh clone by adding the repository root to `sys.path` before importing example support. |
| `examples/paper_reproduction/rayjoin.py` | Made the wrapper runnable directly from a fresh clone by adding the repository root to `sys.path` before importing example support. |

## Local Workspace Cleanup

Ignored local-only generated directories were removed from the working tree:

- empty `future/`;
- ignored `build/` outputs and the old nested probe cache;
- empty `dist/` and `external/`;
- Python `__pycache__` and source-tree egg-info caches under examples, scripts,
  source, and tests.

These were not tracked public release files.

## Exit Checks Run

- Public forbidden-language scan over `README.md`, `docs`, `tutorials`, and
  `examples`: no hits.
- Paper-reproduction wrappers: both default JSON commands succeeded.
- Fresh Linux tag-clone probe caught and then fixed direct wrapper imports.
- `tests.v4_goal4640_public_docs_cleanup_test`,
  `tests.v4_goal4774_release_packaging_audit_test`,
  `tests.v4_goal4775_release_staging_manifest_test`, and
  `tests.v4_release_clean_checkout_gate_test`: passed.
- `scripts/v4_universe_audit.py --strict-release`: passed.
- `scripts/v4_catalog_regression_gate.py --mode dry-run`: passed.
