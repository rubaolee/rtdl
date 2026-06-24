# Goal4248 Current Public Docs Claim-Boundary Scan

Date: 2026-06-09
Status: pass
Evidence status: internal release-prep audit only

## Purpose

Goal4248 adds a current v2.10 public-doc scanner so learner/user-facing docs do
not accidentally authorize release, broad speedup, package-install, true
zero-copy, automatic partner selection, paper reproduction, RayJoin superiority,
or AMD/HIPRT performance claims.

This scan intentionally does not reuse the older Goal1906 scanner, because that
file is part of an older dirty working-tree lane. Goal4248 is scoped to the
current public docs that normal users see first:

- `README.md`
- `docs/learn/**/*.md`
- `docs/tutorials/**/*.md`
- `examples/README.md`
- `examples/v2_0/research_benchmarks/**/*.md`

## Result

The final scan artifact is
`docs/reports/goal4248_current_public_docs_claim_boundary_scan.json`.

| Metric | Value |
| --- | ---: |
| Public files scanned | 31 |
| Claim-sensitive findings | 116 |
| Hard blockers | 0 |
| Accepted boundary or negative-context findings | 98 |
| Accepted scoped-evidence findings | 18 |

All claim-boundary authorization flags in the JSON artifact remain false:

- `release_authorized`
- `public_speedup_claim_authorized`
- `whole_app_speedup_claim_authorized`
- `broad_rt_core_claim_authorized`
- `rtdl_beats_rayjoin_claim_authorized`
- `paper_reproduction_claim_authorized`
- `true_zero_copy_claim_authorized`
- `automatic_partner_selection_authorized`
- `amd_performance_claim_authorized`
- `package_install_claim_authorized`

## Repairs Made

The first scanner run found four hard blockers. They were wording hazards, not
evidence defects, and were fixed directly in public docs.

| File | Original issue | Action |
| --- | --- | --- |
| `README.md` | The dependency command contained `pip install` plus a nearby `package-install` phrase that could be read as an install promise. | Reworded the command comment to say it installs dependencies only and does not install RTDL. |
| `examples/README.md` | The dependency command contained `pip install` with no adjacent source-tree boundary. | Added the same dependency-only, does-not-install-RTDL boundary comment. |
| `docs/tutorials/nearest_neighbor_workloads.md` | The phrase `accelerated backends` was too broad for a learner-facing tutorial. | Replaced it with `configured RT backends`. |
| `README.md` | The same prerequisite snippet also triggered the `package-install` detector. | Covered by the dependency-only rewording above. |

The second scanner run passed with zero hard blockers.

## Boundary

This goal is a documentation quality gate. It does not authorize a release or
any public performance claim. It only confirms that the scanned public docs keep
the current v2.10 claim boundaries visible and that positive performance wording
is either scoped to reviewed evidence or paired with an explicit negative
boundary.

Remaining release gates are unchanged:

- formal release packet;
- exact public claim wording;
- fresh multi-AI release consensus over that packet;
- AMD/HIPRT evidence only when AMD hardware is available and claimed.
