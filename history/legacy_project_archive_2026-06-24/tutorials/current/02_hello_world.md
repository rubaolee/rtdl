# Hello World

Status: V3 rebuild tutorial.

Run:

```powershell
py -3 examples\current\getting_started\rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

What it teaches:

- an RTDL kernel names its input shapes;
- `traverse` emits candidate geometry relations;
- `refine` applies the predicate;
- `emit` returns typed rows;
- the CPU Python reference path is the first correctness anchor.

The example casts a visible rectangle into two triangles. A horizontal ray hits
that rectangle, so the result has one logical visible object and two triangle
hits. The printed text is the label attached by app code after RTDL returns the
hit count.

Read next:

- [Backend Choice](03_backend_choice.md)
