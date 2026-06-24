# Phoenix V3 RTDBSCAN Component-Signature Optimization

Status: code optimization landed, RTX evidence pending.

This is not a release report and not an M7 promotion.

```text
status: rtdbscan_component_signature_optimization_pending_rtx_evidence
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## What Changed

Route:

```text
optix_rt_core_flags_numba_prepared_grid_column_signature_3d
```

Before this change, the prepared-grid column-signature path built its signature
with `_cluster_signature_from_partner_columns`, which copied `point_ids`,
`component_labels`, and `is_core` to host before computing the compact
signature.

After this change, the path uses `_cluster_signature_from_numba_label_columns`,
which reuses the existing generic
`run_numba_label_count_and_flag_count_i64` continuation. The route now records:

```text
column_signature_strategy: numba_label_count_and_flag_count_label_columns
column_signature_uses_numba_label_count_and_flag_count: true
column_signature_materializes_point_ids: false
column_signature_materializes_core_flags: false
```

This is a generic engine optimization. It does not add a DBSCAN-native ABI,
does not add DBSCAN-specific native semantics, and does not authorize a full
RTDBSCAN speedup claim.

## Current Boundary

The previous RTDBSCAN no-go packet remains current until RTX reruns are done:

```text
docs/rebuild/v3/phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.md
```

This code change may reopen `component_union`, but only after a serious
same-contract RTX rerun shows the new route materially improves the
component-signature continuation while preserving canonical component-size
signature parity.

Required before any M7 reconsideration:

- rerun same-contract RTDBSCAN OptiX and Embree rows on RTX hardware after this
  code change;
- show component-signature continuation improvement at 65,536, 262,144, and
  524,288 points;
- preserve canonical component-size signature parity;
- obtain external review before any M7 promotion.

## Verification

Focused local tests:

```powershell
py -3 -m unittest tests.v3_phoenix_rtdbscan_component_signature_optimization_test tests.v3_phoenix_rtdbscan_continuation_bottleneck_no_go_test tests.v3_phoenix_rtdbscan_same_contract_rerun_test tests.v3_rebuild_tutorial_surface_test
```

Result: pass.

Full rebuild matrix:

```powershell
py -3 scripts\run_test_matrix.py --group v3_rebuild
```

Result: pass, 46 modules, 215 tests.

## Goal-Level Decision Audit

Decision: land a generic component-signature continuation optimization but keep
RTDBSCAN out of M7 until RTX evidence exists.

1. Was I foolish?

   No. This changes a measured generic bottleneck without inventing
   DBSCAN-specific native semantics.

2. If yes, what actions made the decision foolish?

   It would be foolish to call this an M7 fix before same-contract RTX reruns
   quantify the effect.

3. Was there another path?

   Yes: rerun old evidence unchanged or write more no-go prose. Neither changes
   the bottleneck.

4. Can I now try a different path that actually solves the problem?

   Yes. Use the existing generic Numba label/flag-count continuation in the
   prepared-grid column-signature path, then require a serious RTX rerun.
