---
review: goal906_graph_rt_doc_sync_after_goal905
date: 2026-04-24
reviewer: claude-sonnet-4-6
verdict: ACCEPT
---

# Goal906 Claude Review

**Verdict: ACCEPT**

Stale host-indexed-only graph wording is fixed and the no-RTX-claim-before-cloud
invariant is preserved at every enforcement layer.

---

## What Was Checked

### Stale wording removed

`docs/tutorials/graph_workloads.md` previously implied OptiX graph paths were
only host-indexed CSR fallbacks. After Goal906 the tutorial now states:

- default OptiX graph mode remains host-indexed (conservative, for existing users)
- explicit `--optix-graph-mode native` is packaged for BFS and triangle-count
- `--require-rt-core` is "rejected intentionally" for BFS/triangle until the
  combined Goal889/905 RTX cloud gate proves row-digest parity

All three phrases required by `test_tutorials_record_rejected_app_families` in
`goal821_public_docs_require_rt_core_test.py` are present:
`"host-indexed CSR fallback"`, `"--optix-graph-mode native"`,
`"reject \`--require-rt-core\` intentionally"`.

`docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md` Tier 3 entry for
`graph_analytics` now reads "explicit native OptiX graph-ray mode is packaged
but RTX-gated" and the Goal903-905 sequence entry explicitly says graph remains
deferred until the cloud gate passes and is independently reviewed.

`scripts/goal848_v1_rt_core_goal_series.py` Goal852 scope describes RTX
validation for visibility, native BFS, and native triangle-count sub-paths, with
acceptance requiring a strict RTX artifact and keeping shortest-path / graph
database / distributed analytics claims excluded.

`scripts/goal868_graph_redesign_decision_packet.py` now handles both fixture
states. The native-packaged branch resolves to
`"nvidia_rt_core_claim_today": "not_allowed"` and
`"local_recommendation": "run_combined_graph_rtx_gate"` — not a claim.

### No-RTX-claim-before-cloud preserved

Five independent enforcement layers are intact:

1. **Code**: `rt_core_accelerated: False` is hardcoded at the app level in
   `examples/rtdl_graph_analytics_app.py:177`. The sub-section `_run_visibility_edges`
   correctly sets `rt_core_accelerated: backend == "optix"` only for the
   scoped line-of-sight sub-path, which is the documented RT-core candidate;
   the outer app value is never True.

2. **Code**: `_enforce_rt_core_requirement` raises `RuntimeError` with
   `"limited to --scenario visibility_edges"` for any non-visibility
   `--require-rt-core` call on the optix backend.

3. **Test gate**: `test_component_apps_require_rt_core_fail_before_running_optix`
   (`goal814`) verifies `rtdl_graph_bfs.run_backend("optix", require_rt_core=True)`
   and `rtdl_graph_triangle_count.run_backend("optix", require_rt_core=True)`
   both raise RuntimeError with "not NVIDIA RT-core traversal".

4. **Test gate**: `test_tutorials_record_rejected_app_families` (`goal821`)
   enforces the rejection wording must be present in the tutorial; any future
   edit that removes it will fail this test.

5. **Planning artifact**: `goal868` decision packet boundary field records
   "native OptiX graph-ray candidate generation is now packaged but remains
   RTX-gated before promotion" — no authorization granted.

### Consistency with goal903 test expectations

`goal903_embree_graph_ray_traversal_test.py` expects
`"OptiX BFS and triangle_count remain host-indexed by default"` and
`"native graph-ray mode remains gated"` in `honesty_boundary`. Both phrases
appear verbatim in `rtdl_graph_analytics_app.py:182-184`. Consistent.

`goal889_graph_visibility_optix_gate_test.py` expects records labelled
`"optix_native_graph_ray_bfs"` and `"optix_native_graph_ray_triangle_count"` in
the gate output, confirming the native paths are registered but not claimed as
RT-core until the strict gate passes with a real RTX artifact.

---

## Boundary

This review confirms documentation and gate synchronization only. It does not
authorize `graph_analytics` for any RT-core claim. Graph promotion still requires
a real RTX cloud artifact (Goal855/Goal852) and post-cloud independent review.
