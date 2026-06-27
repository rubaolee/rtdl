# Goal 1424 v1.5.1 COLLECT_K_BOUNDED Native App-Generic Audit

## Verdict

`COLLECT_K_BOUNDED` is app-generic at the contract, Python reference, and
result-validator layers, but stable primitive promotion remains blocked because
the current native Embree and OptiX collection entrypoints are still
polygon-pair-specific.

This audit does not demote the documented experimental public-candidate status.
It does not authorize stable primitive promotion, public speedup wording,
zero-copy wording, whole-app claims, release-tag action, or a release.

## Current Native Evidence

- Embree symbol:
  `src/native/embree/rtdl_embree_api.cpp` /
  `rtdl_embree_collect_polygon_pair_candidates_bounded`
- OptiX symbol:
  `src/native/optix/rtdl_optix_api.cpp` /
  `rtdl_optix_collect_polygon_pair_candidates_bounded`

These symbols validate the current measured polygon-pair candidate package, but
they are not an app-name-free native `COLLECT_K_BOUNDED` ABI.

## Stable-Promotion Blocker

Stable promotion is blocked until the native layer has:

- an app-name-free native `COLLECT_K_BOUNDED` ABI
- a polygon-pair adapter routed through that generic ABI
- Embree and OptiX parity tests for the generic ABI
- renewed 3-AI stable-promotion review

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 27 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`f72ecd79fc3b7624f562b4cdd01c611825214375`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 27 tests` / `OK`.
