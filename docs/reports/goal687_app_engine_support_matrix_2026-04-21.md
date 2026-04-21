# Goal 687 App Engine Support Matrix

## Scope

Goal687 adds an app-level support matrix so users can see the support degree of
each public RTDL app on CPU/Python, Embree, OptiX, Vulkan, HIPRT, and Apple RT.

This is intentionally separate from the feature-level engine matrix. A feature
can support an engine while a particular app CLI does not expose that engine.

## Changes

- Added `src/rtdsl/app_support_matrix.py`.
- Exported:
  - `rtdsl.APP_ENGINES`
  - `rtdsl.APP_SUPPORT_STATUSES`
  - `rtdsl.public_apps()`
  - `rtdsl.app_engine_support(...)`
  - `rtdsl.app_engine_support_matrix()`
- Added public doc `docs/app_engine_support_matrix.md`.
- Linked the matrix from:
  - `README.md`
  - `docs/README.md`
  - `docs/application_catalog.md`
  - `docs/release_facing_examples.md`
  - `examples/README.md`
- Added `tests/goal687_app_engine_support_matrix_test.py`.
- Added the app matrix doc to the public markdown-link smoke set.

## Status Vocabulary

- `direct_cli_native`: the app CLI exposes this engine and uses native backend
  support for the RTDL core.
- `direct_cli_native_assisted`: the app path exposes native/native-assisted
  backend work.
- `direct_cli_compatibility_fallback`: the app exposes a documented
  compatibility path; not a speedup claim.
- `portable_cpu_oracle`: the app has a portable CPU/Python correctness path.
- `partial_cpu_oracle`: only part of the app has a CPU/Python oracle; another
  scenario may be hardware-gated.
- `not_exposed_by_app_cli`: the app does not expose this engine today.
- `apple_specific`: the app is specifically an Apple RT demo; non-Apple engines
  are not applicable entry points.

## Key Read

- The unified DB and graph apps expose CPU/Python, Embree, OptiX, and Vulkan.
  HIPRT and Apple RT lower-level feature paths may exist, but these unified app
  CLIs do not expose them today.
- The unified Apple RT demo is Apple-specific and uses Apple RT as
  `direct_cli_native_assisted`.
- Several spatial/proximity apps expose only CPU/Python and Embree because
  their public app CLIs were intentionally kept narrow even though related
  primitives may exist on other engines.
- The HIPRT demo is HIPRT-specific and does not imply AMD GPU validation.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal687_app_engine_support_matrix_test tests.goal686_app_catalog_cleanup_test tests.goal512_public_doc_smoke_audit_test
```

Result: `12` tests OK.

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result: `valid: true`, `252` commands across `14` public docs.

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/app_support_matrix.py src/rtdsl/__init__.py tests/goal687_app_engine_support_matrix_test.py
git diff --check
```

Result: compile and whitespace checks passed.

## Boundary

- This is documentation and machine-readable app-support metadata.
- It is not a new backend implementation.
- `not_exposed_by_app_cli` means the current public app script does not expose
  that engine; it is not a statement that a related lower-level feature can
  never support that engine.
- App-level Python orchestration remains Python-owned unless a native backend
  helper is explicitly named.
