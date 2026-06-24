# Phoenix V3 RTDBSCAN Optimized Large Repeat5 Evidence

status: rtdbscan_component_signature_optimized_large_repeat5_evidence

This artifact repairs the repeat-count weakness found by the Claude review for the 262,144 and 524,288 point rows. It does not authorize release wording by itself.

| Point count | Repeat | Measured iterations | Embree sec | OptiX sec | Speedup | Same signature | Continuation dominates OptiX |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 262144 | 5 | 4 | 2.69801 | 2.40133 | 1.12355x | `True` | `True` |
| 524288 | 5 | 4 | 9.00833 | 8.17457 | 1.10199x | `True` | `True` |

Claim boundary: large-scale correctness is OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation.
No release, public speedup, paper, broad V3, or V2 claim is authorized by this artifact alone.
