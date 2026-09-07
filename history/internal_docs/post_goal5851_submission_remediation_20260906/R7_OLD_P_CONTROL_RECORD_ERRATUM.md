# R7 Old-P Control-Record Erratum

Date: 2026-09-06 America/New_York.

This is an append-only correction to control records associated with the old
paper snapshot P. It does not alter, relabel, or approve P, its PDF, either old
control record, or the independent review that rejected those PDF bytes.

## Bound identities

| Object | Identity |
| --- | --- |
| Old P commit | `c6020fd63097b35b5294778cf54c2fb84c879ad6` |
| Old P tree | `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| Old P PDF SHA-256 | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| Unchanged nine-member artifact SHA-256 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| Old R4 report SHA-256 | `2e534bbd2986bba0a7838889e43ecce705381c2b76925f7cfd1cdddf55447af2` |
| Old R7 request SHA-256 | `000ed47cb0296bf59a31521b7f6ec92bcf0495447e7e8d59febfeee39e4db491` |
| Independent lead review SHA-256 | `c449a6c6eed4f177496a762b38f13434a09b1447aa3b3521db56c66b818d5ddd` |
| Independent lead verdict | `REVISE_AND_REREVIEW_CHANGED_BYTES` |

## Corrections

1. `R4_MANUSCRIPT_REWRITE_AND_RENDER_REPORT.md` lines 71 and 95--96
   recorded the intended disposition of the A/E first-result comparisons as
   post hoc and non-gating, but overstated its realization in old P. The old P
   main text and Table 6 caption did not explicitly state that qualification.

2. `R7_FINAL_BYTES_REVIEW_REQUEST.md` lines 120--124 said that "the
   first-result rows" were post hoc and non-gating. That wording improperly
   grouped two different histories. Only A/E first-result comparisons are post
   hoc, non-gating diagnostics. A/C implementation-entry had a historical
   registered criterion; the current paper treats that endpoint as a
   lifecycle-confounded, non-confirmatory diagnostic and makes no positive
   entry-latency claim.

## Successor rule

The manuscript correction must appear in a new paper snapshot P-prime and in a
new exact-byte review request. The old independent review is evidence against
old P and does not count as approval of P-prime. R7 remains open, every claim
authorization remains false, and no upload or submission is represented by
this erratum.
