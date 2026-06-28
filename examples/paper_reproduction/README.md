# Paper Reproduction Apps

This V4 folder separates paper-oriented work from the standard 10 benchmark
apps.

Current paper-oriented entrypoints:

| Paper-oriented app | Command |
| --- | --- |
| RT-BarnesHut | `py -3 examples\paper_reproduction\rt_barneshut.py --help` |
| RayJoin | `py -3 examples\paper_reproduction\rayjoin.py --help` |

These scripts forward to the corresponding RTDL app implementation while
keeping the paper-reproduction label separate from the ordinary benchmark suite.

Read [paper_reproduction_scope.md](paper_reproduction_scope.md) before using
these wrappers. It explains what each wrapper routes to and which tutorial
program to study first.
