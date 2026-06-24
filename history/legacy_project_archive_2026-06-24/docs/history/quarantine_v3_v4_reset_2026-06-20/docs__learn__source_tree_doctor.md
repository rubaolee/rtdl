# Source-Tree Doctor

Status: current V4.0.0 source-tree setup check.

Use the doctor before native backend or partner experiments. It checks the
repository layout, current version marker, V4 release package, V3 app-author
guidance, core imports, the current V4 test-matrix entrypoint, optional partner modules, and
optional native library hints.

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

Current V4 release suite:

```bash
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v4_current
```

## How To Read It

- `PASS` on required checks means the source tree is usable.
- `WARN` on optional modules means only that optional native or partner paths
  may not run in this environment.
- `PASS` on optional editable metadata means this checkout has local editable
  install metadata.
- `PASS` on `V4 current test matrix` means the current V4 release-suite runner
  is registered. The doctor does not run that suite unless you run the command
  above.
- Missing CuPy affects CUDA-array partner examples.
- Missing Numba affects Python-source custom CUDA-style continuation examples.
- Missing `RTDL_OPTIX_LIBRARY` affects OptiX examples, not portable CPU
  examples.

The doctor is not a benchmark and does not authorize performance claims. It is
only an environment sanity check. V4.0.0 remains source-tree only: package,
PyPI, wheel, stable SDK, public true-zero-copy, async, and public speedup claims
are still blocked unless a later release package says otherwise.

## Reviewer-Only Archive Check

Archive reviewers can opt into the preserved V4 preparatory embedding/C ABI
presence checks:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --include-v4-prep
```

That mode checks only that the archived files and reviewer targets still exist
under `docs/history/v4_preparatory_embedding/`.

- `PASS` on `V4 preparatory C ABI surface` means the archived draft header,
  source-tree shared-library/staging/prefix-stage/archive targets, pkg-config
  and CMake metadata, C examples, Python `ctypes` lifecycle examples,
  host AABB2 query examples, CUDA metadata examples, and DLPack-like metadata
  examples are still present for archive review.
- `PASS` on `V4 preparatory C ABI docs` means the archived draft, stability,
  ownership/threading, symbol-manifest, zero-copy, toolchain support, and
  binding/device interop matrix docs are still present for archive review.

It does not build `make build-c-api`, `make stage-c-api`,
`make stage-c-api-prefix`, or `make package-c-api-stage`; it does not freeze the ABI,
validate runtime behavior, run CMake, or make the archived preparatory C ABI a
stable V4.0.0 SDK.
In particular, it does not run CMake.
