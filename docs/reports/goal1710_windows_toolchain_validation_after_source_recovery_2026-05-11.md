# Goal1710 Windows Toolchain Validation After Source Recovery

Date: 2026-05-11

Status: local Windows validation after Goal1708 source recovery and Goal1709
Gemini read-only audit.

## Context

Goal1707 recorded that `tests.goal903_embree_graph_ray_traversal_test` could
not complete locally because the Oracle native helper failed to build under the
Windows SDK/UCRT headers. Goal1708 recovered the source truncation fallout, and
Goal1709 independently accepted that recovery.

This follow-up isolates the remaining local blocker as environment setup rather
than source corruption or a native ABI regression.

## Toolchain Finding

The default Codex PowerShell environment did not have a Visual Studio C++
environment active:

- `RTDL_VCVARS64` was unset.
- `VSINSTALLDIR`, `VCINSTALLDIR`, `WindowsSdkDir`, `INCLUDE`, and `LIB` were
  unset in the active shell.
- `cl` was not visible on PATH.

The installed Build Tools vcvars path is:

```text
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
```

Setting `RTDL_VCVARS64` to that path allowed the Oracle native helper to build:

```powershell
$env:RTDL_VCVARS64='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$env:PYTHONPATH='src;.'
py -3 -c "from rtdsl.oracle_runtime import _ensure_oracle_library; print(_ensure_oracle_library())"
```

Result:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\build\librtdl_oracle.dll
```

The produced DLL was observed locally at:

```text
build\librtdl_oracle.dll
```

with size `318976` bytes.

## Validation

After exporting `RTDL_VCVARS64`, the previously blocked graph/oracle validation
passed:

```powershell
$env:RTDL_VCVARS64='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal903_embree_graph_ray_traversal_test -q
```

Result:

```text
Ran 8 tests in 2.909s
OK
```

The combined local recovery/toolchain slice also passed:

```powershell
$env:RTDL_VCVARS64='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1704_legacy_purity_symbol_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal903_embree_graph_ray_traversal_test -q
```

Result:

```text
Ran 28 tests in 3.740s
OK
```

## Claude Background Attempt

Claude Code was launched in the background for the same Goal1710 task, but no
`goal1710` report or review file was produced before this local Codex validation
completed. This report records the verified local result directly.

## Boundary

This resolves the local Windows SDK/UCRT Oracle-build blocker for the Embree
graph validation path. It does not provide pod or hardware execution evidence.

Release readiness remains:

```text
needs-more-evidence
```

The next blocker is pod/hardware validation for the recovered app-agnostic
native-engine state.

