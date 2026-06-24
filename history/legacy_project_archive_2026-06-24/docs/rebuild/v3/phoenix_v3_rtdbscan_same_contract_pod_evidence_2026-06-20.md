# Phoenix V3 RTDBSCAN Same-Contract Pod Evidence

status: rtdbscan_same_contract_pod_evidence_not_promoted

This is a Phoenix V3 focused pod rerun for RTDBSCAN. It exists because the
previous all-app RTDBSCAN ratio row showed a huge OptiX/Embree number, but that
row compared an optimized OptiX component-signature route against an Embree
neighbor-row materialization route and had `matches_reference: null`.

This rerun uses a stricter same-contract comparison:

- Embree: `embree_core_flags_numba_prepared_grid_column_signature_3d`
- OptiX: `optix_rt_core_flags_numba_prepared_grid_column_signature_3d`
- Dataset: `clustered3d`
- Contract: fixed-radius count-threshold rows/columns feeding the same Numba
  prepared grid component-signature continuation
- Hardware: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, 20475 MiB
- Raw artifact:
  `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_same_contract_20260620_fresh/summary.json`

## Result

The fair same-contract rerun does not support the old `1483x` RTDBSCAN reading.
It shows a real but small OptiX advantage on the checked same-contract rows:
`1.150x` at 65,536 points, `1.079x` at 262,144 points, and `1.071x` at
524,288 points.

| Point count | Embree sec | OptiX sec | OptiX speedup | RT-threshold speedup | Same signature | Continuation dominates OptiX |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4,096 | 0.018533 | 0.012644 | 1.466x | 2.061x | true | false |
| 65,536 | 0.390824 | 0.339776 | 1.150x | 1.297x | true | false |
| 262,144 | 2.746820 | 2.545090 | 1.079x | 1.312x | true | true |
| 524,288 | 9.152090 | 8.545060 | 1.071x | 1.470x | true | true |

The 4,096-point control row passes CPU reference validation for both backends.
The large rows skip CPU reference validation, but Embree and OptiX produce the
same canonical component-size signature.

## Interpretation

RTDBSCAN remains useful internal V3 evidence, but not an M7 release row. The
fresh same-contract data says:

- the OptiX fixed-radius count-threshold phase is faster than the Embree
  compact threshold phase;
- by 262,144 and 524,288 points, the shared Numba component-signature
  continuation dominates OptiX wall time;
- the old all-app `1483x` row must not be used as public RTDBSCAN speedup
  wording;
- the M23 grouped-stream 524,288-point component-signature result remains a
  separate internal route, not a promoted public row.

## Current Decision

RTDBSCAN is still not promoted to M7.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

To reopen RTDBSCAN as an M7 candidate, the next packet must either show a
meaningful reusable engine improvement beyond the shared continuation bottleneck
or narrow the claim to a reviewed, user-useful component-signature contract.
That future packet still needs external review plus Codex consensus.

## Goal-Level Decision Self-Audit

1. Was I foolish? No. This rerun replaced an unfair row-materialization
   comparison with a same-contract comparison.
2. If yes, what actions made the decision foolish? Not applicable for this
   decision. The known foolish action would have been promoting the old `1483x`
   number.
3. Was there another path? Yes. We could have tried to promote only the M23
   grouped-stream hot label result, but it still lacks public row wording and a
   fair public baseline.
4. Can I now try a different path? Yes. RTDBSCAN can stay internal while Phoenix
   focuses M7 promotion effort on stronger reusable rows such as the
   repeat-aware grouped-sum contract, or on a new generic continuation
   optimization that attacks the measured bottleneck.
