# Local Workspace Debris Archive

Date: 2026-06-27

Purpose: keep old, untracked local work products out of the current V4 public
release surface without deleting them. This archive is not part of the V4 user
path and should not be cited as release documentation.

The `payload/` directory is ignored by Git on purpose. It may contain untracked
V3/Phoenix helper scripts, local review helpers, and paper-reproduction patches
that were visible at the repository front door before this cleanup pass.

Release rule: current user-facing V4 material lives in `README.md`, `docs/`,
`tutorials/current/`, and `examples/v4/`. Historical and audit material must
stay in `history/` or `future/v4/` and must not leak into the first-time user
path.
