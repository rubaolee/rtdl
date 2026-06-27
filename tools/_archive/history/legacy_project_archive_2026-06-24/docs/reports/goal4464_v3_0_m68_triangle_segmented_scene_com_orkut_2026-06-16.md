# Goal4464 V3.0 M68 Triangle Segmented Scene com-orkut

Goal4464 extends the source-range segmented RT-2A1 Triangle Counting route to
the largest SNAP paper row, `com-orkut`.

Result: the route matched the expected `627,584,181` triangles on `com-orkut`
without materializing either the global two-hop relation or one global triangle
scene. This closes the largest Goal2593 RTDL OOM row as a correctness and
scalability milestone. It is not a public RTDL-vs-cuGraph, RTDL-vs-authors, or
RT-core speedup claim.

## Dataset

| Dataset | SNAP edges | Expected triangles | Binary edge file |
| --- | ---: | ---: | --- |
| `com-orkut` | 117,185,083 | 627,584,181 | `build/goal2593_snap_edges/com-orkut.edge` |

Preparation evidence:

- Downloaded `447,251,958` gzip bytes from SNAP.
- Converted `117,185,083` binary edges, `937,480,664` bytes.
- `edge_count_matches_snap=true`.

## Old Blocker

Goal2593 failed both RTDL paper-dataset routes on `com-orkut` before they could
produce a count:

| Old route | Status | Failure |
| --- | --- | --- |
| RTDL 2A1 | failed | CUDA allocation request for `68,639,445,368` bytes |
| RTDL 1A2 | failed | CUDA allocation request for `68,639,445,368` bytes |
| Authors `rt_tc` | failed | process died with `SIGKILL` after about `149.152s` |
| Authors `bs_tc` | failed | process died with `SIGKILL` after about `147.387s` |
| cuGraph | ok | `7.229s` total, `5.191s` triangle-count phase |

The current result should be read against that blocker. RTDL now has a generic
RT route that can run the largest row exactly. It is still much slower than the
old cuGraph row and therefore does not support speedup wording.
The old RTDL failure mode was specifically a 68,639,445,368-byte CUDA allocation request, not an incorrect triangle count.

## M68 Route

The app route is `rt_graph_2a1_segmented_scene_generic_rt`.

The app partner builds a CuPy directed CSR and a per-directed-edge two-hop count
estimate. The RTDL engine still receives generic `Triangle3D` primitives,
generic `Ray3D` probes, and a weighted any-hit sum over a prepared OptiX scene.
No graph-specific native ABI or graph-specific OptiX program was added.

Two probes were important:

- `--scene-max-directed-edges 8000000` failed at OptiX triangle-scene
  preparation with `CUDA driver error: out of memory`.
- `--scene-max-directed-edges 4000000` failed the same way.
- `--scene-max-directed-edges 2000000` passed and is now the conservative
  default for the segmented-scene app and paper-dataset runner.

In short, 8M and 4M directed-edge scene caps still OOM on this row, while the
2M cap passes.

Formal command:

```bash
python3 scripts/v3_0_m66_triangle_segmented_paper_dataset_measure.py \
  --input com_orkut build/goal2593_snap_edges/com-orkut.edge 627584181 \
  --mode segmented_scenes \
  --goal 4464 \
  --milestone v3_0_m68 \
  --warmup 1 \
  --repeat 3 \
  --segment-max-two-hop-rows 5000000 \
  --scene-max-directed-edges 2000000 \
  --hardware 'RTX 4000 Ada pod' \
  --output docs/reports/goal4464_v3_0_m68_triangle_segmented_scene_com_orkut_2026-06-16.json
```

## Measured Result

| Field | Value |
| --- | ---: |
| Observed triangles | 627,584,181 |
| Expected triangles | 627,584,181 |
| Directed-edge triangle primitives | 117,117,316 |
| Duplicate two-hop logical rays | 8,579,930,671 |
| Source-range scenes | 59 |
| Ray segments | 1,744 |
| Max directed edges per scene | 2,000,000 |
| Max two-hop rows in one scene | 279,026,541 |
| Max two-hop rows per ray segment | 5,000,000 |

Measured timing on the RTX 4000 Ada pod, warmup 1 and repeat 3:

| Phase | Time |
| --- | ---: |
| Build CuPy contract | 3.889s |
| Plan segmented source/ray ranges | 28.885s |
| Prepare scenes, measured-run median | 0.713s |
| Build triangle columns, measured-run median | 0.014s |
| Build duplicate-ray segments, measured-run median | 6.752s |
| RT query traversal, measured-run median | 19.013s |
| Total wall time including warmup | 140.037s |

The timing says something precise: RT traversal over the segmented generic
ray/triangle contract is not the only cost center. The dominant remaining debt
is app-side planning and repeated duplicate-ray segment construction, followed
by the RT traversal itself. That is a V3 optimization target, not a claim that
the current generic RT route beats specialized graph systems.

## Claim Boundary

Allowed:

- RTDL V3 can express the RT-Graph RT-2A1 shape with generic ray/triangle
  primitives plus an app-owned CuPy partner.
- The route now runs `com-lj`, `soc-LiveJournal1`, and `com-orkut` without
  global two-hop summary materialization.
- The source-range segmented variant also avoids one global triangle scene.

Blocked:

- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording.
- RTDL beats authors-code wording.
- Paper-system reproduction wording.
- Automatic CuPy-vs-Numba partner selection.
- Graph-specific native engine logic.

Next work is a same-contract comparison packet for the now-passing rows and a
targeted optimization pass on planning and duplicate-ray construction.

## Evidence

- `docs/reports/goal4464_v3_0_m68_triangle_segmented_scene_com_orkut_2026-06-16.json`
- `docs/reports/goal4464_snap_prepare_com_orkut_2026-06-16.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_rtdl.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_author_rt.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_author_bs.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_cugraph.json`
