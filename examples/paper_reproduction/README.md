# Paper Reproduction Apps

This folder separates paper-oriented V4 work from the standard 10 benchmark
apps.

Current paper-oriented entrypoints:

| Paper-oriented app | Command |
| --- | --- |
| RT-BarnesHut | `py -3 examples\paper_reproduction\rt_barneshut.py --json` |
| RayJoin | `py -3 examples\paper_reproduction\rayjoin.py --json` |

Linux or macOS users can run the same entrypoints with `python3` and forward
slashes, for example:

```bash
python3 examples/paper_reproduction/rt_barneshut.py --json
python3 examples/paper_reproduction/rayjoin.py --json
```

These scripts forward to the corresponding RTDL app implementation while
keeping the paper-reproduction label separate from the ordinary benchmark suite.

Read [paper_reproduction_scope.md](paper_reproduction_scope.md) before using
these wrappers. It explains what each wrapper routes to and which tutorial
program to study first.
