# Claude Handoff: Hidden-Star Demo Review

Please review the newly adopted hidden-star stable Earth demo slice for correctness, regressions, maintainability, and repo-surface honesty.

## Scope

Focus on these files:

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal168_hidden_star_stable_ball_demo_test.py`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_milestone_qa.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/tests/goal187_v0_3_audit_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal168_hidden_star_stable_rtdl_shadow_demo_2026-04-09.md`

## Context

This repo previously treated the smooth-camera orbit demo as the primary 3D demo source.

A new Windows-produced bundle was imported and adopted instead:

- hidden star behind Earth
- Earth fixed
- star itself hidden
- visible effect is the moving lit region across Earth
- RTDL is used for both:
  - primary camera hit queries
  - shadow visibility queries

The stability design change is:

- old unstable shadow construction:
  - surface point -> light
- new accepted construction:
  - light -> surface point

This keeps RTDL in the shadow stage while avoiding the earlier self-shadow instability.

The repo surface was updated so this hidden-star source is now the main 3D demo source, while the smooth-camera line remains preserved as a comparison path.

## What To Check

Please prioritize:

1. real bugs or regressions
2. misleading repo-surface/doc changes
3. maintainability problems in the new demo source
4. mismatch between the claimed RTDL/Python boundary and what the code actually does

Please be explicit if:

- the new demo is structurally sound
- the tests are too weak
- the doc/front-door switch is misleading
- the imported code still carries wrong path assumptions or stale design assumptions

## Required Output

Write your response to:

- `/Users/rl2025/rtdl_python_only/docs/reports/claude_hidden_star_demo_review_2026-04-09.md`

Use exactly three short sections titled:

1. `Verdict`
2. `Findings`
3. `Summary`
