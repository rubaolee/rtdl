# Claude Review — Goal4807 Authorization

Date: 2026-06-30

Verdict:

`approve_goal4807_read_only_api_map_from_clean_v4_checkout`

Scope:

- Authorization is limited to Goal4807 only.
- Goal4807 is read-only.
- No user app implementation is authorized.
- No POD run is authorized.
- No RTDL runtime/source edits are authorized.
- No edits to `src/rtdsl/**`, `src/native/**`, or the `v4.0.0` tag are
  authorized.

Required Goal4807 first action:

1. Create a fresh clean `v4.0.0` checkout.
2. Record full clean-environment proof:
   - `git rev-parse HEAD` must equal `6ca0849b9930295f742485cae9a17196216e0dcf`.
   - `git status --porcelain` must be pasted in full and must be empty.
   - import path / `PYTHONPATH` proof must show no imports from the dirty main
     development worktree.
3. Produce a read-only API map for RayJoin Section 5.7.
4. For every Section 5.7 stage, classify the released callable status as one of:
   - `generic_rtdl_operator`
   - `numba_user_continuation`
   - `bundled_rayjoin_helper`
   - `author_or_v214_baseline`
   - `missing_released_capability`
5. Keep `blocked_by_released_rtdl_capability_gap` as a live and likely outcome.

Non-authorization:

- Do not implement `Goal4808`.
- Do not run POD performance tests.
- Do not patch RTDL.
- Do not claim that bundled `rayjoin_overlay` / `rayjoin_paper_suite` proves
  generic RTDL language reproduction.

