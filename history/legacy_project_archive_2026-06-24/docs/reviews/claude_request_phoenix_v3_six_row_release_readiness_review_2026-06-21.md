# Claude Request - Phoenix V3 Six-Row Release-Readiness Review

Please critically review the current Phoenix V3 state after the latest
classification, Robot Collision no-probe repair, Triangle Claude refresh, docs
polish, and gates.

This is not a request for praise. The user needs a hard answer:

1. Are we building a V3 engine/language surface rather than isolated benchmark
   app optimizations?
2. Does the current V3 work represent real technical optimization beyond V2.x,
   or only small 1.01x-style wording?
3. Is current V3 ready for a major release, or only ready as a bounded six-row
   exact-claim surface with release still blocked?
4. Is the current work materially necessary, or was V3 already basically done
   and this is only micro-polish?
5. What must happen next before a responsible user-facing V3 release can be
   declared?

Files to review:

```text
README.md
docs/learn/current_claim_boundaries.md
docs/application_catalog.md
docs/backend_maturity.md
docs/performance_model.md
docs/rebuild/v3/README.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/reports/phoenix_v3_status_and_next_steps_2026-06-21.md
tutorials/current/README.md
tutorials/current/07_grouped_sum_prepared_query.md
tutorials/current/09_rtdbscan_component_signature_route_split.md
tutorials/current/10_triangle_prepared_graph_chunk.md
tutorials/current/12_aabb_candidate_stream.md
tutorials/current/13_hausdorff_threshold_summary.md
tutorials/current/14_robot_collision_flag_stream.md
docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md
docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md
```

Latest local gates:

```text
py -3 -m unittest tests.v3_phoenix_triangle_prepared_graph_80000_m7_final_review_packet_test tests.v3_phoenix_m7_row_classification_packet_test tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test
Ran 34 tests
OK

py -3 scripts/run_test_matrix.py --group v3_rebuild
47 modules / 218 tests
OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
```

Current classification facts:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 6
route_map_m7_qualified_release_rows: 5
supplemental_m7_qualified_release_rows: 1
blocked_or_internal_rows: 14
optimization_required_reopen_queue: none
```

Current exact M7 rows:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
aabb_candidate_stream_all_count_only_float32_32768
component_union_clustered3d_65536_524288_repeat5_row_scoped
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
```

Important negative evidence:

```text
same-row geomean V3 speedup vs V2.14: 1.012x
broad_v3_faster_than_v2_claim_authorized: false
Spatial RayJoin author RT remains faster than RTDL OptiX on the PIP row.
RTNN wall timing loses for all three distributions.
Contact broadphase wall timing loses.
Barnes-Hut fastest route is fused Numba CUDA, not prepared OptiX.
```

Please produce:

- verdict: release-ready / bounded six-row surface only / reject;
- P0 release blockers;
- P1/P2 fixes;
- answer to the five user questions above;
- final recommendation for what Codex should tell the user now.
