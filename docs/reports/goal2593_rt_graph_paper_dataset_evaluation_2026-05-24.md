# Goal2593 RT-Graph Paper-Dataset Evaluation

Date: 2026-05-24

## Decision

The earlier K4 synthetic closeout is not sufficient for finalizing the
RT-Graph triangle-counting benchmark app. On the actual RT-Graph/SNAP paper
datasets, the conclusion changes:

- RTDL is correct and runnable on the smaller and medium paper datasets through
  the Python+CuPy+generic OptiX 2A1 path.
- RAPIDS cuGraph is the strongest end-to-end baseline on all paper datasets
  that completed.
- RTDL 1A2 runs out of memory on `wiki-Talk` and `cit-Patents`.
- Both RTDL 2A1 and 1A2 run out of memory on `com-lj`,
  `soc-LiveJournal1`, and `com-orkut`.
- Authors' `rt_tc` and `bs_tc` validate correctness and show extremely fast
  pure count kernels, but their full pipelines are dominated by preprocessing
  and graph-to-RT/GPU construction. On `com-orkut`, both authors binaries were
  SIGKILLed on the current 24 GB A5000 pod.

The benchmark app is closed with a documented scalability limitation. A
segmented paper-dataset-capable RTDL lowering path is the follow-up target, not
a requirement for this bounded closeout.

## Sources

The authors' repository is `https://github.com/rubaolee/RT-Graph`, local commit
`e7675f2e0cd06077c5050da13f455cc0c2320208`. Its README lists the triangle
counting datasets and expected triangle counts. The README says all TC datasets
come from the Stanford Large Network Dataset Collection.

Dataset preparation used:

- `scripts/goal2593_rt_graph_snap_prepare.py`
- raw evidence: `docs/reports/goal2593_paper_dataset_raw/goal2593_snap_prepare_all.json`

Evaluation used:

- `scripts/goal2593_rt_graph_paper_dataset_eval.py`
- RTDL app: `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- authors binaries: `scratch/external/RT-Graph/tc/bin/rt_tc`,
  `scratch/external/RT-Graph/tc/bin/bs_tc`
- cuGraph baseline: `scripts/goal2592_rt_graph_cugraph_baseline.py`

Raw result files are under:

- `docs/reports/goal2593_paper_dataset_raw/`

## Environment

Pod:

```text
ssh root@203.57.40.104 -p 10001 -i ~/.ssh/id_ed25519_rtdl_codex
```

Hardware/software:

- GPU: NVIDIA RTX A5000, 24564 MiB
- Driver: 550.127.05
- CUDA runtime path: `/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- RAPIDS cuGraph: 26.04.000
- RAPIDS cuDF: 26.04.000

## Prepared Paper Datasets

All downloaded edge counts matched the RT-Graph README table.

| Dataset | Edges | Expected triangles | Converted binary |
|---|---:|---:|---|
| `com-dblp` | 1,049,866 | 2,224,385 | `build/goal2593_snap_edges/com-dblp.edge` |
| `com-youtube` | 2,987,624 | 3,056,386 | `build/goal2593_snap_edges/com-youtube.edge` |
| `wiki-Talk` | 5,021,410 | 9,203,519 | `build/goal2593_snap_edges/wiki-Talk.edge` |
| `cit-Patents` | 16,518,948 | 7,515,023 | `build/goal2593_snap_edges/cit-Patents.edge` |
| `com-lj` | 34,681,189 | 177,820,130 | `build/goal2593_snap_edges/com-lj.edge` |
| `soc-LiveJournal1` | 68,993,773 | 285,730,264 | `build/goal2593_snap_edges/soc-LiveJournal1.edge` |
| `com-orkut` | 117,185,083 | 627,584,181 | `build/goal2593_snap_edges/com-orkut.edge` |

## End-To-End Performance Matrix

Times are milliseconds. Small/medium datasets used 3 repeats with 1 warmup.
Large datasets used 1 or 2 measured runs because the authors' large-dataset
pipelines are expensive and RTDL fails early on memory. `failed` means the
method did not produce a result on this pod.

| Dataset | RTDL 2A1 total | RTDL 1A2 total | cuGraph total | authors `rt_tc` pipeline | authors `bs_tc` pipeline |
|---|---:|---:|---:|---:|---:|
| `com-dblp` | 210.060 | 241.116 | 81.078 | 703.128 | 701.328 |
| `com-youtube` | 773.854 | 947.759 | 134.368 | 2253.242 | 2342.094 |
| `wiki-Talk` | 2190.360 | failed: CUDA OOM | 194.562 | 7871.026 | 7866.749 |
| `cit-Patents` | 1716.011 | failed: CUDA OOM | 528.418 | 5487.187 | 5252.953 |
| `com-lj` | failed: CUDA OOM | failed: CUDA OOM | 1713.029 | 40801.618 | 40758.953 |
| `soc-LiveJournal1` | failed: CUDA OOM | failed: CUDA OOM | 2377.534 | 65658.375 | 63205.347 |
| `com-orkut` | failed: CUDA OOM | failed: CUDA OOM | 7229.100 | failed: SIGKILL | failed: SIGKILL |

## Core Timing Boundary

The authors' pure kernels remain very fast. RTDL's current weakness is not the
OptiX traversal microphase on successful inputs; it is the unsegmented
partner-side construction of the directed graph, two-hop rows, and geometric
lowering arrays.

| Dataset | RTDL 2A1 traversal | cuGraph triangle_count | authors `rt_tc` count | authors `bs_tc` count |
|---|---:|---:|---:|---:|
| `com-dblp` | 1.511 | 32.264 | 0.711 | 0.204 |
| `com-youtube` | 9.203 | 55.377 | 4.663 | 0.708 |
| `wiki-Talk` | 31.809 | 76.992 | 15.018 | 2.067 |
| `cit-Patents` | 35.384 | 230.805 | 12.457 | 2.065 |
| `com-lj` | failed: CUDA OOM | 861.013 | 72.968 | 10.615 |
| `soc-LiveJournal1` | failed: CUDA OOM | 1136.924 | 103.401 | 13.687 |
| `com-orkut` | failed: CUDA OOM | 5190.751 | failed: SIGKILL | failed: SIGKILL |

## Correctness

Every successful method returned the expected triangle count from the authors'
README. This includes RTDL 2A1 on `com-dblp`, `com-youtube`, `wiki-Talk`, and
`cit-Patents`; RTDL 1A2 on `com-dblp` and `com-youtube`; cuGraph on all seven
datasets; and the authors binaries on all successful runs.

## Memory Failures

RTDL failures occur before native traversal, inside the current CuPy summary
contract expansion. The observed allocation failures were:

| Dataset | RTDL allocation failure |
|---|---:|
| `com-lj` | 7.43 GB request |
| `soc-LiveJournal1` | 11.07 GB request |
| `com-orkut` | 68.64 GB request |

This is a design limitation, not an OptiX correctness failure. The current RTDL
paper-dataset path materializes the two-hop summary relation globally. Real
paper graphs require segmented or streamed construction and execution.

## PostgreSQL Status

PostgreSQL was not included in the final paper-dataset matrix. A first
`com-dblp` attempt completed during interactive logging, but the larger
PostgreSQL batch was stopped after `com-youtube` remained in table construction
for several minutes. A later rerun timed out and left a child `CREATE TABLE AS`
process, which was killed. Because no clean final JSON evidence was preserved,
PostgreSQL is deferred for the paper-dataset matrix.

The K4 synthetic report still contains PostgreSQL evidence, but it should not
be extrapolated to paper datasets.

## Updated Conclusion

The benchmark is finished as a bounded internal benchmark app under the accepted
limitation. The correct next engineering target is not another speedup claim; it
is a paper-dataset-capable RTDL lowering:

1. Keep the engine app-agnostic.
2. Add a segmented/streamed RT-Graph triangle-counting lowering in Python/CuPy
   or a reusable partner primitive.
3. Avoid global materialization of all two-hop relations.
4. Preserve the same generic engine contract: device columns for rays,
   triangles, weights, and scalar reductions.
5. Re-run the paper-dataset matrix after the segmented path exists.

The closeout claim boundary is:

RTDL reproduces RT-Graph-style triangle-counting correctness on small and
medium paper datasets through a generic OptiX primitive path, but the current
unsegmented lowering does not scale to the largest RT-Graph paper datasets on
the tested 24 GB A5000 pod. RAPIDS cuGraph is currently the strongest
end-to-end baseline on the real paper datasets. No paper-dataset speedup claim
is authorized.
