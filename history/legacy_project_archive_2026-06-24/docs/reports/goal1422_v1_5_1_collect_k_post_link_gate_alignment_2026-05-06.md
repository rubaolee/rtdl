# Goal 1422 v1.5.1 COLLECT_K_BOUNDED Post-Link Gate Alignment

## Verdict

The v1.5.1 `COLLECT_K_BOUNDED` release-surface gate now reflects the accepted
Goal1421 public-doc-link consensus.

This alignment is not stable primitive promotion, not public speedup wording,
not zero-copy wording, not a whole-app claim, not a release-tag action, and not
a release.

## Change

- Updated the release-surface gate status from pre-link review language to
  post-link discoverability language.
- Recorded the Goal1420 release-surface gate consensus and Goal1421 public-doc
  link consensus in the runtime gate dictionary.
- Updated the v1.5.1 candidate package docs so they no longer imply that public
  doc discoverability is still pending.
- Added a regression test for post-link gate alignment and no-overclaiming.

## Boundary

The candidate package remains:

- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 21 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d3fc7f636e6c9f7249adb60f8cd89a4ae5cea7a5`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 21 tests` / `OK`.
