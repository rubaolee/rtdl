# Local Workspace Debris Archive

Date: 2026-06-27

Purpose: keep old, untracked local work products out of the current V4 public
release surface without deleting them. This archive is not part of the V4 user
path and should not be cited as release documentation.

The `payload/` directory is ignored by Git on purpose. It contains local
release-excluded work products that were visible in the workspace before this
cleanup pass, including old V3/Phoenix helpers, old local tests, external
checkouts, paper-reproduction patches, and helper scripts that are not required
by the V4 test or release-evidence contract.

Some V4 review/evidence/package artifacts were restored from this payload and
tracked after the initial sweep revealed that the current V4 verification suite
depends on them. That is intentional: test-contract evidence belongs in
`future/v4/` or `dist/`, not in ignored local-only payload storage.

Release rule: current user-facing V4 material lives in `README.md`, `docs/`,
`tutorials/current/`, and `examples/v4/`. Historical and audit material must
stay in `history/` or `future/v4/` and must not leak into the first-time user
path.
