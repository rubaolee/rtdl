Now I have enough detail to evaluate all three questions against the actual code. Let me write the review.

---

## Review: goal1569 carry alias design

### Verdict

The report's core invariant claim is **correct**. The unsafe-shortcut section accurately describes the failure mode. Design A is a **reasonable but incomplete** first diagnostic. Several implementation-level caveats are missing that could cause silent bugs or misleading measurements.

---

### Agreement: Invariant Claim

The claim holds exactly as stated. The derived-descriptor kernels (`rtdl_optix_core.cpp:2446–2447`) compute segment addresses as:

```cuda
current_base + (pair_index * 2)     * segment_capacity * 2   // first segment
current_base + (pair_index * 2 + 1) * segment_capacity * 2   // second segment
```

The carry copy at `rtdl_optix_api.cpp:1611` places the carry at:

```cpp
output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_count
```

This is the exact derived position the next level's kernel expects. Aliasing `current_rows.back()` directly would point to a location in the *previous* level's source buffer at the *previous* level's stride — neither the address nor the stride matches what the next derived kernel computes. The invariant break is real.

---

### Agreement: Design A as Diagnostic

Design A is a sound first experiment because:

- The non-derived pointer-descriptor path already exists and has distinct kernel variants (`collect_k_bounded_i64_row_width2_final_materialize_level`, `rtdl_optix_core.cpp:2386–2429`; compact variant at `2947–2986`). No new kernel code is required for the diagnostic.
- Switching the whole odd level to pointer mode avoids the mixed-addressing propagation problem that Design B inherits.
- The regression guard (131072 must stay on the derived path) is the correct control.

The "Con" about giving back metadata savings is real but unquantified. Design A measures whether that tradeoff is net positive on 65537 — that is the right thing to measure.

---

### Caveats Before Coding

**1. The count copy is not eliminated by Design A.**
The carry count `cuMemcpyDtoD` at `rtdl_optix_api.cpp:1621–1622` copies 8 bytes and remains necessary even with row aliasing. The profiled `0.035588 ms` across five carry copies is row-data dominated, but the diagnostic code must still issue the count copy. Missing it silently drops the device count for the last segment at the aliased level and will produce wrong merge results.

**2. Pointer array upload cost must be measured, not assumed negligible.**
Switching a level to pointer mode requires uploading `first_row_ptrs[]`, `second_row_ptrs[]`, and `output_row_ptrs[]` to device — three arrays of `pair_count * 8` bytes each, plus synchronization. For the `65537` case this is small, but the measurement must be explicit; the upload latency should appear in the reported per-level timing, not hidden inside async launch overhead.

**3. Verify pointer-path kernel activation coverage.**
The pointer-descriptor variants may not be exercised in the current fastest path. Before using them for the diagnostic, confirm that the `use_device_level_counts` branch correctly selects the counts-aware pointer kernel (not the non-counts variant), and that the kernel compiles and produces correct output on a trivial no-carry case before running the carry alias experiment.

**4. Segment capacity mismatch requires correct count at the aliased slot.**
The carry segment from level L has capacity `segment_capacity_L`; level L+1 uses `output_segment_capacity_{L+1} = 2 * segment_capacity_L`. The pointer-descriptor kernel reads the count from `current_counts_level_device[pair_count]`. If the diagnostic omits the count copy (see caveat 1), the pointer kernel will read a stale or zero count for the aliased segment and silently produce a truncated or empty merge output.

**5. Output slot for the aliased carry pair is still derived.**
In Design A the *outputs* of all pairs at the odd level are written into the output stage at derived positions — the output is fully derived regardless of whether inputs are pointer-addressed. This is correct and means level L+2 can revert to full derived mode. This implicit return to derived mode should be stated explicitly in the implementation notes so a future reader doesn't assume pointer mode must propagate forward.

**6. Both kernel variants (materialize and compact) must be switched together.**
The merge path uses both a materialize kernel and a compact kernel for each level. Design A must switch both to their pointer-descriptor variants for the odd level. Switching only materialize while leaving compact on the derived path will silently misaddress compact outputs.

---

### Recommendation

Proceed with Design A as a diagnostic. Before writing any code:

1. Add explicit per-level timing probes that separate row-copy cost, count-copy cost, and pointer-array upload cost. The current `carry_copy_ms` aggregate conflates all three.
2. Write a correctness-only test first: run the pointer-descriptor path on a level with no carry, compare output against the derived path. This de-risks the kernel variant switch before introducing the alias.
3. Keep the count copy unconditional in Design A — it is cheap and its absence is a silent correctness hazard.
4. Do not advance to Design B or C until Design A measurements on `65537` and `131072` are recorded and the pointer-array upload overhead is characterized.
