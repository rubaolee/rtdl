# Goal4940 RayJoin Path-Split Adapter POD Gate

Date: 2026-07-04

## Verdict

`byte_equal_but_not_faster_stop__compiled_path_split_required`

Goal4940 wired the Goal4939 generic path-split row-buffer prototype into the RayJoin Section 5.7 public sample app adapter and ran the POD gate.

The route preserved byte-for-byte correctness, but it missed the same-run writer performance gate. The experimental RayJoin app wiring was reverted. The generic Goal4939 API remains valid and retained.

## Purpose

Goal4937 proved that downstream materialization was too late. Goal4938 moved the boundary upstream to path/chain splitting. Goal4939 implemented a generic host-columnar path-split row-buffer prototype.

Goal4940 tested whether that generic prototype can replace the RayJoin app chain loop on the public sample.

## Implementation Tested

Temporary app adapter route:

```text
RayJoin app computes split-event columns and interval descriptors
  -> assemble_grouped_path_split_records
  -> materialize_grouped_output_row_buffer
  -> RayJoin app formats author-compatible text
```

Boundary preserved:

- RTDL core receives neutral chain/split/event/descriptor columns.
- RayJoin app owns labels, keep/drop policy, face-pair ids, point ids, and final text formatting.
- No RayJoin semantics were added to RTDL core.

## POD

- Host: `157.157.221.29:24344`
- GPU: NVIDIA RTX 4000 Ada Generation
- Dataset: RayJoin public sample, County x Soil
- Output directory on POD: `Paper-reproduction-apps/rayjoin-paper/_runs/goal4940/rtdl`
- Local artifacts: `history/internal_docs/goal4940_pod_artifacts/`

## Results

| Route | Byte Equal | Total Elapsed | Writer Time |
|---|---:|---:|---:|
| existing plain writer | true | 6.135681s | 2.559022s |
| generic path-split adapter | true | 7.753231s | 4.175830s |

Performance gate:

- Required: path-split adapter writer beats same-run plain writer.
- Observed: `4.175830s` vs `2.559022s`.
- Result: failed.

## Path-Split Route Breakdown

| Phase | Seconds |
|---|---:|
| `skip_plan_sec` | 0.065587 |
| `group_xsects_map0_sec` | 0.007265 |
| `group_xsects_map1_sec` | 0.014033 |
| `path_split_descriptor_build_map0_sec` | 0.162320 |
| `path_split_descriptor_build_map1_sec` | 0.118066 |
| `path_split_materialize_map0_sec` | 1.362668 |
| `path_split_materialize_map1_sec` | 1.025879 |
| `path_split_format_map0_sec` | 0.772231 |
| `path_split_format_map1_sec` | 0.582574 |

The route produced:

- Map 0: 36,833 groups, 378,372 item rows, 20,860 split events.
- Map 1: 27,626 groups, 294,999 item rows, 20,860 split events.
- Combined output: 64,459 chains, 673,371 points, 737,830 lines.

## Interpretation

Goal4940 proves the boundary is semantically correct but not yet performant.

The host-columnar Python prototype did move the conceptual boundary earlier than Goal4937. But it still implements path splitting and materialization in Python/NumPy-host code. That creates a new large cost:

```text
path_split_materialize_map0 + map1 = 2.388547s
path_split_format_map0 + map1 = 1.354805s
```

So it replaced the old custom Python chain loop with a generic host-columnar Python path-split/materialize path that is still slower than the existing specialized writer.

This means the next performance step is not another app adapter patch. It must either:

1. compile the generic path-split/materialize implementation, or
2. move it into a native/device-resident row-buffer path.

If that is not pursued, the writer performance line should stop.

## Source State

The experimental RayJoin app adapter edits were reverted after the POD gate failed.

Retained:

- Goal4939 generic core API and tests;
- this Goal4940 report;
- POD JSON artifacts;
- external review packet.

Not retained:

- the slower default RayJoin app route.

## Non-Claims

Goal4940 does not authorize:

- RayJoin speedup claims;
- public performance wording;
- release claims;
- keeping the slower app route as default;
- hiding author/RayJoin text semantics in RTDL core.

## Next Decision

There are only two honest choices:

1. **Proceed to Goal4941**: implement a compiled/native generic path-split materializer, still with non-RayJoin proof first, then RayJoin gate.
2. **Stop Layer 3 RayJoin writer optimization**: keep the current specialized writer as product state and record that host-columnar generic path split is correct but too slow.

Do not continue micro-patching Goal4940's app adapter.

## Exit Label

`byte_equal_but_not_faster_stop__compiled_path_split_required`
