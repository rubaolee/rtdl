All three width files confirmed from the same session: same hostname (`0256b71980f1`), same build (`torch 2.8.0+cu128`), timestamps within 37 seconds of each other. The gate passed and ratios match the scorecard exactly.

---

## Verdict: `accept_goal4628_second_gate_existing_pod_evidence`

Fresh POD rerun: **not required.**

---

### Findings

**1. Fixed-radius prerequisite (Q1)**

Satisfied. The required artifacts exist: `v4_fixed_radius.py`, `fixed_radius_device_array_frontdoor.md`, `fixed_radius_torch_device_arrays.py`, both fixed-radius API/docs tests, and the amendment closure document. The prerequisite is visible in the scorecard struct and tested. No gap here.

**2. Validity as second non-fixed-radius gate (Q2)**

Valid. Goal4627's completion consensus explicitly selected `raydb_style` / grouped-i64 as the Goal4628 gate. The operator is generic (`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`), not fixed-radius, not app-identity. The selection logic is sound and the prior promotion review chain for goal4617 exists.

**3. POD evidence sufficiency (Q3)**

Existing evidence is sufficient. All three width files are from a single RTX A5000 session within a 37-second window (22:40:52–22:41:29 UTC, 2026-06-24), same hostname, same Python/Torch build. Seven repeats with 2 warmup runs per point is serious measurement. No stale-build gap, no same-contract gap, no product-boundary gap was found.

**4. Same-contract integrity (Q4)**

The comparison is clean and honest. Both routes share:
- Same prepared scene, prepared ray batch, prepared primitive payload
- Same input contract (caller-supplied torch device columns)
- Same hardware and session

The sole difference is the output path: legacy downloads group rows to host (`group_rows_downloaded_to_host: true`, `host_materialization_in_hot_path: true`); V4 writes directly to device columns (`native_direct_device_output_columns: true`, `host_materialization_in_hot_path: false`). The ratio is median-vs-median in both cases. Ratios in the scorecard code match the JSON to full precision.

**5. Width 256 interpretation (Q5)**

No narrowing, rerun, or rejection required. The 1.641x minimum at width=256 / 32,768 rays is structurally honest: with only 128 output groups, the legacy host materialization is inexpensive (128 rows × small row size), so the boundary removal buys less. The raw timings for that point are tight clusters (legacy: 0.234–0.265ms; device: 0.136–0.178ms) — no noise anomaly. The 2.978x at 131,072 rays confirms the benefit grows with ray count even at wide groups, as expected. The packet explains this correctly and does not generalize the 1.6x figure.

**6. Boundary preservation (Q6)**

All seven non-authorization flags are `False` in the scorecard and enforced by `validate_v4_goal4628_second_gate_scorecard()`. The status field reads `goal4628_second_tier2_gate_scorecard_not_release`. No release, broad-speedup, whole-app, true-zero-copy, Tier-3, CuPy, C ABI, or app-kernel claims are present or implied.

**7. Required amendments (Q7)**

None. The packet, scorecard code, and test are internally consistent, correctly bounded, and the evidence is structurally sound for this gate.
