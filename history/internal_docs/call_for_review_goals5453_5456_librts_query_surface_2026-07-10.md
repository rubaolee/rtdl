# Call For Review - Goals5453-5456 LibRTS Query Surface

Please strictly review the first major LibRTS paper-app node as one packet.

## Scope

```text
Goal5453 provenance scaffold + local CPU oracle
Goal5454 same-input point-contains count gate
Goal5455 direction-discriminating range-contains count gate
Goal5456 predicate-discriminating range-intersects count + RTDL row gate
```

Primary reports and evidence:

```text
history/internal_docs/goal5453_librts_paper_reproduction_provenance_scaffold_2026-07-10.md
history/internal_docs/goal5454_librts_same_input_point_contains_gate_2026-07-10.md
history/internal_docs/goal5455_librts_same_input_range_contains_gate_2026-07-10.md
history/internal_docs/goal5456_librts_same_input_range_intersects_gate_2026-07-10.md
Paper-reproduction-apps/librts-paper/data/manifest.json
Paper-reproduction-apps/librts-paper/results/librts_goal5454_same_input_point_contains.json
Paper-reproduction-apps/librts-paper/results/librts_goal5455_same_input_range_contains.json
Paper-reproduction-apps/librts-paper/results/librts_goal5456_same_input_range_intersects.json
```

## Review Questions

1. Is paper/source/artifact provenance accurately pinned?
2. Are all live author runs verified against the pinned commit?
3. Are same-input identities supported by hashes rather than prose alone?
4. Does point-contains honestly prove count agreement while limiting author
   relation-row claims?
5. Does range-contains distinguish correct direction (`5`) from reverse (`2`)?
6. Does range-intersects distinguish its predicate (`8`) from contains (`5`)?
7. Are RTDL exact/native rows accurately classified per operation?
8. Are all used RTDL APIs generic AABB/index APIs with no LibRTS identity?
9. Are author build adaptations compatibility-only and app-owned?
10. Is Embree absent from the complete campaign evidence?
11. Are all timing fields diagnostic only with no ratio or performance claim?
12. Are mutation, Ray Multicast, PIP, datasets, figures, and full-paper claims
    correctly open?
13. Is a mutation-contract audit, rather than immediate app-specific code, the
    correct next step?

Requested verdict:

```text
approve_goals5453_5456_librts_bounded_query_surface
```
