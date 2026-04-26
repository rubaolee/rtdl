# Goal 673 External Review — Claude

Date: 2026-04-20
Reviewer: Claude via CLI

## Verdict

APPROVED.

Claude returned this verdict summary:

> All five Goal673 claims verified.

Verified points:

- Host ray storage removed: `PreparedRays2D` holds only `ray_count` plus `DevPtr d_rays`; the host `std::vector<GpuRay>` is stack-local and freed after GPU upload.
- C ABI null guards added: output pointers and pointer/count pairs are null-checked at the ABI surface; the prepared scene handle is guarded one level inside, which is defensible and does not create crash risk.
- Closed-buffer lifecycle test added: `test_closed_prepared_ray_buffer_is_rejected` covers this path.
- Linux native correctness preserved: `ensure_ray_anyhit_2d_pipeline()` refactor is a behavioral no-op and `run_ray_anyhit_optix` remains unchanged.
- Goal672 boundary unchanged: `g_rayanyhit_count` is separate from `g_rayanyhit`; the row-output path is untouched.

Non-blocking notes:

- `PreparedRayAnyHit2D` still retains a host triangle copy after construction; this is a follow-up memory-footprint opportunity.
- There is no test for calling `count()` on a closed scene handle; the guard exists but is uncovered.
