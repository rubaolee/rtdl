# Goal4383 Hausdorff Large Threshold Refresh

Date: 2026-06-14

Status: v2.14 cleanup evidence for the same-contract Hausdorff threshold-decision primitive. This strengthens the previous 4,096-point row, but it is not an exact Hausdorff witness-distance app claim.

## Contract

Both backends run the same generic RTDL primitive:

`PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_2D / scalar threshold count`

The app answers the decision subproblem: for both directed passes, does every source point have at least one target within `hausdorff_threshold=0.25`? The deterministic tiled oracle says the true Hausdorff distance is `0.30`, so the expected decision is `within_threshold=false`.

## Results

| Case | Backend | Points A | Points B | Decision matches oracle | Prepare sec | Sum of directed hot query medians sec | Measured query total sec |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| copies=16,384 | Embree | 65,536 | 65,536 | true | 0.310203 | 0.482530 | 2.420485 |
| copies=16,384 | OptiX RT cores | 65,536 | 65,536 | true | 0.892876 | 0.251894 | 1.162414 |
| copies=65,536 | Embree | 262,144 | 262,144 | true | 1.541708 | 1.947288 | 6.196873 |
| copies=65,536 | OptiX RT cores | 262,144 | 262,144 | true | 1.768748 | 1.056837 | 3.530949 |
| copies=262,144 | Embree | 1,048,576 | 1,048,576 | true | 5.657996 | 8.738029 | 17.476059 |
| copies=262,144 | OptiX RT cores | 1,048,576 | 1,048,576 | true | 5.890569 | 5.524162 | 11.048324 |

## Same-Contract Speedups

| Case | Hot query speedup, Embree / OptiX | Interpretation |
| --- | ---: | --- |
| 65,536 x 65,536 threshold decision | 1.92x | Large enough to leave the sub-millisecond regime. |
| 262,144 x 262,144 threshold decision | 1.84x | Seconds-level repeated query total; same decision and oracle result. |
| 1,048,576 x 1,048,576 threshold decision | 1.58x | Human-scale hot query: 8.74s Embree vs 5.52s OptiX for the two directed passes. |

## Conclusion

Hausdorff no longer needs to be described as only a 4,096-point repeated row for the threshold-decision contract. v2.14 now has a large same-contract OptiX-vs-Embree row with 1,048,576 points per side and oracle-checked decision parity.

The public wording must stay narrow: this is a prepared fixed-radius Hausdorff-threshold decision, not exact Hausdorff nearest-witness computation, not full X-HD paper reproduction, and not a claim that RT cores accelerate dense exact Hausdorff distance more broadly.
