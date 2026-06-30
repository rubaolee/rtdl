# Goal4806 Claude Review Erratum Response

Date: 2026-06-30

Claude verdict:

`block_handoff_until_runtime_modification_path_is_fully_excluded`

The verdict is accepted.

## What Was Correct In Claude's Review

Claude identified two blocking issues that must control any future Goal4806
work.

### 1. Clean-tree claims are not enough

The prior handoff stated that cleanup left only the archive directory untracked.
That statement must not be used as proof that the main worktree is a valid
released-V4 test environment.

Future Goal4806 work must use a separate clean `v4.0.0` checkout and record:

- exact commit `6ca0849b9930295f742485cae9a17196216e0dcf`;
- empty `git status --porcelain`;
- no imports from the dirty development tree.

### 2. Built-in RayJoin modules create circular evidence

Released RTDL contains RayJoin-specific modules:

- `src/rtdsl/rayjoin_overlay.py`
- `src/rtdsl/rayjoin_paper_suite.py`
- `src/rtdsl/rayjoin_artifacts.py`
- `src/rtdsl/v2_13_rayjoin_authors_code_packet.py`

Using these modules may be useful for compatibility, but it does not by itself
prove that a user can compose RayJoin Section 5.7 from generic RTDL language
features.  A future app must classify calls into:

- generic RTDL primitive/operator;
- partner/Numba user continuation;
- bundled RayJoin-specific helper;
- author/V2.14 baseline helper.

Only the generic and partner/user-continuation categories support the language
claim.  The bundled RayJoin helper category supports only "RTDL ships a RayJoin
compatibility helper."

## Current Local Recheck

This section is superseded by Claude's second review and must not be cited as
clean-tree evidence.

Claude rechecked the shared tree and reported a contradictory dirty runtime
state, including modified files under `src/native/**` and `src/rtdsl/**`.
Whether that reflected a different worktree view, a later/earlier tree state, or
selective status output, the conclusion is the same:

- the main development worktree is not accepted as Goal4806 evidence;
- any prior local "clean" statement is not authoritative;
- only a fresh `v4.0.0` checkout created inside Goal4807 can prove the released
  environment.

Goal4807 must paste the full output of its own clean-check commands, not inherit
or summarize this paragraph.

## Required Amendment To Future Goal4807

Goal4807 must be read-only and must run against a clean `v4.0.0` checkout.  It
must not implement anything.  Its output must answer:

1. Which Section 5.7 stages can be expressed by generic released RTDL/V4
   surfaces?
2. Which stages only work by calling bundled RayJoin-specific modules?
3. Which stages require missing released capabilities?
4. Does released V4.0.0 support a real V4+Numba user implementation, or is the
   honest result `blocked_by_released_rtdl_capability_gap`?

Standing rule for all Goal4806 follow-up work:

- no edits to `src/rtdsl/**`;
- no edits to `src/native/**`;
- no edits to the `v4.0.0` tag or release contents;
- missing released capability is recorded as a product gap, not patched inside
  Goal4806.

No POD run is authorized until Goal4807 resolves this classification.
