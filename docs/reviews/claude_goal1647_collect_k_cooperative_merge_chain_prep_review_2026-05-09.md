I now have everything I need for a complete review.

---

## Goal1647 Local Prep Review

### Verdict: **Approved — no blockers. Three minor findings worth noting before the pod run.**

---

### Correctness of the capability-only approach

The implementation is correct. `rtdl_optix_collect_k_cooperative_launch_capability` (lines 9–50 of `rtdl_optix_api.cpp`) does exactly what it claims:

- Calls `cuInit(0)` → `cuDeviceGet(&device, 0)` → five `cuDeviceGetAttribute` calls.
- No kernel launch, no module load, no context kept alive after the call.
- Falls entirely inside the existing `handle_native_call` wrapper, so error propagation is consistent with every other entry point.
- All five output-pointer nulls are checked before any CUDA call — clean fail-closed.

The five chosen attributes are the right set for the downstream cooperative-kernel residency calculation: SM count bounds the grid, max-threads-per-block bounds occupancy per SM, and opt-in shared memory size is needed if the merge kernel wants extended smem.

---

### Claim-boundary safety

The Python probe (`goal1647_v1_6_x_optix_collect_k_cooperative_capability_probe.py`) is tight:

- Six explicit `False` sentinel fields in the JSON output: `performance_evidence_authorized`, `fastest_candidate_behavior_changed`, `public_speedup_wording_authorized`, `stable_collect_k_promotion_authorized`, `broad_rtx_wording_authorized`, `release_action_authorized`.
- `next_probe_allowed` is correctly set to `bool(cooperative_launch.value)` — the capability result gates the next step, nothing else.
- `_claim_boundary()` text is explicit and comprehensive.
- The static tests verify all boundary fields are present in source. That's the right approach for a no-pod prep step where you can't run the binary.

The report and tests are consistent with each other and with Goal1646 consensus (opt-in only, not enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`).

---

### CUDA / cooperative-launch risks

**Three findings (none blocking):**

**1. Device index is hardcoded to `device = 0`.**
`cuDeviceGet(&device, 0)` always probes device 0. In a single-GPU development machine this is fine. In a multi-GPU pod, device 0 may not be the device the collect-k workload will actually run on. The probe will at least tell you whether the pod has *a* cooperative-capable device, but it won't catch the case where device 0 supports cooperative launch and the target device does not. For a first-pass probe this is acceptable — just be aware the result is device-0-specific.

**2. Output pointers are not zeroed on entry.**
If `cuDeviceGetAttribute` fails on attribute 3 of 5, outputs 1–2 contain valid data and outputs 3–5 are uninitialized. The non-zero return code from `handle_native_call` prevents callers from misusing those outputs (the Python script raises on `rc != 0`), so this is not a correctness bug in practice. A zero-initializing block at the top of the function (`*cooperative_launch_supported_out = 0; ...`) would make the failure mode cleaner.

**3. `CU_DEVICE_ATTRIBUTE_COOPERATIVE_MULTI_DEVICE_LAUNCH` is deprecated in modern CUDA.**
CUDA 9+ deprecated cross-device cooperative groups for general hardware; in newer toolkits this attribute may silently return 0 regardless of hardware. Querying it is safe (no error), but treating a `false` result as definitive for multi-device cooperative work would be wrong. Since you're recording it "for completeness" only and the implementation-gate is `cooperative_launch_supported`, not the multi-device field, this is fine — just document it as informational-only in the pod run notes.

---

### Is this a good no-pod preparation step?

Yes. The work is appropriately scoped:

- The C entry point is minimal and non-invasive — no new state, no change to any existing call path.
- The Python probe is self-contained via ctypes (no Python CUDA bindings required in the pod environment).
- The `next_probe_allowed` gating in the JSON output gives the pod a clean stop condition before any merge-chain implementation work begins.
- The pod plan step 4 ("stop if `cooperative_launch_supported` is false") correctly avoids burning pod time on devices that don't support it.
- The 1.15x first-probe threshold in the report is a reasonable pre-commitment that avoids accepting a marginal result as a good win.

The one preparation gap: the pod plan says "implement the opt-in cooperative merge-chain diagnostic behind a new diagnostic flag only" (step 5), but no skeleton for that flag name is defined yet. That's expected for a prep step — just make sure the flag naming is decided before the pod run starts, so the pod doesn't invent its own convention.
