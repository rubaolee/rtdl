# Goal 1421 v1.5.1 COLLECT_K_BOUNDED Public Doc Link Patch

## Verdict

The v1.5.1 `COLLECT_K_BOUNDED` candidate docs are linked from the public documentation spine with explicit caution wording.

This patch does not authorize stable primitive promotion, public speedup wording, zero-copy wording, whole-app claims, release-tag action, or a release.

## Updated Public Links

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`

## Linked Candidate Package

- `docs/release_reports/v1_5_1/README.md`
- `docs/release_reports/v1_5_1/collect_k_bounded.md`
- `docs/release_reports/v1_5_1/release_surface_gate.md`

## Boundary

The link text keeps the candidate docs framed as a documented experimental public-candidate surface only:

- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no release tag action
- no whole-app speedup claim

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 18 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`
after applying the same patch over `origin/main` at
`ff0161489edf4b52be69a3c057f4ecbb7fbb9982`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 18 tests` / `OK`.
