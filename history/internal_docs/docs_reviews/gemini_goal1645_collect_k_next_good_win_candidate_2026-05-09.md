I've investigated the `COLLECT_K_BOUNDED` performance bottleneck on the `row_width=2` subpath for OptiX. The bottleneck primarily lies in memory bandwidth and latency during the merge and final materialization steps. 

I propose the following two optimizations to hit the 1.3x-1.5x performance target:

1.  **128-bit Vector Loads:** Replace individual 64-bit pair loads with a custom 16-byte aligned type (`struct __align__(16) CollectKLongLong2`). This allows the PTX compiler to emit 128-bit `LDG.E.128` instructions, effectively halving the global memory transactions during the heavily utilized binary search steps (`collect_k_final_lower_bound` / `collect_k_final_upper_bound`) and materialization routines.
2.  **Merge Loop Register Caching:** In the sequential merge kernels (`collect_k_bounded_i64_row_width2_merge_level` and `merge_two`), the current `while` loop re-loads both `first` and `second` values from global memory on every iteration, resulting in O(N) redundant loads. We can cache the active pair in local registers and only load the next element from global memory when advancing the corresponding index.

Does this strategy sound good to you? Once you confirm, I will draft the implementation plan.
