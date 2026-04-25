# Goal917 Existing RTX Artifact Intake

Date: 2026-04-25

## Purpose

Goal916 identified three existing 2026-04-25 RTX A5000 cloud artifacts that
should be reviewed before another paid pod is started. Goal917 performs that
bounded intake. It does not promote app readiness by itself and does not
authorize public RTX speedup claims.

## Evidence Files

Raw JSON artifacts were present locally under `docs/reports/cloud_2026_04_25/`.
For repository evidence, compressed copies and raw-file SHA-256 hashes were
created:

- `docs/reports/cloud_2026_04_25/goal811_service_coverage_rtx.json.gz`
- `docs/reports/cloud_2026_04_25/goal811_event_hotspot_rtx.json.gz`
- `docs/reports/cloud_2026_04_25/goal888_road_hazard_native_optix_gate_rtx.json.gz`
- `docs/reports/cloud_2026_04_25/goal917_intake_raw_artifact_sha256.txt`

## Artifact Summary

| App | Artifact | Scale | RTX result | Local intake verdict |
| --- | --- | ---: | --- | --- |
| `service_coverage_gaps` | `goal811_service_coverage_rtx.json` | `copies=20000` | `optix_prepare=6.518379669636488s`, `optix_query=0.6260500205680728s`, `python_postprocess=0.03535711392760277s`; summary has `household_count=80000`, `covered_household_count=60000`, `uncovered_household_count=20000` | Usable RTX phase artifact for bounded prepared gap-summary review. Needs two-AI promotion review before matrix update. |
| `event_hotspot_screening` | `goal811_event_hotspot_rtx.json` | `copies=20000` | `optix_prepare=6.69359050039202s`, `optix_query=1.1063673989847302s`, `python_postprocess=0.11933588702231646s`; summary has `event_count=120000`, `hotspot_count=99999` | Usable RTX phase artifact for bounded prepared count-summary review. Needs baseline scale review because the committed Embree baseline artifact is still at `copies=2000`. |
| `road_hazard_screening` | `goal888_road_hazard_native_optix_gate_rtx.json` | `copies=20000` | `status=pass`, `strict_pass=true`, `strict_failures=[]`; CPU reference `sec=2.277230924926698`; OptiX native `sec=7.212322797626257`; `parity_vs_cpu_python_reference=true` | Usable correctness artifact for native OptiX road-hazard summary gate. It does not support a speedup claim because native OptiX is slower than CPU reference in this artifact. |

## Baseline Cross-Check

Service coverage has matching local baseline summaries at the same scale:

- CPU oracle baseline: `copies=20000`, summary SHA
  `ffcb2b43892c5efa4feb6aa157efb20e697ede986984fbf4a15ec1ad7217273d`.
- Embree summary baseline: `copies=20000`, summary SHA
  `ffcb2b43892c5efa4feb6aa157efb20e697ede986984fbf4a15ec1ad7217273d`.
- RTX artifact summary counts match the same semantic result.

Event hotspot has a CPU oracle baseline at the same scale, but the committed
Embree summary baseline visible in this workspace is still at `copies=2000`.
There are dirty local baseline JSON edits that appear to move the CPU oracle
baseline to `copies=20000`; those files were not staged in this goal. Before
promotion, the project should either commit a clean same-scale Embree baseline
or explicitly waive the Embree baseline for this path with reviewer agreement.

Road hazard has strict CPU-vs-OptiX parity in the RTX artifact itself. The
artifact is useful for correctness readiness but not performance promotion:
native OptiX is slower than CPU reference in this run.

## Decisions

- `service_coverage_gaps`: candidate for promotion from
  `needs_real_rtx_artifact` to claim-review readiness after external review.
- `event_hotspot_screening`: hold until same-scale Embree baseline state is
  cleaned up or explicitly reviewed.
- `road_hazard_screening`: keep as `needs_real_rtx_artifact` or
  `rt_core_partial_ready` for performance purposes. The artifact proves native
  RTX execution and correctness parity, but it does not justify a speedup or
  ready-for-claim status.

## Boundary

This intake only says which existing artifacts are worth using. It does not
change public support matrices, maturity states, or release claims.

## Next Local Actions

1. Ask Claude and Gemini to review this intake.
2. If both accept, update only the service coverage readiness packet if the
   reviewers agree the baseline contract is satisfied.
3. Keep event hotspot and road hazard in the next local-work queue unless a
   reviewer explicitly accepts their current evidence for a narrower status.
4. Do not start another pod until Goal914 graph/Jaccard and the remaining
   missing deferred gates are batched.
