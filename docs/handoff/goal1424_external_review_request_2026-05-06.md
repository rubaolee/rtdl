# Goal 1424 External Review Request

Please review the v1.5.1 `COLLECT_K_BOUNDED` native app-generic audit patch.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/__init__.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `docs/reports/goal1424_v1_5_1_collect_k_native_app_generic_audit_2026-05-06.md`

## Intended Patch

The patch records the current boundary precisely:

- `COLLECT_K_BOUNDED` is app-generic at the contract, Python reference, and
  result-validator layers.
- The current native Embree and OptiX exported collection symbols are still
  polygon-pair-specific.
- Stable primitive promotion remains blocked until an app-name-free native
  `COLLECT_K_BOUNDED` ABI, adapters, Embree/OptiX parity tests, and renewed
  3-AI stable-promotion review exist.

The patch must preserve this boundary:

- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action or release

## Validation To Check

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 27 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`f72ecd79fc3b7624f562b4cdd01c611825214375`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 27 tests` / `OK`.

## Requested Verdict

Return one of:

- `ACCEPT`
- `ACCEPT WITH NOTES`
- `BLOCK`

If blocking, identify the exact blocker only. Do not speculate.
