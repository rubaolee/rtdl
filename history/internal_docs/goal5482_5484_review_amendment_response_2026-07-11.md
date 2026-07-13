# Goals5482-5484 Review Amendment Response

Date: 2026-07-11

Status: `externally_reviewed_and_approved__amendment_closed`

The review finding was accepted: six exact-input result-count matches must not
be described as pointwise point-to-polygon relation equality.

## RA-1 implementation

The following now explicitly carry:

```json
"pointwise_containment_equivalence_claimed": false
```

- Goal5481 result JSON;
- all five Goal5482 per-case result JSONs;
- the Goal5482 aggregate result;
- the Goal5484 denominator audit result;
- both exact point-count gate implementations;
- the LibRTS manifest boundaries.

The result/report/README text now states:

```text
equal counts do not establish equal point-to-polygon relations
```

The package cross-references
`librts_goal5467_representative_same_input_pip.json`, where `71,626` rows were
compared with a canonical SHA-256. That is explicitly identified as a separate
app-instrumented representative PIP workload, not relation-level evidence for
the six exact Figure-6 point-contains cases.

## Performance wording correction

The report now says plainly that the observed RTDL route wall is seconds-scale
while the author's internal Query Time is sub-millisecond on these cases. The
phase boundaries differ, so this is not converted into a ratio; it is retained
as a warning that the current RTDL route is much slower.

## Regression evidence

The Goal5484 test suite now contains a deliberate counterexample: two
point-to-polygon relation sets with equal cardinality but different assignments.
It passes alongside the hash-tamper, count-only API, denominator-selection, and
mismatch-rejection tests.

Final focused verification:

```text
11 tests OK
JSON parse OK
git diff --check OK
```

The external review has now independently accepted the amendment. Goals5482-
5484 are closed at the exact-input count and denominator-audit scope described
above; broader Figure-6, performance, relation, and full-paper claims remain
closed.
