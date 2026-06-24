# Goal4393 V3.0 M1 Execution-Graph IR Design

Date: 2026-06-15

Status: M1 frozen after 3-AI review. This document authorizes only M2 planner-skeleton work, not native execution or performance claims.

IR version: `rtdl.v3_0.execution_graph_ir.m1`

Current gate state: `v3_0_m1_ir_frozen_m2_skeleton_allowed`

## Decision

V3.0 will introduce an app-agnostic execution-graph IR. The IR is the contract between user-facing RTDL primitives, backend lowering, explicit partner continuation, residency accounting, and benchmark evidence.

The design goal is not to make native code understand a benchmark application. The design goal is to let applications compose generic ray-tracing primitives, stream values, and continuation nodes without repeated host materialization or hidden partner work.

This M1 document freezes the target shape for M2. M2 may implement validators and the minimum no-execution `PreparedGraph` object. Native execution, backend execution, app-specific lowering, and public performance claims remain blocked.

## Relation To Existing V2.X Pieces

V3.0 should reuse and upgrade existing contracts rather than replacing them casually:

| Existing V2 piece | V3.0 role | Required change |
| --- | --- | --- |
| `src/rtdsl/ir.py` `RTExecutionPlan` | Legacy single-kernel plan model | Kept as compatibility. It is not the V3 graph IR because it has workload-style fields and no graph values, residency, stream binding, or partner nodes. |
| `src/rtdsl/schemas/rtdl_plan.schema.json` | Legacy v1alpha schema | Kept as compatibility. It must not be extended with new V3 app-specific workload enums. |
| `RtdlBufferDescriptor` | Storage descriptor for graph values | Reused as the storage-descriptor substrate, but V3 must allow nonzero stream handles only after M3 evidence rules are implemented. |
| `RtdlPreparedSessionDescriptor` | Prepared primitive session metadata | Becomes one possible `PreparedHandle` value in the graph. |
| `V28TypedResultStreamContract` | Internal typed stream predecessor | Promoted conceptually into `GraphValue(kind=stream)` with required status columns, ordering, capacity, and overflow state. |
| `RtdlPartnerContinuationSpec` | Partner operation predecessor | Becomes the basis for `PartnerNode`, with explicit best-partner plus Numba reference rules. |
| `PreparedExecutionReport` | Phase accounting predecessor | Becomes the basis for graph-level `ExecutionReport` phase markers. |
| `PrimitiveAdvisoryPlan` | Explain-only recipe planner | Remains advisory. It may inform M2 validation but must not silently execute or select partners. |

## Core Rule

The V3.0 native engine remains app-agnostic.

Application semantics stay in:

- Python application logic;
- explicit partner continuation code;
- data contracts that map caller-owned ids and payloads to generic RTDL values.

The native V3.0 layer may expose generic primitive traversal, hit metadata, row streams, topology streams, summaries, reductions, compaction, component union, frontier traversal, vector accumulation, and phase accounting. It must not expose native benchmark engines.

## Public API Candidate Names

These names are allowed as stable V3.0 public concepts:

```text
GraphValue
ValueKind
Residency
Lifetime
StreamBinding
PhaseMarker
PrimitiveNode
ContinuationNode
PartnerNode
MaterializeNode
ValidationNode
BackendPlan
PreparedGraph
ExecutionReport
GraphValidationError
```

These names are app-agnostic by construction. M2 must not add V3 public Python API names containing benchmark or domain application tokens.

## Forbidden V3 Public API And Native Tokens

The following tokens are forbidden in V3 public Python API names and V3 native exported symbols:

```text
rayjoin
lsi
pip
overlay
dbscan
rt_dbscan
barnes
barnes_hut
raydb
database
sql
robot
robot_collision
contact
contact_manifold
librts
rtnn
hausdorff
triangle_counting
paper
author
```

These words may appear in benchmark reports and review docs. They must not appear in V3 public Python API names or V3 native exported symbols.

## Graph Object

The V3 graph object is immutable once prepared.

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `graph_id` | string | Caller-supplied stable id for diagnostics. |
| `ir_version` | string | Must be `rtdl.v3_0.execution_graph_ir.m1` for M1. |
| `values` | tuple[`GraphValue`] | Typed values read or produced by graph nodes. |
| `nodes` | tuple[`PrimitiveNode` or `ContinuationNode` or `PartnerNode` or `MaterializeNode` or `ValidationNode`] | Ordered graph nodes. |
| `phase_markers` | tuple[`PhaseMarker`] | Mandatory phase accounting plan. |
| `target_backends` | tuple[string] | One or more of `cpu`, `embree`, `optix`, `hiprt`, `apple_rt`, `vulkan`. |
| `partner_policy` | mapping | Best-partner plus Numba-reference rule for this graph. |
| `claim_boundary` | mapping | All public claim authorization flags default to false. |
| `evidence_requirements` | tuple[string] | Required evidence before promotion or public wording. |

Graph-level invariants:

- Every node input and output must refer to a declared `GraphValue`.
- A value may have one producer, except for declared external inputs.
- Every node must bind to one or more phase markers.
- Every graph must declare at least `prepare`, `rt_traversal`, `continuation_or_reduction`, `download_or_materialization`, and `validation` phase markers, even when a phase records zero seconds.
- Graphs must fail validation if they authorize public speedup, true-zero-copy, hidden partner selection, automatic backend selection, or app-specific native engine logic.

## ClaimBoundary

`claim_boundary` is a required mapping on Graph, BackendPlan, PreparedGraph, and ExecutionReport metadata.

Required boolean keys:

| Key | Required value before M7 | Meaning |
| --- | --- | --- |
| `public_speedup_authorized` | false | Whether public performance wording is authorized. |
| `rt_core_speedup_authorized` | false | Whether public RT-core speedup wording is authorized. |
| `true_zero_copy_authorized` | false | Whether true-zero-copy wording is authorized. |
| `same_stream_claim_authorized` | false | Whether same-stream continuation wording is authorized. |
| `device_resident_claim_authorized` | false | Whether device-resident continuation wording is authorized. |
| `hidden_partner_selection_authorized` | false | Whether a graph may select a partner without user disclosure. |
| `automatic_partner_selection_authorized` | false | Whether a graph may choose a partner automatically. |
| `automatic_backend_selection_authorized` | false | Whether a graph may choose a backend automatically for promoted claims. |
| `app_specific_native_engine_authorized` | false | Whether native app-specific engine logic is authorized. |
| `raw_optix_callback_user_api_authorized` | false | Whether users may provide raw arbitrary OptiX callbacks through the stable API. |
| `paper_reproduction_claim_authorized` | false | Whether paper-system reproduction wording is authorized. |

ClaimBoundary invariants:

- M2 validators must reject any true value in these keys.
- Later milestones may add evidence-derived reporting fields, but they must not remove these keys.
- A missing key is a validation failure.

## PartnerPolicy

`partner_policy` is a required graph-level mapping that makes partner expectations machine-checkable.

Required keys:

| Key | Allowed values or type | Meaning |
| --- | --- | --- |
| `explicit_partner_required` | bool | Must be true for graphs with PartnerNode. |
| `best_partner` | string or null | Best practical partner selected by the benchmark plan, for example `cupy`, `triton`, or `torch`. |
| `numba_reference_required` | bool | Must be true when benchmark continuation needs a partner. |
| `numba_omission_justification` | string or null | Required non-empty text only when `numba_reference_required` is false. |
| `partner_timing_separated` | bool | Must be true for benchmark or comparison graphs. |
| `auto_selection_allowed` | bool | Must be false in V3.0 M1/M2. |
| `allowed_partners` | tuple[string] | Subset of `python_reference`, `numba`, `cupy`, `triton`, `torch`. |
| `benchmark_requires_dual_partner_rows` | bool | True when benchmark tables must include best-partner and Numba rows. |

PartnerPolicy invariants:

- `auto_selection_allowed` must be false.
- `explicit_partner_required` must be true if any PartnerNode exists.
- Benchmark graphs with PartnerNode must have `best_partner` and `numba_reference_required=true`.
- If `numba_reference_required=false`, `numba_omission_justification` must be non-empty and cited in the pilot report.
- Partner timing must be separated from RT traversal for any benchmark or backend comparison row.

## GraphValue

`GraphValue` is the only way a node exchanges data.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `name` | string | Stable value name. Must be app-agnostic. |
| `kind` | `geometry`, `parameter`, `prepared_handle`, `candidate_stream`, `hit_stream`, `topology_stream`, `row_stream`, `summary`, `status`, `partner_output`, `validation_output` | Logical value kind. |
| `dtype` | string | Scalar, vector, struct, or opaque handle type. |
| `shape` | tuple[int or symbolic] | Element shape or symbolic bounded shape. |
| `storage` | `host`, `cuda`, `embree_cpu`, `backend_native`, `dual`, `opaque` | Where data is physically stored or owned. |
| `residency` | `host_resident`, `device_resident`, `backend_resident`, `dual_resident`, `materialized`, `unknown_pending_evidence` | Residency claim state. |
| `lifetime` | `caller_retained`, `session_retained`, `borrowed`, `native_owned`, `partner_owned`, `released` | Lifetime authority. |
| `stream_binding` | `StreamBinding` or null | Stream/order contract for GPU or async values. |
| `producer` | string or null | Producing node id, null for external inputs. |
| `consumers` | tuple[string] | Consumer node ids. |
| `capacity` | integer or null | Required for bounded streams and output buffers. |
| `overflow_policy` | `not_applicable`, `fail_closed`, `grow_explicitly`, `truncate_forbidden` | How bounded outputs behave. |
| `materialization_policy` | `forbidden`, `allowed_explicit`, `required`, `already_materialized` | Whether host materialization is allowed. |
| `evidence` | tuple[string] | Evidence tags required before claims. |

GraphValue invariants:

- Device-resident values must have stream binding unless they are opaque prepared handles.
- `true_zero_copy_claim_authorized` is not a GraphValue field. It is always derived from evidence at report time.
- Bounded streams must declare `capacity`, `row_count` status value, and overflow policy.
- Host materialization must be represented by a `MaterializeNode`; it cannot be implicit.
- App-owned payload columns may be carried, but their names must describe generic roles such as `group_key`, `item_id`, `payload`, `score`, or `status`, not benchmark domains.

## StreamBinding

`StreamBinding` records ordering, not ownership.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `stream_id` | string | Logical stream id scoped to the graph. |
| `backend_stream_handle` | integer or null | Native handle if observed. Null means unproven. |
| `ordering` | `same_stream`, `event_wait`, `host_synchronized`, `not_proven` | Producer-consumer ordering state. |
| `producer_event` | string or null | Event name when `event_wait` is used. |
| `consumer_wait` | string or null | Consumer-side wait evidence. |
| `evidence` | tuple[string] | CUDA event, Nsight, or backend timing evidence labels. |

StreamBinding invariants:

- Same-stream wording requires `ordering=same_stream` plus CUDA event or Nsight evidence.
- Event-based wording requires both producer and consumer event labels.
- `not_proven` is valid for internal execution, but it blocks same-stream, device-resident continuation, and true-zero-copy public wording.

## Node Types

### PrimitiveNode

`PrimitiveNode` represents an RTDL primitive or backend-native generic traversal.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `node_id` | string | Unique node id. |
| `primitive_id` | string | App-agnostic primitive id. |
| `inputs` | tuple[string] | Input GraphValue names. |
| `outputs` | tuple[string] | Output GraphValue names. |
| `backend_contract` | `BackendContract` mapping | Logical backend contract for same-output lowering. |
| `phase` | string | Bound phase marker, usually `rt_traversal` or `build`. |
| `lowering_hints` | `LoweringHints` mapping | Non-semantic backend hints. |
| `capacity_policy` | `CapacityPolicy` mapping | Bounded-output and overflow behavior. |
| `same_contract_key` | string | Key shared by backend comparison rows. |

Allowed primitive families:

```text
primitive.aabb_query_2d
primitive.ray_triangle_intersect_3d
primitive.segment_intersect_2d
primitive.closed_shape_boundary_event_2d
primitive.fixed_radius_candidate_2d
primitive.fixed_radius_candidate_3d
primitive.aggregate_frontier_2d
primitive.aggregate_frontier_3d
primitive.generic_row_stream
primitive.generic_hit_stream
```

PrimitiveNode invariants:

- `primitive_id` must be app-agnostic.
- `backend_contract` may name OptiX, Embree, HIPRT, CPU, Apple RT, or Vulkan lowerings, but not a benchmark engine.
- OptiX lowering may use built-in hit attributes and internal shaders, but users must not supply raw arbitrary OptiX callbacks as the public RTDL API.
- Embree lowering must expose the same logical inputs and outputs as OptiX when the graph is used for backend comparison.

`BackendContract` required keys:

| Key | Allowed values or type | Meaning |
| --- | --- | --- |
| `contract_id` | string | Stable logical contract id. |
| `allowed_backends` | tuple[string] | Backends allowed for this primitive node. |
| `input_contract` | tuple[string] | Required logical input roles. |
| `output_contract` | tuple[string] | Required logical output roles. |
| `precision_policy` | string | Precision contract, for example `float32`, `float64`, or `mixed_explicit`. |
| `determinism_policy` | string | Determinism and tie policy. |

`LoweringHints` required keys:

| Key | Allowed values or type | Meaning |
| --- | --- | --- |
| `preferred_build_quality` | string or null | Backend build hint, not a contract change. |
| `preferred_traversal_mode` | string or null | Backend traversal hint, not a contract change. |
| `allow_internal_backend_programs` | bool | Allows RTDL-owned internal shaders or kernels. |
| `allow_user_raw_callbacks` | bool | Must be false for stable public API. |

`CapacityPolicy` required keys:

| Key | Allowed values or type | Meaning |
| --- | --- | --- |
| `capacity_value` | integer or symbolic string or null | Bounded output capacity. |
| `overflow_policy` | `not_applicable`, `fail_closed`, `grow_explicitly`, `truncate_forbidden` | Overflow behavior. |
| `complete_candidate_coverage_required` | bool | Whether exact candidate coverage is required. |

### ContinuationNode

`ContinuationNode` represents generic RTDL-owned continuation. It is not a partner node.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `node_id` | string | Unique node id. |
| `operation` | string | One of the allowed continuation operations below. |
| `inputs` | tuple[string] | Input GraphValue names. |
| `outputs` | tuple[string] | Output GraphValue names. |
| `phase` | string | Usually `continuation_or_reduction`. |
| `stream_binding` | `StreamBinding` or null | Required for device-resident continuation. |
| `deterministic` | bool | Whether output order and tie rules are deterministic. |
| `capacity_policy` | `CapacityPolicy` mapping | Required for bounded outputs. |

Allowed operations:

```text
continuation.compact_mask
continuation.grouped_count
continuation.grouped_sum
continuation.grouped_min
continuation.grouped_max
continuation.grouped_argmin
continuation.grouped_argmax
continuation.grouped_topk
continuation.component_union
continuation.frontier_expand
continuation.vector_sum
continuation.status_reduce
```

ContinuationNode invariants:

- Operations must be generic and reusable across workloads.
- `continuation.component_union` cannot be accepted as an application-specific clustering engine.
- `continuation.vector_sum` cannot be accepted as an application-specific force-law engine.
- `continuation.frontier_expand` cannot be accepted as an application-specific tree solver.

### PartnerNode

`PartnerNode` represents explicit caller-selected partner continuation.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `node_id` | string | Unique node id. |
| `partner` | `python_reference`, `numba`, `cupy`, `triton`, `torch` | Explicit caller-selected partner. |
| `operation` | string | Generic partner operation name. |
| `inputs` | tuple[string] | Input GraphValue names. |
| `outputs` | tuple[string] | Output GraphValue names. |
| `stream_binding` | `StreamBinding` or null | Required for same-stream/device-resident claims. |
| `phase` | string | Must be `continuation_or_reduction` or a more specific partner phase. |
| `reference_required` | bool | Whether a reference path is required. |
| `numba_reference_required` | bool | Whether this benchmark requires a Numba row. |
| `omission_justification` | string or null | Required only when a Numba reference is omitted. |
| `timing_separated` | bool | Must be true for benchmark and comparison graphs. |

Allowed partners:

```text
python_reference
numba
cupy
triton
torch
```

PartnerNode invariants:

- Partner nodes must not replace RT traversal for RT-core claims.
- Partner selection must be explicit. `auto` is invalid.
- A best practical partner row and a Numba reference row are required for benchmark apps that need partner continuation.
- If a Numba reference is omitted, the pilot document must justify why no Numba continuation path exists.
- Partner phase time must be separated from RT traversal time.
- Partner work must not be described as RTDL-only performance unless the table explicitly labels the partner.

`omission_justification` invariants:

- If `numba_reference_required=true`, `omission_justification` must be null.
- If `numba_reference_required=false` on a benchmark graph, `omission_justification` must be non-empty.
- The justification must be copied into the pilot report.

### MaterializeNode

`MaterializeNode` makes host materialization explicit.

Required fields:

- `node_id`
- `inputs`
- `outputs`
- `direction`
- `reason`
- `phase`
- `bytes`
- `evidence`

Allowed directions:

```text
host_to_device
device_to_host
backend_to_host
host_to_backend
device_to_device
```

MaterializeNode invariants:

- Any host/device transfer in a performance row must appear as a materialize or transfer node.
- Hidden materialization is a validation failure.
- If data starts on device, the graph must say so explicitly.
- If data starts on host, upload and packing phases must be reported or explicitly excluded.

### ValidationNode

`ValidationNode` records correctness checks and same-contract baselines.

Required fields:

- `node_id`
- `contract`
- `inputs`
- `oracle`
- `tolerance`
- `phase`
- `comparison_scope`

ValidationNode invariants:

- Validation timing must be separated from steady-state timing.
- Backend comparisons must use the same contract key.
- Paper-system comparisons must record author code, dataset, timing basis, and count/tie caveats.

## PhaseMarker

Mandatory graph phase names:

```text
prepare
build
upload
query_prepare
rt_traversal
stream_handoff
continuation_or_reduction
download_or_materialization
validation
host_wrapper
```

PhaseMarker fields:

| Field | Meaning |
| --- | --- |
| `name` | Phase name. |
| `role` | Human-readable role. |
| `required` | Whether the graph must report it. |
| `steady_state_candidate` | Whether the phase can be part of hot-path timing. |
| `setup_candidate` | Whether the phase belongs to setup/cold timing. |
| `evidence_required` | Evidence labels needed for promotion. |

Phase invariants:

- RT traversal, partner continuation, and materialization must be independently measurable.
- CUDA GPU phases need CUDA event or Nsight-level evidence before public same-stream or device-resident wording.
- Embree CPU phases need separate build, traversal, continuation, and host-wrapper timing.
- Warmup and repeated-run statistics belong in `ExecutionReport`, not in node definitions.

## BackendPlan

`BackendPlan` is the result of lowering a validated graph for one backend. M1 defines it, but M2 may only implement a skeleton validator.

Required fields:

- `backend`
- `graph_id`
- `same_contract_key`
- `lowered_nodes`
- `prepared_handles`
- `phase_markers`
- `unsupported_nodes`
- `required_partner_nodes`
- `claim_boundary`

BackendPlan invariants:

- `same_contract_key` must match across OptiX and Embree comparison rows.
- Unsupported nodes fail closed unless the graph declares a reference-only path.
- Backend lowering must not introduce new public app semantics.
- BackendPlan cannot authorize public speedup claims.

## PreparedGraph

`PreparedGraph` is the no-execution prepared object that M2 may implement after M1 freezes.

Required fields:

| Field | Allowed values or type | Meaning |
| --- | --- | --- |
| `graph_id` | string | Stable graph id. |
| `ir_version` | string | Must match the validated graph IR version. |
| `validated_graph` | graph metadata object | The validated graph payload or immutable reference. |
| `backend_plan` | `BackendPlan` or null | Present only after backend validation. |
| `state` | `pending_validation`, `validated`, `prepared`, `invalidated`, `closed` | Lifecycle state. |
| `value_table` | mapping[string, `GraphValue`] | Values keyed by name. |
| `phase_plan` | tuple[`PhaseMarker`] | Planned phase markers. |
| `partner_policy` | `PartnerPolicy` mapping | Graph-level partner policy. |
| `claim_boundary` | `ClaimBoundary` mapping | Claim authorization boundary. |
| `validation_errors` | tuple[string] | Empty when state is `validated` or `prepared`. |

PreparedGraph invariants:

- M2 `PreparedGraph` construction may validate and store metadata but must not execute native code.
- `state=prepared` means structurally prepared, not executed.
- `invalidated` and `closed` states must prevent later execution in future milestones unless a new graph is prepared.
- `claim_boundary` must use the exact ClaimBoundary schema and all keys must remain false in M2.
- `backend_plan` cannot authorize execution in M2.

## ExecutionReport

`ExecutionReport` records evidence after a graph run.

Required fields:

- `graph_id`
- `ir_version`
- `backend`
- `partner`
- `hardware`
- `dataset`
- `scale`
- `data_start_residency`
- `warmups`
- `repeats`
- `timing_statistic`
- `phase_timings`
- `correctness_contract`
- `same_contract_key`
- `evidence_paths`
- `claim_boundary`

ExecutionReport invariants:

- Every timing table must disclose backend and partner.
- Setup and steady-state timing must be separated.
- Public performance claims require M7 review, even if M1-M6 reports look favorable.
- If any phase is excluded, the report must say so in a machine-readable field.

## Same-Contract Comparison Rule

OptiX RT-core and Embree CPU comparisons are valid only when:

- both are lowered from the same graph;
- both use the same `same_contract_key`;
- both expose the same logical outputs;
- both report the same inclusion/exclusion policy for build, upload, download, warmup, validation, and host wrapper;
- both disclose partner work, if any;
- both run under named hardware and dataset scale.

If these conditions are not true, the comparison is diagnostic only.

## Evidence Rule

The following claims require the following evidence:

| Claim | Required evidence |
| --- | --- |
| same-stream partner continuation | CUDA events or Nsight stream correlation proving producer and consumer ordering |
| device-resident continuation | pointer identity or backend-native handle evidence, lifetime authority, no forced host materialization, and transfer counters |
| true zero-copy | device-resident continuation evidence plus proof that no hidden copy or host staging occurred |
| OptiX-vs-Embree speedup | same graph, same contract, same scale, phase split, repeated runs |
| author-system comparison | author code version, exact dataset, timing basis, correctness contract, and row/count caveats |
| public V3.0 speedup | M7 release-grade benchmark harness and external review |

## Benchmark Mapping Is Not Public API

The following mapping guides pilots only. It must not leak into V3 public API or native names.

| Benchmark workload | Generic V3 route |
| --- | --- |
| spatial join and point membership workloads | `primitive.segment_intersect_2d`, `primitive.closed_shape_boundary_event_2d`, `continuation.grouped_count`, `continuation.compact_mask` |
| density clustering workloads | `primitive.fixed_radius_candidate_2d/3d`, `continuation.grouped_count`, `continuation.component_union` |
| aggregate tree workloads | `primitive.aggregate_frontier_2d/3d`, `continuation.frontier_expand`, `continuation.vector_sum` |
| collision and contact workloads | `primitive.aabb_query_2d`, generic witness streams, `continuation.compact_mask`, app-owned refinement |
| graph and ranked-summary workloads | `primitive.generic_hit_stream`, `continuation.grouped_topk`, `continuation.grouped_sum` |

## M2 Implementation Scope If M1 Passes

M2 may implement:

- dataclasses or typed records for GraphValue, StreamBinding, PhaseMarker, node types, BackendPlan, PreparedGraph, and GraphValidationError;
- pure-Python validation rules;
- serialization to a schema-like dictionary;
- static app-name forbiddance for V3 public API and V3 native export metadata;
- no-op `PreparedGraph` construction that does not execute;
- compatibility adapters that describe how existing V2 descriptors map into V3 values.

M2 may not implement:

- native fused kernels;
- backend execution;
- app-specific lowering;
- automatic partner selection;
- public speedup claim generation;
- true-zero-copy or same-stream promotion.

## M1 Exit Criteria

M1 is complete because:

1. this document is reviewed by Claude and Gemini;
2. review-requested fixes are applied;
3. tests validate the design gate and forbidden naming boundary;
4. a consensus document records acceptable verdicts;
5. the consensus state is `v3_0_m1_ir_frozen_m2_skeleton_allowed`.

The current state is:

`v3_0_m1_ir_frozen_m2_skeleton_allowed`
