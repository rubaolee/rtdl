I have all the material needed. The read of `refresh.md` was denied, which is fine — the review can proceed on the code and packet files.

---

## Goal1293 Pre-Pod Gate Review: Goal1292 v1.5 Generic OptiX Evidence Packet

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-05-05  
**Branch:** `main` @ `dd89f68`

---

### Verdict: `ACCEPT_WITH_NON_BLOCKING_NOTES`

---

### Review Against Each Question

**Q1 — Is Goal1292 safe and useful to run on a pod before further local engineering?**

Yes on both counts. The pod command sequence is: probe → source env → build → sanity-test → primitive runner → graph wrapper. All steps are read-only on persistent pod state except writes into the designated result directory. The runner catches all backend exceptions with `status: "failed"` and continues, so a partial OptiX environment (e.g., build succeeds but runtime crashes) produces diagnosable output rather than a silent abort. The env probe step is sequenced first, so the pod environment is captured before any failure interpretation, satisfying the stated success criterion.

**Q2 — Are the packet commands and required artifacts sufficient?**

Yes. The three-step evidence chain covers all three required diagnostic areas:

| Diagnostic | Coverage |
|---|---|
| Correctness | CPU oracle rows comparison via `_parity()`, direct hit_count match, prepared `hit_count` vs CPU oracle |
| OptiX prepared query timing | `run_phases` records `scene_prepare_sec`, `ray_prepare_sec`, `query_anyhit_count_sec`, `first`, `mean`, and `min` separately |
| Graph wrapper repeat timing | `--visibility-query-repeats 100` flows through `_run_visibility_edges` → `run_prepared_visibility_anyhit_count` → `run_phases` with first/mean/min; preserved in the artifact |

The `--copies 10000` / `--query-repeats 100` fixture (20 000 rays, 100 repeat queries) is appropriately scaled for RTX timing evidence. The graph wrapper at `--copies 30000` (120 000 rays) similarly provides scale.

**Q3 — Are the boundaries correct?**

Yes, and they are enforced in code, not just documentation:

- `public_wording_authorized: False` is emitted in every output artifact: the packet JSON, the runner JSON, `generic_prepared_status.py`, and the `claim_boundary` field of every result dict.
- The `FROZEN_BEFORE_V2_1_GENERIC_BACKENDS` tuple in `generic_primitives.py:23` causes an explicit `ValueError` if `vulkan`, `hiprt`, or `apple_rt` are passed to any generic primitive function, before any dispatch occurs.
- `rt_core_accelerated` is set to `True` only when `backend == "optix" and scenario == "visibility_edges"` (`rtdl_graph_analytics_app.py:369`). BFS and triangle_count are not claimed.
- The `honesty_boundary` string in the graph app explicitly states: *"Only visibility_edges is an OptiX ray/triangle any-hit RT-core candidate; OptiX BFS and triangle_count remain host-indexed by default."*
- The packet boundary string explicitly excludes whole-app speedup claims and new Vulkan/HIPRT/Apple RT implementation.

**Q4 — Are there any blocking issues that should be fixed before pod execution?**

No blocking issues found.

---

### Blocking Issues

None.

---

### Non-Blocking Notes

1. **Packet `source_commit` is one commit behind HEAD.** The pre-generated packet records `7516562` (the commit before `dd89f68 Add v1.5 OptiX evidence packet`). This is expected — the packet was generated before its own commit — but means the static packet file and the actual pod HEAD will differ by one commit. The runner script re-calls `_git_head()` independently, so `generic_optix_evidence.json` will record the correct pod-time commit. No action required; worth noting for traceability.

2. **Graph wrapper uses stdout redirect, not `--output`.** The pod command is `... > graph_visibility_optix_repeats.json`. This works correctly because `main()` in `rtdl_graph_analytics_app.py` emits exactly one `print(json.dumps(...))`. However, any future warning or progress line added to stdout would corrupt the JSON without a visible error. Non-blocking for this pod run; consider adding `--output` support to the graph app in a future goal.

3. **`vulkan` is present in `BACKENDS` in `rtdl_graph_analytics_app.py:19` without a CLI-level freeze guard.** The underlying generic primitive API enforces the v2.1 freeze via `ValueError`, but the graph app itself will accept `--backend vulkan` and dispatch before that guard is reached in the prepared-summary path. The pod run uses `--backend optix` only, so this is not a pod risk. A CLI-level guard (rejecting frozen backends at `run_app()` entry) would close the gap cleanly.

---

### Final Statement

Goal1292 packet, runner, test suite, and boundary enforcement are internally consistent and correct. The evidence chain is sufficient to diagnose correctness, prepared OptiX query timing, and graph wrapper repeat timing on an RTX pod. No public wording is authorized, no whole-app speedup claim is made, and the Vulkan/HIPRT/Apple RT freeze is enforced in code. The known Embree prepared parity gap is honestly documented and does not affect OptiX evidence collection.

**This review supports inclusion in a 3-AI consensus pre-pod gate. The pod run may proceed.**
