# External Review - Goal5451 X-HD Same-Input Directed-HDResult Closeout

Date: 2026-07-10

## Verdict

```text
approve_goal5451_xhd_same_input_directed_hdresult_closeout
```

Blocking findings: none.

Required amendments: none.

## Review Summary

Goal5451 is approved as the honest closeout of the owner-approved X-HD scope:

```text
same input files -> same directed input1-to-input2 HDResult within tolerance
```

The review independently verified:

- the directed-definition discriminator: author and RTDL return `0.5` for
  directed A-to-B, while reverse-directed and symmetric Hausdorff are `9.0`;
- all 7 primary cases are same-input author-vs-RTDL comparisons;
- all 7 primary cases use exact-witness routes and match within tolerance;
- all 3 additional fast-scalar routes match the scalar result while correctly
  retaining `per_source_witness_exact=false`;
- claim-boundary fields keep exact artifacts, all figures, internal worklist or
  hash parity, RT-core equivalence, full-paper reproduction, and performance
  parity/speedup false;
- the performance appendix keeps author internal time, author process wall,
  RTDL fresh route/total, and explicit-warm measurements separate;
- the Stop-Loss Gate passes and author artifact-parity work remains closed.

## Verified Primary Matrix

| Case | Category | Input identity | Exact witness | Result |
|---|---|---|---:|---:|
| directed2d_asymmetric | definition discriminator | bounded checked-in fixture | true | matched |
| dragon_happy | graphics 3-D | Level-B same-source public graphics | true | matched |
| thai_happy_scaled | graphics 3-D | Level-B same-source public graphics | true | matched |
| thai_asian_scaled | graphics 3-D | Level-B same-source public graphics | true | matched |
| county_zcta_bounded | geo 2-D | Level-B bounded geo fixture | true | matched |
| water_bg_bounded | geo 2-D | Level-B bounded geo fixture | true | matched |
| water_bg_full_public_paper_config | geo 2-D | Level-B full-public same-source geo, not exact file hash | true | matched |

Observed absolute differences range from `0` to about `5.3e-6`, within the
per-case tolerances `1e-6`, `1e-5`, or `2e-6`.

## Non-Blocking Notes

1. Keep the 7-case identity classification visible in the closeout report so
   bounded fixtures, same-source public inputs, and full-public-but-not-exact
   inputs cannot be conflated.
2. The full-public WaterBodies-to-BlockGroups case is the tightest tolerance
   margin: about `1.31e-6` against `2e-6`. It passes. The tolerance basis
   should remain tied to the recorded author float32 / RTDL float64 comparison
   in Goal5314.
3. Every use of `complete` must remain qualified as
   `same_input_directed_hdresult`, not full X-HD paper reproduction.

## Answers To Review Questions

1. Yes. The asymmetric fixture behaviorally distinguishes directed A-to-B from
   symmetric Hausdorff.
2. Yes. All seven primary rows use the same files for author and RTDL and carry
   explicit input-identity labels.
3. Yes. All seven values match within their declared tolerance.
4. Yes. Exact-witness graphics routes correctly form the primary matrix;
   fast-scalar routes are secondary scalar-only evidence.
5. Yes. Scalar correctness and per-source witness correctness are explicitly
   separated.
6. Yes. Hausdorff remains an app composition over generic RTDL nearest,
   witness, reduction, cell-MBR, and frontier assets.
7. Yes. Goal5128's facility-service-radius consumer is an adequate independent
   non-X-HD consumer.
8. Yes. Performance regimes and phase boundaries are separately reported.
9. Yes. No ratio is authorized because the measured author internal phase,
   author process wall, RTDL fresh route/total, and explicit-warm route are
   different denominators.
10. Yes. Every forbidden claim remains false.
11. Yes. The unavailable exact-artifact requirement was removed from the active
    owner-approved scope, not falsely reported as solved.
12. Yes. The project may close this line as
    `same_input_directed_hdresult_reproduction_complete`.

## Ingestion Clarification

The review text initially described the performance comparison as using
different hardware. Goal5217 actually records the author and RTDL repeated
matrix on the same POD. The no-ratio conclusion remains correct because the
phase, runtime, and algorithmic denominators differ. Future summaries must use
that reason and must not repeat the hardware-difference phrase for Goal5217.

## Final Conclusion

The current X-HD line is externally approved and closed at the precise scope:

```text
Given the same input files, author hd_exec and RTDL produce the same directed
input1-to-input2 HDResult within tolerance.
```

This approval does not recover original paper input bytes, reproduce all paper
figures, establish author internal artifact parity, prove author RT-core
algorithm equivalence, or prove performance parity/speedup.
