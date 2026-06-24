# Goal4508 / V3 M112 RTNN Clean-Target Closeout

## Conclusion

RTNN is internally closed as a V3 clean target: RTDL has a same-input OptiX/Embree gate, a current full-batch aggregate-only OptiX route, an app front door for external point files, a same-input author-code diagnostic comparison, and measured CuPy plus Numba chunked partner-continuation runtime at 1,048,576 queries. The closeout is intentionally not a public RTNN paper-reproduction or RTDL-beats-author claim.

## Closeout Matrix

| Lane | Evidence | Primary measure | Reading | Boundary |
| --- | --- | --- | --- | --- |
| RTDL OptiX vs Embree same-input backend gate | Goal4500 / V3 M104 | OptiX 7.802572s; Embree 120.927761s | RTDL/OptiX is 15.50x faster than RTDL/Embree for this same-input, same-contract gate. | RTDL-internal backend comparison only; strict kth-id checksum remains tie-sensitive, and this is not exact RTNN paper reproduction. |
| Current RTDL aggregate-only route | Goal4502 / V3 M106 | hot query 0.153553s; cold load+pack+prepare+query 4.823698s | Full-batch non-graph prepared direct aggregate is the current fastest RTDL aggregate-only route; graph/device partials are not the aggregate-only default. | Aggregate output surface differs from the author full K-id materialization surface; do not collapse these rows into author-output equivalence. |
| RTNN app front door | Goal4503 / V3 M107 | hot query 0.153737s; cold load+pack+prepare+query 4.833464s | The promoted RTNN app can ingest an external point file and reaches the current full-batch aggregate route without regenerating synthetic data. | Front-door proof only; it does not change paper-reproduction or public-speedup boundaries. |
| Author-code diagnostic comparison | Goal4501 / V3 M105 plus Goal4502 / V3 M106 | author total-search 0.347280s; author pure compute 0.010274s; author cold process 2.049657s; RTDL aggregate hot 0.153553s | RTDL's aggregate query is faster than the author synchronized total-search timer for this aggregate surface, while the author remains much faster in pure compute and cold whole-process timing. | Useful diagnostic, not an RTDL-beats-author same-output claim. |
| Partner-continuation chunked runtime | Goal4505 / V3 M109 through Goal4507 / V3 M111 | uniform CuPy 0.082908s / Numba 0.083390s; shell CuPy 0.609413s / Numba 0.609404s; clustered CuPy 2.041410s / Numba 2.036964s | Large partner continuation now has real runtime evidence for both partners, with signatures matching and materialization outside the hot window. | Partner-continuation evidence only; not an aggregate-only full-batch direct comparison and not a paper dataset substitute. |

## Partner Matrix

| Distribution | Chunks | CuPy hot median-sum | Numba hot median-sum | Signature | No hidden copy |
| --- | ---: | ---: | ---: | --- | --- |
| uniform | 16 | 0.082908s | 0.083390s | `True` | `True` |
| shell | 16 | 0.609413s | 0.609404s | `True` | `True` |
| clustered | 16 | 2.041410s | 2.036964s | `True` | `True` |

## What Closed

- RTDL OptiX and Embree now have a same-input same-contract RTNN-shaped gate on the bounded KITTI-1M CSV.
- The current RTDL aggregate-only route is the full-batch prepared direct aggregate, not the capped graph path.
- The RTNN benchmark app can run the real point-file front door into that current route.
- Author RTNN has a same-input diagnostic row, with output-contract caveats stated inline.
- Partner continuation has large 1,048,576-query runtime evidence for both CuPy and Numba.

## Still Blocked

- Exact RTNN paper reproduction is blocked until the official dataset recipes are frozen or acquired.
- Same-output author comparison is blocked because author RTNN materializes a full K-id buffer while RTDL's best route returns ranked-summary aggregates.
- Public RT-core speedup, whole-app speedup, automatic partner selection, and RTDL-beats-author wording remain blocked.

## Next Step

abstract the M19 chunked partner runtime into a reusable prepared graph chunk executor, then use the same audit style on RT-DBSCAN and Triangle Counting.
