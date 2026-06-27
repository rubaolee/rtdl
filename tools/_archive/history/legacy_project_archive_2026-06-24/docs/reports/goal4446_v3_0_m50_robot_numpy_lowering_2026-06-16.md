# Goal4446 / V3.0 M50 Robot Collision NumPy Lowering

Status: `accept-with-boundary`

M50 closes the largest robot-collision setup debt recorded by Goal4428/M31. M31 already showed a strong same-contract traversal win for OptiX over Embree, but cold setup still paid Python-heavy app lowering and prepared query descriptor construction. M50 keeps the same generic `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1` contract and replaces the largest Python object path with vectorized NumPy endpoint arrays plus NumPy-backed host query buffers.

This is a cold/setup and query-lowering optimization. It is not a new robot-specific native ABI, not a planner claim, not true zero-copy, and not a public whole-app speedup claim.

## What Changed

| Piece | M31 path | M50 path |
|---|---|---|
| App lowering | Python tuples of per-segment endpoints plus optional `ProbeGroup` metadata | `lowering_mode="numpy_arrays"` builds `(N, 3)` float64 start/end arrays and can skip app-level group metadata for timing/summary probes |
| Query packing | Python loop creates millions of `_RtdlSegment3D` ctypes records | NumPy structured array fast path creates `RtdlSegment3D` host records vectorized |
| Group offsets | Python list to ctypes uint32 array | NumPy uint32 offset fast path |
| Native contract | unchanged generic grouped finite 3D segment any-hit flags | unchanged generic grouped finite 3D segment any-hit flags |
| Claim boundary | no robot/planner/swept/exact-solid claim | same |

## Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Artifact:

```text
docs/reports/goal4446_v3_0_m50_robot_numpy_lowering_xlarge_2026-06-16.json
```

Baseline artifact:

```text
docs/reports/goal4428_v3_0_m31_robot_collision_prepared_any_hit_refresh_xlarge_2026-06-16.json
```

Dataset and contract are unchanged:

- 262,144 poses
- 8,192 obstacles
- 4 links
- 1,048,576 groups
- 9,437,184 query segments
- 16,384 static obstacle triangles
- warmup 1, repeat 5 for both Embree and OptiX
- same compact flag signature hash across backends
- same flagged group count: 345,374

## Results

| Backend | App lowering M31 | App lowering M50 | Improvement | Prepared query build M31 | Prepared query build M50 | Improvement | Prepared total median M31 | Prepared total median M50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Embree | 17.795s | 2.783s | 6.4x | 46.286s | 0.409s | 113.2x | 1.168s | 1.153s |
| OptiX | 14.261s | 0.535s | 26.7x | 48.057s | 0.426s | 112.8x | 0.630s | 0.610s |

The prepared hot traversal comparison remains consistent:

| Metric | Embree | OptiX | Embree / OptiX |
|---|---:|---:|---:|
| Traversal median | 0.417235s | 0.061122s | 6.83x |
| Total prepared-buffer run median | 1.152659s | 0.610302s | 1.89x |
| Total measured window | 4.610616s | 2.456390s | not a speedup metric |

## Interpretation

The old setup cost was not inherent to RTDL's generic collision primitive. It was mostly Python-side materialization: endpoint tuples, per-segment ctypes record construction, and group offset copying. M50 removes the largest part of that overhead without changing the native engine contract.

For the xlarge robot-collision fixture, prepared query construction drops from about 46-48 seconds to about 0.41-0.43 seconds. App lowering also drops sharply, especially on the OptiX row where the second backend benefits from already-hot Python/NumPy imports and memory allocator state. The hot prepared-buffer totals stay close to M31, which is what we want: this milestone optimizes cold/setup staging, not the traversal kernel itself.

The path still uses host-owned query buffers for the Embree/OptiX prepared-buffer comparison. The descriptor now records `numpy_structured_host_rtdl_segment3d_array` and `numpy_host_uint32_offsets`, but `true_zero_copy_authorized` remains false.

## Allowed Wording

The robot-collision benchmark now has a vectorized NumPy lowering path for the same generic prepared grouped-segment any-hit contract. On the RTX 4000 Ada xlarge fixture, this cuts prepared query descriptor construction by about 113x while preserving the M31 same-contract Embree/OptiX flag signature and flagged-count parity.

## Forbidden Wording

Do not claim a robot-specific native API, continuous collision detection, exact solid collision, planner acceleration, true zero-copy, paper reproduction, or public whole-app speedup from M50. The promoted evidence remains a generic sampled grouped-segment any-hit contract.
