# Call For Review: Goal4868 Duplicate Half-Edge Core Contract

Date: 2026-07-02

Please review:

- `history/internal_docs/goal4868_duplicate_half_edge_core_contract_report_2026-07-02.md`
- `history/internal_docs/goal4868_duplicate_half_edge_micro_probe_after_core_canonical.json`
- `history/internal_docs/goal4868_specific_pip_probe_after_core_canonical.json`
- `history/internal_docs/goal4868_author_rtdl_contract_patch.diff`
- `history/internal_docs/goal4868_author_rtdl_contract_block_water_stderr_with_output.txt`
- `history/internal_docs/goal4868_rtdl_vs_author_contract_block_water_prefix100k_summary.json`
- code changes in:
  - `src/native/optix/rtdl_optix_core.cpp`
  - `src/native/optix/rtdl_optix_workloads.cpp`
  - `tests/goal4373_rayjoin_cdb_point_location_route_test.py`

## Review Questions

1. Is the duplicate-half-edge canonicalization a valid RTDL directed-segment point-location contract repair, rather than a hidden RayJoin output-chain patch?
2. Is the chosen rule well specified enough for product use: unordered scaled endpoint pair, smallest stable source segment id, canonical face computed from canonical segment direction?
3. Is it correct that the canonicalization belongs in core point-location output, so row output, device segment ids, device face ids, and positive-face count share one semantic contract?
4. Do the focused tests and micro probe prove that input-order dependence is removed on the controlled duplicate half-edge case?
5. Does the Block x Water witness evidence justify saying the known 5693875 exterior/interior failure moved in the intended direction?
6. Is it correct to treat the 7906217 change as expected under the new contract, meaning the old AuthorPatch output is no longer the fair comparator?
7. Should the next comparison be against an explicitly named `Author+RTDLContractPatch` baseline, not against the old AuthorPatch output?
8. Is the author-side patch shape acceptable as a comparator patch: per-edge canonical map plus `get_face_id_for_edge_id(eid)`, instead of modifying unrelated overlay formatting?
9. Does the first-100,000-line prefix match justify continuing with bounded window/prefix/full-stream comparisons under `Author+RTDLContractPatch`?
10. Is any additional unit or synthetic test required before a larger full-stream comparison is attempted?
11. Should Goal4868 close with:

`completed_core_duplicate_half_edge_contract__micro_gate_passed__block_water_witness_moved__author_contract_patch_built__prefix100k_match`

## Non-Authorization

This review must not authorize:

- a full Section 5.7 reproduction claim;
- performance claims;
- claiming that original AuthorPatch follows the RTDL duplicate-half-edge contract;
- public docs/tutorial changes;
- broad RayJoin or RTDL claims beyond the bounded point-location contract repair.
