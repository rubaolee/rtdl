# Call For Review: Goal4861 Section 5.7 Re-Entry After LSI Row Repair

Date: 2026-07-02

Please critically review Goal4861.

## Files To Review

- `history/internal_docs/goal4861_section57_reentry_after_lsi_row_repair_result_2026-07-02.md`
- `history/internal_docs/goal4861_section57_public_route_reentry_gate_summary.json`
- `history/internal_docs/goal4861_bundled_helper_streaming_compare_summary.json`
- `history/internal_docs/goal4860_planar_map_lsi_row_materialization_repair_result_2026-07-02.md`
- `history/internal_docs/antigravity_goal4860_planar_map_lsi_row_materialization_repair_review_2026-07-02.md`

## Context

Goal4860 repaired a real Section 5.2 LSI row-materialization bug:

- County x Zipcode: `count == rows == expected == 961165`;
- Australia representative: `count == rows == expected == 13622`.

Goal4861 re-entered Section 5.7 from the repaired LSI rows and checked whether
the remaining County x Zipcode overlay failure belongs to:

- Section 5.2 LSI;
- Section 5.3 PIP;
- or Section 5.7 output-chain assembly.

## Result Summary

Public route:

- Route label: `generic_public_primitives_plus_app_layer`.
- Public LSI passed.
- County x Zipcode PIP consistency passed.
- Public output-chain assembler is not exposed.
- Public LSI rows still lack scaled/rational coordinate fields.
- Preferred route status:
  `blocked_after_public_lsi_and_pip`.
- Exit label:
  `blocked_by_output_chain_app_logic_gap`.

Fallback route:

- Route label: `bounded_bundled_helper_reproduction`.
- Streaming compare against AuthorPatch output failed at line 123678:

```text
author: 41230 2 42104 42105 280 290
rtdl:   41230 2 42104 42105 294 295
```

This first mismatch keeps the same chain id and point ids, but changes the face
ids.  The report classifies this as output-chain face assignment / overlay
assembly, not LSI/PIP.

## Requested Verdict Labels

Choose one:

- `approve_goal4861_blocked_at_output_chain_face_assignment_and_authorize_goal4862`
- `approve_with_required_amendments_before_goal4862`
- `reject_goal4861_classification_and_require_more_lsi_or_pip_single_stage_testing`

## Questions

1. Does the evidence justify saying the original bug was correctly sent back to
   Section 5.2 LSI row materialization and repaired by Goal4860?
2. Does the Goal4861 public-route gate justify saying County x Zipcode LSI and
   PIP are clean enough to stop blaming the current first difference on those
   single stages?
3. Is it correct to classify the preferred public route as
   `blocked_by_output_chain_app_logic_gap` rather than claiming a public
   generic Section 5.7 reproduction?
4. Is the fallback route correctly labeled as
   `bounded_bundled_helper_reproduction`?
5. Does the first difference at chain `41230` support an output-chain face-id
   assignment diagnosis?
6. Should Section 5.7 correctness and performance remain unauthorized?
7. Is Goal4862, a localized chain-41230 face-assignment diagnostic, the right
   next step?
8. Are any additional single-stage 5.2 or 5.3 gates required before Goal4862?

## Non-Authorization

This review must not authorize:

- Section 5.7 byte-equal correctness;
- Section 5.7 topology-equivalent correctness;
- Section 5.7 performance;
- broad RayJoin paper reproduction;
- presenting bundled-helper evidence as generic public-language reproduction.
