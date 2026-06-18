# Source-Tree Doctor

Status: current v3.0 source-tree setup check for V3 development and release use.

Use the doctor before native backend or partner experiments. It checks the
repository layout, current version marker, V3 app-author guidance, core
imports, the current V3 test-matrix entrypoint, optional V4 preparatory C ABI
file/doc surfaces, optional partner modules, and optional native library hints.

## Run It

From the repository root:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
```

If you prefer a local editable checkout for development:

```bash
python -m pip install -e .
python scripts/rtdl_source_tree_doctor.py
```

Editable checkout support only makes this repository importable as `rtdsl` in
your active Python environment. It is not a PyPI, wheel, or distribution-package
support claim.

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py
```

Machine-readable output:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --json
```

Portable smoke run:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
```

Current V3 closure suite:

```bash
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v3_current
```

## How To Read It

- `PASS` on required checks means the source tree is usable.
- `WARN` on optional modules means only that optional native or partner paths
  may not run in this environment.
- `PASS` on optional editable metadata means this checkout has local editable
  install metadata.
- `PASS` on `V3 current test matrix` means the current V3 closure-suite runner
  is registered. The doctor does not run that suite unless you run the command
  above.
- `PASS` on `V4 preparatory C ABI surface` means the public C header, source-tree
  shared-library/staging/prefix-stage/archive targets, pkg-config and CMake
  metadata, C examples including the host-runtime metadata and CUDA
  buffer-metadata examples, Python `ctypes` lifecycle examples, Python `ctypes`
  host AABB2 query examples, Python `ctypes` CUDA metadata examples, and
  Python `ctypes` DLPack-like metadata examples are present. These are V4.0
  preparatory artifacts, not V3.0 release criteria. It does not build
  `make build-c-api`, `make stage-c-api`,
  `make stage-c-api-prefix`, or `make package-c-api-stage`, and it does not run
  CMake.
- `PASS` on `V4 preparatory C ABI docs` means the draft, stability,
  ownership/threading, symbol-manifest, zero-copy, toolchain support, and
  binding/device interop matrix are preserved under
  `docs/history/v4_preparatory_embedding/` with explicit V4.0 scope wording. It
  does not freeze the ABI, validate runtime behavior, or make embedding part of
  V3.0.
- Missing CuPy affects CUDA-array partner examples.
- Missing Numba affects Python-source custom CUDA-style continuation examples.
- Missing `RTDL_OPTIX_LIBRARY` affects OptiX examples, not portable CPU
  examples.

The doctor is not a benchmark and does not authorize performance claims. It is
only an environment sanity check. V3.0 excludes embedding/SDK/zero-copy work;
those items are V4.0 scope.
