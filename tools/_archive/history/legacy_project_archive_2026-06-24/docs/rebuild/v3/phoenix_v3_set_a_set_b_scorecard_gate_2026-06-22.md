# Phoenix V3 Set A / Set B Scorecard Gate

Status: `classification_frozen_current_scorecard_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
```

## Current Scorecard

| Metric | Value |
| --- | ---: |
| Rows classified | 52 / 52 |
| Set A rows | 42 |
| Set B rows | 10 |
| Set A geomean | 1.013x |
| Set B geomean | 1.007x |
| Set A apps over 1.05x | 1 / 5 required |
| Set A severe regressions below 0.90x | 1 |
| Set B rows below 0.95x | 1 |
| Focused material productized probes | 3 / 2 required |

## Set A App Geomeans

| App | V3 vs V2.14 |
| --- | ---: |
| `barnes_hut` | 0.844x |
| `hausdorff_xhd` | 1.149x |
| `rt_dbscan` | 0.988x |
| `rtnn` | 1.003x |
| `spatial_rayjoin` | 1.027x |
| `triangle_counting` | 0.987x |

## Set B App Geomeans

| App | V3 vs V2.14 |
| --- | ---: |
| `contact_manifold` | 1.017x |
| `librts_spatial_index` | 0.937x |
| `raydb_style` | 1.046x |
| `robot_collision` | 0.993x |

## Interpretation

The frozen classification makes the current failure more precise:
Set A does not show material productized-path superiority, Set B has
an identified sub-0.95x control row. The focused material
productized-probe precondition is closed at 3/2, but
full all-app pod spend remains blocked by the Set-A severe regression,
the Set-A app-win/geomean shortfall, and the Set-B parity row.

This gate does not authorize release or public performance wording.
