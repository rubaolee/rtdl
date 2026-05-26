# Goal2625: Segmented Row Stream Contract

Date: 2026-05-26

Status: completed CPU/reference contract slice. This report does not claim
native OptiX/Embree page emission, public speedups, or app-level benchmark
improvements.

## Purpose

Several benchmark apps now pressure the same runtime limitation: exact row
outputs can become too large to safely materialize as one table. Triangle
counting, RT-DBSCAN adjacency, contact broadphase rows, and RayDB-style grouped
candidate paths need a generic way to page rows, resume from a continuation
token, and prove whether the current output is complete.

Goal2625 defines that shared substrate as:

```text
SEGMENTED_ROW_STREAM
alias: CHUNKED_ROW_CONTINUATION
contract: rtdl.segmented_row_stream.v1
```

## Contract

`SEGMENTED_ROW_STREAM` owns only generic row pagination:

- explicit row schema;
- positive page capacity;
- deterministic stream-local continuation tokens;
- exact reconstruction from complete page sequences;
- visible incomplete-window state when more pages remain;
- fail-closed overflow when an explicit total-row capacity is exceeded.

The failure mode is:

```text
failure_mode=fail_closed_overflow
partial_result_returned=False
```

This is deliberately no app semantics. The primitive does not know about graph
triangles, DBSCAN clusters, contacts, SQL, Barnes-Hut forces, or other domain
meaning. Apps may interpret rows after consuming them, but RTDL owns only row
schema, pagination, completion, and capacity metadata.

## Implementation

Added `src/rtdsl/segmented_row_stream.py` with:

- `SegmentedRowPage`;
- `SegmentedRowStream`;
- `SegmentedRowStreamOverflowError`;
- `segmented_row_stream_contract()`;
- `emit_segmented_row_page()`;
- `emit_segmented_row_stream()`;
- `reconstruct_segmented_row_stream()`;
- `validate_segmented_row_pages()`;
- token helpers `make_segmented_row_token()` and
  `parse_segmented_row_token()`.

The public source-tree import surface in `rtdsl.__init__` now exports the
contract, dataclasses, and helpers.

## Primitive Hierarchy Update

The existing hierarchy node:

```text
continuation.segmented_chunked_rows
```

is promoted from `candidate_behavior` to `internal_substrate`. That is a
runtime-organization statement, not a stable external primitive claim. Native
backend page emission still requires later evidence.

## Verification Scope

The targeted tests cover:

- contract metadata and exports;
- deterministic page offsets and continuation tokens;
- exact reconstruction for complete streams;
- incomplete-window detection;
- fail-closed total-capacity overflow;
- schema and row-width validation;
- composition with existing `AABB_INDEX_QUERY_2D` candidate rows;
- hierarchy/catalog documentation.

External review:

- Claude accepted with no blocking issues.
- Gemini accepted with no blocking issues.
- Consensus is recorded in
  `docs/reports/goal2625_segmented_row_stream_3ai_consensus_2026-05-26.md`.

Local command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2625_segmented_row_stream_test tests.goal2624_primitive_hierarchy_test tests.goal2622_contact_manifold_generic_aabb_discovery_test tests.goal2623_optix_aabb_pair_rows_test
```

Result: 30 tests passed, with 3 expected OptiX-library skips on this Mac.

## Next Work

The next engineering slice should choose one pressure path and replace
all-at-once materialization with this contract:

1. Triangle counting large-paper-dataset row lowering.
2. Contact-manifold AABB broadphase rows.
3. RT-DBSCAN fixed-radius neighbor/adjacency row continuation.

After one path is integrated, native OptiX/Embree page emission can be
designed around the same row-page contract instead of adding app-specific
capacity workarounds.
