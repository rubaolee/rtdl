# Goal 464: v0.7 Linux Fresh-Checkout Validation

Date: 2026-04-16

## Purpose

Validate the current v0.7 DB package from a fresh Linux checkout after the
post-demo pre-stage refresh.

## Scope

This goal must:

- sync the current worktree to a clean Linux validation directory
- verify Python import and PostgreSQL availability
- build missing fresh-checkout backend libraries for OptiX and Vulkan
- verify Embree, OptiX, and Vulkan runtime availability from the fresh checkout
- run focused v0.7 DB correctness tests, including PostgreSQL-backed tests
- run the v0.7 DB app-level and kernel-form demos
- run fresh Linux RTDL and PostgreSQL performance evidence
- keep staging, commit, tag, push, merge, and release authorization false
- receive 2-AI consensus before closure

## Acceptance Criteria

- Fresh Linux checkout imports `rtdsl`.
- Embree, OptiX, and Vulkan runtime probes succeed after required fresh-checkout
  builds.
- PostgreSQL accepts local connections and Python `psycopg2` can connect.
- Focused v0.7 DB correctness tests pass.
- App-level and kernel-form v0.7 DB demos run on Linux.
- Fresh performance artifacts are saved under `docs/reports/`.
- The report states the Linux GPU caveat honestly.
- The git index remains empty.
