# What RTDL Is

GPUs have several kinds of hardware. CUDA cores run ordinary parallel kernels.
RT cores are specialized for traversal questions: which primitive is hit, which
box overlaps, which candidate is nearby, or which spatial cell should be used.

RTDL V4 is a Python eDSL for writing programs around those RT-shaped questions.
The point is not to call a large app wrapper. The point is to describe the
geometric query your program needs and then choose how the query is executed.

A useful first mental model is:

```text
input geometry -> traverse -> refine -> emit rows -> Python program result
```

The first program uses a ray and three rectangles. Only the middle rectangle is
hit, and that rectangle carries the label `hello, world`.

The basic pattern is:

1. declare the input geometry;
2. traverse candidate pairs with an acceleration structure;
3. refine candidates with the predicate you need;
4. emit result rows;
5. let ordinary Python turn those rows into the surrounding program output.

Start from the repository root:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\sorting_rows.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
```

The first program prints `hello, world`. The second program shows a small
sorting problem lowered into RTDL rows. Do this before opening the V4
front-door planner: the planner is useful only after the relation shape is
clear.

Next: [Hello RTDL](02_hello_world.md)
