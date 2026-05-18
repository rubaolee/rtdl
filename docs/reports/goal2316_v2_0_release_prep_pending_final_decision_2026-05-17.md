# Goal2316 v2.0 Release Prep Pending Final Decision

## Purpose

Prepare the v2.0 release lane after the RayJoin-style project closure, while
explicitly waiting for the user's final release decision. This is not a tag,
version bump, publish step, or announcement.

## Current State

| Area | Status |
| --- | --- |
| Native engine boundary | App-agnostic release surface remains the governing rule. |
| Python+partner+RTDL architecture | Protocol-first, with PyTorch/CuPy partner paths and Python app orchestration. |
| Learner docs | Reorganized around a current v2.0 pre-release surface, with older history routed away from the normal learner path. |
| Tutorial/docs validation | Earlier tutorial pod validation exists; current release prep keeps source-tree usage only. |
| v2.0 perf matrix | Existing post-streaming-witness packet remains the main all-app OptiX/RT release-prep matrix. |
| RayJoin-style project | Closed for v2.0 with boundary by Goal2315; future work moved to `docs/research/future_version_to_do_list.md`. |
| External review | Goal2314 adds fresh Gemini review for the final RayJoin delta; final v2.0 release consensus still requires the strict release-rule review packet over current head. |

## Release Candidate Position

The repository can be presented as a v2.0 pre-release candidate awaiting final
authorization. The correct public wording is:

- "RTDL v2.0 is a Python+partner+RTDL pre-release candidate."
- "The RayJoin-style LSI/PIP research lane is closed for v2.0 with bounded
  same-query evidence."
- "Final v2.0 release waits for the user's explicit decision and the required
  final release consensus over current head."

## Do Not Do Yet

- Do not create or move a release tag.
- Do not publish a release announcement.
- Do not change version files to say v2.0 is released.
- Do not claim RTDL beats RayJoin.
- Do not claim broad RT-core speedup, arbitrary PyTorch/CuPy acceleration,
  package-install support, or true zero-copy beyond measured slices.

## Final Pre-Button Checklist

Before the actual v2.0 release button is pressed:

1. Run the focused v2.0 release-prep test slice from current `origin/main`.
2. Obtain the final required external review packet over current head.
3. Write the final 3-AI v2.0 release consensus file, with distinct external AI
   families under the standing redline.
4. Confirm the user explicitly authorizes the release action.
5. Only then perform the tag/version/publish operation requested by the user.

## Verdict

`prepared-waiting-final-decision`

The engineering/research cleanup requested here is complete enough to stop
working on RayJoin for v2.0 and shift into final release-prep mode. The last
release step remains intentionally unpressed.
