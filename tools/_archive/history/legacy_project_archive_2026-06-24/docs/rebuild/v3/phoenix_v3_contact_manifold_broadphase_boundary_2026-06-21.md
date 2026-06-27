# Phoenix V3 Contact Manifold Broadphase Boundary

Status: rebuild boundary packet, not a release.

## Verdict

`contact_manifold / generic_aabb_broadphase_collect_k` is valid Phoenix V3
evidence for generic AABB broadphase candidate discovery plus bounded row
collection. It is not M7-qualified.

```text
status: contact_manifold_broadphase_boundary_not_m7
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
full_contact_solver_claim_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: claude_approved_boundary_not_m7
current_packet_2ai_consensus_status: claude_codex_consensus_complete_no_m7_promotion
```

The row is useful because it matches CPU reference and passes the v2.4 phase
timing contract. It is not a full contact solver or physics-engine speedup
claim, and the current wall path is slower on OptiX.

## Evidence

Source artifacts:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/paired_v2_v3_summary.json
```

Current-side row:

| Metric | Embree | OptiX | OptiX / Embree reading |
| --- | ---: | ---: | ---: |
| Query median | 0.030064855 s | 0.024347018 s | 1.235x |
| Collect-k bounded rows | 0.024335913 s | 0.008820392 s | 2.759x |
| Prepare AABB index | 0.067336693 s | 0.276901305 s | 0.243x |
| Broadphase phase wall | 0.549597338 s | 0.856680974 s | 0.642x |
| Wall median | 1.323679082 s | 1.648467004 s | 0.803x |

Wall ratios below 1.0 mean OptiX is slower. The current OptiX hot query and
bounded-row collection improve, but the AABB-index preparation and wall timing
offset the hot-path gain.

The `1.235x` query ratio is scoped only to
`emit_aabb_intersection_pair_rows_2d`. It is not wall timing and not full contact-solver throughput.

Contract facts:

| Field | Value |
| --- | --- |
| Candidate primitive | `AABB_INDEX_QUERY_2D` |
| Candidate contract | `generic_aabb_intersection_pair_rows_2d` |
| Primitive under test | `COLLECT_K_BOUNDED` |
| Row schema | `query_group_id`, `query_triangle_id`, `scene_triangle_id` |
| Valid count | 4,096 |
| Witness capacity | 4,096 |
| Overflowed | false |
| Matches CPU reference | true |
| Phase validation | accept |

Machine-readable boundary phrase for gates and tutorials:
`matches_cpu_reference: true`.

V2.14 paired context:

| Backend | Standard-row V3 speedup versus V2.14 |
| --- | ---: |
| Embree | 1.004x |
| OptiX | 0.989x |

The paired rows are standard `goal2626` rows. They do not authorize a broad
V3-over-V2 contact-manifold speedup claim.

## Claim Boundary

Allowed rebuild wording:

- RTDL has a generic AABB candidate stream with bounded row collection.
- The query metric is 1.235x OptiX over Embree.
- The collect-k materialization phase is 2.759x OptiX over Embree.
- The row matches CPU reference and phase validation accepts the v2.4 contract.
- The wall path is slower on OptiX: Wall OptiX / Embree is 0.803x.

Forbidden public wording:

- Do not claim Contact Manifold V3 is 1.235x faster end to end.
- Do not claim RTDL accelerates the full contact solver.
- Do not claim AABB broadphase collect-k proves physics/contact-manifold acceleration.
- Do not claim `contact_manifold` is M7-qualified.
- Do not claim V3 is broadly faster than V2 for contact manifold.

## M7 Blockers

- Wall timing is slower for OptiX.
- The row covers candidate discovery and bounded row collection, not full
  contact solving.
- OptiX AABB-index preparation cost offsets the hot query gain.
- AABB-index preparation is about 4.1x slower on OptiX and must be fixed before
  M7 candidacy.
- The exact row fills `valid_count == witness_capacity == 4096`; larger-dataset
  overflow-path behavior is not validated.
- Standard paired V2.14 rows are parity or regression.
- Fresh external review is closed for boundary status, but a future M7
  promotion still requires a new public-row review.

Current review records:

```text
docs/reviews/claude_phoenix_v3_contact_manifold_broadphase_boundary_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_contact_manifold_broadphase_boundary_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: keep contact manifold as a generic broadphase boundary lesson, not as
an M7 row.

1. Was I foolish?

   No. CPU reference and phase validation make the row teachable, but wall
   timing and solver scope block release wording.

2. If yes, what actions made the decision foolish?

   It would be foolish to publish the 1.235x query ratio without the 0.803x
   wall ratio and full-solver non-claim.

3. Was there another path?

   Yes: tune AABB-index preparation and rerun. That is future engineering, not
   current release evidence.

4. Can I now try a different path that actually solves the problem?

   Yes. Teach the generic broadphase/collect-k contract honestly and keep M7 at
   zero until wall timing, scope, and external review close.
