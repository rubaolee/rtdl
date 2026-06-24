# Contact Manifold Broadphase Boundary

Status: rebuild lesson, not a release claim.

This lesson reads the current contact-manifold evidence as generic AABB
broadphase candidate discovery plus bounded row collection. The final contact
interpretation remains app-owned.

Source files:

```text
examples\current\research_benchmarks\contact_manifold\rtdl_contact_manifold_benchmark_app.py
docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md
docs/reviews/claude_phoenix_v3_contact_manifold_broadphase_boundary_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_contact_manifold_broadphase_boundary_2ai_consensus_2026-06-21.md
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/paired_v2_v3_summary.json
```

Typical local command shape:

```powershell
py -3 examples\current\research_benchmarks\contact_manifold\rtdl_contact_manifold_benchmark_app.py --mode aabb_broadphase_collect_k --dataset grid --discovery-backend optix
```

## What The Row Measures

The row is `contact_manifold / generic_aabb_broadphase_collect_k` and maps to
`aabb_candidate_stream` plus bounded witness-row collection.

| Metric | Reading |
| --- | ---: |
| Query median, OptiX over Embree | 1.235x |
| Collect-k bounded rows, OptiX over Embree | 2.759x |
| Prepare AABB index, OptiX over Embree | 0.243x |
| Broadphase phase wall, OptiX over Embree | 0.642x |
| Wall OptiX / Embree | 0.803x |
| Standard paired OptiX V3 over V2.14 | 0.989x |

Wall ratios below 1.0 mean OptiX is slower. The current row has a useful hot
query and collect-k signal, but the wall path is not faster.
The 1.235x query metric is only
`emit_aabb_intersection_pair_rows_2d`; it is not wall timing and not full contact-solver throughput. AABB-index preparation is about 4.1x slower on
OptiX, and the exact row fills its 4,096 witness capacity, so larger overflow
behavior is not validated.

## What To Learn

Use this as a rebuild example of separating generic RTDL candidate discovery
from app-owned interpretation:

1. Build a generic 2-D AABB candidate stream.
2. Collect bounded integer witness rows.
3. Validate against CPU reference.
4. Keep broadphase timing separate from full contact-solver claims.

The contract facts are strong for a lesson: `matches_cpu_reference: true`,
`overflowed: false`, `valid_count: 4096`, and v2.4 phase validation is
`accept`.

## What Not To Claim

- Do not claim Contact Manifold V3 is 1.235x faster end to end.
- Do not claim RTDL accelerates the full contact solver.
- Do not claim AABB broadphase collect-k proves physics/contact-manifold acceleration.
- Do not claim this is a V3-over-V2 large speedup.
- Do not claim this is M7-qualified.

This remains a rebuild tutorial and not a release claim.
