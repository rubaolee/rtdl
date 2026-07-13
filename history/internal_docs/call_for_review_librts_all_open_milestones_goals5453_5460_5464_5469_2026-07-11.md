# Consolidated Call For Review: LibRTS Open Milestones

Please strictly review the currently open LibRTS paper-app milestones as one
coherent correctness-and-system-extraction packet:

```text
Goals5453-5460
Goals5464-5469
```

Goals5461-5463 are not open debt: their sparse-refit and rollback amendments
were already externally reviewed and approved in:

```text
history/internal_docs/review_goals5461_5463_optix_aabb_sparse_refit_verified_2026-07-10.md
```

## Packet Structure

Query and mutation surface:

```text
history/internal_docs/call_for_review_goals5453_5456_librts_query_surface_2026-07-10.md
history/internal_docs/call_for_review_goals5457_5460_librts_generic_mutation_milestone_2026-07-10.md
```

PIP correctness:

```text
history/internal_docs/call_for_review_goals5464_5465_librts_bounded_same_input_pip_2026-07-10.md
history/internal_docs/call_for_review_goals5466_5467_librts_representative_pip_2026-07-10.md
```

Ray-Multicast feasibility and generic extraction:

```text
history/internal_docs/call_for_review_goals5468_5469_librts_ray_multicast_feasibility_2026-07-11.md
```

## Consolidated Claims To Verify

1. Tiny point-contains, range-contains, and range-intersects author/RTDL counts
   match on the same inputs; only RTDL row equality is claimed where the author
   binary is count-only.
2. The deterministic mutation count sequence matches, while author and RTDL
   execution-model differences remain visible.
3. Tiny PIP discriminates MBR candidates from polygon refinement.
4. The Level-B representative PIP gate compares complete app-instrumented
   author/RTDL pair rows and preserves the standard RTDL six-row semantic
   difference instead of changing core semantics.
5. Ray-Multicast is correctly mapped to static disjoint-layer traversal
   fanout, not relabeled batching or multi-stream execution.
6. `src/rtdsl/partitioned_traversal.py` is app-neutral and has a behavioral
   Contact-Manifold non-app consumer.
7. The new reference contract proves pair coverage and static load reduction
   only; it does not claim native completion or runtime benefit.
8. The proposed POD spike has exact-row, load-telemetry, phase-timing, non-app,
   and stop-on-no-win gates.

## Required Boundary

Do not approve any summary claiming:

- exact paper datasets;
- complete author pair rows outside the instrumented Goal5467 gate;
- native Ray-Multicast completion or equivalence;
- Figure 9 or Figure 12 reproduction;
- author-performance parity or whole-program speedup;
- a LibRTS-specific RTDL core primitive;
- Embree evidence.

## Requested Verdict Shape

```text
Overall verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Per-goal disposition:
  Goal5453:
  Goal5454:
  Goal5455:
  Goal5456:
  Goal5457:
  Goal5458:
  Goal5459:
  Goal5460:
  Goal5464:
  Goal5465:
  Goal5466:
  Goal5467:
  Goal5468:
  Goal5469:
POD-spike authorization decision:
Final label:
```

Requested label if approved:

```text
approve_librts_goals5453_5460_5464_5469_open_milestones__
authorize_bounded_generic_partitioned_traversal_pod_spike
```
