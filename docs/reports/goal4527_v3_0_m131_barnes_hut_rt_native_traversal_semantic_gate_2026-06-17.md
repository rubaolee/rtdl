# Goal4527 / V3 M131 Barnes-Hut RT-Native Traversal Semantic Gate

## Conclusion

M131 prevents an incorrect Barnes-Hut RT-native implementation from landing. A direct OptiX GAS containing every aggregate-tree node cannot, by itself, express the Barnes-Hut rule that accepting a parent aggregate suppresses all descendants; reporting nodes independently would double count unless a separate reviewed hierarchical traversal/skip design exists. The fail-closed ABI therefore stays in place, and Barnes-Hut remains a future design target rather than a current V3 app implementation blocker.

## Decision

- Replace fail-closed ABI now: `False`
- Implement naive all-node OptiX any-hit: `False`
- Current runtime queue remains empty: `True`

## Queue

- Barnes-Hut class: `future_design_target`
- Runtime queue: ``
- Design blocker queue: ``
- Future design target queue: `barnes_hut`
- Next runtime build target: `None`

## Future Barnes-Hut Requirement

A future Barnes-Hut RT-native route must use a reviewed generic hierarchical traversal lowering that proves accepted aggregate subtrees are not double counted, keeps force-law code outside app-specific native engine callbacks, and beats fused CPU/Numba and fused Numba CUDA under the same force-summary contract.

## Boundary

- No runtime was executed.
- No current Barnes-Hut route changed.
- No RT-core speedup, public speedup, automatic partner-selection, or app-specific native-engine wording is authorized.
