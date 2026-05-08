# Goal 1518: Embree Polygon Native-Assisted Performance

## Verdict

`goal1518_embree_polygon_native_assisted_perf_recorded`

- Valid: `True`
- Git commit: `1ed76168c535a24f1480021258d869d2380e819f`
- Repeats: `3`

## Polygon Pair Summary

| Copies | Rows median sec | Summary median sec | Summary/row ratio | Rows JSON bytes | Summary JSON bytes | JSON reduction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 0.050687 | 0.055210 | 0.918x | 68488 | 3915 | 17.494x |
| 1024 | 0.253564 | 0.253902 | 0.999x | 267502 | 3923 | 68.188x |
| 4096 | 2.500900 | 1.394112 | 1.794x | 1075441 | 3926 | 273.928x |

## Polygon Set Jaccard

| Copies | CPU median sec | Embree median sec | Embree/CPU ratio | CPU JSON bytes | Embree JSON bytes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 0.006395 | 0.009959 | 0.642x | 3354 | 9661 |
| 256 | 0.025121 | 0.110025 | 0.228x | 3359 | 18668 |
| 1024 | 0.109506 | 1.603601 | 0.068x | 3367 | 55701 |

## Timing Scope

Python app run_case plus json.dumps timing for selected polygon app modes. Embree uses native-assisted candidate discovery; exact polygon/set refinement and JSON serialization remain in the measured Python app envelope.

## Claim Boundary

Goal1518 records CPU Embree native-assisted polygon app timing for exact measured modes only. It does not authorize public speedup wording, broad polygon/GIS claims, broad RTX wording, whole-app claims, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, or release action.
