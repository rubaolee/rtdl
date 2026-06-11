# Source-Tree Doctor

Status: current v2.10 source-tree setup check.

Use the doctor before native backend or partner experiments. It checks the
repository layout, current version marker, core imports, optional partner
modules, and optional native library hints.

## Run It

From the repository root:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
```

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

## How To Read It

- `PASS` on required checks means the source tree is usable.
- `WARN` on optional modules means only that optional native or partner paths
  may not run in this environment.
- Missing CuPy affects CUDA-array partner examples.
- Missing Numba affects Python-source custom CUDA-style continuation examples.
- Missing `RTDL_OPTIX_LIBRARY` affects OptiX examples, not portable CPU
  examples.

The doctor is not a benchmark and does not authorize performance claims. It is
only an environment sanity check.
