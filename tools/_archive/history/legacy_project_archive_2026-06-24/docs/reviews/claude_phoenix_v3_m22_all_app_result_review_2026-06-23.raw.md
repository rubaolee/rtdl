## Verdict: `approve_blocked_not_release`

**Bottom line.** The run is structurally valid evidence (rc=0, 51 matched rows, zero source mismatches), but it fails every preregistered performance bar and contains at least one V3 correctness defect. This is not a close call — the overall geomean is 15 points short of the 1.20x gate, only 4 of 10 apps clear 1.05x against a required 8, and `barnes_hut` is a hard protocol-level severe regression. No release, no public speedup claim.

---

## Findings by Severity

**1. V3 correctness failure — code defect (Critical)**
`rayjoin_optix_promoted_overlay_seed_tiled_x2048` crashes with an unexpected `point_order_mode` argument. This is a V3 bug, not a baseline issue. It invalidates that app's full result row and may mask real performance. Must be fixed before any future run counts those rows.

**2. `barnes_hut` severe regression — 0.831x (Critical/Blocking)**
Fails two independent protocol gates simultaneously: `barnes_hut_app_geomean_floor` (0.831x vs 0.900x) and `new_app_level_severe_regression_floor` (0.831x vs 0.900x). A regression of this magnitude in a shipped app is a release blocker independent of aggregate geomean results.

**3. Overall geomean gate failed — 1.049x vs 1.20x required (High)**
The gap is 14.4 percentage points. Set-A (1.013x) is essentially neutral. Set-B (1.210x) clears the bar in isolation, but Set-A dragging the combined result this far under indicates the shared execution/residency trunk is not delivering for the majority configuration.

**4. App count gate failed — 4/10 vs 8/10 required above 1.05x (High)**
Only `librts_spatial_index` (1.827x), `contact_manifold` (1.421x), `hausdorff_xhd` (1.134x), and `spatial_rayjoin` (1.068x) clear the threshold. `robot_collision` (1.027x), `rtnn` (1.003x), and `rt_dbscan` (1.002x) are effectively neutral. This pattern — strong Set-B outliers masking a flat or negative Set-A — is a structural concern, not noise.

**5. `librts_spatial_index` OptiX watch row regression — 0.803x (Medium)**
The app geomean is 1.827x, so the aabb_index_all_count_only OptiX configuration is locally regressing against a fast backdrop. This is a targeted correctness or scheduling issue within the app, not a general `librts` problem, but the watch alert is live and must be traced before claiming that app's geomean is clean.

**6. V2.14 baseline correctness failures on two apps (Low/Confounding)**
`spatial_rayjoin_optix_prepared_full_route` (OptiX invalid value) and triangle-counting OptiX rows (unsupported PTX/toolchain) fail in the V2.14 baseline. These rows cannot be used for valid V3 vs. V2.14 comparison. The reported speedup for `spatial_rayjoin` (1.068x) should be treated as provisional until baseline rows are clean.

---

## Corrections to Codex's Conclusion

Codex's conclusion is accurate. One addition: the V3 correctness failure on `rayjoin_optix_promoted_overlay_seed_tiled_x2048` should be ranked above the Barnes-Hut regression in fix priority, because it represents a V3 code defect (wrong argument passed to the kernel/API), whereas `barnes_hut` is a performance regression. A code defect can silently corrupt timing data or produce phantom speedups in adjacent rows; it needs to be closed first so subsequent focused probes are not built on a broken binary.

---

## Concrete Next Actions Before Another All-App Run

1. **Fix V3 `rayjoin_optix` argument defect.** Identify and remove the unexpected `point_order_mode` parameter. Confirm the row runs to completion and produces numerically correct output.

2. **Diagnose and fix `barnes_hut` regression.** Root-cause the 0.831x result — scheduling, kernel selection, or memory layout change. Do not proceed to all-app until a focused probe on `barnes_hut` alone shows >= 0.900x.

3. **Trace `librts_spatial_index` OptiX watch row.** Run the aabb_index_all_count_only OptiX configuration in isolation. The 0.803x result within a 1.827x-geomean app is a local defect. Identify the specific codepath and fix or exclude with justification.

4. **Prove Set-A execution/residency trunk on focused probes.** Set-A geomean of 1.013x with only 2 apps over 1.05x is the underlying structural problem. Run a focused probe suite on Set-A apps with residency tracing before assuming a fix to the above items will move the aggregate geomean.

5. **Repair V2.14 baseline rows before comparing `spatial_rayjoin` and triangle-counting.** Either resolve the OptiX invalid value and PTX toolchain errors, or formally exclude those rows and mark the `spatial_rayjoin` speedup as unverified.

6. **Do not rerun all-app until all five items above are addressed.** Rerunning with known correctness defects and a live severe regression will produce another protocol failure and consume run budget without information gain.

---

## Non-Authorization Block

**Release is not authorized.**
**Public speedup claims ("V3 is faster than V2.x") are not authorized.**
**Broad comparative claims are not authorized.**

These blocks remain in effect until the preregistered gate (overall geomean >= 1.20x, >= 8/10 apps above 1.05x, zero severe regressions) is met under a passing protocol gate status, and row-level correctness failures are resolved.
