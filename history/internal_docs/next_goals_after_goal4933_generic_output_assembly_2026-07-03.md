# Next Goals After Goal4933: Generic Output Assembly Line

Date: 2026-07-03

Current base commit:

`36754ae54 Add generic output assembly smoke evidence`

## Current Fact

Goal4933 closed the first generic output-assembly attempt with an honest result:

- Correctness: pass. Both RayJoin Section 5.7 public-sample routes are byte-equal.
- Generic layer: on path. `assemble_grouped_sequences` processed `673371` item rows into `64459` groups.
- Performance: not a win. Writer time regressed from `2.069s` plain to `2.982s` on the generic-wired path.
- Cause: the generic layer only groups descriptors/items; the expensive author-compatible line materialization still runs in Python chain loops.

Therefore the next work is not more Python micro-tuning. The next work is a gated investigation into whether a **generic compiled output backend** can remove the Python chain-loop without becoming a RayJoin-specific writer.

## Governing Rules

1. No RayJoin-specific output writer in RTDL core.
2. No V3/V4 claims. This is v2.14.2 exploratory performance work.
3. Correctness is a hard gate before timing.
4. Timing claims require warmed-cache, same-contract comparison.
5. If the only viable speedup requires author/RayJoin-specific output semantics in core, stop this optimization line and record it as an app-output boundary.
6. Each completed goal needs external review. Antigravity is enough for ordinary goals; Claude review debt is allowed when Claude is unavailable. A release or architecture decision needs Claude when available.

## Goal4934: Generic Compiled Output Backend Feasibility Gate

Purpose:

Decide whether the remaining RayJoin writer bottleneck can be expressed as a generic output problem, or whether it is inherently app-specific author-format logic.

Work:

- Read the current `section57_overlay_numba.py` writer path and identify exactly which operations are:
  - generic grouping/ordering;
  - generic item/header materialization;
  - app-specific author text formatting;
  - polygon/point id assignment;
  - file IO.
- Define the smallest generic output IR that could be shared by other apps:
  - group descriptors;
  - item rows;
  - optional per-group header fields;
  - payload columns;
  - deterministic order;
  - no RayJoin naming.
- Create no production runtime code unless needed for measurement stubs.

Verification:

- A report lists every writer subphase and classifies it as generic or app-specific.
- The report includes a concrete proposed generic API shape, or explicitly says no such API is honest.
- The report includes a red-line check: no `RayJoin`, `overlay`, `section57`, or author-output-chain identity in RTDL core.
- External review agrees with one exit label below.

Exit labels:

- `generic_compiled_output_backend_feasible`: proceed to Goal4935.
- `app_specific_writer_boundary_stop`: stop the performance line; keep Goal4932/4933 only as correct generic grouping work.
- `needs_more_measurement`: do one bounded measurement goal before deciding.

## Goal4935: Prototype A Generic Compiled/Vectorized Output Materializer

Entry condition:

Goal4934 exits `generic_compiled_output_backend_feasible`.

Purpose:

Build the smallest generic materializer that turns grouped descriptors/items into output records faster than the current Python chain-loop, without encoding RayJoin semantics.

Work:

- Implement a generic output materialization prototype under RTDL generic naming.
- It may be host-columnar, NumPy/Numba/vectorized, or native compiled, but the API must not know RayJoin.
- It should accept generic columns and emit generic record buffers or line fragments.
- Keep app-owned final formatting separate if needed.

Verification:

- Unit tests cover:
  - deterministic grouped output;
  - non-RayJoin grouped pair output;
  - tiny RayJoin adapter byte equality;
  - rejection of app-identity strings in generic core.
- Performance microbench uses synthetic data at Section 5.7 scale.
- Minimum continuation threshold:
  - materializer itself must be faster than the current Python chain-loop component it replaces;
  - if it cannot beat the Python loop on synthetic scale, stop.

Exit labels:

- `generic_materializer_beats_python_loop`: proceed to Goal4936.
- `correct_but_not_faster_stop`: stop implementation and keep only correctness/API evidence.
- `rejected_as_app_specific`: stop and do not place it in RTDL core.

## Goal4936: Wire The Generic Materializer Into RayJoin Public Sample

Entry condition:

Goal4935 exits `generic_materializer_beats_python_loop`.

Purpose:

Test whether the generic materializer helps the real RayJoin Section 5.7 public-sample app.

Work:

- Wire the generic materializer into `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`.
- Keep author-compatible final text formatting app-owned.
- Run the public sample on POD with warmed cache.

Verification:

- Byte-equal to the public answer.
- Same data, same warmed-cache protocol as Goal4933.
- Compare:
  - plain writer: `2.069s` from Goal4933;
  - Goal4933 generic writer: `2.982s`;
  - new materializer writer.
- To continue beyond this goal, the new writer must beat the plain writer by a meaningful margin:
  - target: `output_chain_write_sec <= 1.65s`;
  - minimum: strictly below `2.069s` with repeated-run confirmation.

Exit labels:

- `rayjoin_writer_speedup_generic_and_byte_equal`: proceed to Goal4937.
- `byte_equal_but_not_faster_stop`: stop the performance line.
- `correctness_failed_redo_or_revert`: revert app wiring and diagnose.

## Goal4937: Non-RayJoin Generality Proof

Entry condition:

Goal4936 exits `rayjoin_writer_speedup_generic_and_byte_equal`.

Purpose:

Prove the materializer is not a RayJoin writer hidden behind generic names.

Work:

- Use the same generic output materializer on one non-RayJoin workload:
  - grouped segment-pair output;
  - grouped hit rows;
  - kNN/radius neighbor row output;
  - or another existing benchmark-style grouped output.
- No RayJoin app files may be imported.

Verification:

- Non-RayJoin test passes.
- Same materializer API is used.
- No app-identity terms appear in the generic core.
- Performance is at least not worse than the old Python output loop for that non-RayJoin case.

Exit labels:

- `genericity_proven_on_second_workload`: proceed to Goal4938.
- `rayjoin_only_reject_core_promotion`: remove or isolate the materializer as app-level only.

## Goal4938: Repeated POD Performance Scorecard

Entry condition:

Goal4937 exits `genericity_proven_on_second_workload`.

Purpose:

Produce a serious repeated-run performance readout for v2.14.2 output assembly improvements.

Work:

- Run warmed-cache repeated trials on POD.
- Compare:
  - AuthorOfficial comparator where available;
  - RTDL plain route;
  - RTDL current Goal4933 generic route;
  - RTDL new materializer route.
- Use the same public sample and any available representative pairs.

Verification:

- At least 5 repeated runs per route.
- Median, min, max, and raw JSON artifacts.
- Byte-equal correctness for every performance row.
- No geomean headline unless every row is same-contract and correctness-passing.

Exit labels:

- `performance_scorecard_supports_v2_14_2_output_assembly`: proceed to Goal4939.
- `performance_scorecard_does_not_support_release_claim`: stop with internal evidence only.

## Goal4939: v2.14.2 Public/Private Boundary Decision

Entry condition:

Goal4938 exits `performance_scorecard_supports_v2_14_2_output_assembly`, or the owner explicitly chooses to ship only the generic API without speed claims.

Purpose:

Decide what, if anything, becomes public in v2.14.2.

Work:

- Decide whether the new output assembly API is:
  - public user API;
  - experimental/internal API;
  - RayJoin app-local only;
  - or removed.
- Draft public wording only if the scorecard supports it.
- Keep all RayJoin reproduction details in `Paper-reproduction-apps/` and internal docs, not in the user-facing front page unless intentionally published.

Verification:

- Public surface scan has no internal goal/review leakage.
- Docs do not claim speedups unsupported by Goal4938.
- Examples/tutorials are not polluted with paper-reproduction internals.

Exit labels:

- `ready_for_v2_14_2_public_docs_update`
- `keep_internal_no_public_claim`
- `remove_or_archive_experimental_api`

## Goal4940: External Release Decision

Entry condition:

Goal4939 exits `ready_for_v2_14_2_public_docs_update`.

Purpose:

Get final approval for any v2.14.2 public claim related to output assembly.

Work:

- Prepare final packet:
  - code summary;
  - correctness evidence;
  - repeated performance evidence;
  - public wording;
  - non-claims.
- Send to external review.

Verification:

- Antigravity review complete.
- Claude review when available, or explicit review debt if not available.
- Final owner decision recorded.

Exit labels:

- `authorize_v2_14_2_output_assembly_release`
- `release_without_performance_claim`
- `do_not_release_output_assembly_changes`

## Immediate Next Action

Start with Goal4934 only.

Do not implement Goal4935 until Goal4934 proves that a generic compiled output backend is honest and feasible.
