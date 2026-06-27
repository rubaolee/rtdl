# Phoenix V3 M31 LibRTS Watch Rows Existing-Evidence Analysis

Date: 2026-06-23

Status: `existing_evidence_analysis_watch_rows_not_closed_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
new_pod_run_performed: false
```

## Scope

This is a local analysis of existing M25/M27 LibRTS AABB evidence. It does not
run POD and does not change release status.

Evidence inspected:

- `docs/rebuild/v3/evidence/phoenix_v3_m25_librts_aabb_optix_runner_focused_20260623_124946`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_embree_stress_triage_20260623_130838`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_20260623_131633`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_extra_20260623_131735`

## OptiX Cold Single-Shot Row

Metric: paired V2.14/current speedup, computed as `v2_query_sec / current_query_sec`.

| sample | current sec | V2.14 sec | current speedup |
| ---: | ---: | ---: | ---: |
| 1 | 0.541959584 | 0.287921481 | 0.531x |
| 2 | 0.262608394 | 0.323190220 | 1.231x |
| 3 | 0.271197304 | 0.318295859 | 1.174x |
| 4 | 0.297451943 | 0.301309660 | 1.013x |
| 5 | 0.286616348 | 0.253155112 | 0.883x |
| 6 | 0.263328463 | 0.257144421 | 0.977x |
| 7 | 0.278677516 | 0.300088473 | 1.077x |
| 8 | 0.243741795 | 0.270549342 | 1.110x |

Aggregate:

```text
all_samples_geomean: 0.973x
all_samples_median: 1.045x
all_samples_pass_0_95: 6 / 8
drop_sample_1_geomean: 1.060x
drop_sample_1_median: 1.077x
drop_sample_1_pass_0_95: 6 / 7
```

Interpretation:

- The worst failure is current sample 1, which looks like a cold-start or
  one-time initialization outlier.
- Removing that sample makes the geomean healthy, but the row still has a
  `0.883x` paired sample and therefore should not be declared closed.
- M27's `improved_not_closed` classification remains correct.

## Embree 32768 Stress Row

Metric: paired V2.14/current speedup, computed as `v2_query_sec / current_query_sec`.

| sample | current sec | V2.14 sec | current speedup |
| ---: | ---: | ---: | ---: |
| 1 | 0.806993507 | 0.912685543 | 1.131x |
| 2 | 0.996299259 | 0.895104237 | 0.898x |
| 3 | 0.997105952 | 0.908242274 | 0.911x |

Aggregate:

```text
geomean: 0.975x
median: 0.911x
pass_0_95: 1 / 3
```

Interpretation:

- The geomean is above 0.950x, so this is not a simple deterministic mean
  failure.
- The median is below 0.950x and 2/3 paired samples fail, so the stability watch
  remains real.
- M27's `stability_watch_blocker` classification remains correct.

## Engineering Read

No current evidence supports a broad LibRTS algorithm rewrite. The next LibRTS
POD, if authorized later, should be a focused stability protocol:

1. pre-warm process/runtime explicitly;
2. separate first-sample cold-start from steady cold-repeat samples;
3. record current and V2.14 in alternating order to reduce drift;
4. keep OptiX cold single-shot and Embree 32768 stress as Set-B/control watch
   rows, not Set-A runtime-trunk proof.

Do not run all-app for this.

## Goal-Level Decision Audit

Decision: keep LibRTS watch rows open and classify the next POD need as a
stability/cold-start protocol, not an immediate broad code rewrite.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be declaring LibRTS closed because the geomeans look
   acceptable, or rewriting generic runtime code based on one cold outlier.

3. Was there another path?

   Yes: spend POD immediately or hide the row because LibRTS app-level geomean
   was strong. Both would repeat the M22 mistake of masking row-level problems.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep the row open, define a stability protocol, and spend POD only when
   this blocker becomes the next authorized all-app precondition.
