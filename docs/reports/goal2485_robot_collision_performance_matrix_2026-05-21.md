# Goal2485 Robot Collision Performance Matrix

Date: 2026-05-21

Status: Goal2485 is complete.

## Scope

Goal2485 collects bounded internal evidence for the robot-collision benchmark
after Goal2484 defined the prepared repeat protocol.

This is internal evidence only. A public speedup claim is not authorized, and
authors-code comparison is not authorized.

## Protocol

All rows use:

```text
dataset: scaled
warmup rule: drop warmup rows and report tail medians
```

Local Mac artifact:

```text
docs/reports/goal2485_robot_collision_perf_matrix_local_2026-05-21.json
```

Pod artifact:

```text
docs/reports/goal2485_robot_collision_perf_matrix_pod/summary.json
```

Pod access used:

```text
ssh root@69.30.85.236 -p 22190 -i ~/.ssh/id_ed25519_rtdl_codex
```

Pod environment:

```text
GPU: NVIDIA RTX A5000
Driver: 570.211.01
CUDA: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: /workspace/vendor/optix-dev/include/optix.h
Source commit: a9193856547bf692069955a3dbaf6c3e00c09b1b
```

Build evidence:

```text
make build-optix: returncode 0
goal2484/2485 py_compile: returncode 0
```

## Local Matrix

Local Mac scaled fixture:

```text
pose_count: 64
link_count: 3
obstacle_count: 16
static_obstacle_triangle_count: 32
repeats: 7
warmup: 2
```

| Row | Status | Tail Median Total |
| --- | --- | ---: |
| CPU reference | ok | 0.12501391599926137 s |
| Embree prepared | ok | 0.0024037919993133983 s |
| OptiX prepared | skipped locally | n/a |

Local Embree phase medians:

```text
prepare_build:      0.00016204100029426627
query_pack:         0.002358624999942549
traversal:          0.0000155
output_postprocess: 0.000005708000571758021
```

## Pod Matrix

Pod scaled fixture:

```text
pose_count: 256
link_count: 3
obstacle_count: 32
static_obstacle_triangle_count: 64
group_count: 768
segment_count: 6912
repeats: 9
warmup: 2
```

| Row | Status | Tail Median Total |
| --- | --- | ---: |
| CPU reference | ok | 3.5098454765975475 s |
| Embree prepared | ok | 0.04113018698990345 s |
| OptiX prepared | ok | 0.036702703684568405 s |

Pod Embree phase medians:

```text
prepare_build:      0.0073759350925683975
query_pack:         0.04044578969478607
traversal:          0.000197899
output_postprocess: 0.00009544938802719116
```

Pod OptiX phase medians:

```text
prepare_build:      0.17713521048426628
query_pack:         0.03588758036494255
traversal:          0.000129123
output_postprocess: 0.00010140612721443176
```

Both Embree and OptiX matched the Goal2481 probe reference on all measured rows.
Both reported stable signatures and prepared scene reuse.

## Interpretation

The dominant cost in the prepared native rows is still Python-side query packing,
not native traversal. On the pod matrix:

- Embree `traversal` median is about `0.000197899 s`;
- OptiX `traversal` median is about `0.000129123 s`;
- Embree total median is about `0.04113018698990345 s`;
- OptiX total median is about `0.036702703684568405 s`.

This means the next performance work, if needed, is app/runtime query-buffer
reuse or device-column handoff, not a new robot-specific native primitive.

## Claim Boundary

Goal2485 does not claim:

- public speedup;
- paper reproduction;
- authors-code comparison;
- exact solid collision;
- continuous or swept collision;
- native robot/link/pose/planner/collision APIs;
- package-install support;
- release/tag action.

The numbers are useful as internal engineering evidence for this exact sampled
probe subpath only.
