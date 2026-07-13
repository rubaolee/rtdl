# Goal5041 - v2.14.4 Device-Columnar API Design And Implementation Plan

Date: 2026-07-05

Status: design for review, not implementation

Proposed exit label after review:

```text
approve_v2_14_4_device_columnar_prepared_pipeline_api_plan
```

## External Review Conditions Incorporated

Claude approved this plan with four conditions.  They are now first-class gates for the implementation goals, not optional notes:

```text
C1 - Existing core rayjoin_* / RayjoinCdb* symbols require explicit remediate-or-defer decisions.
C2 - device_order_by may ship public in v2.14.4; device_group_by remains internal unless a true device-resident reduce passes POD verification.
C3 - keep the existing four-state stream-ordering vocabulary; device-residency must be derived from actual column metadata, never self-declared.
C4 - the RayJoin <=0.36s regression gate must also assert device-residency flags, not timing alone.
```

## One-Sentence Positioning

v2.14.4 is not "RayJoin faster again."  v2.14.4 is the release that turns the reusable pieces proven during the RayJoin v2.14.3 work into a formal RTDL device-columnar prepared pipeline API, with RayJoin retained only as a correctness and performance regression test.

## Why This Exists

The RayJoin paper-reproduction work exposed a language-system gap:

```text
RTDL primitive -> Python rows -> Python continuation -> Python writer
```

is the wrong default for multi-stage spatial pipelines.

The useful system shape is:

```text
RTDL primitive -> typed device columns -> generic ordering/group/reduce -> partner continuation -> binary downstream operator
```

v2.14.3 proved pieces of that route inside the RayJoin app:

- native/device LSI pair-id columns;
- directed point-location/PIP face-id device columns;
- generic row-buffer / device-column metadata;
- CUDA-array-interface / Numba handoff;
- native CUDA/Thrust lexsort;
- prepared base sessions and prepared query batches;
- device-resident binary carrier experiments;
- strict regime accounting: cold CLI, warm-process fresh, prepared replay, and prepared query-batch are different numbers.

v2.14.4 must now remove the accidental app ownership of those capabilities.

## Locked Performance Baseline

v2.14.4 cannot lose the v2.14.3 RayJoin performance baseline.  The baseline is from Goal5040 and Goal5039:

| Measurement boundary | Current evidence |
|---|---:|
| RTDL top4 paper text wall time | `79.931s` |
| AuthorOfficial top4 paper text wall time | `113.011s` |
| RTDL post-read paper text route | `64.383s` |
| AuthorOfficial post-read paper text route | `12.182s` |
| RTDL prepared binary route, six-batch top4 sum | `0.328842s` |
| AuthorOfficial core phases, top4 | `0.187042s` |
| RTDL binary/core ratio | `1.76x` slower |

Important correction carried into v2.14.4:

```text
47ms is a single query-batch median.
329ms is the whole top4 six-batch prepared binary route.
```

Do not use `47ms` as the full top4 performance number.

## Product Boundary

RTDL is the language system.  RayJoin is one app on top of it.

### RTDL May Own

- device-column descriptors and ownership/lifetime metadata;
- primitive outputs as typed device-column streams;
- generic prepared base/session/query-batch lifecycle;
- generic device ordering: lexsort/order-by over typed columns;
- generic segmented/grouped reductions only after device-resident reduce verification;
- generic partner handoff to Numba/CuPy/CUDA-array-interface consumers;
- regime metadata and timing fields;
- fail-closed validation for overflow, lifetime, backend support, and host materialization.

### RayJoin App Must Own

- CDB-specific paper reproduction workflow;
- author-compatible Section 5.7 output-chain text writer;
- overlay-specific carrier and descriptor interpretation;
- author comparator labels and patch disclosure;
- duplicate-half-edge comparison contract;
- top4 representative dataset selection;
- any "paper reproduction" wording.

### Forbidden For v2.14.4

- no RayJoin output-chain writer in RTDL core;
- no `rayjoin_*` naming in new public API;
- no new core/native symbols containing `rayjoin`;
- existing core/native `rayjoin_*` or `RayjoinCdb*` symbols must be classified as rename-now, public-wrapper-with-deferred-native-rename, keep-internal-with-debt, or move-to-app;
- no raw OptiX callback / any-hit / closest-hit user API;
- no Layer 4 in-traversal fusion compiler;
- no author-performance parity claim from this system API work;
- no "zero-copy" public wording unless verified by metadata and reviewer approval.

## Existing Assets To Consolidate

This is not a from-scratch API.

Known assets already present in the tree include:

- `src/rtdsl/device_column_row_buffer.py`
- `src/rtdsl/columnar_partner.py`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/current_prepared_session_residency_profiles.py`
- native/device-column outputs in `src/rtdsl/optix_runtime.py`
- existing grouped/count/reduction device-column tests from earlier v2.x work
- recent RayJoin app proof artifacts from Goals 4974-5040

The first implementation step must inventory these assets and decide which become stable public API, which remain internal substrate, and which are legacy naming debt.

## Proposed Public API Concepts

Names below are design names.  Implementation may choose exact names during API review, but the concepts and contracts should remain.

### 1. `DeviceColumnBuffer`

Purpose: typed, owned or borrowed columnar data resident on a device.

Required properties:

```text
columns: tuple[DeviceColumnDescriptor, ...]
row_count: int
device: "cuda" | "cpu" | backend-specific device token
producer: str
source_mode: "native_device_columns" | "partner_device_columns" | "host_columns"
materializes_host_rows_for_bridge: bool
producer_consumer_stream_ordering:
  "not_proven"
  | "same_stream"
  | "producer_event_waited_by_consumer"
  | "host_synchronized_before_consumer"
owner: closeable lifetime owner or borrowed owner token
```

Required behavior:

- context-manager lifetime;
- explicit `close()`;
- idempotent cleanup;
- metadata export;
- device-residency derived from actual column interfaces and `materializes_host_rows_for_bridge`, never self-declared by CLI flags or app summaries;
- fail-closed if a consumer requires device residency and the buffer materializes host rows;
- optional conversion to NumPy/CuPy only through explicit methods whose names contain `copy` when they copy.

Non-goal:

- this is not a general memory allocator;
- it does not encode RayJoin carrier semantics.

### 2. `PreparedGeometrySession`

Purpose: prepare a base spatial dataset once, then execute one or more query batches.

Required properties:

```text
base_id / cache_key
backend
scale_domain or coordinate domain
prepared_state_kind
compile_setup_sec
workspace_setup_sec
query_batch_count
regime_label
```

Regime labels must be first-class:

```text
cold_cli_one_shot
warm_process_fresh
prepared_base_distinct_query_batch
prepared_replay_same_input_diagnostic
```

Required behavior:

- `prepare_base(...)`;
- `prepare_query_batch(...)`;
- `run(query_batch, output="device_columns")`;
- metadata that distinguishes reusable compile setup from per-input workspace setup;
- no silent promotion of replay numbers to query-many numbers.

### 3. `DeviceOrderBy`

Purpose: generic GPU ordering over device columns.

Minimal API shape:

```python
order = rt.device_order_by(
    columns=[key0, key1, key2],
    directions=["asc", "asc", "asc"],
    null_policy="none",
)
```

Implementation may use native CUDA/Thrust/CUB or CuPy, but the public contract is generic:

- stable or explicitly unstable ordering must be declared;
- accepted dtype combinations must be declared;
- overflow/capacity must fail closed;
- result order column is device-resident;
- no RayJoin descriptor vocabulary in the API.

### 4. `DeviceSegmentedReduce`

Purpose: generic group-by / reduce over device columns.

Minimal API shape:

```python
groups = rt.device_group_by(
    keys=[label_a, label_b],
    values=[length],
    reductions={"count": "count", "sum_length": ("sum", length)},
)
```

Target operations:

- count;
- sum;
- min/max if already available;
- compact group key output;
- device-resident result columns.

Important v2.14.4 exposure rule:

```text
device_order_by is a public v2.14.4 target.
device_group_by remains internal/experimental unless Goal5046 proves a true device-resident reduce path on POD.
```

The current `columnar_partner.py` blocker list says existing grouped count/sum reductions still read host `row_values`.  Shipping a public `device_group_by` while that is true would repeat the self-declared-residency mistake.  RayJoin can use internal grouping assets as an app/regression path, but public promotion requires CPU parity, POD proof, and metadata showing no host row materialization.

### 5. `PartnerContinuation`

Purpose: connect RTDL device columns to partner kernels without forcing Python row materialization.

Minimal API shape:

```python
with rt.partner_continuation("numba", inputs=device_columns) as cont:
    out = cont.map_kernel(kernel, outputs=output_schema)
```

Required behavior:

- accept `DeviceColumnBuffer`;
- expose CUDA array interface or DLPack when safe;
- record whether host materialization happened;
- synchronize or return event/stream metadata;
- own output lifetime or attach it to a parent owner;
- keep fallback host route explicit and measurable.

Numba is the first partner for v2.14.4.  CuPy may be used for validation or generic sort/reduce if it is already available, but v2.14.4 should not become a CuPy-only release.

## API Migration Target For RayJoin

Current RayJoin app route should be rewritten from app-internal flags:

```text
--device-columnar
--native-lexsort
--bounded-exact-lsi-device-columns
--point-location-device-face-columns
--prepared-lsi-base-session
--query-chain-batches
...
```

to an app using public RTDL concepts:

```python
with rt.prepare_planar_map_lsi_2d(base, output="device_columns") as lsi:
    batches = rt.query_batches(query, by="chain", count=6)
    pair_columns = [lsi.run(batch).columns for batch in batches]

projected = rt.partner_continuation("numba").map(
    rayjoin_app.project_intersections,
    inputs=pair_columns,
)

ordered = rt.device_order_by(
    [projected.edge_id, projected.t, projected.side, projected.other_id]
)

faces = point_location.run_device_points(projected.midpoints)

descriptor_columns = rayjoin_app.build_descriptor_columns(
    ordered,
    faces,
)

summary = rt.device_group_by(
    keys=[descriptor_columns.label_a, descriptor_columns.label_b],
    values=[descriptor_columns.group_length],
    reductions={"count": "count"},
)
```

The RayJoin-specific pieces remain in `rayjoin_app.*`.  RTDL owns only `prepare`, `device columns`, `order_by`, verified grouping/reduce primitives, and `partner_continuation`.

The `rt.device_group_by(...)` line above is conditional on Goal5046 passing the public device-resident reduce gate.  If `device_group_by` does not pass, the RayJoin migration must either use an internal experimental grouped-reduce route with explicit metadata or keep the app-owned binary consumer.  It must not publish `device_group_by` as a stable public primitive by implication.

## Required Non-RayJoin Proof

v2.14.4 cannot claim genericity from RayJoin alone.

At least one non-RayJoin app must use the same public API.  Acceptable minimal proof:

```text
generic point-location aggregation:
  point-location face_id device columns
  -> device_group_by(face_id)
  -> count points per face
```

or:

```text
generic segment-pair relation aggregation:
  segment-pair left_id/right_id device columns
  -> device_order_by(left_id, right_id)
  -> device_group_by(left_id)
  -> count pairs per left segment
```

Requirements:

- no import from RayJoin app code;
- no `rayjoin` column names;
- correctness compared with CPU/NumPy reference;
- metadata proves whether host rows were materialized;
- POD GPU run if the route uses CUDA.
- if `device_group_by` remains internal after Goal5046, the v2.14.4 proof may use public `device_order_by` plus internal grouped-reduce metadata, but the public claim must be limited accordingly.

## Performance Gates

### RayJoin Regression Gate

After migrating the RayJoin prepared binary route to the public API:

```text
baseline top4 six-batch prepared binary route: 0.328842s
allowed regression threshold: <= 0.36s median-of-N
```

Suggested measurement:

- same top4 input;
- same six chain-contiguous query batches;
- same writer-free binary descriptor consumer;
- N >= 5 process runs;
- report median six-batch sum, not per-batch median only;
- assert device-residency metadata alongside timing:

```text
lsi_pair_input_device_resident == true
lsi_pair_host_to_device_copy_used == false
materializes_host_rows_for_bridge == false for public device-column handoff boundaries
```

- reject a timing pass if these metadata checks fail;
- preserve structural anchors:

```text
lsi_row_counts:
[127926, 21424, 67840, 66414, 56228, 88490]

descriptor_pair_counts:
[6316, 2756, 4723, 3058, 2873, 2987]
```

If the public API migration exceeds `0.36s`, v2.14.4 must either fix the regression or explicitly label the API route experimental and keep the v2.14.3 app route as the performance baseline.

### Paper Text Correctness Gate

The paper text route remains a correctness anchor:

```text
RTDL top4 paper text output SHA-256:
076227b072340e754b7f2cb54de3c37d8054e2a393e87fdb8a4f7368a297b690
```

v2.14.4 API work must not break this route.

### Non-RayJoin Genericity Gate

The non-RayJoin proof must pass local correctness tests and, for CUDA device-column claims, POD execution.

### Claim Boundary Gate

Any docs or reports must keep these statements true:

- v2.14.4 is a system API release, not a RayJoin performance release;
- `47ms` is per-batch, not whole top4;
- the whole top4 prepared binary route baseline is `0.329s`;
- post-read paper text route remains slower than AuthorOfficial;
- no author-performance parity claim.

## Implementation Plan

### Goal5041 - Design And External Review

Deliverables:

- this design document;
- call-for-review document;
- reviewer decision before implementation.

Exit labels:

```text
approve_v2_14_4_device_columnar_prepared_pipeline_api_plan
revise_v2_14_4_api_plan_before_implementation
block_v2_14_4_api_plan_as_rayjoin_specific
```

### Goal5042 - Existing Asset Inventory And API Mapping

Purpose:

Map existing internal assets to proposed public API concepts.

Work:

- inspect `device_column_row_buffer.py`, `columnar_partner.py`, `hit_stream_handoff.py`, `optix_runtime.py`, prepared-session modules, and existing grouped/count/lexsort tests;
- classify each as `promote`, `wrap`, `keep_internal`, `rename_debt`, or `discard`;
- for every existing core/native `rayjoin_*`, `RayjoinCdb*`, or `rtdl_optix_*rayjoin*` symbol/class, record one of:

```text
rename_now
wrap_with_public_alias_defer_native_rename
keep_internal_with_debt
move_to_app
```

- include at minimum the legacy point-location native symbols/classes and the LSI predicate alias family:

```text
rtdl_optix_prepare_rayjoin_cdb_point_location_2d
rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d
rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_face_id_columns
PreparedRayjoinCdbPointLocation2D / PreparedOptixRayjoinCdbPointLocationPoints2D
rayjoin_lsi / RTDL_OPTIX_SEGMENT_PAIR_PREDICATE legacy alias
```

- identify duplicate API surfaces.

Verification:

- no new runtime implementation;
- explicit mapping table;
- explicit remediate-or-defer table for existing RayJoin-named core/native symbols;
- no RayJoin app code used as API evidence except as consumer evidence.

Exit:

```text
completed_asset_inventory_for_v2_14_4_api
```

### Goal5043 - Public `DeviceColumnBuffer` Contract

Purpose:

Stabilize the typed device-column stream contract.

Work:

- define public metadata object;
- expose safe context-manager lifetime;
- standardize `materializes_host_rows_for_bridge`;
- preserve the existing four-state stream-ordering vocabulary:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

- derive device-residency from actual column interfaces plus bridge metadata, never from self-declared app flags;
- standardize schema/dtype/device/owner fields;
- add tests for close, borrowed owner, invalid schema, host-materialization metadata.

Verification:

- local tests;
- at least one existing native device-column producer wrapped through the public contract;
- no performance claim yet.

Exit:

```text
completed_public_device_column_buffer_contract
```

### Goal5044 - Public Prepared Session / Query-Batch Contract

Purpose:

Make prepared base/query-batch lifecycle an RTDL concept instead of RayJoin flags.

Work:

- define `PreparedGeometrySession`;
- expose regime labels;
- expose base preparation, query-batch preparation, and run metadata;
- include compile setup vs per-input workspace fields.

Verification:

- local lifecycle tests;
- fail-closed replay/query-many label tests;
- no silent reuse of same-input replay as distinct-query performance.

Exit:

```text
completed_public_prepared_session_query_batch_contract
```

### Goal5045 - Public `device_order_by`

Purpose:

Promote the generic native CUDA/Thrust lexsort capability to an RTDL ordering primitive.

Work:

- wrap existing native lexsort helper behind a generic API;
- define dtype support and stability semantics;
- keep Numba/CuPy fallback explicit if available;
- add CPU reference tests.

Verification:

- local correctness tests on small arrays;
- POD correctness/performance smoke;
- no RayJoin descriptor wording in core API.

Exit:

```text
completed_public_device_order_by_cuda_lexsort
```

### Goal5046 - Public `device_group_by` / Segmented Reduce

Purpose:

Decide whether reusable grouped reduction over device columns is ready for public exposure.

Work:

- consolidate existing grouped count/sum device-column assets;
- expose compact key output;
- support count and sum at minimum;
- document overflow/fallback behavior.
- explicitly account for the current `columnar_partner.py` blocker that grouped count/sum reductions read host `row_values`;
- if no true device-resident reduce path exists, keep `device_group_by` internal/experimental.

Verification:

- CPU reference parity;
- local tests;
- POD smoke on CUDA route;
- metadata proves no host row materialization for any public `device_group_by` claim;
- no RayJoin carrier semantics in API.

Exit:

```text
completed_public_device_group_by_segmented_reduce
completed_internal_only_device_group_by_until_device_resident_reduce
blocked_device_group_by_public_due_to_host_row_values
```

### Goal5047 - Numba `PartnerContinuation` API

Purpose:

Formalize Numba as the first partner continuation over RTDL device columns.

Work:

- pass `DeviceColumnBuffer` inputs to Numba kernels;
- record stream/synchronization behavior;
- expose output device-column buffers;
- provide explicit host fallback only when requested.

Verification:

- Numba CUDA POD test;
- local skip behavior when CUDA unavailable;
- metadata proves whether host materialization occurred.

Exit:

```text
completed_numba_partner_continuation_public_api
```

### Goal5048 - Non-RayJoin Genericity Proof

Purpose:

Prove the API is not RayJoin-shaped.

Work:

- build one non-RayJoin app using `DeviceColumnBuffer`, `PreparedSession` if relevant, public `device_order_by`, public-or-internal verified grouping metadata, and optional Numba continuation;
- compare with CPU reference.

Verification:

- no RayJoin imports;
- no RayJoin column names;
- local tests plus POD if CUDA path used.
- if `device_group_by` exits internal-only, the proof must say so and must not imply public grouped-reduce availability.

Exit:

```text
completed_non_rayjoin_device_columnar_pipeline_proof
```

### Goal5049 - RayJoin Migration To Public API

Purpose:

Migrate the v2.14.3 prepared binary route to the new public API while preserving performance.

Work:

- replace app-private flag plumbing where possible with public API calls;
- keep RayJoin-specific descriptor construction in the app layer;
- retain old route behind a debug flag until performance gate passes.

Verification:

- top4 prepared binary six-batch sum `<= 0.36s` median-of-N;
- residency gate passes:

```text
lsi_pair_input_device_resident == true
lsi_pair_host_to_device_copy_used == false
public DeviceColumnBuffer materializes_host_rows_for_bridge == false where the route claims device-resident handoff
```

- structural anchors unchanged;
- paper text route byte-equal unchanged;
- no public API names contain RayJoin.

Exit:

```text
completed_rayjoin_migration_to_public_api_no_perf_regression
blocked_rayjoin_migration_due_to_api_perf_regression
```

### Goal5050 - v2.14.4 Docs, Public Boundary, And Release Packet

Purpose:

Document v2.14.4 as a system API release.

Work:

- update RTDL docs and primitive catalog;
- update RayJoin paper app README with corrected `47ms`/`329ms` wording;
- leak scan public surface and exported/native symbol names for `rayjoin`, `RayJoin`, `RayjoinCdb`, and `rtdl_optix_.*rayjoin`;
- document any Goal5042 deferred native naming debt as internal implementation debt, not as public API;
- final performance and correctness packet.

Verification:

- docs contain no internal goal/reviewer leaks in public surface;
- public API and docs contain no new RayJoin-named primitives;
- native symbol-name scan has a remediate-or-defer entry for every remaining RayJoin-named symbol;
- no author parity overclaim;
- external review approves.

Exit:

```text
approve_v2_14_4_release_staging_device_columnar_api
```

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| API becomes RayJoin-shaped | invalidates v2.14.4 system positioning | non-RayJoin proof and naming audit |
| Performance regresses while API gets cleaner | user loses v2.14.3 gain | hard RayJoin gate `<=0.36s` six-batch sum |
| Device-resident metadata self-declares instead of verifies | repeats v2.14.3 measurement bug | derive flags from buffer metadata only |
| `device_group_by` ships before true device-resident reduce exists | repeats host-row hidden-copy problem | keep internal unless POD proves no host `row_values` path |
| Existing RayJoin-named core symbols are ignored | public genericity claim is overstated | Goal5042 remediate-or-defer table and Goal5050 native-symbol scan |
| Replay/query-many confusion returns | fake speedup | first-class regime labels in API and docs |
| Lifetime bugs in device buffers | correctness instability | context-manager tests, owner retention, explicit synchronization/event metadata |
| Existing v2.x assets conflict | duplicate APIs | Goal5042 asset inventory before implementation |

## Decision Needed From Review

The reviewer should answer:

1. Is this correctly scoped as a system API release rather than RayJoin app work?
2. Are the proposed APIs generic enough?
3. Is the RayJoin performance gate strict enough?
4. Is one non-RayJoin proof sufficient for v2.14.4?
5. Should any API be split or deferred before implementation begins?
6. Did the C1-C4 external review conditions land in the correct implementation goals?

Implementation must not start until this design is reviewed.
