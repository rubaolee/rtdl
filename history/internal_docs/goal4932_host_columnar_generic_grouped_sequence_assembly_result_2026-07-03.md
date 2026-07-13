# Goal4932 Result: Host-Columnar Generic Grouped-Sequence Assembly Prototype

Date: 2026-07-03

Exit label: `complete_host_columnar_generic_assembly_prototype_no_performance_claim`

## Purpose

Implement the Stage A prototype authorized by Goal4931:

- host-columnar only;
- generic grouped sequence assembly;
- no native traversal changes;
- no device-resident row-buffer implementation;
- no RayJoin-specific output formatting in RTDL core.

## Files Changed

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py
src/rtdsl/output_assembly.py
src/rtdsl/__init__.py
tests/goal4932_generic_output_assembly_test.py
```

## Implemented API

Goal4932 adds a public, generic output-assembly module:

```python
from rtdsl import GroupedSequenceAssemblyPlan
from rtdsl import GroupedSequenceAssemblyResult
from rtdsl import assemble_grouped_sequences
```

The API converts equal-length typed columns into deterministic grouped
sequences:

```text
columns + plan
  -> filter by validity column
  -> stable sort by group keys and order keys
  -> optional consecutive dedupe by group + dedupe keys
  -> group offsets / group lengths / payload columns
```

The result is a compact structural representation:

- `group_keys`;
- `group_offsets`;
- `group_lengths`;
- `item_indices`;
- `item_columns`;
- `stats`.

It does not write text. It does not know application output formats.

## Genericity Boundary

The core module intentionally contains no app identity. The test checks that
`src/rtdsl/output_assembly.py` contains no lower-case matches for:

```text
rayjoin
overlay
section57
```

The API names are generic:

- `GroupedSequenceAssemblyPlan`;
- `GroupedSequenceAssemblyResult`;
- `assemble_grouped_sequences`.

No RayJoin exact text/topology formatting moved into RTDL core.

## Proof Workloads

### 1. Generic deterministic grouping

Rows are grouped by `group_id`, ordered by `rank`, and payloads are returned in
deterministic order. This proves the basic grouped-sequence contract.

### 2. Generic validity + dedupe

Rows are filtered by an `emit` validity column and consecutively de-duplicated by
`point_id` within each group. This is a generic structural operation, not an app
format rule.

### 3. Non-RayJoin spatial join grouped pairs

Rows shaped as `{left_id, right_id, score, emit}` are grouped by `left_id` and
ordered by `right_id`, producing grouped candidate lists:

```text
{1: [10, 12], 3: [30, 31]}
```

This is the required non-RayJoin proof that the prototype is not only a RayJoin
helper.

### 4. Section 5.7-like chain descriptor shape

Rows shaped as `{chain_id, point_order, point_id, x, y, emit}` are assembled into
group offsets and item payload arrays. This proves the generic structure can
represent the shape that the RayJoin app adapter needs.

Important boundary: this is not the full RayJoin writer and does not write
AuthorOfficial bytes. Final formatting remains app-owned.

### 5. Tiny RayJoin app-adapter byte-equality proof

`section57_overlay_numba.py` now routes its app-layer point-line grouping through
`assemble_grouped_sequences` before final text writing. The final text/topology
format remains in the app wrapper.

The test constructs two tiny chains with no intersections and compares:

- baseline `section57_overlay.write_output_chains_streaming`;
- `section57_overlay_numba.write_output_chains_streaming_numba_skip`, now using
  generic grouped-sequence assembly for final point-line grouping.

The byte output is identical, and the returned writer metadata records:

```text
generic_output_assembly.enabled = true
generic_output_assembly.group_count = 2
chain_count = 2
```

This is a real app-adapter wiring proof on a tiny controlled case. It is not a
public-sample performance result.

## Verification

Commands run locally:

```powershell
py -m py_compile src/rtdsl/output_assembly.py
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py
```

Result: pass.

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
py -m unittest tests.goal4932_generic_output_assembly_test
```

Result:

```text
Ran 7 tests
OK
```

Adjacent public API regression:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
py -m unittest tests.goal4913_planar_map_workspace_api_test tests.goal4932_generic_output_assembly_test
```

Result:

```text
Ran 11 tests
OK
```

## POD Status

The new POD is reachable only with the historical current-pod key:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod root@157.157.221.29 -p 24344
```

Probe result:

```text
hostname: ce489c3fad22
GPU: NVIDIA RTX 4000 Ada Generation, 20475 MiB, driver 580.65.06
```

The POD currently has no repository checkout under `/root`. Goal4932 did not run
POD performance, and no performance claim is made.

## What This Does Not Prove

Goal4932 does not prove:

- full RayJoin Section 5.7 writer rewiring;
- RayJoin byte equality through the new assembler on the public sample;
- any hot-path speedup;
- device-resident row-buffer behavior;
- native or CUDA execution;
- Layer 4 in-traversal fusion.

It proves that the generic host-columnar structural assembly API exists, is
exported, is deterministic, is not app-identity-specific at the core module
boundary, and can be used by the RayJoin app adapter on a tiny byte-equal case.

It does not prove public-sample byte equality or performance movement.

## Recommended Next Goal

**Goal4933: RayJoin Public-Sample Generic Assembly POD Smoke**

Scope:

- keep RTDL core generic;
- run the already-wired `section57_overlay_numba.py` public sample path on POD;
- preserve AuthorOfficial byte equality on the public sample;
- measure structural assembly before/after;
- keep final text/topology formatting in the app adapter;
- preserve the non-RayJoin proof workload.

Goal4933 is the first goal that may measure whether the generic assembler moves
the Goal4930 structural assembly bottleneck. Goal4932 itself is not a
performance result.
