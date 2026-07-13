# External Review Verification: Goals5482-5484

Date: 2026-07-11

## Verdict

```text
approve_goals5482_5484_librts_exact_figure6_point_contains_closeout
```

Blocking findings: none.

Required amendments: none. RA-1 is closed.

## Verified amendments

The closeout now explicitly states that the six cases establish **count-level
agreement only**. Equal totals do not establish equal point-to-polygon
relations. This boundary is present in the matrix report, denominator report,
README, manifest, aggregate result, per-case result JSONs, and both gate
implementations.

The package cross-references:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_same_input_pip.json
```

That separate app-instrumented representative PIP workload contains `71,626`
author/RTDL pair rows with equal canonical SHA-256. The documentation clearly
states that this is relation-level evidence for a different workload, not
pair-row evidence for the six exact Figure-6 point-contains cases.

The requested discriminating negative test is present and passing:

```text
test_equal_counts_do_not_establish_equal_pointwise_relations
```

The performance wording is also aligned: RTDL route wall is seconds-scale while
the author internal Query Time is sub-millisecond for these cases; the phase
boundaries differ, so no ratio is authorized, but the raw evidence is retained
as a warning that the current RTDL route is much slower.

## Scope of approval

This approval closes the Goals5482-5484 exact-input point-contains count and
denominator line only. It does not close:

- Figure-6 reproduction;
- pointwise pair-row equality for these six cases;
- author/RTDL performance parity;
- complete LibRTS paper reproduction;
- Embree comparison.

The project manifest may mark Goals5482-5484 as externally reviewed and
approved. The broader LibRTS app remains in progress at its separately tracked
scope.
