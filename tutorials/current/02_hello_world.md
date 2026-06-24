# Hello World

This V3 example is the smallest useful RTDL scene.

Run:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\current\getting_started\rtdl_hello_world.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

The example builds a tiny ray/triangle scene. One ray crosses one rectangle that
is encoded as two triangles, so the RTDL kernel returns one row with two hits.

Next: [Backend Choice](03_backend_choice.md)
