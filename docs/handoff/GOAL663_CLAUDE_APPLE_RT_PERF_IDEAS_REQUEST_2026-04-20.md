# Goal663 Claude Request: Apple RT Performance Ideas

Please review the current RTDL Apple Metal/MPS RT any-hit performance work and write a concise technical review plus concrete next-step ideas for increasing Apple RT engine performance for the RTDL language/runtime.

Read these files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal662_apple_rt_anyhit_performance_optimization_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal661_mac_visibility_collision_longrun_10s_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal659_mac_visibility_collision_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal659_mac_visibility_collision_perf_test.py`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_prelude.mm`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_mps_geometry.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`

Output file:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal663_claude_apple_rt_perf_ideas_2026-04-20.md`

Required review content:

1. Confirm whether the current Apple RT path is genuinely Metal/MPS RT-backed.
2. Confirm whether the current claim is honest: faster than Shapely/GEOS on the measured app benchmark, but still slower than Embree.
3. List performance ideas in priority order, separating low-risk implement-now ideas from speculative or research-heavy ideas.
4. Identify correctness risks for each idea.
5. Recommend exactly one next implementation step that Codex should attempt first.

Do not claim Apple RT beats Embree unless supported by the measured evidence.
