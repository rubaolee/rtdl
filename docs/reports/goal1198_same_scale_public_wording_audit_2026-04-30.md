# Goal1198 Same-Scale Public Wording Audit

Date: 2026-04-30

Goal1198 audits whether accepted evidence can support public positive ratio wording. It does not authorize public docs, release, or speedup claims by itself.

## Summary

- valid: `False`
- supersedes: Goal1196 Hausdorff positive wording proposal is unsafe because the accepted artifacts are not same-scale.
- safe positive public ratio apps: `road_hazard_screening`
- unsafe or blocked ratio apps: `database_analytics, graph_analytics, polygon_pair_overlap_area_rows, polygon_set_jaccard, hausdorff_distance`

## Rows

| App | Embree copies | OptiX copies | Same scale | Ratio | OptiX faster | Public ratio safe |
| --- | ---: | ---: | --- | ---: | --- | --- |
| `database_analytics` | `30000` | `30000` | `True` | `0.791844` | `False` | `False` |
| `graph_analytics` | `30000` | `30000` | `True` | `n/a` | `False` | `False` |
| `road_hazard_screening` | `20000` | `20000` | `True` | `4.014155` | `True` | `True` |
| `polygon_pair_overlap_area_rows` | `20000` | `20000` | `True` | `0.839019` | `False` | `False` |
| `polygon_set_jaccard` | `8192` | `8192` | `True` | `0.548760` | `False` | `False` |
| `hausdorff_distance` | `2000` | `1200000` | `False` | `13.728463` | `True` | `False` |

## Blockers

- hausdorff_distance has OptiX-faster ratio but not same-scale artifacts

## Conclusion

Only same-scale, OptiX-faster rows may proceed to positive public wording review. In the current evidence, that leaves `road_hazard_screening` only. `hausdorff_distance` remains technically evidence-ready for RT traversal, but its positive ratio wording must be blocked until same-scale or explicitly normalized evidence is collected and reviewed.

