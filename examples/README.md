# RTDL V3.0.0 Examples

Use these examples with the source tree on `PYTHONPATH`.

First run:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\current\getting_started\rtdl_hello_world.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

## Current Layout

| Path | Use |
| --- | --- |
| `current/getting_started/` | First examples and smoke checks. |
| `current/features/` | Feature-level examples. |
| `current/apps/` | Application-shaped examples. |
| `current/partners/` | Explicit partner examples. |
| `current/research_benchmarks/` | Benchmark code inventory for developers. |

The default user path is `current/getting_started/`. Benchmark directories are
developer workspaces.
