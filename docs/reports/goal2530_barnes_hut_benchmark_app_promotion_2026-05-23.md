# Goal2530: Barnes-Hut Benchmark App Promotion

Date: 2026-05-23

## Decision

Promote the existing Barnes-Hut force example into the RTDL research-benchmark
lane as a bounded RT-BarnesHut-style reconstruction instrument.

This is not a closeout. It is the starting gate for the next benchmark app.

## Paper Reference

The benchmark is informed by:

- Vani Nagarajan, Rohan Gangaraju, Kirshanthan Sundararajah, Artem Pelenitsyn,
  and Milind Kulkarni, "RT-BarnesHut: Accelerating Barnes-Hut Using
  Ray-Tracing Hardware," PPoPP 2025.
- DOI: `10.1145/3710848.3710885`

The paper reference is used to define design pressure. It does not authorize
authors-code timing, paper reproduction, or public performance wording.
This promotion is not a full RT-BarnesHut paper reproduction.

## Existing RTDL State

RTDL already has a bounded Barnes-Hut ordinary app:

- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`

That app currently supports:

- one-level body-to-quadtree-node candidate rows;
- Python-owned opening-rule evaluation;
- Python force-vector oracle for a tiny fixture;
- prepared OptiX fixed-radius node-coverage threshold traversal;
- generic partner exact all-pairs softened inverse-square force vectors over
  weighted point columns.

Prior evidence includes:

- `docs/reports/goal504_barnes_hut_force_app_implementation_2026-04-17.md`
- `docs/reports/goal882_barnes_hut_node_coverage_optix_subpath_2026-04-24.md`
- `docs/reports/goal1075_barnes_hut_rich_contract_design_2026-04-28.md`
- `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate_2026-04-28.md`
- `docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.md`
- `docs/reports/goal1979_exact_pairwise_force_partner_barnes_hut_reference_2026-05-14.md`

## What Was Added

New benchmark directory:

- `examples/v2_0/research_benchmarks/barnes_hut/`

New wrapper:

- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`

New benchmark README:

- `examples/v2_0/research_benchmarks/barnes_hut/README.md`

The wrapper exposes explicit modes:

| Mode | Role |
| --- | --- |
| `scope` | Emit benchmark scope, paper reference, supported contracts, and non-goals |
| `cpu_reference` | Existing bounded one-level app with Python force oracle |
| `node_coverage_cpu_oracle` | CPU same-contract node-coverage decision oracle |
| `rtdl_cpu_rows` | Generic fixed-radius candidate rows via RTDL CPU backend |
| `embree_rows` | Same candidate-row contract via Embree |
| `optix_node_coverage_prepared` | Prepared OptiX fixed-radius threshold traversal |
| `partner_exact_force` | Generic weighted-point exact force-vector partner reference |

## Scope Boundary

Authorized as benchmark starting scope:

- RTDL can use this app to study hierarchical spatial aggregation, node
  coverage, opening decisions, and vector force accumulation.
- Existing app code may be reused as the correctness and baseline scaffold.
- Native engines must remain app-name-free for supported primitive paths.

Not authorized:

- full RT-BarnesHut paper reproduction;
- authors-code comparison;
- paper-level dataset or speedup claims;
- whole N-body solver acceleration wording;
- native Barnes-Hut ABI;
- native force-vector or opening-rule shortcuts with app vocabulary.

## Design Pressure For Next Goals

Barnes-Hut is useful because it stresses RTDL differently from the five
finished benchmark apps:

- it needs hierarchical aggregate data rather than flat rows alone;
- it needs an opening predicate that decides between aggregate-node and
  exact-body continuation;
- it needs vector-valued contribution rows, not only scalar counts/flags;
- it needs grouped vector reductions or partner-resident vector accumulation;
- it has prepared tree state but dynamic body/query state across timesteps.

The next implementation goal should choose one generic primitive target, not a
paper-specific native shortcut. The strongest first candidate is:

```text
weighted source points + aggregate tree nodes
+ generic opening predicate metadata
-> accepted aggregate-node rows + fallback exact-body rows
```

The force-vector reduction can then remain partner-owned until RTDL has enough
evidence to define a generic vector reduction primitive.

## Exit Criteria For This Promotion

Goal2530 is complete when:

- the benchmark directory exists;
- the wrapper runs locally for scope and CPU correctness modes;
- docs state the paper reference and claim boundary;
- tests enforce that the promotion does not claim paper reproduction, authors
  code, public speedup, or app-specific native engine behavior.

Goal2530 does not require a GPU pod. Future OptiX evidence does.
