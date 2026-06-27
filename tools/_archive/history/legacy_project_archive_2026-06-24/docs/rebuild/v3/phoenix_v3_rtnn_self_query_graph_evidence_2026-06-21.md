# Phoenix V3 RTNN Self-Query Graph Evidence

## Verdict

The self-query CUDA graph route is now functional at 1,048,576 queries and keeps prepared search columns resident as query columns, but it is not a material performance win over the direct self-query batch route. It adds a generic engine surface and removes the stale 65,536 graph cap; it does not reopen RTNN M7.

## Measurements

| Route | Hot median sec | Input pack sec | Prepare sec | Cold+query sec |
| --- | ---: | ---: | ---: | ---: |
| Direct self-query batch | 0.004359 | 0.175312 | 0.371949 | 0.551620 |
| Self-query graph replay | 0.004389 | 0.178864 | 0.361319 | 0.544572 |

## Comparisons

- Graph over direct hot speedup: `0.993x`
- Graph over direct prepare speedup: `1.029x`
- Graph over direct cold+query speedup: `1.013x`

## Boundary

- Functional generic route: yes.
- M7 promotion: no.
- Public speedup wording: no.
- Broad V3-over-V2 wording: no.
