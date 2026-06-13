# RTDL v2.12 Tag Preparation

Status: ready after publication commit.

Intended tag: `v2.12`

## Required Commit Contents

Only tag a commit that contains:

- `VERSION` set to `v2.12`;
- `pyproject.toml` project version set to `2.12.0`;
- `docs/release_reports/v2_12/README.md`;
- `docs/release_reports/v2_12/publication.md`;
- `docs/release_reports/v2_12/tag_preparation.md`;
- `docs/release_reports/v2_12/public_rt_vs_embree_comparison.md`;
- v2.12 current claim-boundary pages under `docs/learn/`;
- the regenerated public-doc claim scan artifact;
- the optimized v2.12 RT-core versus Embree CPU comparison packet;
- Goal4363 Robot Collision same-contract evidence;
- Goal4364 RayDB-style same-contract evidence.

## Required Validation

Before tagging, rerun:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
PYTHONPATH=src:. python scripts/goal4248_current_public_docs_claim_boundary_scan.py --root . --output docs/reports/goal4248_current_public_docs_claim_boundary_scan.json
PYTHONPATH=src:. python -m unittest \
  tests.goal4365_v2_12_release_publication_test \
  tests.goal4248_current_public_docs_claim_boundary_scan_test \
  tests.goal4278_source_tree_doctor_test \
  tests.goal4307_editable_source_tree_onboarding_test
```

On a configured NVIDIA pod, also run the focused v2.12 comparison tests:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so python3 -m unittest \
  tests.goal4338_current_optix_embree_comparison_index_test \
  tests.goal4341_optimized_embree_optix_comparison_packet_test \
  tests.goal4345_backend_comparison_campaign_closeout_test \
  tests.goal4346_cpu_only_pod_comparison_launch_test \
  tests.goal4365_v2_12_release_publication_test
```

## Tag Command

After the publication commit is created and validated:

```bash
git tag -a v2.12 -m "RTDL v2.12 source-tree release"
```

Check the tag target before publishing it:

```bash
git show --stat --oneline v2.12
```

## Boundary

Do not tag a pre-publication head that lacks the v2.12 worktree content. Do not
move a published `v2.12` tag without a separate explicit maintainer decision.

