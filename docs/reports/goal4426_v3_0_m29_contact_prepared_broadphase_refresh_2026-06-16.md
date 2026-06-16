# Goal4426 V3.0 M29 Contact Prepared Broadphase Refresh

Date: 2026-06-16

Evidence:

`docs/reports/goal4426_v3_0_m29_contact_prepared_broadphase_refresh_grid65536_2026-06-16.json`

Status: complete. This is the V3 refresh for the contact-manifold benchmark row, scoped deliberately to the prepared generic AABB broadphase plus bounded witness-row primitive.

## Contract

Both backends run the same app-agnostic candidate-discovery contract:

`AABB_INDEX_QUERY_2D / generic_aabb_intersection_pair_rows_2d`

The app then applies the app-agnostic bounded row primitive:

`COLLECT_K_BOUNDED / aabb_index_2d_bounded_i64_rows`

No contact-specific native engine logic is allowed. Exact triangle refinement and any higher-level contact interpretation remain app-owned logic after the primitive emits candidate rows. The V2.4 phase-timing bucket named `partner_continuation` records this app-owned exact refinement, but M29 does not require an optimized external partner to make the primitive evidence valid.

## Dataset

The run uses `jittered_grid_65536`:

- 65,536 scene triangles
- 65,536 query triangles
- 4,294,967,296 possible all-pairs checks
- 65,536 emitted AABB candidate rows
- 65,536 final witness rows
- 65,536 all-pairs checks per emitted candidate
- warmup 1, repeat 20 per backend

This is intentionally not a tiny smoke test. The measured prepared-query windows are 11.9565s for OptiX and 13.5524s for Embree.

## Results

| Backend | Prepared build sec | Query median sec | Query total sec, 20 repeats | Python exact refinement sec | Bounded collect sec | Hot query+refine+collect sec | Candidate rows | Matches CPU ref |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Embree CPU | 0.671527 | 0.676819 | 13.552397 | 0.100702 | 0.172050 | 0.949570 | 65,536 | yes |
| OptiX RT cores | 1.021279 | 0.583447 | 11.956548 | 0.120979 | 0.191650 | 0.896077 | 65,536 | yes |

## Same-Contract Ratios

| Metric | Embree sec | OptiX sec | Embree / OptiX | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Prepared AABB query median | 0.676819 | 0.583447 | 1.16x | RT cores are faster on the prepared generic AABB traversal and row emission. |
| Query plus exact refinement plus bounded collect | 0.949570 | 0.896077 | 1.06x | Shared app-owned refinement and row collection compress the end-to-end hot advantage. |
| Prepared scene build | 0.671527 | 1.021279 | 0.66x | Embree builds this prepared AABB structure faster; keep build time separate from steady-state traversal. |

## Why The Gain Is Modest

The result is reasonable, not a failure. This contact row is a sparse, compact broadphase workload: 4.29B conceptual all-pairs checks collapse to 65,536 candidate rows. Once the generic primitive has emitted those rows, both backends pay the same app-owned exact triangle refinement and bounded-row collection costs. Those shared costs are 0.2728s for Embree and 0.3126s for OptiX in this run, large enough to shrink a 1.16x traversal gain to a 1.06x hot-path gain.

So the honest claim is narrow: RTDL can express this contact-witness broadphase through app-agnostic primitives, and OptiX/RT cores are modestly faster than Embree on the prepared AABB query for this fixture. This evidence does not support wording that RTDL has a full contact-manifold solver or a large whole-app speedup here.

It does not authorize a public full contact-manifold solver claim.

## Validation

Both rows report:

- `matches_cpu_reference=true`
- `complete_candidate_coverage=true`
- `overflowed=false`
- `aabb_candidate_pair_count=65536`
- `valid_count=65536`
- `candidate_compactness=1.52587890625e-05`
- `public_speedup_claim_authorized=false`

## Closeout

M29 closes the V3 contact prepared-broadphase refresh. The app remains primitive-first and app-agnostic: RTDL owns generic AABB row emission and bounded row collection, while contact interpretation remains outside native engines. Public wording should describe this as a large deterministic contact-witness broadphase validation with modest RT-core traversal benefit, not as a complete contact-manifold acceleration claim.
