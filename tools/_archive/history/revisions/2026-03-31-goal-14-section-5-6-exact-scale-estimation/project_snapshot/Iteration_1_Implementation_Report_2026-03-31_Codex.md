# Iteration 1 Implementation Report

Date: `2026-03-31`
Author: `Codex`

## What Was Added

- a focused Goal 14 plan:
  - [goal_14_section_5_6_exact_scale_plan.md](/Users/rl2025/rtdl_python_only/docs/goal_14_section_5_6_exact_scale_plan.md)
- a generated estimation report:
  - [goal_14_section_5_6_exact_scale_estimation_2026-03-31.md](/Users/rl2025/rtdl_python_only/docs/reports/goal_14_section_5_6_exact_scale_estimation_2026-03-31.md)
- a reproducible generator:
  - [generate_goal14_section56_estimation.py](/Users/rl2025/rtdl_python_only/scripts/generate_goal14_section56_estimation.py)
- a status note in Goal 13:
  - [goal_13_rayjoin_paper_embree_plan.md](/Users/rl2025/rtdl_python_only/docs/goal_13_rayjoin_paper_embree_plan.md)

## Core Conclusion

The current RTDL implementation does **not** yet support a trustworthy exact-size repetition of RayJoin Section 5.6 on this 16 GiB Mac.

The main blockers are:

- Python-side materialization of millions of polygon / segment / point objects,
- likely memory pressure or swap at the upper paper-scale sizes,
- and very long `pip` query-time estimates even before data-construction and Embree-build costs are included.

## Key Quantitative Summary

- estimated total `lsi` query wall time for the full exact-scale paper-style run:
  - about `1.01 h`
- estimated total `pip` query wall time for the full exact-scale paper-style run:
  - about `55.70 h`
- estimated combined query-only wall time:
  - about `56.71 h`

These numbers are intentionally framed as optimistic lower bounds because they exclude generation, build, serialization, and thermal-throttling costs.

## Review Ask

Gemini should review whether:

- the estimate is technically honest,
- the memory/feasibility conclusion is justified,
- the CPU-vs-GPU comparison guidance is sound,
- and Goal 14 can be accepted as an estimation/report goal.
