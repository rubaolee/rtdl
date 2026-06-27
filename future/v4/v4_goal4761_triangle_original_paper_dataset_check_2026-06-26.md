# V4 Goal4761 Triangle Counting Original Paper Dataset Check

Status: `paper_dataset_check_confirms_current_fixture_is_not_paper_scale`

## Question

The objection is valid: increasing `repeat` makes the timed workload seconds-scale,
but it does not answer whether RTDL has reproduced the original RT-Graph paper
data scale or graph structure.

This check answers whether the original paper/authors used larger datasets.

## Answer

Yes. The original RT-Graph paper and author repository use real graph datasets
that are much larger and more realistic than the current RTDL synthetic
`k4_32768.edgebin` Triangle Counting fixture.

The current RTDL Triangle follow-up input has:

| Current RTDL fixture | Value |
| --- | ---: |
| Input | `/root/v4_goal4753_final_matrix/k4_32768.edgebin` |
| Primitive / directed edge count | `196,608` |
| Oracle triangle count | `131,072` |
| Nature | synthetic K4 clique ladder / RT-Graph-shaped fixture |

The RT-Graph paper Table 3 lists these Triangle Counting datasets:

| Paper dataset | Nodes | Edges | Triangles | Edge count vs current RTDL fixture |
| --- | ---: | ---: | ---: | ---: |
| `com-dblp` | `317,080` | `1,049,866` | `2,224,385` | `5.34x` |
| `com-youtube` | `1,134,890` | `2,987,624` | `3,056,386` | `15.20x` |
| `cit-Patents` | `3,774,768` | `16,518,948` | `7,515,023` | `84.02x` |
| `wiki-Talk` | `2,394,385` | `5,021,410` | `9,203,519` | `25.54x` |
| `com-lj` | `3,997,962` | `34,681,189` | `177,820,130` | `176.40x` |
| `soc-LiveJournal1` | `4,847,571` | `68,993,773` | `285,730,264` | `350.92x` |
| `com-orkut` | `3,072,441` | `117,185,083` | `627,584,181` | `596.03x` |

The author repository README separately lists the same Triangle Counting dataset
table and says the datasets can be downloaded from the Stanford Large Network
Dataset Collection.

## Local Workspace Check

`scratch/external/RT-Graph` is not present in the current local workspace.

The RTDL triangle-counting app does contain the intended author-code command
shape:

```text
cd scratch/external/RT-Graph/tc && ./bin/rt_tc dataset/com-dblp/com-dblp.ungraph.edge.pd 0
cd scratch/external/RT-Graph/tc && ./bin/bs_tc dataset/com-dblp/com-dblp.ungraph.edge.pd 0
```

It also records the future gate:

```text
Before any performance wording, reproduce the RT-Graph triangle-counting
authors-code contract where possible, then compare same-input RTDL
triangle-counting outputs against RT-Graph bs_tc and rt_tc baselines.
```

That gate has not been satisfied by the current synthetic `k4_32768` run.

## Interpretation

The Goal4760 `repeat=10000` Triangle run was useful for one thing only:
it showed that the current synthetic workload's V3/V4-over-V2.14 speedup is not
just a noisy sub-millisecond measurement artifact.

It does not prove paper-scale Triangle Counting performance.

For paper-grade evidence, RTDL must run at least `com-dblp` under the same
semantic route, and preferably add `com-youtube`, `cit-Patents`, and `wiki-Talk`
before making any user-facing claim that resembles RT-Graph paper reproduction.

## Required Next Gate

Before using Triangle Counting as a strong public V4 performance claim:

1. Fetch or prepare at least `com-dblp` from the author/SNAP pipeline.
2. Convert or load it into the RTDL Triangle Counting route without changing
   semantics.
3. Run V2.14, V3.0.2, and V4.0 on the same NVIDIA RT-core hardware.
4. Report correctness parity, total edges, triangle count, route, backend,
   hot time, elapsed time, memory behavior, and whether the comparison is
   author-dataset, SNAP-dataset, or synthetic.
5. Keep the current synthetic result as a regression/stability fixture, not as
   the paper-scale proof.

## Sources Checked

- Paper PDF: `https://xiaodongzhang1911.github.io/Zhang-papers/TR-25-2.pdf`
- Author repository: `https://github.com/xiaozxiong/RT-Graph`
- RTDL local app metadata:
  `examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- RTDL seconds-scale synthetic follow-up:
  `future/v4/v4_goal4760_triangle_1_10s_scale_readout_2026-06-26.md`
