# Goal4816-C RayJoin Section 5.7 App-Only Reproduction Design

Date: 2026-06-30

Status: `goal4816_C_app_only_design_complete_pending_review`

Authorized by:

- `history/internal_docs/antigravity_goal4816_B_capability_map_review_2026-06-30.md`
- Verdict: `approve_goal4816_B_capability_map_authorize_4816_C`

This goal designs the implementation path only. It does not start implementation
and does not authorize POD performance runs.

## Role Constraint: RTDL User, Not RTDL Developer

For Goal4816 and its follow-up implementation goals, the agent must behave like
an RTDL user/application author working with an installed RTDL package.

Consequences:

- Use RTDL's already released design, public modules, documented examples, and
  existing partner-continuation facilities efficiently.
- Do not improve, patch, or extend RTDL runtime/native code to make RayJoin pass.
- Do not treat private underscored helpers as ordinary user API. If a route
  requires private helpers, label it `bundled_rayjoin_helper`, not
  `generic_primitive_numba`.
- If the app implementation is clumsy because it ignores an existing good RTDL
  feature, that is an application-author failure and must be corrected before
  declaring a product gap.
- If a necessary capability is genuinely unavailable to a user of released
  RTDL, record `missing_v2_14_capability`, `unresolved_pip_tie_break_contract`,
  or `missing_input`; do not modify RTDL to hide the gap.

## Non-Negotiable Rule

Goal4816-C must design a RayJoin Section 5.7 reproduction using only released
RTDL v2.14 behavior plus user/application Python and explicit Numba partner
continuations.

It must not:

- modify `src/rtdsl/**`;
- modify `src/native/**`;
- modify the v2.14 release surface;
- add a RayJoin-specific runtime primitive;
- rely on undocumented runtime patches;
- present bundled-helper output as generic user-language reproduction.

## Route Split

Goal4816-C defines two separate routes. They must never be merged in wording.

### Route 1: Bundled Helper Bounded Reproduction

Label:

`bundled_helper_bounded_available_input_reproduction_not_generic`

Purpose:

Use RTDL's shipped RayJoin helper path to reproduce available Section 5.7 CDB
overlay rows. This route can demonstrate that RTDL ships a RayJoin-compatible
helper path for bounded inputs, but it does not prove that a user built Section
5.7 from generic RTDL primitives.

Allowed RTDL assets:

- `rtdsl.rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths`
- `rtdsl.rayjoin_overlay.run_rayjoin_overlay_rtdl`
- internal bundled helpers reached by that path:
  `_run_lsi_rows`, `_run_point_location_faces`, `_PreparedPointLocationRunner`,
  `_assemble_output_chains`, `write_output_chains`

Input requirements:

- Exact paper-preprocessed CDB inputs are required for exact Section 5.7 claims.
- Same-source regenerated CDBs must be labeled `same_source_regenerated_cdb`.
- Current POD state, as checked in Goal4816-B, does not contain the old
  `/workspace/rayjoin_section57_data/cdb_topology` exact root and only has
  same-source County x Zipcode under `/workspace/rayjoin_section57_same_source_cdb`.

Correctness target:

1. strongest: byte-equal author-format overlay output against author code;
2. acceptable bounded diagnostic: topology-equivalent output with documented
   hash/count diagnostics;
3. insufficient for full reproduction: scalar LSI/PIP count only.

Design sketch:

```python
from pathlib import Path

from rtdsl.rayjoin_overlay import run_rayjoin_overlay_rtdl_from_cdb_paths

result = run_rayjoin_overlay_rtdl_from_cdb_paths(
    Path(left_cdb),
    Path(right_cdb),
    backend="optix",
    assemble_output=True,
    output_path=Path(rtdl_output_path),
)
```

Claim boundary:

- This is a bundled helper route.
- It is not generic RTDL language reproduction.
- It can be compared to author code only on the same input provenance and same
  timing/output boundary.

### Route 2: Generic Primitive + Numba Attempt

Label:

`generic_primitive_numba_attempt`

Purpose:

Attempt to write the Section 5.7 application as a user would: generic RTDL
prepared primitives for RT traversal, plus Python/Numba application code for
continuation/output stages. This is the strongest language-capability route,
but Goal4816-B shows it is not yet proven.

Allowed RTDL assets:

- `rtdsl.datasets.load_cdb`
- `rtdsl.datasets.chains_to_segments`
- `rtdsl.datasets.chains_to_rayjoin_cdb_segments`
- `rtdsl.datasets.chains_to_topology_rows`
- package submodule imports from `rtdsl.optix_runtime` when available in the
  installed release:
  `prepare_segment_pair_intersection_optix`,
  `prepare_segment_pair_left_set_optix`,
  `prepare_directed_segment_point_location_2d_optix`
- exported Numba partner continuations:
  `run_numba_compact_mask_i64`,
  `execute_compact_mask_typed_stream_partner_columns`,
  `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`

Disallowed shortcuts:

- directly calling `run_rayjoin_overlay_rtdl_from_cdb_paths`;
- directly calling `_run_lsi_rows`, `_run_point_location_faces`, or
  `_assemble_output_chains`;
- depending on private underscored functions as if they were user-facing API;
- setting private pair-dump environment variables as if they were public API;
- changing native code to expose missing rows;
- silently changing PIP tie-break behavior.

Stage plan:

| Stage | Generic route design | Current design result |
| --- | --- | --- |
| Load CDB/topology | Use `load_cdb` and `chains_to_*` helpers to create segment, CDB, point, and topology columns. | Feasible for available CDB files. |
| LSI traversal | Use `prepare_segment_pair_intersection_optix` and `prepare_segment_pair_left_set_optix`. | Feasible for scalar count. Full overlay requires intersection pair rows and exact coordinates; no clean public row-output API identified outside bundled helper/private dump path. |
| LSI rows/coordinates | User app would need pair ids plus exact intersection coordinates. | Current generic route is blocked unless a public row-output surface exists or the user implements row reconstruction outside RTDL. Mark as `missing_v2_14_capability` for clean generic route if no public row API is accepted. |
| Vertex PIP | Use `prepare_directed_segment_point_location_2d_optix` for point-location rows/face ids. | Feasible as a primitive, but exact clarified author determinism remains `unresolved_pip_tie_break_contract`. |
| Midpoint projection | User Python/Numba can compute midpoints after LSI rows are available. | Blocked by generic LSI row availability if no row surface exists. |
| Midpoint PIP | Reuse directed point-location primitive on generated midpoint points. | Feasible after midpoint inputs exist, with same tie-break caveat. |
| Output-chain assembly | User Python/Numba implements RayJoin chain split/flush/face-id assignment. | Feasible as application logic in principle, but not proven performant and not a RTDL primitive. |
| Numba continuation | Use Numba for compact masks, owner-face/side filtering, or other column continuation. | Feasible for post-RT continuation, not replacement for RT traversal/output-chain semantics. |

Minimal skeleton:

```python
from pathlib import Path

from rtdsl.datasets import chains_to_rayjoin_cdb_segments
from rtdsl.datasets import chains_to_topology_rows
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import prepare_directed_segment_point_location_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix

left = load_cdb(Path(left_cdb))
right = load_cdb(Path(right_cdb))

left_segments = chains_to_rayjoin_cdb_segments(left)
right_segments = chains_to_rayjoin_cdb_segments(right)
left_topology = chains_to_topology_rows(left)
right_topology = chains_to_topology_rows(right)

with prepare_segment_pair_intersection_optix(right_segments) as right_index:
    with prepare_segment_pair_left_set_optix(left_segments) as left_set:
        lsi_count = right_index.count_prepared_left_exact_intersections(left_set)

# This count is not enough for Section 5.7 overlay.
# A clean generic route still needs public pair-row/intersection-coordinate
# output before midpoint/output-chain stages can be implemented without bundled
# helper code.

with prepare_directed_segment_point_location_2d_optix(right_segments) as locator:
    pip_rows = locator.run_raw(left_points)
```

Expected outcome of Route 2 at design time:

- The generic route can express parts of the workload.
- It is not yet a complete generic Section 5.7 route because clean public LSI
  row/coordinate output and exact PIP tie-break closure are not proven.
- The correct exit may be `blocked_by_v2_14_capability_gap` or
  `blocked_by_pip_tie_break_gap`, not a runtime patch.

## Correctness Gates Before Any POD Performance

Any implementation after this design must pass these gates before timing:

1. **Input provenance gate**
   - `paper_preprocessed_cdb`, `historical_exact_cdb`, or
     `same_source_regenerated_cdb` must be stated per pair.
2. **Author baseline gate**
   - author commit and command must be recorded;
   - dirty author tree must be avoided with `git show HEAD:<file>` for source
     semantics.
3. **Output gate**
   - byte-equal author-format output is required for full reproduction;
   - topology-hash/count diagnostics can only support bounded diagnostics;
   - scalar count-only rows cannot pass full overlay correctness.
4. **PIP determinism gate**
   - state whether the route follows committed author `HEAD` behavior or the
     author-reply `t_reported` clarification;
   - repeated-run PIP exterior/non-exterior flips must not be ignored.
5. **Route-label gate**
   - every result must state `bundled_helper` or `generic_primitive_numba`;
   - no result can mix the two labels for claim wording.

## Next Goal Recommendation

Proceed to Goal4816-D only after review of this design.

Goal4816-D should be a local/POD preflight and correctness smoke plan, not a
performance run. It should choose one route:

- if the user wants fastest honest progress, start with Route 1 on the available
  CDB slice and label it bundled-helper bounded reproduction;
- if the user wants the strongest language-capability test, start Route 2 and
  expect an early gap decision unless clean public LSI row output is identified.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No, because the design refuses to hide the main split: bundled helper is
   feasible, generic primitive + Numba is only partially feasible today.

2. **What would make this foolish?**
   It would be foolish to code Route 1 and call it Route 2, or to treat scalar
   LSI/PIP count as overlay.

3. **Is there another path that avoids being trapped?**
   Yes. Keep both routes alive until the user/reviewer chooses the claim
   standard, but make every result carry its route label.

4. **Can I try a better path now?**
   Yes. The next useful work is not performance; it is a correctness smoke plan
   that chooses one route and one available input slice.

## Exit Label

`goal4816_C_app_only_design_complete_pending_review`
