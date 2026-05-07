# Goal 1423 v1.5.1 COLLECT_K_BOUNDED Whole-App Phrase Gate

## Verdict

The v1.5.1 `COLLECT_K_BOUNDED` release-surface gate now mechanically requires
`no whole-app claims` in the candidate package docs.

This is a gate-hardening change only. It does not authorize stable primitive
promotion, public speedup wording, zero-copy wording, whole-app claims,
release-tag action, or a release.

## Change

- Added `no whole-app claims` to
  `V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES`.
- Added regression tests that keep all public-claim boundary phrases together
  in the release gate required phrase set.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 23 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d693bd6a089c5c6fa2b4ea2be95adcb472803f31`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 23 tests` / `OK`.
