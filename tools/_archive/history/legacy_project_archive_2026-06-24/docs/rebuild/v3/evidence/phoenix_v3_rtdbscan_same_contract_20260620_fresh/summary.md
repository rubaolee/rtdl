# Phoenix V3 RTDBSCAN Same-Contract Rerun Evidence

status: rtdbscan_same_contract_fresh_evidence_not_promoted

This packet compares Embree and OptiX on the same RTDBSCAN component-signature
contract: fixed-radius count-threshold rows/columns feeding the same Numba prepared
grid component-signature continuation. It is a fresh evidence packet, not release
authorization.

## Claim Boundary

- Not full DBSCAN paper reproduction.
- Not full DBSCAN label publication.
- Not broad V3 speedup wording.
- Not M7 promotion until external review and Codex consensus.
- Component-signature equality is the large-row validation contract; the small control row also checks CPU reference parity.

## Summary

- Validation control reference pass: `True`
- Large same-signature pass: `True`
- Serious pairs: `3`
- Large pairs: `1`
- Strongest serious OptiX/Embree speedup: `1.1502402630367083`
- Weakest serious OptiX/Embree speedup: `1.071038907298004`

## Pairs

| Point count | Repeat | Embree sec | OptiX sec | OptiX speedup | RT-threshold speedup | Same signature | Continuation dominates OptiX |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4096 | 3 | 0.0185333 | 0.0126443 | 1.46575x | 2.06078x | `True` | `False` |
| 65536 | 5 | 0.390824 | 0.339776 | 1.15024x | 1.29735x | `True` | `False` |
| 262144 | 3 | 2.74682 | 2.54509 | 1.07926x | 1.31185x | `True` | `True` |
| 524288 | 3 | 9.15209 | 8.54506 | 1.07104x | 1.47036x | `True` | `True` |

## Goal-Level Decision Self-Audit

1. Was I foolish? No: this packet replaces a misleading row-materialization comparison with a same-contract rerun.
2. If yes, what actions made the decision foolish? Not applicable for this decision; the known foolish action would be treating the old 1483x row as public proof.
3. Was there another path? Yes: promote only the old grouped-stream M23 hot label result, but that would still lack a fair Embree baseline.
4. Can I now try a different path? Yes: use this same-contract packet to decide whether RTDBSCAN is a modest row-scoped candidate, an internal-only route, or needs further engine work.

