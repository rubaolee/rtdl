# Goal2631 Triangle Counting Generic RT Path

## Result

The triangle-counting benchmark matrix no longer uses the older `--mode run`
graph-kernel fallback for the promoted Embree/OptiX comparison. The matrix now
uses the RT-Graph-style `rt_graph_2a1_generic_rt` path:

- App preprocessing builds the RT-Graph degree-oriented contract and RT-2A1
  relation mapping.
- The engine sees only generic `Triangle3D` primitives, generic `Ray3D` probes,
  and integer ray weights.
- OptiX uses the generic prepared 3-D ray/triangle weighted any-hit summary
  primitive with CuPy-owned device columns.
- No graph- or triangle-count-specific native engine ABI was added.

This fixes the immediate benchmark-front-door problem: triangle counting was
previously measured through a host-indexed graph fallback row, even though the
benchmark already had a paper-shaped generic RT mapping.

## Pod Evidence

Pod command supplied by the user:

```text
ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519
```

Actual key used from this Mac:

```text
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Pod checkout:

```text
/root/rtdl_goal2627/rtdl
```

Validated commit:

```text
ca8d96a7dbea7f1e3f6a566c2a0218f062710bb6
```

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --only-app triangle_counting \
  --artifact-dir /root/rtdl_goal2627/triangle_goal2631_standard \
  --timeout-sec 900
```

Artifacts copied into the repo:

- `docs/reports/goal2631_triangle_generic_rt_path_pod/summary.json`
- `docs/reports/goal2631_triangle_generic_rt_path_pod/summary.md`

## Performance

Standard generated workload: 5,000 K4 cliques, binary RT-Graph-style edge file,
20,000 triangle-count oracle result, warmup 2, repeat 12.

| Backend | Path | Query median |
| --- | --- | ---: |
| Embree | generic RT-2A1 rows, host graph preprocessing outside metric | 0.054287 s |
| OptiX | generic prepared 3-D ray/triangle weighted any-hit summary, CuPy device columns | 0.000326906 s |

OptiX speedup on the measured backend query subpath: 166.06x vs Embree.

Correctness:

- Embree matched the oracle triangle count.
- OptiX matched the oracle triangle count.
- OptiX payload reports `rt_core_accelerated=true` for the generic ray/triangle
  subpath.

## Boundary

This is not a broad paper-system or whole-app speedup claim. The measured
metric intentionally excludes graph preprocessing and geometry lowering, so it
is a backend-query subpath comparison. The full RT-Graph paper dataset problem
still needs segmented/streamed lowering to avoid global two-hop materialization
on the largest graphs.

The key design correction is still valid: the benchmark now exercises RT cores
through an app-agnostic primitive instead of relying on graph-specific fallback
metadata.
