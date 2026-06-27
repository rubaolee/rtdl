# Claude Review: V4 Goal4633 Weighted-Sum Promotion Completion

Date: 2026-06-25

Verdict: `approve_goal4633_promote_measured_after_catalog_update`

## Evidence Cross-Check

Claude verified that the JSON evidence, Markdown summary, Python decision module,
and call-for-review table carry the same four timing pairs and ratios.

Gate arithmetic:

| Rays | Device Median (s) | Host Median (s) | Ratio | Pass `>=1.20x` |
|---:|---:|---:|---:|---|
| 32768 | 0.0000750888 | 0.0001611300 | 2.1459x | yes |
| 131072 | 0.0001438316 | 0.0002348572 | 1.6329x | yes |
| 262144 | 0.0002434943 | 0.0003302824 | 1.3564x | yes |
| 524288 | 0.0004368126 | 0.0005246699 | 1.2011x | yes |

Geomean:

- observed: `1.5457x`
- required: `>=1.50x`
- result: pass

Claude also noted that the 524288-row timing distributions are non-overlapping:

- device max: about `0.000447s`
- host min: about `0.000519s`

Therefore the thin-margin largest row was not treated as an obvious statistical
artifact, and no rerun was required by Claude.

## Boundary Review

Claude accepted the corrected comparison boundary:

- `comparison_class: same_operator_comparable_route`
- host scalar materialization path versus device-resident output path
- not a pure kernel-vs-kernel speedup figure

## Non-Authorization

Claude confirmed that the review does not authorize:

- V4 release;
- whole-app speedup;
- all-benchmark speedup;
- broad V4 speedup wording;
- CuPy performance;
- Tier-3 callback support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python host scope.

## Required Catalog Wording

Claude authorized measured-catalog promotion after catalog update with bounded
wording:

> `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` is a measured Torch
> CUDA V4 Tier-2 surface. It has a same-operator comparable-route measurement
> comparing host-scalar materialization against device-resident output on NVIDIA
> RTX A5000 / Ampere with Torch 2.8.0+cu128. Comparable-route ratio is
> `1.20x-2.15x` across 32K-512K rays, with geomean `1.55x`. The largest shape
> barely clears the per-shape floor, so this is a bounded route win, not a large
> speedup. It does not authorize whole-application, all-benchmark, or broad V4
> speedup claims.

## Findings

No blocking issues.

Minor catalog-update requirements:

- carry the `1.2011x` large-shape caveat into catalog wording;
- promote Torch CUDA only;
- do not include CuPy in measured partners.
