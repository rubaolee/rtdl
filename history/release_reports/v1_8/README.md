# RTDL v1.8 Release Package

Status: released source-tree Python+RTDL language boundary.

Version marker: `v1.8`

Release date: 2026-05-12

## Release Statement

RTDL v1.8 is the first source-tree Python+RTDL language release. It publishes
the learner-facing Python authoring model, the RTDL kernel contract, and the
tracked app-agnostic native-engine release surface.

The release is source-tree based. Use it from a checkout with `PYTHONPATH=src:.`.
It is not a package-install release, not a broad whole-application speedup
claim, and not the Python+partner+RTDL milestone.

## What v1.8 Includes

- A front-door learner path from `README.md` through the quick tutorial,
  examples, architecture pages, and RTDL language docs.
- A Python+RTDL authoring boundary: Python remains the application/control
  layer, while RTDL owns the RT-shaped kernel contract and backend dispatch.
- A tracked native release surface migrated to app-agnostic source/ABI
  terminology through the v1.7 and v1.8 gates.
- Same-contract performance evidence for Embree and OptiX/RT where artifacts
  exist, with evidence-only wording for unavailable cells.
- Post-v1.5 rule audit coverage and distinct-AI release review records.

## What v1.8 Does Not Claim

- No package metadata or install command is published by this release.
- No universal speedup claim is made for backend flags such as `--backend optix`.
- No partner-framework readiness, PyTorch zero-copy, CuPy zero-copy, or v2.0
  partner contract is claimed.
- No promise is made that stale local native libraries already contain the
  latest v1.8 symbols; rebuild backend libraries from the tagged source.

## Evidence

- [Goal1758 legacy native cleanup](../../reports/goal1758_legacy_lsi_overlay_triangle_probe_native_cleanup_2026-05-12.md)
- [Goal1759 release prep](../../reports/goal1759_v1_8_release_prep_after_legacy_native_cleanup_2026-05-12.md)
- [Goal1762 final release-prep consensus](../../reports/goal1762_v1_8_final_release_prep_consensus_2026-05-12.md)
- [Goal1763 public docs and learner path](../../reports/goal1763_v1_8_public_docs_and_learner_path_readiness_2026-05-12.md)
- [Goal1764 post-v1.5 rule audit](../../reports/goal1764_post_v1_5_release_rule_audit_2026-05-12.md)
- [Goal1765 GitHub learner readiness](../../reports/goal1765_github_learner_readiness_double_check_2026-05-12.md)
- [Goal1768 release authorization readiness](../../reports/goal1768_v1_8_release_authorization_readiness_after_docs_audit_2026-05-12.md)
- [Goal1769 release action](../../reports/goal1769_v1_8_release_action_2026-05-12.md)
- [Claude review Goal1766](../../reviews/goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md)
- [Gemini review Goal1767](../../reviews/goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md)

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
PYTHONPATH=src:. python -m unittest tests.goal1769_v1_8_release_action_test
```
