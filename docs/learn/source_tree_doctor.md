# Source-Tree Doctor

The source-tree doctor is the quickest way to check that the current V3 checkout
has the expected front doors and can run the portable hello-world example.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py --run-smoke
```

Linux or macOS:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
```

The doctor is a checkout sanity check. It checks the clean V3 source-tree
surface, important docs, importability, optional native/partner dependencies,
and the hello-world smoke path.

For the broader developer test group:

```bash
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v3_current_surface
```

That matrix is a development gate for the current V3 source tree.
