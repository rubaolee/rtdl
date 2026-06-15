# RTDL v2.13 Tag Preparation

Status: ready after publication commit.

Intended tag: `v2.13`

Post-Goal4378 note: v2.13 is preserved as the already-created source-tree
release marker and now carries a bridge caveat. If a `v2.13` tag has already
been published, do not move it. If it has not been published, do not use this
file to create a stronger new public claim; v2.14 is the next formal cleanup and
benchmark-app boost release target.

## Required Commit Contents

- `VERSION` set to `v2.13`.
- `pyproject.toml` project version set to `2.13.0`.
- `docs/release_reports/v2_13/README.md`.
- `docs/release_reports/v2_13/publication.md`.
- `docs/release_reports/v2_13/tag_preparation.md`.
- `docs/release_reports/v2_13/public_rt_vs_embree_comparison.md` and `.json`.
- Refreshed Goal4349, Goal4368, Goal4369, and Goal4370 evidence artifacts.

## Required Validation

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4349_human_scale_rt_vs_embree_comparison_test \
  tests.goal4368_pip_exact_prepared_points_executor_test \
  tests.goal4369_embree_cpu_fairness_packet_test \
  tests.goal4370_v2_13_public_wording_packet_test \
  tests.goal4371_v2_13_release_publication_test
```

On the NVIDIA pod, run the same focused tests with the native library environment configured.

## Tag Command

```bash
git tag -a v2.13 -m "RTDL v2.13 source-tree release"
```

Do not move a published `v2.13` tag without explicit maintainer decision.

Validation status: `accept`.
