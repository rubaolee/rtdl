# Goal2103 Root, Scripts, And Tests Organization Audit

Status: complete.

Purpose: make the repository front page cleaner and more precise by removing
unnecessary tracked top-level technical folders and adding reader guidance for
large maintenance directories.

## Findings And Operations

| Area | Finding | Operation |
| --- | --- | --- |
| `apps/` | Old proof/demo source sat at the root beside current public examples. | Moved the Python demo to `examples/internal/rtdsl_python_demo.py`; moved old C++ proof apps to `docs/history/source_archive/apps/`. |
| `generated/` | Generated plan bundles appeared as a top-level product surface. | Moved them to `examples/generated/plan_bundles/`. |
| `schemas/` | Two unrelated schemas appeared as one top-level directory. | Moved runtime plan schema to `src/rtdsl/schemas/`; moved system-audit SQL schema to `scripts/schemas/`; updated code paths. |
| tracked `build/` artifacts | Tracked historical build artifacts made the root look like a build output directory. | Moved tracked artifacts to `docs/history/build_artifacts_archive/`. Runtime scripts may still create local untracked `build/`. |
| root handoff files | Local untracked handoff files cluttered the working root. | Moved local root handoff files to `docs/handoff/root_level_archive/` without adding them to the commit. |
| `scripts/` | Hundreds of goal-specific scripts are hard to browse as a normal user. | Added `scripts/README.md` with "use first" guidance and a clear boundary. |
| `tests/` | More than a thousand goal tests are overwhelming without an entry point. | Added `tests/README.md` with current gate commands and directory meaning. |

## Final Tracked Root Shape

Tracked `apps/`, `generated/`, `schemas/`, and `build/` front-door paths are now
absent. Current users should start from:

- `README.md`
- `docs/`
- `examples/`
- `src/`

Maintenance and verification remain available through:

- `scripts/README.md`
- `tests/README.md`
- `docs/audit/README.md`
- `docs/history/README.md`

## Regression Gate

`tests/goal2103_root_scripts_tests_organization_audit_test.py` checks:

- no tracked `apps/`, `generated/`, `schemas/`, or `build/` root paths remain;
- relocated files exist in their new homes;
- `scripts/README.md` and `tests/README.md` exist and explain how to start;
- runtime schema paths still resolve.

## Boundary

This is an organization cleanup. It does not remove audit history, delete source
evidence, change runtime semantics, or authorize release claims.

