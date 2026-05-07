# Goal 1423 External Review Request

Please review the v1.5.1 `COLLECT_K_BOUNDED` whole-app phrase gate hardening
patch.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- `tests/goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test.py`
- `docs/reports/goal1423_v1_5_1_collect_k_whole_app_phrase_gate_2026-05-06.md`

## Intended Patch

The patch adds `no whole-app claims` to
`V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES`, so the release gate
mechanically fails if the v1.5.1 candidate docs drop that boundary phrase.

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
py -3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 23 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d693bd6a089c5c6fa2b4ea2be95adcb472803f31`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 23 tests` / `OK`.

## Requested Verdict

Return one of:

- `ACCEPT`
- `ACCEPT WITH NOTES`
- `BLOCK`

If blocking, identify the exact blocker only. Do not speculate.
