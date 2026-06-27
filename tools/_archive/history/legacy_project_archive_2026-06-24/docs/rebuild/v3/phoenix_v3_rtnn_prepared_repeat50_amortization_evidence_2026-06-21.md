# Phoenix V3 RTNN Prepared Repeat50 Amortization Evidence

Status: `rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release`.

This packet records a scoped prepared-session candidate. It is not V3 release authorization, not a whole RTNN app claim, and not a one-shot nearest-neighbor claim.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added now: 0
```

## Candidate Row

- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`

## POD Result

- Point count: `1048576`
- Repeat count: `50`
- Warm OptiX/CuPy hot-query speedup: `7.889x`
- Warm OptiX/CuPy cold-plus-query speedup: `1.315x`
- Warm OptiX/CuPy runner-wall speedup: `3.761x`

## Phase Rows

| route | input load | pack/prepare | hot query median | runner wall |
|---|---:|---:|---:|---:|
| RTDL OptiX | 0.020568s | 0.428180s | 0.010668s | 1.313235s |
| CuPy grid | 0.014502s | 0.505491s | 0.084158s | 4.938713s |

## Boundaries

- No V3 release authorization.
- No broad V3-over-V2 claim.
- No whole RTNN app claim.
- No one-shot or cold-start RTNN speedup claim; cold-plus-query is only 1.315x.
- No paper-equivalent RTNN claim.

## Review Required Before M7

- External Claude/Gemini review over the exact candidate row id and evidence packet.
- Codex consensus response after external review.
- Public wording review that keeps this scoped to repeat50 prepared-session amortization.

## Goal-Level Decision Audit

Decision: Record RTNN repeat50 prepared-session amortization as a material M7 candidate pending external review, not as immediate promotion.

1. Was I foolish? No. The test matches the V3 prepared-execution thesis and keeps the one-shot/cold-start boundary explicit.
2. If yes, what actions made the decision foolish? It would be foolish to call this a general RTNN win, a paper-equivalent result, or a release row before external review.
3. Was there another path that would have avoided getting stuck on that idea? I could keep pursuing single-run RTNN overhead or wait on AABB review, but repeat50 is the direct way to test V3 prepared-session value.
4. Can I now try a different path that actually solves the problem? Send this exact scoped candidate for external review; if blocked, keep it as pending and continue another generic engine blocker.
