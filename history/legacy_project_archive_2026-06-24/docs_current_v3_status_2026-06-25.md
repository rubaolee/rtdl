# Archived V3.0.0 Status

This file is archived historical context. It is not the current RTDL user line.

The current tree is suitable for learning the Python-hosted RTDL programming
model, running the portable examples, and developing against explicit backend
and partner boundaries.

## Current Promise

V3.0.0 provides a clean RTDL user contract:

- one current documentation path;
- one current tutorial path;
- one current examples path;
- prepared execution and runtime-trunk APIs in the source tree;
- explicit backend and partner selection;
- clear measurement wording for performance-sensitive examples.

## Performance Wording

Performance-sensitive examples use exact, scoped wording: command, metric,
hardware, backend, and measured row. Prefer "this measured row" over broad
system-level language.

## Verification

Use:

```powershell
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py --run-smoke
```

The doctor checks the clean V3.0.0 front doors and runs the portable hello-world
smoke when requested.
