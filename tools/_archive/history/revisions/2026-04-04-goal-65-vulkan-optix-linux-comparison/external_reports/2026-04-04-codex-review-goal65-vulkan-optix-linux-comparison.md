# Codex Review: Goal 65 Vulkan OptiX Linux Comparison

Date: 2026-04-04

Verdict: `APPROVE`

## What I reviewed

- `/Users/rl2025/rtdl_python_only/scripts/goal65_vulkan_optix_linux_comparison.py`
- `/Users/rl2025/rtdl_python_only/tests/goal65_vulkan_optix_linux_comparison_test.py`
- `/Users/rl2025/rtdl_python_only/docs/goal_65_vulkan_optix_linux_comparison.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal65_vulkan_optix_linux_comparison_plan_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal65_vulkan_optix_linux_comparison_2026-04-04.md`
- remote artifact:
  - `/Users/rl2025/rtdl_python_only/build/goal65_summary_remote.json`

## Key checks

1. The harness now measures GPU backends fairly:
   - `prepare`
   - one explicit `cold` run
   - one explicit `warm` run
2. The report correctly treats the native C oracle as the correctness reference.
3. The report correctly narrows the comparison surface where Vulkan cannot fit:
   - whole `County ⊲⊳ Zipcode top4` `lsi`
   - `BlockGroup ⊲⊳ WaterBodies county2300_s06` and larger `lsi`
4. The report does not overclaim Vulkan. It explicitly concludes that Vulkan is
   still provisional and not ready to join the accepted bounded closure set.

## Main conclusion

This is a valid completed comparison round with a negative Vulkan result:

- OptiX remains parity-clean across the Goal 65 surface.
- Vulkan runs on the Linux host, but is only partially parity-clean.
- On the workloads where both GPU backends are parity-clean, OptiX warm runtime
  is consistently better than Vulkan warm runtime.

That is an honest and publishable result.
