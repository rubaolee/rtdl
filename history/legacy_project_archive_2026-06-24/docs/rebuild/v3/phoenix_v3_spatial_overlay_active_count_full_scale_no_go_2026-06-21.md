# Phoenix V3 Spatial Overlay Active-Count Full-Scale Candidate

Status: `spatial_overlay_active_count_full_scale_no_go`.

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added now: 0
```

## Candidate

- Row id: `overlay_active_count_full_scale_shape_pair_15700x7774_repeat1_row_scoped`
- Generic capability: `point_location_topology_stream`
- Output contract: `overlay_active_pair_dependency_count`
- Source evidence: `docs\rebuild\v3\evidence\phoenix_v3_spatial_overlay_full_active_count_20260621\full_overlay_repeat1_m3_failclosed.json`
- Local review-ready: `False`

## Metrics

- Left/right shapes: `15700` / `7774`
- Shape-pair count: `122051800`
- Active count: `19277`
- OptiX / Embree active count: `19277` / `21228`
- OptiX minus Embree active count: `-1951`
- Repeat OptiX/Embree: `1` / `1`
- OptiX timed median sec: `0.01629706472158432`
- Embree timed median sec: `20.57024759799242`
- Embree / OptiX wall speedup: `1262.2056762619693`

## Failed Checks

- `evidence_status_ok`
- `active_counts_match`
- `repeat_floor_met`

## Required Before M7

- External AI review of this exact packet.
- Codex consensus file after external review.
- Public wording must say active-count topology stream only, not full polygon overlay.
- Public wording must not claim RayJoin paper Section 5.7 reproduction or RTDL beats RayJoin.
- Public wording must not claim broad V3-over-V2 speedup.

## Goal-Level Decision Audit

1. Was I foolish? No for this gate. It requires full-scale shape-pair count, stable same-contract counts, complete M3 metadata, and external review before any row can count.
2. If yes, what actions made the decision foolish? The foolish action would be to recycle the old 499x subset row as public proof without full-scale evidence, M3 table, and review; another foolish action was earlier using the Windows py launcher on Linux, which is now corrected to python3.
3. Was there another path? Keep only the PIP route and accept no M7 topology row. That remains valid if this active-count contract fails scale or review.
4. Can I now try a different path? Use this as a narrow reusable topology-stream candidate only if the full-scale evidence passes, then seek Claude/Codex review before changing any release gate.
