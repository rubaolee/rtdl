## External Critical Review: `goal4619` 3D Fixed-Radius Device-Array Feasibility

**Verdict: `accept_with_required_amendments`**

No-Go for goal4619 is upheld. The fallback candidate selection for goal4620 is conditionally accepted, with required amendments to the feasibility brief before that audit begins. Details below.

---

### Reviewer Question 1: Do you agree with the goal4619 No-Go verdict?

**Yes, unambiguously.**

The No-Go is correct. The V4 Python GPU-array device-array surface requires three independent caller-owned device columns (search, query, output) and zero host materialization in the measured hot path. The 3D count-threshold route fails the query-input leg entirely. Promoting it would be a surface contract misrepresentation, not a naming choice.

---

### Reviewer Question 2: Is the evidence sufficient that 3D fixed-radius has output device columns and self-query residency, but lacks a true caller query device-column V4 contract?

**Yes, and the evidence chain is multi-layer, which is appropriate for a No-Go.**

The packet establishes the gap at four independent levels:

1. **ABI level (nm):** No `_3d_device_search_columns` or `_3d_device_query_columns` symbols in the built SO. This is the hardest fact — you cannot paper over missing ABI.
2. **Native C++ level:** `write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix` builds `std::vector<GpuPoint3DHost> gpu_queries` and uploads before launch. This is explicit host-materialization of the query path, not a staging optimization that could be stripped — it is the path.
3. **Python metadata level:** `input_contract: "host_query_points_prepared_native_search_scene"` and `transfer_mode: "host_query_points_to_device_threshold_columns"` and `true_zero_copy_authorized: False` all agree with the C++ finding.
4. **Python call site:** `pack_points(records=query_points, dimension=3)` is called before the native invocation. A V4 device-array surface must not call this in the hot path.

The self-query residency finding is correctly characterized: it avoids host repack only when query == prepared search scene. That is not a general caller query device-column path. Noting it as a future asset rather than a gap-filler is the right call.

**One gap in the evidence packet:** the packet does not show a confirmed negative for 3D on-stream device-search-column symbols — it lists 2D on-stream symbols to show what 3D is missing, but does not explicitly show the nm output for 3D. This is minor because the C++ source audit and Python metadata both independently confirm the host-query architecture. Sufficient for No-Go. A future goal seeking to implement true 3D device-query ABI should rerun nm as baseline step 1.

---

### Reviewer Question 3: Is Codex right to forbid wrapping the current host-query route as a V4 device-array surface?

**Yes. This is a hard boundary and the packet is correct to state it as one.**

A host-query route that materializes `std::vector<GpuPoint3DHost>` and uploads it as part of every query invocation cannot be marketed as a V4 Python GPU-array Tier-2 device-array surface regardless of what is exposed at the Python call signature level. The contract claim would be false at the allocation boundary. This is not a policy preference — it is a factual mismatch between the claimed and actual data path.

There is no wrapping, renaming, or thin-shim approach that corrects this. The only honest paths forward are: (a) implement the missing 3D device-search-column and device-query-column ABI and validate it, or (b) declare No-Go and defer. The packet correctly selects (b).

---

### Reviewer Question 4: Do you approve selecting generic aggregate-tree weighted-vector sum as the fallback candidate for a separate goal4620 feasibility/implementation path?

**Conditionally yes — as a feasibility candidate only, not as a pre-approved surface. Two required amendments to the goal4620 brief are needed before the audit begins.**

The selection logic is sound: the operator is a fused continuation pattern, exercises the V4 design thesis, has prior native scaffolding, and is not named after an application. The packet correctly scopes it as feasibility-first, not implementation authorization.

However, there are two gaps the packet does not close, and they must be addressed in the goal4620 brief before work begins:

**Required Amendment A — Barnes-Hut algorithmic audit is mandatory, not optional.**

The packet says "do not call it Barnes-Hut." That is a naming rule, not an algorithmic audit. If `aggregate_tree_fused_weighted_vector_sum_2d` is algorithmically a Barnes-Hut kernel — hierarchical multipole approximation over a spatial tree, with near/far interaction splitting — then renaming it "generic weighted-vector aggregation" does not make it generic. It makes it a mislabeled app kernel.

The goal4620 feasibility brief must include an explicit algorithmic characterization step: what does the aggregate tree structure represent, is the weighted-vector sum a fixed generic linear operator or does it implement an approximation scheme specific to N-body/gravitational/particle simulation? If the answer is the latter, the fallback must be rejected at that step and a different candidate selected.

**Required Amendment B — device-query-column input contract must be audited before the fallback can proceed.**

The packet's own Non-Authorization section forbids wrapping a host-query route as a V4 device-array surface. The same risk applies to `aggregate_tree_fused_weighted_vector_sum_2d`. The packet does not audit whether this operator accepts caller-owned query device columns or materializes inputs on host. The goal4620 feasibility brief must include an nm audit of the built SO for device-column input symbols, a native source inspection equivalent to what Finding 4 did for 3D fixed-radius, and a Python metadata check for `transfer_mode` and `true_zero_copy_authorized` before the feasibility audit concludes.

If the aggregate-tree operator also materializes inputs on host, the same No-Go logic applies and the fallback must itself receive a No-Go before any implementation work.

The phrase "V3-era scaffolding" in the packet is not evidence that the device-query-column contract exists. V3-era scaffolding may predate the V4 device-array contract and may only cover device output columns, which is the same partial picture that caused 3D fixed-radius to fail. Verify, do not assume.

---

### Reviewer Question 5: If not, what fallback should be selected and why?

The fallback candidate is conditionally accepted (see Q4), so this question is partially moot. However, for the record: if the goal4620 audit finds that `aggregate_tree_fused_weighted_vector_sum_2d` is algorithmically Barnes-Hut or lacks device-query-column input, the alternative fallback candidates proposed in the packet (ranked fixed-radius summary/top-k, other generic fused operators from the V2/V2.x inventory) are appropriate substitutes, provided each receives the same two-step audit: (1) algorithmic genericity, (2) device-query-column input contract. No fallback should be selected without both audits passing.

---

### Reviewer Question 6: Does this packet preserve all claim boundaries?

**Yes, the Non-Authorization section is complete and correctly scoped.**

All prohibited claims are listed. The packet does not assert V4 release, broad speedup, true-zero-copy, Tier-3 callbacks, C ABI/embedding, app-specific kernels, CuPy performance claims, or OptiX 9.1. The self-query residency finding correctly avoids being promoted as a V4 device-array claim. The aggregate-tree fallback selection is correctly framed as feasibility candidate, not implementation authorization. No boundary violations found in this packet.

---

### Summary

| Item | Decision |
|---|---|
| goal4619 No-Go for 3D fixed-radius device-array surface | **Upheld** |
| Evidence sufficiency for No-Go | **Sufficient** (four independent layers) |
| Forbidding host-query wrapping as V4 device-array surface | **Correct, hard boundary** |
| Fallback candidate selection (aggregate-tree weighted-vector sum) | **Conditionally accepted for goal4620 feasibility audit only** |
| Required Amendment A: algorithmic Barnes-Hut audit | **Mandatory before goal4620 begins** |
| Required Amendment B: device-query-column input contract audit | **Mandatory before goal4620 proceeds past feasibility** |
| Claim boundaries in this packet | **Preserved** |

The goal4619 No-Go stands. Goal4620 may proceed to feasibility audit with the aggregate-tree weighted-vector sum as the candidate, provided both required amendments are incorporated into the feasibility brief before any work begins. No implementation is authorized until that feasibility audit returns an affirmative verdict from an equivalent external review.
