**Verdict: All four concerns are correct. No remaining blockers in scope.**

---

### 1. Graph Embree exclusion — CORRECT

`graph_analytics / embree` is excluded because `_engine_selector()` finds no `--backend`/`--mode` flag in the source command, and the `embree` path falls through to the "decorative engine label" exclusion at script:114-127. The OptiX row survives via `_script_is_optix_specific()` (script:110-113) — it detects an optix-named script and proceeds as `planned`. Validation at script:287-289 enforces both statuses as hard assertions.

### 2. DBSCAN shared primitive alias — CORRECT

`dbscan_clustering / optix` is detected at script:148-150 by matching both app name and the exact script filename `goal757_optix_fixed_radius_prepared_perf.py`. It gets `status = "shared_primitive_alias"`, `shared_primitive_canonical = "outlier_detection"`, and both `compare_current` and `compare_v1_0` are forced False (script:163-165, since neither equals `"planned"`). Validation at script:296-302 checks all three properties as hard assertions.

### 3. Blocked release claims — CORRECT

`build_manifest()` hardcodes `release_authorized = False`, `tag_authorized = False`, `public_claim_authorized = False` (script:203-205), and enumerates all six blocked claims including `v1_6_11_release_tag_action` (script:216-223). `validate_manifest()` asserts all three flags are False and all six claims are present (script:263-276). The MD verdict and boundary section repeat this in prose.

### 4. Pod contract — CORRECT

The contract requires two clean checkouts or worktrees, separate per-engine builds with full provenance metadata (commit, GPU, driver, CUDA, OptiX SDK, build command), and treats missing v1.0 scripts or schema drift as `unsupported` — never as slower or faster (script:224-238). Validation at script:303-306 checks the two key phrases (`"two clean checkouts"`, `"unsupported"`) as hard guards. `requires_pod` and `pod_needed_after_local_preflight` are both True.

---

**Summary:** The four reviewed properties are all structurally correct and are each backed by a programmatic validation assertion. The matrix is pod-ready for these concerns; no edits needed.
