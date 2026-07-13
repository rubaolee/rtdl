# Goal4951 Compiled Generic Path-Split Materializer

Date: 2026-07-04

Status: proposed_goal_pending_review

## Purpose

Goal4951 is the next performance goal after Layer 1/2 closure.

Prior evidence says:

- Layer 1/2 connector capability works.
- Current app-layer Numba helper is not a RayJoin performance win.
- Host-columnar Python path-split materialization is semantically correct but too slow.
- The remaining RayJoin public-sample bottleneck is structural path/output assembly, not final file I/O and not prepared-hot PIP traversal.

Therefore Goal4951 tests the only remaining Layer 3 performance path that is still consistent with the genericity rules:

> Compile the generic path-split / grouped-record materializer itself, while keeping RayJoin text formatting app-owned.

## Relationship To Previous Goals

- Goal4938: decided the generic boundary must move upstream to path splitting.
- Goal4939: implemented `assemble_grouped_path_split_records` as a generic host-columnar prototype.
- Goal4940: wired that prototype into the RayJoin public sample and proved byte-equality but a performance regression.
- Goal4949 clean-head erratum: confirmed current source still has writer/structural assembly as a real bottleneck.
- Goal4950: closed Layer 1/2 as capability success but RayJoin performance no-go.

Goal4951 does not repeat Goals 4939/4940. It specifically targets the failed part of Goal4940: Python/host materialization cost.

## Scope

Allowed:

- implement a compiled generic path-split materializer as an internal spike;
- use Numba CPU, native C/C++, or another compiled route if it stays generic;
- add synthetic tests for non-RayJoin path-split fixtures;
- add RayJoin app-adapter wiring only after non-RayJoin synthetic tests pass;
- collect POD timing on the public County x Soil sample.

Forbidden:

- no RayJoin-specific names or semantics in RTDL core;
- no author-compatible text formatting in RTDL core;
- no polygon-overlay keep/drop policy in RTDL core;
- no midpoint face computation in RTDL core;
- no broad performance or release claim;
- no continuation if byte-equality fails.
- no binary-map assumption; the compiled route must accept arbitrary chains and
  split events rather than assuming two maps, two directions, or map indexes.

## Generic Contract

The compiled materializer may know only:

- chains;
- point offsets and counts;
- ordered split events;
- optional primitive descriptor columns;
- optional validity mask;
- output group ids;
- primitive numeric x/y item payloads.

It must not assume a fixed number of input maps, directions, or graph sides.
The generic unit is a collection of independent base chains and ordered split
events.

It must output a neutral row-buffer or equivalent columnar structure:

- group ids / group offsets / group lengths;
- item x/y columns;
- optional descriptor columns;
- statistics.

RayJoin may only adapt:

- its chain topology into generic chain columns;
- its intersection events into generic split-event columns;
- its app labels into descriptor/validity columns;
- final author text formatting after generic assembly.

## Verification Plan

### Gate A: Source Genericity

Any new core source file must reject app-identity language:

- `rayjoin`
- `overlay`
- `section57`
- `author`
- `map0`
- `map1`

These words may appear only in tests or app adapters, not in the generic core module.

### Gate B: Non-RayJoin Synthetic Correctness

A non-RayJoin path segmentation fixture must pass:

- one chain with multiple split events;
- multiple chains;
- a fixture with more than two independent chains to guard against hidden
  binary-map assumptions;
- validity mask skipping at least one interval;
- descriptor preservation;
- consecutive point dedupe.

It must compare exactly to the existing Python `assemble_grouped_path_split_records` + `materialize_grouped_output_row_buffer` result.

### Gate C: RayJoin Public Sample Correctness

If Gate B passes, wire the compiled materializer into the RayJoin public sample as an app adapter.

Required:

- `section57_overlay.py` baseline remains byte-equal;
- compiled path-split route remains byte-equal;
- RayJoin text formatting stays in the app.

### Gate D: Performance

The compiled path-split writer must beat the same-run plain writer.

Minimum useful gate:

- writer speedup >= `1.10x`

Strong gate:

- writer speedup >= `1.25x`

If byte-equal but slower, the route is killed and not retained as default.

## Expected Outcomes

Possible exits:

1. `compiled_path_split_win_continue_productization`
2. `compiled_path_split_correct_but_not_faster_stop`
3. `compiled_path_split_fast_but_wrong_reject`
4. `compiled_path_split_genericity_violation_reject`
5. `compiled_path_split_environment_blocked`

## Decision Audit

This goal is not a looks-busy micro-optimization because it directly attacks the measured structural bottleneck left by Goals 4930, 4938, 4940, and 4949.

It is also not a RayJoin-specific shortcut because the first proof must be non-RayJoin and the generic core must not contain RayJoin vocabulary or semantics.

The kill condition is simple:

> If the compiled generic materializer cannot beat the same-run plain writer while preserving byte-equality, stop this line.
