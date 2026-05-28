# Goal2638 External Critical Reviews

Date: 2026-05-27

Sources: user-pasted review output. Review round 1 came from Gemini 3.1 Pro;
review round 2 came from Claude.

## Review Round 1: Gemini 3.1 Pro

Verdict: Accept with fixes.

Gemini accepted the architectural direction of
`AGGREGATE_FRONTIER_COLLECT_2D`: traversal/frontier ID emission may belong to
RTDL, while Barnes-Hut force laws, scoring, and app reductions must remain
outside the engine.

### Blocking Findings

1. The first row schema was a fixed six-column tuple without reserve/version
   space. Future native Embree/OptiX lowering could require a state or version
   flag and would otherwise break partner adapters.

2. The default Python reference `frontier_rows` included `distance` and
   `opening_ratio`. Even though the native `frontier_i64_rows` stayed ID-only,
   exposing geometry diagnostics in the default primitive payload blurred the
   app-agnostic boundary.

### Non-Blocking Findings

1. Overflow tests covered obvious under-capacity cases but did not explicitly
   test exact-capacity boundaries.

2. Documentation needed stronger disclosure that the primitive currently has
   CPU reference and partner-column adapters only; native Embree/OptiX backend
   execution is still future work.

### Codex Action Status

- Added reserved `metadata_flags` to
  `AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA` and to every row-major i64 row.
- Kept default `frontier_rows` ID-only by removing `distance` and
  `opening_ratio` from default rows.
- Added opt-in `include_debug_diagnostics=True`, returning diagnostics in a
  separate `debug_diagnostics` side channel.
- Added exact-capacity tests for total and per-source row limits.
- Updated the Goal2638 report, primitive catalog, and Barnes-Hut README to
  disclose the backend status and payload boundary.

## Consensus Boundary

This review does not authorize native RT performance claims. Goal2638 remains
a CPU-reference plus partner-column-adapter contract until native Embree/OptiX
symbols are implemented, parity-tested, and separately reviewed.

## Review Round 2: Claude

Claude's review was based on the current on-disk state
after the first fix pass. It kept the verdict at accept-with-fixes and raised
two blocking concerns:

1. `metadata_flags` had become a schema field but needed explicit contract
   semantics, tests, docs, and public export.

2. Barnes-Hut inverse-square force helpers still lived in
   `src/rtdsl/aggregate_tree_reference.py`, which conflicted with the
   Goal2638 boundary even though the new collect primitive itself was clean.

Additional non-blocking findings covered stale docs, incomplete hierarchy
outputs, missing edge tests, misleading overflow wording, ambiguous
`partner_resident_ready` metadata, and default `frontier_rows` extra fields.

### Codex Action Status

- Exported `AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE`.
- Documented `metadata_flags=0` as "no flags set" and required partners to
  ignore unknown future non-zero flags unless a later contract revision defines
  them.
- Added tests for `metadata_flags`, kind codes, resume-index `-1` sentinel,
  source offset slicing, exact total/per-source capacity boundaries,
  single-body empty output, deduplication toggle, and debug diagnostics.
- Renamed columnar metadata from ambiguous `partner_resident_ready` to
  `partner_i64_row_layout_ready`.
- Changed overflow messages from "emitted" to "attempted" because failed
  buffers are abandoned before result materialization.
- Expanded hierarchy outputs to include all schema fields plus `row_offsets`.
- Moved inverse-square force/reference helpers to
  `src/rtdsl/app_reference/aggregate_force_math.py`; top-level compatibility
  exports remain for existing examples/tests.

The remaining boundary is intentional: top-level `rtdsl.*` compatibility names
still exist, but their implementation is now in `rtdsl.app_reference`, not the
aggregate-tree primitive module.

Detailed response matrix:

`docs/reports/goal2638_external_review_response_2026-05-27.md`
