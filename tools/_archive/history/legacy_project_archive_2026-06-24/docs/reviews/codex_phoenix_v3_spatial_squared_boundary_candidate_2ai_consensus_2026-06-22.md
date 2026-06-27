# Codex 2-AI Consensus: Phoenix V3 Spatial Guarded Squared-Boundary Candidate

Date: 2026-06-22

Status: `claude_codex_consensus_accept_with_boundary_not_release`

External review: `docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md`

Candidate packet: `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json`

## Verdict

Codex accepts Claude's verdict: this is a real generic `point_location_topology_stream`
optimization with serious POD evidence, but it is not yet a user-facing Phoenix V3
release row.

The candidate may be carried forward as an accepted-with-boundary env-gated capability
candidate. It must not be counted as an M7-qualified release row until P1 is resolved:
the optimized route must either become the V3 default path or have a reviewed user-facing
activation contract plus repeat POD evidence under that contract.

## What Is Accepted

- The optimization is generic: it changes the closed-shape exact-f64 topology-stream
  predicate and does not special-case RayJoin, counties, CDB files, or the benchmark.
- Correctness evidence is materially stronger than the rejected pure-squared path:
  guarded squared comparison records zero mismatches over 201,260 finite-double cases,
  while the pure squared form records 10 endpoint-adjacent mismatches.
- POD evidence is serious: the guarded-squared plus prefilter-zero route reports
  `1.0804496705532074 ms` median prepared query time versus `1.8956884741783142 ms`
  for the current prefilter-zero route, with exact count stable at `47,262`.
- Claim boundaries remain strict: no public release, no broad V3-vs-V2 claim, no
  RTDL-beats-RayJoin claim, no paper reproduction claim, no true zero-copy claim, and
  no V4/embedding claim are authorized.

## Fixes Applied After Claude Review

Claude P2-A identified dead CUDA helper code: `exact_boundary_contact_f64` used the
unsafe pure-squared predicate and was uncalled.

Codex removed that dead helper from
`src/native/optix/rtdl_optix_workloads.cpp` and added a packet-level guard:
`native_source_does_not_define_dead_exact_boundary_contact`.

Regenerated packets now record source SHA:
`d0beeb3b344f3aae59c847ce001637ccc09b77338293887609a8a5428a2c23d3`.

## What Remains Blocked

P1 default-path resolution remains open.

The candidate currently depends on two env flags:

- `RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO`
- `RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY`

That means a normal V3 user does not yet get this performance by default. Therefore:

- `m7_promotion_authorized` stays false.
- `m7_qualified_release_rows_added` stays 0.
- Phoenix V3 release remains blocked.
- The Spatial capability-family gap is not closed for the major-release surface.

## Required Next Action

Run a P1 default-path characterization:

1. Decide whether both optimizations become default-on for the V3 relation-status
   corrected scalar-count executor.
2. Rebuild and run repeat POD evidence with the default path, not only env-gated flags.
3. Keep exact-count parity at `47,262` for the public county packet and add adverse
   finite-double/topology edge coverage.
4. Request external review again before counting any user-facing M7 row.

## Goal-Level Decision Audit

1. Was I foolish?
   No. I did not convert an env-gated candidate into a release row after review.

2. If yes, what actions made the decision foolish?
   The foolish action would have been to treat Claude's "proceed to M7 consensus as an
   env-gated capability evidence row" as permission to update public V3 release claims.

3. Was there another path that would avoid getting stuck on that idea?
   Yes. The safer path is to accept the evidence, close the P2 maintenance hazard, and
   make P1 default-path characterization the next engineering step.

4. Can I now try a different path that actually solves the problem?
   Yes. The next path is to make the optimized route real for users, then rerun serious
   POD evidence and external review before promoting the Spatial family.
