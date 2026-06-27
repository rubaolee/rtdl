# What RTDL Is

GPUs have several kinds of hardware. CUDA cores run ordinary parallel kernels.
RT cores are specialized for traversal questions: which primitive is hit, which
box overlaps, which candidate is nearby, or which spatial cell should be used.

RTDL V4 is a Python eDSL for writing programs that use those RT-shaped
questions without writing a one-off OptiX program for every app. You describe
the relation you need, choose a partner explicitly, and let RTDL give you the
current operator surface.

The basic pattern is:

1. describe the relation;
2. ask V4 for an operator plan;
3. prepare the operator for your data layout;
4. run it;
5. apply a continuation such as count, argmin, grouped sum, component union, or
   weighted vector sum.

Start from the repository root:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
```

The same check can be written directly:

```python
import rtdsl.v4 as rt

info = rt.claim_boundary_v4()
print(info["public_release_tag"])
print(info["measured_surface_count"])
print(",".join(info["measured_partners"]))
```

The output tells you which V4 front door you are using and which partner names
appear in the current measured operator catalog.

Next: [Hello RTDL](02_hello_world.md)
