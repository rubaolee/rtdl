# RTDL v2.11 Tag Preparation

Status: ready after publication commit.

Intended tag: `v2.11`

## Required Commit Contents

Only tag a commit that contains:

- `VERSION` set to `v2.11`;
- `docs/release_reports/v2_11/README.md`;
- `docs/release_reports/v2_11/publication.md`;
- `docs/release_reports/v2_11/tag_preparation.md`;
- v2.11 current claim-boundary pages under `docs/learn/`;
- the regenerated public-doc claim scan artifact;
- the v2.11 Embree CPU reference evidence;
- the optimized RT-core versus Embree CPU evidence;
- the RayJoin original-code same-stream diagnostic evidence.

## Required Validation

Before tagging, rerun:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
PYTHONPATH=src:. python scripts/goal4248_current_public_docs_claim_boundary_scan.py --root . --output docs/reports/goal4248_current_public_docs_claim_boundary_scan.json
```

On a configured NVIDIA pod, also run:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python -m pytest -q \
  tests/goal4248_current_public_docs_claim_boundary_scan_test.py \
  tests/goal4298_v2_11_embree_cpu_partner_reference_packet_test.py \
  tests/goal4345_backend_comparison_campaign_closeout_test.py \
  tests/goal4349_human_scale_rt_vs_embree_comparison_test.py
```

The last validated pod result for this publication packet was `22 passed`.

## Tag Command

After the publication commit is created and validated:

```bash
git tag -a v2.11 -m "RTDL v2.11 source-tree release"
```

Push only after checking the tag target:

```bash
git show --stat --oneline v2.11
git push origin main
git push origin v2.11
```

## Boundary

Do not tag the pre-publication `main` head if it lacks the v2.11 worktree
content. Do not move a published `v2.11` tag without a separate explicit
maintainer decision.
