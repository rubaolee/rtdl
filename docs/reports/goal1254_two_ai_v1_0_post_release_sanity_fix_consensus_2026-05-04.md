# Goal1254 Two-AI Consensus: v1.0 Post-Release Sanity Fix

Date: 2026-05-04

Status: `ACCEPT`

## Scope

Goal1254 corrects one public quickstart defect found after the `v1.0` tag was
pushed: the root `README.md` included `python3 -m pip install -e .`, but the
repository has no `setup.py` or `pyproject.toml`.

## Inputs

- Codex report:
  `docs/reports/goal1254_v1_0_post_release_sanity_fix_2026-05-04.md`
- Gemini review request:
  `docs/reports/goal1254_gemini_v1_0_post_release_sanity_fix_review_request_2026-05-04.md`
- Gemini review:
  `docs/reports/goal1254_gemini_v1_0_post_release_sanity_fix_review_2026-05-04.md`

## Consensus Verdict

`ACCEPT`

Codex and Gemini agree that:

- removing `python3 -m pip install -e .` from the root quickstart is technically
  correct for the current v1.0 repo state;
- the supported v1.0 usage contract is source-tree execution with
  `PYTHONPATH=src:.`;
- the regression test in
  `tests/goal646_public_front_page_doc_consistency_test.py` correctly prevents
  reintroducing the unsupported editable-install instruction before packaging
  metadata exists;
- the fix does not change any RT-core, Embree, Vulkan, HIPRT, Apple RT,
  speedup, or app-support claim;
- this is acceptable as a post-release `main` documentation fix without moving
  or retagging `v1.0`.

## Boundary

This consensus authorizes committing and pushing the Goal1254 documentation fix
to `main`. It does not authorize moving the existing `v1.0` tag, creating a new
release, adding packaging claims, or changing any public performance wording.
