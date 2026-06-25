I now have all the information I need for a complete and grounded verdict. The critical evidence is in the CUDA kernel itself.

---

## External Critical Review: `goal4620` Aggregate-Tree Fallback Protocol

**Date:** 2026-06-24  
**Verdict: `reject_aggregate_tree_candidate_choose_different_fallback`**

---

### Dispositive Finding: The Kernel Is Barnes-Hut Gravity

Before answering the reviewer questions, the code speaks first. The CUDA kernel `rtdl_aggregate_tree_fused_weighted_vector_sum_2d` at lines 4127–4133 and 4156–4163 of `src/native/optix/rtdl_optix_api.cpp` computes:

**Aggregate path:**
```c
const double dist_sq = dx_node * dx_node + dy_node * dy_node + softening_sq;
const double inv_dist = 1.0 / sqrt(dist_sq);
const double scale = smass * node.mass * inv_dist * inv_dist * inv_dist;
sum_x += dx_node * scale;
sum_y += dy_node * scale;
```

**Exact path:**
```c
const double scale = smass * target_weights[target_index] * inv_dist * inv_dist * inv_dist;
sum_x += dx * scale;
sum_y += dy * scale;
```

This computes `source_mass × target_mass / (r² + ε²)^(3/2) × displacement`. That is Newton's gravitational force law with Plummer softening — textbook Barnes-Hut N-body. The contract text in `aggregate_tree_reference.py` line 1216–1220 names the formula directly: "accumulate target_weight * displacement / softened_distance_cubed." The word "softened_distance_cubed" is the Plummer-softened inverse-square law in nominative form. Renaming `mass` to `weight` and `force` to `vector_sum` does not change the physics.

---

### Reviewer Question Answers

**Q1. Does this protocol correctly incorporate Claude's two required amendments?**

Structurally, yes: Audit A is the algorithmic-genericity test and Audit B is the device-contract test. Both are present with defined go/no-go conditions. However, the protocol's own "Negative / risk signals" section underplays the severity of what it already knows. It frames `softening`, `inverse distance cubed`, and `source_weight * node.mass * inv_dist^3` as "suspicious" risk signals, when they are dispositive: no generic weighted-vector sum operator computes an inverse-cubic force law with a Plummer regularization parameter. The protocol should have concluded the algorithmic audit before asking for implementation permission.

**Q2. Is the aggregate-tree candidate still acceptable as the next feasibility target under these stricter gates?**

No. Audit A fails on the code as it exists. The kernel hardcodes the gravitational force law. No rename, no parameter relabeling, and no reformulated contract text changes the CUDA computation. The Audit A requirement — "the operator is defined as a generic tree-aggregated weighted vector transform independent of an app name" — is unmet because the kernel is inseparable from N-body force semantics. `softening` (Plummer softening) has no meaning outside particle simulation. The only truthful description of this kernel is "Barnes-Hut gravitational force accumulation." Audit A returns No-Go.

**Q3. Should CUDA-only fused device-array operators be allowed in V4.0 Tier-2, or must Tier-2 be RT-core-backed?**

V4.0 Tier-2 must be RT-core-backed. The reasons:

- V4's differentiation from V3 is RT-core acceleration. A CUDA-only kernel inside the OptiX backend library is V3-level internal residency, not V4-level RT-core evidence. This candidate already existed in V3.
- Allowing CUDA-only Tier-2 operators creates a category of "RT-adjacent but not RT-core" entries that will be used in release wording when they shouldn't be.
- The native run path calls `cuLaunchKernel` with no `optixLaunch`, no BVH build (`bvh_build_seconds: 0.0`), and no optixTrace. It is a CUDA kernel that happens to live in the OptiX library. That is not Tier-2 RT-core evidence.

CUDA-only fused device-array operators may be legitimate V4.x internal-infrastructure candidates, but they should not appear in the measured Tier-2 catalog for V4.0.

**Q4. Are the Go/No-Go gates sharp enough to prevent relabeling Barnes-Hut as a generic surface?**

No. The current gates are necessary but insufficient. They require that "the operator is defined as a generic tree-aggregated weighted vector transform with clear mathematical inputs/outputs independent of an app name" and that "softening and inverse distance cubed are either renamed or scoped as non-V4.0." But those conditions can be gamed by strategic renaming. What the gates are missing is a computation-level test:

> If the kernel accumulates `w1 × w2 / distance^n × displacement` for any n ≥ 2 with a Plummer-type regularization term, it is presumptively an N-body force kernel. Acceptance requires extraordinary evidence — beyond renaming — that the same computation has a documented, named use in a non-particle domain at the same power law and softening structure.

Without a test that reaches into the kernel formula itself, the gate can be satisfied by renaming `softening` to `regularization_epsilon` and `mass` to `weight` while the kernel remains unchanged. The gate should also explicitly say: "No-Go if the contract text uses the phrase `softened_distance_cubed` or any equivalent." The existing contract text (aggregate_tree_reference.py:1218–1219) already uses this phrase.

**Q5. Are the device-array gates sharp enough to prevent repeating the goal4619 host-query mistake?**

The run-path gates are adequate. `run_device_columns()` accepts raw device pointers for source columns, and the output is device-resident. The hot path does not materialize frontier rows or contribution rows on host — confirmed in the native run function.

However, the prepare-path gates are insufficient. The existing `prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix()` function in `optix_runtime.py` lines 2785–2792 creates CuPy arrays from host Python iterables — it is not caller-owned device input. More critically, the native prepare function at `rtdl_optix_api.cpp` lines 4583–4584 downloads `target_ids` and `target_weights` from device to host using `download()` calls to build the internal lookup map (`target_index_by_id`). This is a D2H transfer inside the prepare path.

The protocol's Audit B criteria say targets may enter as "RTDL-owned native state, similar to point-group" — but that framing was not applied to this candidate, and the current gate text does not catch the D2H-during-prepare pattern. The gates should explicitly require:

> "The prepare path must either (a) accept caller-owned device arrays for targets without D2H copies for index construction, OR (b) the surface metadata must record `prepared_target_data_downloaded_from_device_to_host_at_prepare_time: true` and this is explicitly disclosed to users."

The current Audit B criteria would not catch the `download(target_ids...)` call because it happens at prepare time, not in the "measured hot run path."

**Q6. May Codex begin the `goal4620` feasibility audit under this protocol?**

No. The feasibility audit is already complete. The dispositive evidence is the CUDA kernel source. Audit A fails. The computation is `m1 × m2 / r³ × displacement` with Plummer softening — Barnes-Hut N-body gravity. No V4 operator catalog entry, no front-door contract, and no surface rename can change the kernel. Codex must:

1. Accept the Audit A No-Go for this candidate.
2. Not describe this operator as a generic weighted-vector sum in any future document.
3. Select a different candidate from the V2/V2.x inventory that does not embed a force law.

---

### Summary of What Is and Is Not Authorized

| Item | Status |
|---|---|
| Implementation of goal4620 as currently specified | **Not authorized** |
| Measured-catalog promotion | **Not authorized** |
| V4 release | **Not authorized** |
| Broad V4 speedup wording | **Not authorized** |
| True-zero-copy wording | **Not authorized** |
| RT-core wording for this operator | **Not authorized** |
| CUDA-only Tier-2 in V4.0 | **Not authorized** |
| "Generic weighted-vector sum" relabeling of this kernel | **Not authorized** |
| OptiX 9.1 scope | **Not authorized** |
| Tier-3 callbacks, C ABI, CuPy claims | **Not authorized** |
| Proceeding to find a different fallback candidate | **Required next step** |

---

### What Must Happen Before Any Fallback Is Accepted

1. The next candidate must not embed a force law. Inspect the CUDA/native kernel before writing any protocol — the protocol review came after the kernel existed here, which is the wrong order.
2. The algorithmic audit must answer "what is the reduction formula?" before the device-contract audit. If the reduction formula is domain-specific, the device-contract audit is moot.
3. Any candidate with a `softening` or `epsilon` regularization parameter whose only natural interpretation is Plummer softening should be presumptively rejected unless a non-physics use case is documented first.
4. RT-core-backed means `optixLaunch` with `optixTrace`, measurable BVH build seconds, and RT-core traversal — not a CUDA kernel compiled into the OptiX DSO.
