# Goal1208 Public Wording Decision After Goal1206

Date: 2026-05-01

Goal1208 is a public-wording decision packet only. It proposes narrow wording states from accepted Goal1206 evidence but does not edit public docs, authorize release, or by itself authorize public RTX speedup claims.

## Summary

- source intake: `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.json`
- source consensus: `docs/reports/goal1206_two_ai_consensus_2026-05-01.md`
- minimum positive public ratio: `1.2`
- proposed reviewed apps: `road_hazard_screening`
- correctness-ready but speedup-blocked apps: `polygon_set_jaccard`
- blocked apps: `database_analytics`
- public speedup claims authorized by this packet: `0`
- public speedup claims applied by this packet: `0`

## Decisions

| App | Path | Decision | Ratio |
| --- | --- | --- | ---: |
| `database_analytics` | `prepared_db_compact_summary` | `keep_public_wording_blocked_no_positive_speedup` | `1.12x` |
| `road_hazard_screening` | `prepared_native_road_hazard_summary` | `propose_public_wording_reviewed` | `3.53x` |
| `polygon_set_jaccard` | `native_assisted_lsi_pip_candidate_discovery` | `correctness_ready_no_speedup_wording` | `n/a` |

## Candidate Public Wording

### database_analytics / prepared_db_compact_summary

RTDL's prepared DB compact-summary RTX sub-path is repaired at 100k and 300k, but the measured 1.12x-1.16x advantage is below the 1.2x public speedup threshold.

Boundary: Only prepared compact-summary scan/group/count/sum traversal is covered; no DBMS, SQL engine, full dashboard, row-materialization, Python setup, or whole-app speedup claim is allowed.

### road_hazard_screening / prepared_native_road_hazard_summary

RTDL's prepared native road-hazard RTX sub-path measured 0.230652 s and 3.53x versus the reviewed same-scale Embree sub-path at 40k copies.

Boundary: Only the prepared native segment/polygon road-hazard summary traversal and threshold-count continuation are covered; default app behavior, GIS/routing, row materialization, Python setup, and whole-app speedup remain outside this wording.

### polygon_set_jaccard / native_assisted_lsi_pip_candidate_discovery

RTDL's polygon-set Jaccard OptiX path has public-safe chunk correctness evidence at chunk 512; no positive RTX speedup wording is authorized because this packet has no same-scale Embree speedup comparison and chunk 64 remains diagnostic-only/parity-failing.

Boundary: Only public-safe chunk correctness/readiness is covered; exact area refinement, Jaccard whole-app speedup, arbitrary chunk sizes, row materialization, and Python postprocess are outside this wording.

