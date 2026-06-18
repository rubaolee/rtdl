# Benchmark Evidence Index

Status: current V3.0 benchmark-app/current-route evidence map.

Use this page to understand the current ten benchmark-app route surface. It is
not a release authorization, performance leaderboard, or history tour. Previous
release packets live in [Historical Release Reports](../history/release_reports/README.md),
and the full pre-cleanup evidence ledger is archived at
[V3.0 Full Benchmark Evidence Ledger](../history/learn/benchmark_evidence_index_full_v3_0_2026-06-18.md).

For conservative performance interpretation, read the
[RT-Core Evidence Matrix](rt_core_evidence_matrix.md). A ten-app packet is not
ten broad RT-core speedup claims.

Machine-readable source:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py --json
```

Human-readable table:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py
```

Front-door dry-run:

```bash
PYTHONPATH=src:. python scripts/goal3823_current_benchmark_front_door_runner.py --dry-run
```

Scale-profile runner:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --materialize-rayjoin-public-cdb \
  --output-dir docs/reports/current_benchmark_scale_profile_rerun
```

The RayJoin public-CDB fixture is materialized only when the explicit
`--materialize-rayjoin-public-cdb` flag is present.

## Current Ten-App Rows

| App | Current front-door row | How to read it |
| --- | --- | --- |
| Hausdorff / X-HD | `hausdorff_xhd_current_optix_threshold` | Primitive-first exact nearest-witness/grouped-max route; not automatic partner-selection or broad speedup wording. |
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | Mixed-explicit route: RTDL/OptiX for prepared scalar/count slices, Numba where bounded PIP continuation is explicit; not full RayJoin paper reproduction. |
| RT-DBSCAN | `rt_dbscan_predicate_direct_status_component_signature` | OptiX fixed-radius count-threshold columns plus explicit CuPy/Numba compact component-signature continuation. |
| Robot collision | `robot_collision_prepared_grouped_segment_any_hit_numpy_lowering` | No-partner prepared grouped-segment any-hit route; sampled screening contract, not full robotics planning. |
| Contact manifold | `contact_manifold_optix_native_collect_k` | No-partner bounded witness collect path; no manifold-native ABI. |
| RayDB-style | `raydb_style_optix_count_primitive_first` | Primitive-first fused grouped reductions; partner rows are only for unfused continuations. |
| Barnes-Hut | `barnes_hut_mixed_explicit_cpu_numba_cuda_or_optix_numba` | Mixed explicit route: fused CPU/Numba or fused Numba CUDA is current scale-dependent guidance; prepared RTDL/OptiX+Numba is evidence, not a Barnes-Hut RT-core speedup claim. |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | Prepared AABB index query slice; not full mutable LibRTS. |
| RTNN | `rtnn_mixed_exact_aggregate_full_batch_or_graph_partner_bridge` | Exact aggregate and partner-bridge routes; public speedup and same-output author claims still blocked where evidence does not authorize them. |
| Triangle counting | `triangle_counting_optix_native_summary` | Current route uses accepted segmented/streamed-lowering limits; cuGraph, author pure-kernel superiority, and automatic partner selection remain blocked. |

## Current Release Evidence

- [v3.0.1 release package](../release_reports/v3_0_1/README.md)
- [v3.0.1 release statement](../release_reports/v3_0_1/release_statement.md)
- [v3.0.1 support matrix](../release_reports/v3_0_1/support_matrix.md)
- [v3.0.1 public wording boundaries](../release_reports/v3_0_1/public_wording_boundaries.md)
- [v3.0.1 final closeout](../release_reports/v3_0_1/final_closeout.md)
- [V3.0 app-author implementation strategy](v3_0_app_author_implementation_strategy.md)
- [Goal4536 V3 internal completion packet](../reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md)
- [Goal4538 V3 completion review consensus](../reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md)
- [Goal4544 V3 app-author strategy doc](../reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.md)
- [Goal4546 current V3 test matrix gate](../reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.md)
- [Goal4614 V3 current-scope completion gate](../reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md)

Important cross-cutting reports include
`goal4215_current_benchmark_scale_profile_after_rtdbscan_policy`, Goal4266
large-scale CuPy/Numba partner comparison, Goal3823 current benchmark
front-door registry, and Goal3828 current benchmark scale-profile registry.

## Audit Anchor Ledger

This ledger is for tests and reviewers, not the normal learning path. Read the
ten-app table first; open the archived full ledger only when you need the old
chronology.

Barnes-Hut anchors: Goal4438 Barnes-Hut prepared aggregate-frontier partner
scale ladder; Goal4439 Barnes-Hut prepared aggregate-frontier app mode;
Goal4440 Barnes-Hut host baselines for the prepared app route; Goal4441
Barnes-Hut host Numba CPU baselines; Goal4442 Barnes-Hut fused Numba CPU
frontier baseline; Goal4448 Barnes-Hut Numba CUDA fused subtree prototype;
Goal4449 reusable aggregate-tree fused Numba CUDA partner API; Goal4450
Barnes-Hut fused Numba CUDA app front-door mode; Goal4458 Barnes-Hut current
route rerank; Goal4483 Barnes-Hut large-scale rerank; Goal4497 Barnes-Hut
RT-native fused feasibility; Goal4512 Barnes-Hut clean-target audit; Goal4517
aggregate-tree fused RT-native contract; Goal4518 Barnes-Hut device-column
RT-core boundary audit; Goal4523 Barnes-Hut RT-native symbol gap; Goal4525
Barnes-Hut RT-native Python wrapper gate; Goal4526 Barnes-Hut RT-native
fail-closed ABI; Goal4527 Barnes-Hut RT-native traversal semantic gate;
Goal4541 Barnes-Hut current route closure gate. Numba wins the prepared
RTDL/OptiX device-column partner route for the measured prepared
aggregate-frontier contract; this is not a universal Numba or RT-core claim.

RTNN anchors: Goal4443 RTNN large app-front-door graph bridge; Goal4459 RTNN
clustered app-front-door graph bridge; Goal4460 RTNN shell app-front-door
graph bridge; Goal4498 RTNN paper dataset targets; Goal4499 RTNN KITTI
paper-family recipe; Goal4500 RTNN KITTI same-input RTDL gate; Goal4501 RTNN
author same-input comparison; Goal4502 RTNN full-batch route refresh; Goal4503
RTNN point-file app front door; Goal4504 RTNN execution-path policy refresh;
Goal4505 RTNN partner-continuation chunk plan; Goal4506 RTNN chunked partner
runtime; Goal4507 RTNN chunked distribution matrix; Goal4508 RTNN clean-target
closeout; Goal4509 prepared graph chunk executor.

RT-DBSCAN anchors: Goal4452 RT-DBSCAN route decision refresh; Goal4484
RT-DBSCAN compact-signature route matrix; Goal4485 RT-DBSCAN 1M
compact-signature route matrix; Goal4486 RT-DBSCAN self-query count-threshold
optimization; Goal4488 RT-DBSCAN direct-status row-columnization; Goal4489
RT-DBSCAN direct-status caller-owned point columns; Goal4490 RT-DBSCAN
point-column app mode; Goal4491 coordinate-column helper build cleanup;
Goal4495 RT-DBSCAN 2M point-column reuse; Goal4496 RT-DBSCAN 2M point-column
prepare profiles; Goal4510 RT-DBSCAN clean-target audit; Goal4519 RT-DBSCAN
chunk-handle gate; Goal4520 RT-DBSCAN chunk-handle smoke; Goal4528 RT-DBSCAN
prepared graph capture.

Triangle anchors: Goal4444 Triangle Numba direct-binary summary refresh;
Goal4453 Triangle Numba device geometry; Goal4454 Triangle Numba summary fast
paths; Goal4455 Triangle partner rerank after M58; Goal4456 Triangle bounded-id
remap fast path; Goal4457 Triangle CuPy no-host-column summary route; Goal4492
Triangle source-group unique feasibility; Goal4493 Triangle local-hash unique
prototype; Goal4494 Triangle integrated local-hash candidate; Goal4511 Triangle
Counting clean-target audit; Goal4521 Triangle unique-count gate; Goal4530
Triangle device key-payload merge; Goal4531 Triangle weighted replay graph
capture; Goal4539 Triangle capture-mode audit; Goal4540 Triangle non-graph
stream closure gate.

Primitive/current-route anchors: Goal4513 primitive app clean-target audit;
Goal4514 RayJoin mixed-explicit clean-target audit; Goal4515 all benchmark app
clean-target closeout; Goal4516 prepared graph chunk adoption gate; Goal4522
route-adequacy consistency; Goal4524 benchmark implementation queue; Goal4533
V3 claim-scope closeout; Goal4534 V3 current app completion gate; Goal4535 V3
completion readiness audit; Goal4542 post-closure surface audit; Goal4543
major performance target refresh; Goal4547 source-tree doctor V3 matrix hint;
Goal4548 legacy full runner repair.

V4 preparatory embedding anchors are historical/preparatory only and are not
V3.0 release scope: Goal4549 embeddability strategy intake; Goal4550 C ABI
draft; Goal4551 C ABI header compile smoke; Goal4552 C ABI stub library;
Goal4553 C ABI C client smoke; Goal4554 C ABI Makefile build target; Goal4555
C ABI header boundary refresh; Goal4556 C ABI exported symbol audit; Goal4557
C ABI fail-closed query entrypoints; Goal4558 C ABI host AABB2 query proof;
Goal4559 C ABI example client; Goal4560 C ABI embedding README; Goal4561 C ABI
AABB2 contract doc; Goal4562 embeddability status refresh; Goal4563 C ABI
AABB2 negative runtime; Goal4564 C ABI source-tree doctor surface; Goal4565 C
ABI stability policy; Goal4566 C ABI symbol manifest; Goal4567 C ABI AABB2
layout validation; Goal4568 zero-copy interop contract; Goal4569 embeddability
progress gate; Goal4570 C ABI ownership/threading contract; Goal4571 C ABI
AABB2 result ordering; Goal4572 C ABI doctor docs surface; Goal4573 C ABI
backend/runtime fail-closed; Goal4574 C ABI patch version refresh; Goal4575 C
ABI version negotiation; Goal4576 C ABI staging bundle; Goal4577 C ABI
pkg-config stage; Goal4578 C ABI capability queries; Goal4579 C ABI
direct-link example; Goal4580 embeddability readiness packet; Goal4581 C ABI
Python ctypes example; Goal4582 C ABI Python ctypes AABB2 query; Goal4583
embeddability readiness refresh; Goal4584 source-tree doctor ctypes surface;
Goal4585 C ABI staging inventory refresh; Goal4586 C ABI pkg-config
relocatable stage; Goal4587 C ABI stage archive; Goal4588 source-tree doctor
stage archive; Goal4589 embeddability shipping readiness refresh; Goal4590
embeddability architecture status refresh; Goal4591 C ABI host external runtime
gate; Goal4592 C ABI CUDA buffer metadata gate; Goal4593 Python ctypes CUDA
metadata bridge; Goal4594 embeddability metadata readiness refresh; Goal4595 C
ABI prefix stage; Goal4596 source-tree doctor prefix stage; Goal4597
prefix-stage Python ctypes smoke; Goal4598 embeddability architecture prefix
status; Goal4599 Python ctypes layout audit; Goal4600 C ABI CMake prefix
stage; Goal4601 embeddability delivery status refresh; Goal4602 C ABI archive
CMake smoke; Goal4603 embeddability delivery archive CMake refresh; Goal4604
toolchain support matrix; Goal4605 binding/device interop matrix; Goal4606
neutral buffer protocol gate; Goal4607 Python ctypes DLPack-like metadata
bridge; Goal4608 archive-stage Python ctypes smoke; Goal4609 archive-stage C
examples smoke; Goal4610 C ABI independent-context concurrency smoke; Goal4611
C ABI last-error diagnostics smoke; Goal4612 C ABI last-error staged example;
Goal4613 prefix-stage C examples smoke.

## Exact Audit Anchors

These one-line anchors keep older verification checks stable after the
human-readable ledger was shortened.

- Numba wins the prepared RTDL/OptiX device-column partner route
- public speedup and same-output author claims still blocked
- Goal4452 RT-DBSCAN route decision refresh
- Goal4484 RT-DBSCAN compact-signature route matrix
- Goal4485 RT-DBSCAN 1M compact-signature route matrix
- Goal4486 RT-DBSCAN self-query count-threshold optimization
- Goal4488 RT-DBSCAN direct-status row-columnization
- Goal4489 RT-DBSCAN direct-status caller-owned point columns
- Goal4490 RT-DBSCAN point-column app mode
- Goal4491 coordinate-column helper build cleanup
- Goal4492 Triangle source-group unique feasibility
- Goal4493 Triangle local-hash unique prototype
- Goal4494 Triangle integrated local-hash candidate
- Goal4495 RT-DBSCAN 2M point-column reuse
- Goal4496 RT-DBSCAN 2M point-column prepare profiles
- Goal4497 Barnes-Hut RT-native fused feasibility
- Goal4498 RTNN paper dataset targets
- Goal4499 RTNN KITTI paper-family recipe
- Goal4500 RTNN KITTI same-input RTDL gate
- Goal4501 RTNN author same-input comparison
- Goal4502 RTNN full-batch route refresh
- Goal4504 RTNN execution-path policy refresh
- Goal4505 RTNN partner-continuation chunk plan
- Goal4506 RTNN chunked partner runtime
- Goal4507 RTNN chunked distribution matrix
- Goal4508 RTNN clean-target closeout
- Goal4509 prepared graph chunk executor
- Goal4510 RT-DBSCAN clean-target audit
- Goal4511 Triangle Counting clean-target audit
- Goal4512 Barnes-Hut clean-target audit
- Goal4513 primitive app clean-target audit
- Goal4514 RayJoin mixed-explicit clean-target audit
- Goal4515 all benchmark app clean-target closeout
- Goal4516 prepared graph chunk adoption gate
- Goal4517 aggregate-tree fused RT-native contract
- Goal4518 Barnes-Hut device-column RT-core boundary audit
- Goal4519 RT-DBSCAN chunk-handle gate
- Goal4520 RT-DBSCAN chunk-handle smoke
- Goal4521 Triangle unique-count gate
- Goal4522 route-adequacy consistency
- Goal4523 Barnes-Hut RT-native symbol gap
- Goal4524 benchmark implementation queue
- Goal4525 Barnes-Hut RT-native Python wrapper gate
- Goal4526 Barnes-Hut RT-native fail-closed ABI
- Goal4527 Barnes-Hut RT-native traversal semantic gate
- Goal4528 RT-DBSCAN prepared graph capture
- Goal4530 Triangle device key-payload merge
- Goal4531 Triangle weighted replay graph capture
- Goal4533 V3 claim-scope closeout
- Goal4534 V3 current app completion gate
- Goal4535 V3 completion readiness audit
- Goal4536 V3 internal completion packet
- Goal4538 V3 completion review consensus
- Goal4539 Triangle capture-mode audit
- Goal4540 Triangle non-graph stream closure gate
- Goal4541 Barnes-Hut current route closure gate
- Goal4542 post-closure surface audit
- Goal4543 major performance target refresh
- Goal4546 current V3 test matrix gate
- Goal4547 source-tree doctor V3 matrix hint
- Goal4548 legacy full runner repair
- Goal4549 embeddability strategy intake
- Goal4550 C ABI draft
- Goal4551 C ABI header compile smoke
- Goal4552 C ABI stub library
- Goal4553 C ABI C client smoke
- Goal4554 C ABI Makefile build target
- Goal4555 C ABI header boundary refresh
- Goal4556 C ABI exported symbol audit
- Goal4557 C ABI fail-closed query entrypoints
- Goal4558 C ABI host AABB2 query proof
- Goal4559 C ABI example client
- Goal4560 C ABI embedding README
- Goal4561 C ABI AABB2 contract doc
- Goal4562 embeddability status refresh
- Goal4563 C ABI AABB2 negative runtime
- Goal4564 C ABI source-tree doctor surface
- Goal4565 C ABI stability policy
- Goal4566 C ABI symbol manifest
- Goal4567 C ABI AABB2 layout validation
- Goal4568 zero-copy interop contract
- Goal4569 embeddability progress gate
- Goal4570 C ABI ownership/threading contract
- Goal4571 C ABI AABB2 result ordering
- Goal4572 C ABI doctor docs surface
- Goal4573 C ABI backend/runtime fail-closed
- Goal4574 C ABI patch version refresh
- Goal4575 C ABI version negotiation
- Goal4576 C ABI staging bundle
- Goal4577 C ABI pkg-config stage
- Goal4578 C ABI capability queries
- Goal4579 C ABI direct-link example
- Goal4580 embeddability readiness packet
- Goal4581 C ABI Python ctypes example
- Goal4582 C ABI Python ctypes AABB2 query
- Goal4583 embeddability readiness refresh
- Goal4584 source-tree doctor ctypes surface
- Goal4585 C ABI staging inventory refresh
- Goal4586 C ABI pkg-config relocatable stage
- Goal4587 C ABI stage archive
- Goal4588 source-tree doctor stage archive
- Goal4589 embeddability shipping readiness refresh
- Goal4590 embeddability architecture status refresh
- Goal4591 C ABI host external runtime gate
- Goal4592 C ABI CUDA buffer metadata gate
- Goal4593 Python ctypes CUDA metadata bridge
- Goal4594 embeddability metadata readiness refresh
- Goal4595 C ABI prefix stage
- Goal4596 source-tree doctor prefix stage
- Goal4597 prefix-stage Python ctypes smoke
- Goal4598 embeddability architecture prefix status
- Goal4599 Python ctypes layout audit
- Goal4600 C ABI CMake prefix stage
- Goal4601 embeddability delivery status refresh
- Goal4602 C ABI archive CMake smoke
- Goal4603 embeddability delivery archive CMake refresh
- Goal4604 toolchain support matrix
- Goal4605 binding/device interop matrix
- Goal4606 neutral buffer protocol gate
- Goal4607 Python ctypes DLPack-like metadata bridge
- Goal4608 archive-stage Python ctypes smoke
- Goal4609 archive-stage C examples smoke
- Goal4610 C ABI independent-context concurrency smoke
- Goal4611 C ABI last-error diagnostics smoke
- Goal4612 C ABI last-error staged example
- Goal4613 prefix-stage C examples smoke

## Reading Rules

- A front-door row proves that the current command executes and keeps claim
  flags clean. It is not a performance leaderboard.
- A ten-app packet is not ten broad RT-core speedup claims.
- Scale-profile rows are useful for performance planning, but must be read by
  exact app, command, hardware, backend, partner, and dataset.
- CuPy/Numba comparison rows are partner-continuation evidence only. They do
  not become RT-core or whole-application speedup claims.
- If a row needs OptiX, use a pod or workstation with `RTDL_OPTIX_LIBRARY`
  pointing to `librtdl_optix`.
- If a row needs Numba, install the CUDA-capable Numba stack on the pod before
  running the packet.

For setup checks before running any benchmark, use the
[Source-Tree Doctor](source_tree_doctor.md).
