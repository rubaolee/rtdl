# Goal1254 v1.0 Post-Release Sanity Fix

Date: 2026-05-04

## Scope

This is a narrow post-release sanity correction after pushing `main` and tag
`v1.0`.

## Fresh Tag Sanity

Remote tag checkout:

```bash
git clone --depth 1 --branch v1.0 https://github.com/rubaolee/rtdl.git /tmp/rtdl_v1_0_sanity_X4XTkh/rtdl
```

Observed:

- tag resolves to release commit `b9c9620af78a2fab92083d43af312bb6310e452a`
- `VERSION` is `v1.0`
- release docs and root docs expose `v1.0`
- `PYTHONPATH=src:. python examples/rtdl_hello_world.py` prints `hello, world`
- source-tree import works with `PYTHONPATH=src:.`
- focused release-surface tests pass from the tag checkout

## Issue Found

The root `README.md` quickstart included:

```bash
python3 -m pip install -e .
```

That command is invalid for the current repository because v1.0 does not include
`setup.py` or `pyproject.toml`. The supported v1.0 usage contract is source-tree
execution with `PYTHONPATH=src:.`.

## Fix

Updated `README.md` to remove the unsupported editable-install command and state
that RTDL v1.0 is used directly from the source tree.

Added a regression check in
`tests/goal646_public_front_page_doc_consistency_test.py` so the root quickstart
does not reintroduce `python3 -m pip install -e .` before packaging metadata
exists.

## Verification

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

Fresh tag source-tree smoke result:

```text
IMPORT_OK rtdsl
hello, world
Ran 24 tests in 0.188s
OK
```

## Claim Boundary

This fix does not change any RT-core, Embree, Vulkan, HIPRT, Apple RT, speedup,
or app-support claim. It only corrects a public quickstart command to match the
current v1.0 source-tree usage contract.
