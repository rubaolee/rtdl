# Goal 1422 External Review Request

Please review the v1.5.1 `COLLECT_K_BOUNDED` post-link gate alignment patch.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- `tests/goal1422_v1_5_1_collect_k_post_link_gate_alignment_test.py`
- `docs/release_reports/v1_5_1/README.md`
- `docs/release_reports/v1_5_1/collect_k_bounded.md`
- `docs/release_reports/v1_5_1/release_surface_gate.md`
- `docs/reports/goal1422_v1_5_1_collect_k_post_link_gate_alignment_2026-05-06.md`

## Intended Patch

Goal1421 already accepted linking the v1.5.1 candidate package from the public
documentation spine. This patch updates the candidate package and release gate
metadata so they no longer imply that public-doc discoverability is still
pending.

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
py -3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 21 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d3fc7f636e6c9f7249adb60f8cd89a4ae5cea7a5`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 21 tests` / `OK`.

## Requested Verdict

Return one of:

- `ACCEPT`
- `ACCEPT WITH NOTES`
- `BLOCK`

If blocking, identify the exact blocker only. Do not speculate.
