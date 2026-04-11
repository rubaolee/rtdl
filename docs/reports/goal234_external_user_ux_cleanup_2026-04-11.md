# Goal 234 Report: External User UX Cleanup

Date: 2026-04-11
Status: implemented

## Summary

An external fresh-clone user audit found that the CPU-first path was real, but
the public release-prep docs still had three concrete problems:

- mixed `python` / `python3` command conventions on beginner-facing pages
- public nearest-neighbor example docs overclaimed `optix` and `vulkan`
  backends that the public top-level example CLIs do not expose
- the public workload cookbook still leaked maintainer-local absolute paths

This goal fixes those issues directly in the public docs.

## External Audit Preserved

Source audit path reported by the external reviewer:

- `C:\\Users\\Lestat\\Desktop\\work\\rtdl_v0_4_release_prep_review\\docs\\reports\\v0_4_external_user_experience_audit_2026-04-10.md`

Key accepted findings from that audit:

- fresh-clone CPU-first path works
- public docs still need command-style cleanup
- public nearest-neighbor example docs should not claim unsupported
  `optix` / `vulkan` CLI flags
- maintainer-local paths should not appear in public cookbook docs

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/quick_tutorial.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/tutorials/hello_world.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/tutorials/nearest_neighbor_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/rtdl/workload_cookbook.md`

## What Changed

- switched the public onboarding/tutorial commands from `python3` to `python`
- added a Windows `cmd.exe` block to the quick tutorial second-run section
- narrowed the public nearest-neighbor CLI backend claims to what the scripts
  actually expose today
- kept the runtime/backend truth explicit:
  - OptiX and Vulkan closure exists
  - but not through the current public top-level nearest-neighbor CLIs
- removed maintainer-local absolute paths from the workload cookbook

## Outcome

The external-user release-prep issues are reduced from vague polish concerns to
cleared or explicitly bounded documentation points.
