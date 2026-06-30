# Windows Codex Start Here

Use this file as the first entry point on the Windows machine.

## Paths

- Refresh/context file:
  - `C:\Users\lestat\Desktop\refresh.md`
- Working repo copy:
  - `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop`
- Main work handoff:
  - `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\docs\handoff\WINDOWS_CODEX_RT_V0_6_CONTINUATION_HANDOFF_2026-04-14.md`
- Current consolidated report:
  - `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\docs\reports\v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md`

## Required startup order

1. Open and read `C:\Users\lestat\Desktop\refresh.md`.
2. Open the repo at `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop`.
3. Read `WINDOWS_CODEX_RT_V0_6_CONTINUATION_HANDOFF_2026-04-14.md`.
4. Read `v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md`.
5. Continue work from the copied repo state, not from public Git.

## Important context

- Public Git was rolled back earlier and is not the authoritative source for the corrected RT `v0.6` branch state.
- The copied desktop repo contains the current corrected RT work.
- Read `refresh.md` after compaction or restart before substantial work.
- Do not commit or push yet. Finish the current version work first, then decide the Git/branch action explicitly.

## Current task

Fix the large-batch Embree `triangle_count` correctness bug.

Current known facts:

- Large-batch BFS is correct:
  - Windows Embree matches Linux PostgreSQL exactly.
- Large-batch triangle is incorrect on Embree:
  - Windows CPU truth matches Linux PostgreSQL.
  - Windows Embree matches Linux Embree.
  - Therefore the bug is in the Embree triangle path.

Known hashes for the failing large-batch triangle case:

- Correct truth / PostgreSQL hash:
  - `17c12026dd9af23b12d979f41c77bc5fa406cc5c4bc2641bf423d72094693ff8`
- Incorrect Embree hash:
  - `1112c342267382b12eadcf5db3b6e11aa10a3528a9e3b832a557b67df4fb9779`

Likely fix surfaces:

- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/rtdsl/embree_runtime.py`

## Do not assume

- Do not assume public `main` or public tags contain this corrected RT work.
- Do not claim large-batch triangle correctness is closed until Embree matches truth again.
- Do not create commits or push from Windows unless explicitly instructed after this version is finished.
