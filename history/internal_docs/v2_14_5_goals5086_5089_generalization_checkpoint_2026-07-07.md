# v2.14.5 Goals5086-5089 Generalization Checkpoint

Date: 2026-07-07

## Verdict Label

```text
completed_v2_14_5_generalization_checkpoint_goals5086_5089
```

## Scope

This checkpoint covers the first v2.14.5 batch after v2.14.4 closure:

```text
Goal5086 public RTDL API surface audit
Goal5087 unified paper-app skeleton and manifest schema
Goal5088 third validation candidate selection
Goal5089 RT-DBSCAN paper-app requirements scaffold
```

The batch advances the project from "two successful paper-app lines" to a
repeatable paper-app program:

- classify the RTDL API surface,
- define a paper-app template,
- choose the third validation family,
- scaffold that family without overclaiming.

## Goal5086 Summary

Created:

```text
history/internal_docs/goal5086_public_rtdl_api_surface_audit_2026-07-07.md
history/internal_docs/call_for_review_goal5086_public_rtdl_api_surface_audit_2026-07-07.md
```

Main result:

- Planar-map LSI/PIP are public documentable APIs with OptiX/backend limits.
- `AggregateHierarchy3D` reference execution is public documentable generic API.
- device-column and row-buffer APIs are advanced/experimental and must not be
  described as true zero-copy or whole-app speedups.
- `device_order_by` is public-contract but not release-authorized.
- `device_group_by` is not public.
- RayJoin-named native symbols and `rtdsl.rayjoin_overlay` remain legacy/naming
  debt, not primary public language surface.
- Paper-specific comparators, output formatting, author patches, and workload
  choices stay app-owned.

## Goal5087 Summary

Created:

```text
Paper-reproduction-apps/PAPER_APP_TEMPLATE.md
Paper-reproduction-apps/paper_app_manifest.schema.json
history/internal_docs/goal5087_unified_paper_app_skeleton_result_2026-07-07.md
history/internal_docs/call_for_review_goal5087_unified_paper_app_skeleton_2026-07-07.md
```

Updated:

```text
Paper-reproduction-apps/README.md
```

Main result:

- Future paper apps have a required README shape and manifest vocabulary.
- The manifest records public APIs, experimental APIs, app-owned assets,
  reproduction status, comparator/input/output policy, performance regimes, and
  forbidden claims.
- This is a reader-facing contract, not a runtime input.

## Goal5088 Summary

Created:

```text
history/internal_docs/goal5088_third_validation_candidate_selection_2026-07-07.md
history/internal_docs/call_for_review_goal5088_third_validation_candidate_selection_2026-07-07.md
```

Main result:

- Selected RT-DBSCAN-style as the third validation candidate.
- Reason: it exercises fixed-radius/count-threshold traversal, core flags/core
  counts, and partner component continuation, which is distinct from both
  RayJoin and RT-BarnesHut.
- The selection does not claim reproduction. It only authorizes a requirements
  and scaffold step.

## Goal5089 Summary

Created:

```text
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
history/internal_docs/goal5089_rt_dbscan_paper_app_requirements_scaffold_2026-07-07.md
history/internal_docs/call_for_review_goal5089_rt_dbscan_paper_app_requirements_scaffold_2026-07-07.md
```

Updated:

```text
Paper-reproduction-apps/README.md
```

Main result:

- Added `rt-dbscan-paper` as the third paper-app scaffold.
- Manifest status is `not_started`.
- Paper metadata uses existing local benchmark metadata:
  `RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware`, IPDPS 2023,
  DOI `10.1109/IPDPS54959.2023.00100`.
- Author artifact and exact paper inputs are explicitly not pinned yet.
- Recommended first bounded target is prepared fixed-radius core flags or core
  counts; bounded component signature is optional after requirements review.

## Verification

JSON validation:

```text
py -m json.tool Paper-reproduction-apps/paper_app_manifest.schema.json
py -m json.tool Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
```

Both passed. The local Python launcher printed its known prefix warning, but
returned success.

Public-surface leak scans across the modified public paper-app docs returned:

```text
0 matches
```

for:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

No runtime behavior was changed in this checkpoint.

## Claim Boundary

This checkpoint does not:

- claim RT-DBSCAN reproduction,
- claim exact RT-DBSCAN paper input recovery,
- claim RT-DBSCAN performance,
- make `device_order_by` release-authorized,
- make `device_group_by` public,
- remove RayJoin legacy naming debt,
- promote app-specific comparator or output logic into RTDL core.

## Next Recommended Goal

Goal5090 should be:

```text
RT-DBSCAN requirements audit and first bounded target decision
```

It should decide:

1. author artifact status,
2. paper input status,
3. first bounded target,
4. comparator,
5. reusable benchmark assets,
6. whether a local smoke gate can be written without overclaiming.
