# RT-DBSCAN Scripts

Current paper-app scripts:

```text
run_core_count_smoke.py
run_authorofficial_core_count_gate.py
setup_authorofficial_core_count.sh
```

This is a local requirements smoke wrapper. It runs the existing RTDL DBSCAN
app on a tiny synthetic fixture and checks the integer `core_count` against the
RTDL CPU reference/oracle path. It is not an author-comparator gate.

The current source assets are:

```text
examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
examples/current/apps/ml/rtdl_dbscan_clustering_app.py
```

Future scripts should wrap or reuse those assets only after the paper-app
requirements goal decides the bounded target and comparator.

`run_authorofficial_core_count_gate.py` is the bounded same-input gate runner
for the first AuthorOfficial target. Without `--author-binary`, it runs the
local RTDL comparator only. With a patched author binary, it runs:

```text
sample02-rtdbscan [input] [size] [epsilon] [minPts] [author_output]
```

and compares the emitted `core_count` against the RTDL result.

`setup_authorofficial_core_count.sh` is a Linux/POD helper that clones the
author repository, checks out the pinned `rt-dbscan` commit, applies the
core-count output patch, and attempts to build `sample02-rtdbscan`.
