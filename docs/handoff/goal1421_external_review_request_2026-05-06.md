# Goal 1421 External Review Request

Please review the v1.5.1 `COLLECT_K_BOUNDED` public-doc link patch.

## Files To Review

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `tests/goal1421_v1_5_1_collect_k_public_doc_link_test.py`
- `docs/reports/goal1421_v1_5_1_collect_k_public_doc_link_patch_2026-05-06.md`

## Intended Patch

The patch should make the v1.5.1 `COLLECT_K_BOUNDED` candidate docs
discoverable from the public documentation spine.

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
py -3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 18 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`ff0161489edf4b52be69a3c057f4ecbb7fbb9982`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 18 tests` / `OK`.

## Requested Verdict

Return one of:

- `ACCEPT`
- `ACCEPT WITH NOTES`
- `BLOCK`

If blocking, identify the exact blocker only. Do not speculate.
