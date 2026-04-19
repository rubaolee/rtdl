# RTDL v0.9 Release Package

This package records the released `v0.9.0` line.

`v0.9.0` is released. The current evidence says that HIPRT has Linux
`run_hiprt` parity coverage for the 18-workload matrix, with explicit
performance and platform boundaries. After the original Goal 570 release gate,
Goals 571-574 added and closed the RTXRMQ paper workload, including the new
`ray_triangle_closest_hit` primitive for CPU reference, `run_cpu`, and Embree.

The final release gate is Goal 575. Goal 576 records that broader archive-link
debt is non-blocking for the current public v0.9 release path.

Release note: Goal 578 starts the `v0.9.1` Apple RT line on main. It adds
`run_apple_rt` for 3D `ray_triangle_closest_hit` through Apple Metal/MPS on
macOS Apple Silicon. This is a bounded released slice, not a full
Apple backend parity claim or speedup claim.

Start here:

- [Support Matrix](support_matrix.md)
- [Goal 560 HIPRT Backend Performance Comparison](../../reports/goal560_hiprt_backend_perf_compare_2026-04-18.md)
- [Goal 560 Raw Linux JSON](../../reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json)
- [Goal 560 External Review](../../reports/goal560_external_review_2026-04-18.md)
- [Goal 562 v0.9 Pre-Release Test Gate](../../reports/goal562_v0_9_pre_release_test_gate_2026-04-18.md)
- [Goal 562 External Review](../../reports/goal562_external_review_2026-04-18.md)
- [Goal 563 Documentation Audit](../../reports/goal563_v0_9_documentation_audit_2026-04-18.md)
- [Goal 564 Release-Candidate Flow Audit](../../reports/goal564_v0_9_release_candidate_flow_audit_2026-04-18.md)
- [Goal 564 Claude Review](../../reports/goal564_external_review_2026-04-18.md)
- [Goal 564 Gemini Flash Review](../../reports/goal564_gemini_flash_review_2026-04-18.md)
- [Goal 565 Prepared HIPRT Performance Round](../../reports/goal565_hiprt_prepared_ray_perf_2026-04-18.md)
- [Goal 566 Prepared HIPRT 3D Nearest-Neighbor Performance Round](../../reports/goal566_hiprt_prepared_nn_perf_2026-04-18.md)
- [Goal 567 Prepared HIPRT Graph CSR Performance Round](../../reports/goal567_hiprt_prepared_graph_perf_2026-04-18.md)
- [Goal 568 Prepared HIPRT DB Table Reuse](../../reports/goal568_hiprt_prepared_db_perf_2026-04-18.md)
- [Goal 569 Post-Goal568 Release-Gate Refresh](../../reports/goal569_v0_9_post_goal568_release_gate_refresh_2026-04-18.md)
- [Goal 570 Final Pre-Release Test/Doc/Audit Gate](../../reports/goal570_v0_9_final_pre_release_test_doc_audit_2026-04-18.md)
- [Goal 571 RTXRMQ Paper-Derived Workload](../../reports/goal571_rtxrmq_paper_workload_engine_compare_2026-04-18.md)
- [Goal 572 Post-RTXRMQ Release Addendum](../../reports/goal572_v0_9_post_rtxrmq_release_addendum_2026-04-18.md)
- [Goal 573 RTXRMQ Closest-Hit Feature](../../reports/goal573_rtxrmq_closest_hit_feature_2026-04-18.md)
- [Goal 574 Post-Closest-Hit Release Addendum](../../reports/goal574_v0_9_post_closest_hit_release_addendum_2026-04-18.md)
- [Goal 575 Final Release Gate After Closest-Hit](../../reports/goal575_v0_9_final_release_gate_after_closest_hit_2026-04-18.md)
- [Goal 575 Codex Final Review](../../reports/goal575_codex_final_review_2026-04-18.md)
- [Goal 575 Gemini Flash Review](../../reports/goal575_gemini_flash_review_2026-04-18.md)
- [Goal 576 Archive Link Audit](../../reports/goal576_v0_9_archive_link_audit_2026-04-18.md)
- [Goal 576 Codex Review](../../reports/goal576_codex_review_2026-04-18.md)
- [Goal 576 Gemini Flash Review](../../reports/goal576_gemini_flash_review_2026-04-18.md)
- [Goal 578 v0.9.1 Apple RT Backend Bring-Up](../../reports/goal578_v0_9_1_apple_rt_backend_bringup_2026-04-18.md)
- [Goal 578 Gemini Flash Review](../../reports/goal578_gemini_flash_review_2026-04-18.md)
- [Goal 578 Claude Review](../../reports/goal578_claude_review_2026-04-18.md)
