# Source-Tree Doctor

Status: current v2.14 source-tree setup check for V3 development.

Use the doctor before native backend or partner experiments. It checks the
repository layout, current version marker, V3 app-author guidance, core
imports, the current V3 test-matrix entrypoint, the V3 C ABI embedding and docs
surfaces, optional partner modules, and optional native library hints.

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
- `PASS` on `V3 C ABI embedding surface` means the public C header, source-tree
  shared-library target, and embedding example files are present. It does not
  build `make build-c-api`.
- `PASS` on `V3 C ABI docs surface` means the draft, stability,
  ownership/threading, symbol-manifest, zero-copy, and Learn README C ABI links
  are present. It does not freeze the ABI or validate runtime behavior.
- Missing CuPy affects CUDA-array partner examples.
- Missing Numba affects Python-source custom CUDA-style continuation examples.
- Missing `RTDL_OPTIX_LIBRARY` affects OptiX examples, not portable CPU
  examples.

The doctor is not a benchmark and does not authorize performance claims. It is
only an environment sanity check.
