# Goal 398 Review: v0.6 Vulkan RT Graph Mapping And Triangle Closure

Reviewer: Claude Sonnet 4.6
Date: 2026-04-14

---

## Verdict

**Accept as a bounded closure with one named caveat.**

The implementation delivers a complete, honest Vulkan ABI path for `triangle_count` with
parity-tested dispatch and a clean test surface. The bounded scope is respected and
well-documented. The one caveat — that `run_triangle_probe_vulkan_host_indexed` performs
no GPU computation — is accurately named and consistent with the precedent set by Goal 395
BFS, but must remain visible as a hard limit on what "Vulkan triangle probe" means today.

---

## Findings & Evaluation

### 1. Is the implementation genuinely Vulkan-specific rather than a disguised oracle fallback?

Partially — and honestly so. `run_triangle_probe_vulkan_host_indexed`
(`rtdl_vulkan_core.cpp:3506`) is a pure C++ host-side CSR traversal using a stamp-based
neighbor-marking algorithm. It allocates no Vulkan device buffers, invokes no SPIR-V
shaders, and calls no Vulkan API functions. Structurally it is identical in kind to the
oracle/CPU reference path.

What separates it from a disguised fallback:

- It lives behind the `rtdl_vulkan_*` C ABI, not a Python-level oracle redirect.
- The function name carries the `_host_indexed` qualifier, which is explicit about the
  absence of GPU execution.
- The report (`goal398_v0_6_vulkan_rt_graph_mapping_and_triangle_closure_2026-04-14.md`)
  repeats this language precisely: "native host-indexed Vulkan helper over the graph CSR
  inputs, not as a disguised oracle fallback."

This is a legitimate bounded scope, not misrepresentation. The same pattern was accepted
for Goal 395 BFS. Accepting it here is consistent.

**Minor concern:** the `unique` deduplication path inside the loop
(`rtdl_vulkan_core.cpp:3588`) is O(n²) — `std::any_of` over the entire accumulated
`rows` vector for each candidate. This is harmless for the micro-graphs in the test suite
but would degrade badly at scale. This should be tracked as a future limitation, not a
blocker for this bounded closure.

### 2. Is the runtime/API boundary honest about the host-indexed limitation?

Yes. Three independent signals confirm it:

- The C implementation function is named `run_triangle_probe_vulkan_host_indexed`.
- The ABI entry point (`rtdl_vulkan_api.cpp:250`) calls that name without aliasing.
- The Python dispatch (`vulkan_runtime.py:742`) routes to the symbol
  `rtdl_vulkan_run_triangle_probe` with no silent fallback to the oracle at runtime.

The prelude header (`rtdl_vulkan_prelude.h`) lists the public ABI surface correctly and
includes `rtdl_vulkan_run_triangle_probe` alongside the BFS entry point. No hidden
re-routing is present.

### 3. Are the tests appropriate for this bounded closure?

Yes. The four tests in `goal398_v0_6_rt_graph_triangle_vulkan_test.py` cover the right
surface:

| Test | What it verifies |
|---|---|
| `test_run_vulkan_matches_python_reference_for_triangle_probe` | Output parity vs. CPU reference on a complete triangle graph |
| `test_run_vulkan_matches_oracle_for_triangle_probe` | Output parity vs. oracle on a single-seed subcase |
| `test_prepare_vulkan_accepts_graph_triangle_kernel` | `PreparedVulkanKernel` API surface and correct row emission |
| `test_run_vulkan_rejects_invalid_seed_vertex` | Error propagation for out-of-bounds seed |

The `@skipUnless(vulkan_available())` guard is applied correctly at class level. Skipping
when the runtime is absent is the right local behavior; parity is still proven through
the Python and oracle paths in sibling test modules (Goals 390, 392, 396, 397).

The test graph (`row_offsets=(0,2,4,6,6), column_indices=(1,2,0,2,0,1)`) is a complete
triangle K₃ with an isolated vertex — an appropriate minimal structure to exercise the
common-neighbor intersection logic.

### 4. CSR validation quality

The validation in `run_triangle_probe_vulkan_host_indexed` (`core.cpp:3519-3545`) is
thorough: it checks null pointers, non-decreasing offsets, the invariant
`row_offsets[last] == edge_count`, and that all column indices are valid vertex IDs.
This matches the validation level in the BFS path and is correct for a bounded graph
closure.

---

## Conclusion

Goal 398 is a clean, honest bounded closure. The Vulkan `triangle_count` ABI path exists,
is correctly wired through `PreparedVulkanKernel` and `run_vulkan`, passes parity tests
against both the Python reference and the oracle, and validates inputs defensively. The
`_host_indexed` naming convention accurately discloses that no GPU execution occurs for
this workload. The O(n²) uniqueness check is a noted future limitation, not a defect
within the bounded scope. Accept.