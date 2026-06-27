# Iteration 1 Codex Proposal

Codex proposed:
- replace the broken local `lsi` BVH/`rtcIntersect1` path with a parity-first native analytic segment loop
- keep the public RTDL kernel and ABI surface unchanged
- mark current local `lsi` lowering as `native_loop`
- treat any future sort-sweep or BVH-backed redesign as a separate optimization goal

Reasoning:
- Goal 29 and Goal 30 already showed that the active candidate path was dropping true pairs before refine
- another epsilon-only patch would be heuristic and not acceptable under the current audit bar
