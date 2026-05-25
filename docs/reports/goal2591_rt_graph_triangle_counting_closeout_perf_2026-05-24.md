# Goal2591 RT-Graph Triangle Counting Closeout Performance

Date: 2026-05-24

## Decision

Superseded by
`docs/reports/goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md`.
This report remains useful for synthetic K4 evidence only; it should not be used
as the final closeout for the RT-Graph triangle-counting benchmark app.

Under the synthetic K4-only scope originally tested here, the RT-Graph
triangle-counting benchmark app appeared ready to finalize as an internal
benchmark app, with the current claim boundary preserved. That conclusion no
longer applies to the stronger paper-dataset standard. The K4 evidence has
same-input correctness and performance comparisons against:

- RT-Graph authors' RT implementation: `scratch/external/RT-Graph/tc/bin/rt_tc`
- RT-Graph CUDA/GPU triangle-counting baseline: `scratch/external/RT-Graph/tc/bin/bs_tc`
- RAPIDS cuGraph `triangle_count` as a well-known GPU graph-library baseline
- Indexed PostgreSQL relational join baseline
- RTDL Python+CuPy+generic OptiX 3-D device-column path

All tested systems returned the same triangle counts on the K4 clique inputs.

## Environment

Pod SSH:

```text
ssh root@203.57.40.104 -p 10001 -i ~/.ssh/id_ed25519_rtdl_codex
```

Hardware/software:

- GPU: NVIDIA RTX A5000
- Driver: 550.127.05
- CUDA: 12.8 toolkit, with `/usr/local/cuda-12.8/compat` enabled for NVRTC/PTX loading
- OptiX SDK: `/root/vendor/NVIDIA-OptiX-SDK-7.7.0-linux64-x86_64`
- PostgreSQL: 16.14
- RAPIDS cuGraph: 26.04.000
- RAPIDS cuDF: 26.04.000

Raw evidence:

- `docs/reports/goal2591_rt_graph_rtdl_author_baselines_r7_2026-05-24.json`
- `docs/reports/goal2591_rt_graph_postgres_baseline_2026-05-24.json`
- `docs/reports/goal2592_rt_graph_cugraph_baseline_r7_2026-05-24.json`

Runners:

- `scripts/goal2591_rt_graph_rtdl_author_baselines.py`
- `scripts/goal2591_rt_graph_postgres_baseline.py`
- `scripts/goal2592_rt_graph_cugraph_baseline.py`

## Same-Input Correctness

| Input | Edges | Expected triangles | RTDL | Authors `rt_tc` | GPU `bs_tc` | cuGraph | PostgreSQL |
|---|---:|---:|---:|---:|---:|---:|---:|
| K4 x 10k | 60,000 | 40,000 | 40,000 | 40,000 | 40,000 | 40,000 | 40,000 |
| K4 x 50k | 300,000 | 200,000 | 200,000 | 200,000 | 200,000 | 200,000 | 200,000 |
| K4 x 100k | 600,000 | 400,000 | 400,000 | 400,000 | 400,000 | 400,000 | 400,000 |

## App-Level Runtime Comparison

Median over 5 measured runs after 2 warmups, milliseconds.

`RTDL total` is app-level RTDL+CuPy+OptiX time. `rt_tc pipeline` is the authors'
reported preprocessing + CSR + graph-to-RT + ray construction + BVH + counting,
excluding file read. `bs_tc pipeline` is the authors' CUDA baseline preprocessing
+ CSR + GPU preprocessing + counting, excluding file read. `cuGraph total`
builds a cuDF edge dataframe, builds an undirected cuGraph graph, runs
`cugraph.triangle_count`, and reduces per-vertex counts to a total triangle
count. `PostgreSQL query` is indexed query execution time only; `PostgreSQL
setup+query` includes TSV conversion, load/dedup, index/analyze, and query
execution.

| Input | RTDL 2A1 total | RTDL 1A2 total | cuGraph total | Authors `rt_tc` pipeline | GPU `bs_tc` pipeline | PostgreSQL query | PostgreSQL setup+query |
|---|---:|---:|---:|---:|---:|---:|---:|
| K4 x 10k | 9.105 | 12.596 | 9.814 | 318.096 | 497.266 | 36.883 | 264.493 |
| K4 x 50k | 16.999 | 27.643 | 48.734 | 393.838 | 446.910 | 239.787 | 962.213 |
| K4 x 100k | 33.546 | 43.539 | 77.073 | 400.059 | 528.159 | 388.329 | 1735.459 |

Main conclusion: for this benchmark shape, RTDL's best app path is faster than
the authors' full `rt_tc` and `bs_tc` pipelines because CuPy preprocessing plus
device-column RTDL lowering avoids the authors' larger CPU preprocessing and
host/device construction costs. RTDL's best path is also faster than cuGraph on
the 50k and 100k K4 inputs; cuGraph is close on the 10k input but its graph
construction and generic `triangle_count` costs dominate as the synthetic K4
batch grows. PostgreSQL is useful as a correctness oracle but is not competitive
as a performance baseline even with indexes.

## cuGraph Timing Boundary

The cuGraph baseline is a recognizable GPU graph-library comparison, not a
paper-code implementation of the RT-Graph approach. It uses standard cuDF
ingest plus cuGraph graph construction and `triangle_count`.

| Input | cuGraph total | cuGraph graph build | cuGraph triangle_count |
|---|---:|---:|---:|
| K4 x 10k | 9.814 | 5.700 | 3.009 |
| K4 x 50k | 48.734 | 27.098 | 21.286 |
| K4 x 100k | 77.073 | 45.350 | 29.870 |

The cuGraph result strengthens the benchmark story because it adds a mature GPU
graph-library baseline. It does not replace the author-code comparisons.

## Core Timing Boundary

The app-level result should not be misread as RTDL's pure RT traversal beating
the authors' specialized trace kernels. Pure core timings show the opposite on
the trace/count microphase.

| Input | RTDL 2A1 backend | RTDL 2A1 traversal | Authors `rt_tc` RT-side prep+trace | Authors `rt_tc` trace/count only | GPU `bs_tc` GPU prep+count | GPU `bs_tc` count only |
|---|---:|---:|---:|---:|---:|---:|
| K4 x 10k | 3.233 | 0.0716 | 10.982 | 0.0523 | 12.092 | 0.0134 |
| K4 x 50k | 5.557 | 0.1640 | 87.423 | 0.1161 | 11.694 | 0.0215 |
| K4 x 100k | 7.807 | 0.2766 | 80.525 | 0.1484 | 85.206 | 0.1975 |

The fair closeout statement is:

RTDL wins the benchmark pipeline for this app because the Python+CuPy partner
preprocessing and generic device-column OptiX path reduce whole-app overhead.
The authors' specialized RT and CUDA kernels still have very low pure counting
times, and RTDL should not claim pure trace-kernel superiority.

## PostgreSQL Method

The PostgreSQL baseline used a conventional indexed normalized-edge triangle
join:

```sql
CREATE UNLOGGED TABLE raw_edges(src integer NOT NULL, dst integer NOT NULL);
CREATE UNLOGGED TABLE edges AS
  SELECT DISTINCT LEAST(src, dst) AS u, GREATEST(src, dst) AS v
  FROM raw_edges
  WHERE src <> dst;
CREATE UNIQUE INDEX edges_uv_idx ON edges(u, v);
CREATE INDEX edges_vu_idx ON edges(v, u);
ANALYZE edges;

SELECT count(*)
FROM edges e1
JOIN edges e2 ON e1.u = e2.u AND e1.v < e2.v
JOIN edges e3 ON e3.u = e1.v AND e3.v = e2.v;
```

This is not RT-Graph's degree-oriented 2A1/1A2 lowering, but it is a standard
indexed relational triangle-count contract on the same undirected input.

## Finalization Boundary

I would finalize this benchmark app now with these boundaries:

- Benchmark scope is triangle counting only.
- Authors-code comparison is available for the tested K4 synthetic inputs.
- GPU baseline comparison is `bs_tc`, the CUDA triangle-counting baseline from
  the RT-Graph authors' repository.
- Well-known GPU graph-library comparison is RAPIDS cuGraph `triangle_count`.
- PostgreSQL is retained as a correctness and database-style baseline, not as a
  competitive GPU baseline.
- Public speedup wording is still not authorized until the project-required
  external review/consensus is done.
- The native RTDL engine remains app-name-free for this path; RT-Graph-specific
  lowering stays in Python benchmark code.

Further optimization should be deferred unless the next goal is specifically
pure trace-kernel parity with the authors' specialized RT implementation.
