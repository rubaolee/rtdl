# Goal1231 Two-AI Consensus: Front-Page Simplification

Date: 2026-05-03

Participants:

- Codex
- Gemini CLI

## Decision

VERDICT: ACCEPT

## Consensus

The root `README.md` should function as a clean public landing page, not as a
full goal-history report. The Goal1231 rewrite is accepted because it reduces
the front page from a dense report dump to a concise entry point while
preserving the required public facts:

- current released version: `v0.9.8`
- explicit `v1.0`/`v1.5`/`v2.0` positioning
- strict NVIDIA RT-core claim boundaries
- `12 reviewed` bounded RTX sub-path rows
- blocked/not-reviewed public wording states
- links to support matrices, app inventory, and detailed evidence reports

The updated tests are accepted. They keep the public-claim honesty checks while
removing brittle line-wrap assumptions and adding a direct guard that the root
README remains a landing page.

## Verification

Focused public-doc and README boundary tests passed:

```bash
python3 -m unittest \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal1228_v1_0_positioning_docs_test \
  tests.goal1230_v1_0_app_acceleration_inventory_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal1221_v0_9_8_release_action_test \
  tests.goal508_hausdorff_perf_doc_refresh_test \
  tests.goal510_app_perf_doc_refresh_test \
  tests.goal506_public_entry_v08_alignment_test \
  tests.goal1231_front_page_simplification_test -v
```

Result: `OK`.
