# Goal 388 Review: v0.6 RT Graph Lowering And Runtime Contract

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_388_v0_6_rt_graph_lowering_runtime_contract.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal388_v0_6_rt_graph_lowering_runtime_contract_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal388_v0_6_rt_graph_lowering_runtime_contract_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal388_v0_6_rt_graph_lowering_runtime_contract_review_2026-04-14.md`

## Verdict

Goal 388 is accepted.

The contract is now explicit enough to guide real implementation:

- lowering preserves graph-aware kernel semantics
- runtime owns CSR normalization plus RT preparation
- host owns outer algorithm state and loops
- backend hooks remain narrow and backend-independent
- backend equivalence is defined at the bounded graph-step semantic level

## External Consensus

Gemini approved the goal and confirmed that the lowering/runtime split preserves
the RTDL kernel model while keeping the host/runtime/backend boundary honest.

Claude also accepted the goal, with one useful tightening request:

- define "semantically equivalent" more concretely in the backend hook contract

That tightening is now reflected in the report.

## Next Dependency

The next correct goals are the first bounded truth-path closures for the RTDL
graph kernel form:

- Goal 389: RT-kernel `bfs` truth-path closure
- Goal 390: RT-kernel `triangle_count` truth-path closure
