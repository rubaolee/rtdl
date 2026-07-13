# Goal5002 Result: Fresh LSI Compile / Pipeline Prewarm Probe

Date: 2026-07-05

## Verdict

```text
completed_fresh_lsi_compile_prewarm_probe__global_compile_removable__workspace_still_dominates
```

Goal5002 shows that the fresh LSI producer has a large generic one-time
compile / pipeline-ensure cost that can be triggered by a tiny non-RayJoin LSI
probe before the top4 RayJoin overlay route runs.

It does not show that the full fresh one-shot overlay cost disappears. If the
prewarm itself is counted inside the same one-shot command, the cost is merely
moved earlier. The product-relevant conclusion is narrower:

- RTDL has a generic global LSI pipeline / split-kernel initialization cost.
- That cost is prewarmable without a RayJoin-specific kernel or RayJoin input.
- The remaining fresh LSI producer floor is per-input workspace work.

## Goal

Goal5001 selected:

```text
target_fresh_lsi_producer_first
```

Goal5002 therefore tested the first suspected LSI sub-cost:

```text
exact_pipeline_ensure + split_kernel_ensure ~= 0.9s
```

The question was whether this cost is:

1. generic and globally reusable, therefore prewarmable; or
2. tied to the actual top4 County x Zipcode input, therefore not removable from
   the fresh LSI producer.

## Probe

Internal probe script:

```text
history/internal_docs/goal5002_lsi_compile_prewarm_probe.py
```

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Artifacts:

```text
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/baseline_no_prewarm.json
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/tiny_lsi_prewarm_then_fresh.json
```

The prewarm uses only the public generic LSI route:

```python
with base.prepare_planar_map_lsi_2d_optix(right) as lsi:
    with lsi.prepare_query(left) as query:
        columns = query.run_bounded_pair_id_device_columns(max_rows=8)
```

The tiny input has one crossing segment pair and emits one pair-id row. It does
not import `rtdsl.rayjoin_overlay`, does not use RayJoin CDB data, and does not
encode overlay semantics.

## Measurement Matrix

Both runs then execute the top4 County x Zipcode writer-free binary route:

```text
--device-columnar
--bounded-exact-lsi-device-columns
--bounded-exact-lsi-capacity 1000000
--point-location-device-face-columns
--fast-scaled-point-pack
--device-resident-carrier
```

| Case | LSI rows | descriptors | writer-free hot sec | LSI phase sec | exact pipeline ensure | split kernel ensure | compile-like total | grouped range ensure | scaled cache ensure | workspace-like total | native launch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| No prewarm | 428322 | 15014 | 5.569958 | 2.701178 | 0.556461 | 0.432257 | 0.988718 | 1.011743 | 0.696493 | 1.708235 | 0.002219 |
| Tiny generic LSI prewarm | 428322 | 15014 | 4.481890 | 1.750720 | 0.000000461 | 0.000000130 | 0.000000591 | 1.015267 | 0.731428 | 1.746695 | 0.002177 |

The tiny prewarm itself took:

```text
prewarm elapsed: 1.349097s
prewarm row count: 1
prewarm exact_pipeline_ensure: 0.453162s
prewarm split_kernel_ensure: 0.344619s
```

## Interpretation

The result is decisive for the compile / pipeline portion:

```text
top4 compile-like cost before prewarm:
  exact_pipeline_ensure + split_kernel_ensure
  = 0.556461 + 0.432257
  = 0.988718s

top4 compile-like cost after tiny generic prewarm:
  exact_pipeline_ensure + split_kernel_ensure
  = 0.000000461 + 0.000000130
  = 0.000000591s
```

So the compile-like LSI producer cost is a generic global initialization cost,
not a top4-input-specific computation cost. It can be triggered by a tiny
generic LSI run.

The remaining LSI producer after prewarm is still large:

```text
grouped_range_ensure + scaled_cache_ensure
= 1.015267 + 0.731428
= 1.746695s
```

That remaining cost is per-input workspace-like work. It did not disappear
under tiny prewarm, and it is now the main LSI target.

## What This Proves

1. A future generic RTDL LSI runtime precompile / prewarm hook is technically
   plausible.
2. The hook can be generic. It does not need RayJoin CDBs or RayJoin overlay
   semantics.
3. The previously measured `~0.9s` compile / pipeline portion of fresh LSI is
   not inherent to each top4 input.
4. The next real LSI floor is the per-input grouped range / scaled cache setup.

## What This Does Not Prove

This does not prove:

- author-performance parity;
- a new public v2.14.3 headline;
- true query-many;
- that one-shot CLI total time improves if the prewarm time is counted inside
  the same command;
- that the `~1.7s` per-input LSI workspace can be removed;
- full device-resident overlay completion;
- any RayJoin-specific RTDL core optimization.

## Generic-System Boundary

This goal made no runtime or native code changes. It used existing public /
generic LSI entry points as a probe.

The acceptable product direction is generic:

```text
prepare_planar_map_lsi_2d_optix / bounded pair-id device columns
-> generic runtime precompile / prewarm hook
-> any planar-map LSI user benefits
```

The unacceptable direction remains:

```text
RayJoin-specific top4 or overlay preload hidden in RTDL core
```

No such RayJoin-specific path was added.

## Next Goal

The recommended next goal is:

```text
Goal5003: LSI Per-Input Workspace Floor Decision
```

Questions for Goal5003:

1. Can `grouped_range_ensure + scaled_cache_ensure ~= 1.7s` be reduced by a
   generic resident workspace route?
2. If not, should v2.14.3 accept this as the fresh LSI floor?
3. Should a generic LSI runtime prewarm / precompile API be promoted as a
   separate product feature, with explicit benchmark rules that keep prewarm
   time out of only those regimes where process/service startup precompile is
   a real product behavior?

## Exit Label

```text
completed_fresh_lsi_compile_prewarm_probe__global_compile_removable__workspace_still_dominates
```
