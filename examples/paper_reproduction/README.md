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

These scripts keep paper-reproduction work separate from the ordinary benchmark
suite. Some paper workloads route to the current benchmark implementation; some
use a paper-specific runner when the paper program has stricter inputs or
timing rules.

RayJoin Section 5.7 Polygon Overlay uses the paper-specific runner:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-plan --dataset-root data/rayjoin_section57_cdb
python3 examples/paper_reproduction/rayjoin.py --section57-compare-v214 --json
```

Read [paper_reproduction_scope.md](paper_reproduction_scope.md) before using
these wrappers. It explains what each wrapper routes to and which comparison
claims require exact inputs.
