# Goal1947 - v2 Source-Tree-Only Policy Consensus

Status: accepted-with-boundary-not-release-authorization

Date: 2026-05-13

## Scope

Goal1947 closes the narrow v2.0 package-install policy question:

Should v2.0 be allowed to ship as a source-tree-only release, with
package-install support explicitly out of scope?

This consensus covers only that question. It does not authorize v2.0 release,
broaden performance claims, authorize package-install wording, or replace the
final v2.0 release consensus.

## Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal1943_v2_source_tree_only_release_decision_packet_2026-05-13.md` | accept source-tree-only as the engineering recommendation |
| Gemini | `docs/reviews/goal1944_gemini_review_v2_source_tree_only_policy_2026-05-13.md` | `accept-with-boundary` |
| Claude | `docs/reviews/goal1945_claude_review_v2_source_tree_only_policy_2026-05-13.md` | `accept-with-boundary` |

## Consensus Decision

The v2.0 release may be source-tree-only.

Allowed user-facing wording:

```text
RTDL v2.0 is used from the repository source tree. Set `PYTHONPATH=src:.` before
running examples, tests, or scripts. Package-install support is not part of this
release.
```

Blocked wording remains blocked:

- `pip install rtdl`
- `pip install -e .`
- `RTDL is available as a Python package`
- `Install RTDL from PyPI`
- `Package-install support is validated`

## Boundaries

This consensus does not change any of the following:

- v2.0 release authorization remains blocked until final release consensus and
  explicit user release action.
- Whole-app speedup claims remain blocked.
- Broad RT-core speedup claims remain blocked.
- Arbitrary PyTorch/CuPy acceleration claims remain blocked.
- True zero-copy and direct device-pointer handoff wording remains scoped to the
  reviewed selected OptiX partner contracts.
- The four all-app control rows remain controls, not v2 partner speedup rows.

## Claude Conditions

Claude's Goal1945 conditions are accepted into the consensus:

1. Keep scanner coverage in view before final release. If new public-facing
   files are added, include them in claim-boundary scanning or manually review
   them for package-install wording.
2. Treat this file as the source-tree/package consensus artifact, not as final
   v2.0 release authorization.
3. Keep Goal1911 release authorization false until final release consensus and
   explicit user release action exist.

## Remaining v2.0 Blockers

After this consensus, the package/source-tree blocker is closed. The remaining
hard blockers are:

- final v2.0 release consensus over the complete evidence packet;
- explicit user-requested release action.
