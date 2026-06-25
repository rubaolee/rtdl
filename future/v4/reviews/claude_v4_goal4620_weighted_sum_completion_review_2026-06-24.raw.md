I have read all the material I need. Rendering the verdict now.

---

`accept_goal4620_complete_candidate_not_promoted`

---

## Findings

### Reviewer Question Answers

**Q1: Does the implementation stay within the Claude-authorized Candidate A scope?**

Yes. The only new surface is `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`. No Candidate B/C/D/E work is present. No aggregate-tree path appears. The executor route reuses the pre-verified `prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor` — the exact method that Amendment 1 required be confirmed before implementation started. Scope is clean.

**Q2: Are all three Claude amendments closed?**

Closed and verifiable in the code:

- **Amendment 1** — confirmed in consensus doc with command-level pass output; method, return type, and metadata keys all match what was required. The Python session at `v4_ray_triangle.py:445` calls exactly that method.
- **Amendment 2** — `scene_preparation_ownership` and `scene_data_residency` are present in the claim boundary at lines 164–167 of `v4_ray_triangle.py`. The test at line 221 of `v4_ray_triangle_device_array_api_test.py` asserts the value directly.
- **Amendment 3** — RTDL-allocated primary path implemented (`allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4` -> `torch.zeros((1,), dtype=torch.uint64)`). Caller-override path supported. The `output_scalar_allocation` key is set to `"rtdl_allocated_default"` or `"caller_supplied_override"` at lines 464–467 and recorded in the run metadata at line 487. Test at line 218 asserts the override path; catalog gate exercises the default path.

**Q3: Is the POD evidence sufficient for candidate completion, while still insufficient for measured-catalog promotion?**

Yes. Two sizes (32768, 131072), parity=true at both, five repeats after two warmups. The ratio is explicitly framed as a same-contract comparison (device-output front door vs existing host-scalar route), not a cross-workload V4 speedup claim. The evidence doc and POD gate both carry explicit non-authorization blocks. The surface's `measured_partners: ()` is unchanged in `V4_TIER2_CANDIDATE_OPERATOR_SURFACES`. That is the structural gate — candidate completion does not touch it.

**Q4: Are the catalog/front-door/docs updates honest?**

Yes. `claim_boundary_v4()` in `v4.py` has exactly 5 entries in `measured_surfaces` and exactly 1 entry in `candidate_surfaces`. The front-door test at line 30 (`self.assertEqual(5, len(boundary["measured_surfaces"]))`) and line 40 (`self.assertEqual(1, len(boundary["candidate_surfaces"]))`) assert this directly. Docs say "not a release announcement," "not measured," and "candidate." No broad speedup wording observed.

**Q5: Is the nonzero stream fix correct and properly bounded?**

Correct and bounded. `torch.cuda.Stream()` always creates a new non-default CUDA stream; the default/null stream is `torch.cuda.default_stream()` with pointer 0. The fix is in `_default_cuda_stream` at line 430, called only from the weighted-sum session's `run()`, not from any other surface. The `cuda_stream_ptr_nonzero: true` in POD evidence confirms the native executor receives a nonzero pointer in production.

**Q6: May `goal4620` be marked complete as a candidate implementation?**

Yes, subject to the advisory below and the required 3-AI completion consensus or explicit review debt already stated in the packet.

---

### Advisory (not a blocking finding)

The catalog gate evidence reports the weighted-sum row status as `candidate_measured`. That label means the gate example executed and produced a measurement — it does not mean the surface was promoted to the measured catalog. The authoritative gate is `measured_partners: ()` in `V4_TIER2_CANDIDATE_OPERATOR_SURFACES`, which is unchanged. However, the label `candidate_measured` is ambiguous and could mislead a future reviewer reading the gate output in isolation. Consider renaming it `candidate_gate_passed` in the gate script on the next convenient pass.

---

### Explicit Non-Authorization Boundaries (confirmed, not extended)

This review does not authorize and finds no evidence that the implementation has claimed:

- Measured-catalog promotion
- V4 release or release-candidate status
- Broad V4 speedup claims
- Whole-application speedup claims
- True-zero-copy wording (`true_zero_copy_authorized: False` in claim boundary and all POD metadata)
- OptiX 9.1 scope (`validated_optix_abi: None` in the claim boundary; `optix_9_1_validated: False`)
- CuPy performance claims (CuPy path raises `RuntimeError` at `v4_ray_triangle.py:463` and returns no `api_surface` from the planner)
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- App-specific native kernels
