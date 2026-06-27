# V4 Goal4763 Triangle Counting `com-dblp` Paper-Dataset Readout

Status: `paper_dataset_seconds_scale_triangle_counting_complete`

## Why This Run Exists

The earlier Triangle Counting evidence used a synthetic K4 clique-ladder fixture.
Repeating that fixture made timing more stable, but it did not answer whether
RTDL performs on an original RT-Graph paper dataset.

This run fixes that for the smallest Triangle Counting dataset from the
RT-Graph paper: `com-dblp`.

## Dataset

| Field | Value |
| --- | ---: |
| Dataset | `com-dblp` |
| Source | SNAP `com-dblp.ungraph.txt.gz` |
| Paper nodes | `317,080` |
| Paper edges | `1,049,866` |
| Paper triangles | `2,224,385` |
| Converted RTDL binary edges | `1,049,866` |
| Duplicate/self edges removed during conversion | `0` |
| Current synthetic fixture edge count for comparison | `196,608` |

This is a real paper dataset, not the synthetic K4 fixture.

## Environment

| Field | Value |
| --- | --- |
| POD | `root@194.68.245.170 -p 22089` |
| GPU | `NVIDIA RTX A5000` |
| V2 root | `/root/rtdl_v2_14_tag` |
| V3 root | `/root/rtdl_v3_0_2_tag` |
| V4 root | `/root/rtdl_v4_candidate_pod` |
| Python | `/root/rtdl_v4_venv/bin/python` |
| Backend | NVIDIA OptiX / RT-core |
| Partner | CuPy |

Old V2/V3 tag runs used the V4 compatibility OptiX library, as required by the
current POD runbook because the POD does not contain the old OptiX SDK headers.

## Routes

| Version | Route |
| --- | --- |
| V2.14 | `rt_graph_2a1_generic_rt` |
| V3.0.2 | `rt_graph_2a1_segmented_generic_rt` |
| V4.0 | `rt_graph_2a1_segmented_generic_rt` |

V3/V4 used:

```text
--segment-ray-representation unique_weighted
--segment-query-schedule prepared_segment_replay
```

## Correctness And Scale

| Version | Weighted triangle count | Matches paper count | Primitives | Physical rays | Logical rays | Segments |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| V2.14 | `2,224,385` | yes | `1,006,685` | `3,413,500` | n/a | n/a |
| V3.0.2 | `2,224,385` | yes | `1,006,685` | `3,413,520` | `5,413,528` | `6` |
| V4.0 | `2,224,385` | yes | `1,006,685` | `3,413,520` | `5,413,528` | `6` |

Independent RTDL contract/oracle summary:

| Field | Value |
| --- | ---: |
| Original edge count | `1,049,866` |
| Compacted vertex count | `317,080` |
| Triangle count | `2,224,385` |
| 2A1 two-hop ray count | `3,413,500` |
| Duplicate two-hop relation count | `5,413,528` |

## Seconds-Scale Result (`repeat=1000`)

This is the primary result because it is both paper-dataset and seconds-scale.

| Version | Query total sec | Query median ms | Pipeline total sec | Count ok |
| --- | ---: | ---: | ---: | --- |
| V2.14 | `11.160` | `6.384` | `12.903` | yes |
| V3.0.2 | `2.223` | `2.189` | `4.109` | yes |
| V4.0 | `2.156` | `2.148` | `4.250` | yes |

| Ratio | Query total | Query median | Pipeline total |
| --- | ---: | ---: | ---: |
| V3.0.2 / V2.14 | `5.020x` | `2.917x` | `3.140x` |
| V4.0 / V2.14 | `5.177x` | `2.972x` | `3.036x` |
| V4.0 / V3.0.2 | `1.031x` | `1.019x` | `0.967x` |

## Short Repeat Cross-Check (`repeat=3`)

| Version | Query total ms | Query median ms | Pipeline total ms | Count ok |
| --- | ---: | ---: | ---: | --- |
| V2.14 | `20.701` | `6.897` | `1771.208` | yes |
| V3.0.2 | `7.763` | `2.459` | `1769.797` | yes |
| V4.0 | `7.017` | `2.284` | `1706.483` | yes |

| Ratio | Query total | Query median | Pipeline total |
| --- | ---: | ---: | ---: |
| V3.0.2 / V2.14 | `2.667x` | `2.805x` | `1.001x` |
| V4.0 / V2.14 | `2.950x` | `3.020x` | `1.038x` |
| V4.0 / V3.0.2 | `1.106x` | `1.076x` | `1.037x` |

The short-repeat row is retained only as a cross-check. The release-facing
Triangle paper-dataset number should use the seconds-scale `repeat=1000` row.

## Interpretation

This result is materially stronger than the previous synthetic Triangle row:

- It uses a real RT-Graph paper dataset, `com-dblp`.
- It matches the paper triangle count exactly: `2,224,385`.
- It gives seconds-scale timing on the same dataset and same hardware.
- V4/V2.14 query-total speedup is `5.177x`.
- Most of the large speedup is historical V3 route evolution; V4 over V3 is only
  `1.031x` on query total and slightly slower on total pipeline.

The honest user-facing wording is:

```text
On the RT-Graph paper `com-dblp` dataset, RTDL V4 preserves the modern segmented
Triangle Counting route and runs the RT-core query workload 5.18x faster than
the V2.14 generic route on the same NVIDIA RTX A5000, with exact triangle-count
parity. The incremental V4-over-V3 gain is small, about 1.03x on query total.
```

Do not word this as:

```text
V4 invented the entire 5.18x Triangle speedup.
```

That would be false. The correct provenance is V2.14 -> V3 route evolution plus
V4 preservation/modest improvement.

## Boundary

This run does not claim:

- author `rt_tc` / `bs_tc` binary reproduction;
- all RT-Graph paper datasets reproduced;
- broad all-app V4 speedup;
- public V4 release authorization.

It does establish that the Triangle Counting row is no longer toy-only: RTDL has
now run a real RT-Graph paper dataset with exact count parity and seconds-scale
timing.

## Evidence

- `future/v4/evidence/v4_goal4762_triangle_com_dblp_paper_2026-06-26/summary.json`
- `future/v4/evidence/v4_goal4762_triangle_com_dblp_paper_2026-06-26/raw/`
- `future/v4/evidence/v4_goal4763_triangle_com_dblp_paper_repeat1000_2026-06-26/summary.json`
- `future/v4/evidence/v4_goal4763_triangle_com_dblp_paper_repeat1000_2026-06-26/raw/`
- `scripts/v4_goal4762_triangle_com_dblp_pod_run.sh`
