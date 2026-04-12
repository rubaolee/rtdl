## Codex Consensus: Goal 289 v0.5 KITTI 4096 Boundary

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

Consensus:

- Goal 289 is technically sound and honestly bounded.
- The `4096` duplicate-free KITTI result captures a new cuNSearch correctness
  boundary that is distinct from the earlier duplicate-point failure.
- The reduced-candidate probe supports a narrow conclusion only:
  - the first failing query becomes correct when the candidate set is reduced to
    its true top neighbors
- That evidence is sufficient to say the `4096` failure is not explained by:
  - exact duplicate points
  - a simple local ordering or tie issue on the first failing query
- That evidence is not sufficient to claim a full root cause inside cuNSearch.

Operational read:

- strict duplicate-free parity is now demonstrated through `2048`
- strict duplicate-free parity is blocked at `4096`
- PostGIS remains parity-clean on the measured bounded KITTI cases
- further cuNSearch scaling work should proceed behind this explicit large-set
  boundary instead of weakening correctness claims
