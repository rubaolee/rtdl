# Backend Choice

V3 keeps backend choice explicit.

Start with the CPU reference path when learning or checking correctness. Move
to native or partner-backed paths only when the example, backend dependency, and
measurement scope are clear.

Do not infer performance from a backend name. A backend can be correct for one
row, slower for another row, and unsupported for a third row.

Useful first examples:

```powershell
py -3 examples\current\getting_started\rtdl_hello_world.py
py -3 examples\current\getting_started\rtdl_hello_world_backends.py
```

Next: [Prepared Runtime](04_prepared_runtime.md)
