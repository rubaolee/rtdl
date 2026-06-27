# First Run

Run the V4 front-door quickstart from the repository root.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
```

The quickstart returns JSON. The important fields are:

- `front_door_status`: the current V4 front-door state;
- `measured_surface_count`: the number of measured V4 operator surfaces;
- `measured_partners`: partner scopes with evidence;
- the `v4.0.0` public release tag and claim-boundary flags. The tag is
  published, while broad speedup, Tier-3 callback, zero-copy, and embedding
  claims remain false.

Next: [Front-Door Quickstart](02_hello_world.md)
