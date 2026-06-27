# Goal2786 Batched Vector-Sum Offsets Review

## Verdict: `accept-with-boundary`

The work in Goal2786 is well-documented, tested, and aligns with the stated goals of providing a generic, atomics-free batched vector-sum offset kernel. Crucially, it honestly reports negative performance findings (batched values were slower than single-group offsets, and Triton is still slower than Torch), and correctly updates all guidance to reflect these findings, preventing any unwarranted auto-selection or performance claims. The explicit blocking of public speedup, RT-core speedup, true-zero-copy, whole-app, and v2.5 release claims is consistently enforced across all relevant files, including the report, code, and tests.

## Review Questions:

### 1. Does Goal2786 keep the vector-sum continuation generic, without embedding Barnes-Hut, N-body, or force-law application logic?
**Answer:** Yes, Goal2786 explicitly states and implements the vector-sum continuation as generic, focusing solely on vector reduction tuning without embedding Barnes-Hut, N-body, or force-law application logic. This is reinforced in the report's purpose and boundary, the `v2_5_triton_app_migration.py` comments for Barnes-Hut, and the generic nature of the implemented Triton kernel.

### 2. Does the batched row-offset kernel remain atomics-free and correctness-tested against the Torch same-contract branch?
**Answer:** Yes, the batched row-offset kernel (`_triton_grouped_vector_sum_f64x2_offsets_batched_kernel`) remains atomics-free. This is verified by explicit test assertions checking for the absence of `tl.atomic_add` within the kernel. Correctness is tested and confirmed against the Torch same-contract branch using `torch.allclose` in the provided test suite.

### 3. Is the pod timing evidence interpreted honestly, especially that `groups_per_program=1` remained best and all batched values were slower?
**Answer:** Yes, the pod timing evidence is interpreted honestly. The report clearly states that `groups_per_program=1` remained the best performing configuration, and all other batched values were slower. The raw pod artifact JSON data directly supports this conclusion, showing the `groups_per_program=1` consistently having the lowest median execution time and the highest speedup ratio over Triton atomic, while still being slower than Torch. The test suite also explicitly verifies these claims from the report against the artifact.

### 4. Does the partner-selection/app-migration guidance correctly keep Triton auto-selection blocked for dense grouped vector sums after Goal2786?
**Answer:** Yes, the partner-selection and app-migration guidance explicitly and correctly keeps Triton auto-selection blocked for dense grouped vector sums after Goal2786. Both `v2_5_partner_selection_guidance.py` and `v2_5_triton_app_migration.py` contain clear recommendations and notes, backed by test cases, that prevent auto-selection due to Triton's performance being slower than Torch for this specific operation.

### 5. Are public speedup, RT-core speedup, true-zero-copy, whole-app, and v2.5 release claims still blocked?
**Answer:** Yes, all public speedup, RT-core speedup, true-zero-copy, whole-app, and v2.5 release claims remain explicitly blocked. This is consistently stated in the Goal2786 report's "Boundary" section, confirmed in the pod artifact's `claim_boundary` fields, enforced by validation logic in the `v2_5_partner_selection_guidance.py` and `v2_5_triton_app_migration.py` files (both at initialization and during validation checks), and verified by the test suite. The `future_version_to_do_list.md` also reiterates these blocks for related future work.
