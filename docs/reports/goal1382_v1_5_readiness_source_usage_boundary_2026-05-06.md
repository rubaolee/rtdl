# Goal1382: v1.5 Readiness Source Usage Boundary

Date: 2026-05-06

Source commit before change: `ff263895332b88eec04a6e7b2fdb39994c84c342`

## Scope

This goal hardens the internal v1.5 readiness decision against accidental
packaging or install-support claims.

Current public usage remains source-tree execution only:

```text
PYTHONPATH=src:. python ...
```

## Added Guard

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_SOURCE_USAGE_MODE = "source_tree_pythonpath"`
- `V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND = "PYTHONPATH=src:. python ..."`

`v1_5_internal_readiness_decision()` now reports:

- `source_usage_mode`
- `source_usage_command`
- `editable_install_claim_authorized: False`
- `package_release_artifact_authorized: False`

`validate_v1_5_internal_readiness_decision()` requires the exact source-tree
usage mode and command, and rejects editable-install or package-artifact
authorization.

This preserves the current project boundary: internal v1.5 readiness work does
not imply `pip install -e .` support, packaging metadata, public release
artifacts, or public v1.5 release wording.

## Local Validation

Focused readiness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK
```

v1.5 slice:

```text
PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 0.044s
OK
```
