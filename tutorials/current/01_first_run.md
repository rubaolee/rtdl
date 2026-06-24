# First Run

Run the source-tree doctor from the repository root.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py --run-smoke
```

Linux or macOS:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
```

The doctor checks the current V3 front doors and runs the portable hello-world
smoke when requested. It is a checkout sanity check.

Next: [Hello World](02_hello_world.md)
