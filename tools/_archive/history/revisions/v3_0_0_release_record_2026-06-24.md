# RTDL V3.0.0 Release Record

Date: 2026-06-24
Status: V3.0.0 public source-tree release surface prepared

## Release Scope

V3.0.0 is the current RTDL user surface:

- Python-hosted `rtdsl` package
- clean `README.md`, `docs/`, `tutorials/`, and `examples/` front doors
- runnable getting-started examples
- explicit backend and partner selection
- prepared execution APIs and current V3 runtime-trunk source surface
- scoped performance wording only

This release record does not authorize broad V3-over-V2 speed claims.

## Version Facts

- `VERSION`: `v3.0.0`
- `pyproject.toml`: `version = "3.0.0"`
- package name: `rtdl-source-tree`

## Gates Run

Windows source tree:

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\run_test_matrix.py --group v3_current_surface
```

Result: `23 tests OK`.

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\v3_release_wording_gate.py --pretty
```

Result: `status: pass`, `release_authorized: true`, `public_speedup_claim_authorized: false`.

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\rtdl_source_tree_doctor.py --run-smoke
```

Result: core V3 checks passed and hello-world smoke ran.

Local Linux source-tree sanity check:

```bash
PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --run-smoke
```

Result: core V3 checks passed and hello-world smoke ran.

Local Linux wheel build:

```bash
python3 -m pip wheel . -w dist --no-deps
```

Result: built `rtdl_source_tree-3.0.0-py3-none-any.whl`.

## Notes

The Windows Python launcher prints `Could not find platform independent libraries <prefix>` on stderr in this environment. The V3 commands still returned success.

The local Linux package validation used a temporary copy of the release surface. Full history was not copied into that temporary directory; the authoritative workspace keeps history under `history/`.
