# Goal1899 - v2 Strict Birth Gate Current Board

Status: active-blockers-pod-and-consensus-pending

Date: 2026-05-13

## Scope

Goal1899 is the current working board for the stricter Goal1814 v2.0 birth
gate. It summarizes what moved since the first partner preview and what still
blocks the v2.0 release label.

## Current Board

| Goal1814 blocker | Current state | Evidence | Next action |
| --- | --- | --- | --- |
| True zero-copy | Evidenced for selected OptiX partner input/output device-column paths; broad release wording still bounded to those contracts. | Goals1819, 1821, 1823, 1826, 1831, 1834, 1836, 1838, 1845, 1847, 1848, 1940 | Keep public wording scoped to the selected OptiX contracts; do not generalize to every backend or arbitrary partner tensors. |
| Direct device-pointer handoff | Implemented and fail-closed for selected partner descriptors; still bounded to specific primitives and contracts. | Goals1819, 1821, 1823, 1826 | Keep descriptor/lifetime/stream wording narrow; do not generalize to arbitrary partner code. |
| Broad RT-core speedup | Still not a broad claim. Strong positive rows now exist for fixed-radius and segment any-hit; robot is positive but subsecond; DB/graph/exact polygon remain controls. | Goals1881, 1886, 1889, 1895, 1897, 1903, 1904, 1905, 1937, 1940, 1941, 1942 | Final release wording must say which rows are positive, which are controls, and which claims remain out of scope. |
| Whole-application acceleration | Not ready as a blanket claim. Implemented v2 rows have pod timing, but four active rows are evidence-only controls and robot remains positive-subsecond. | Goals1878, 1881, 1886, 1889, 1895, 1931, 1937, 1940, 1942 | Use row-by-row claims only; do not turn the rollup into whole-app acceleration marketing. |
| Arbitrary PyTorch/CuPy acceleration boundary | Source doc written and linked; public wording scanner passes; Gemini accepted with boundary; still needs final release consensus. | Goal1814 plus Goals1900, 1906, 1907, 1908 | Fold accepted wording into final v2.0 release gate without expanding beyond reviewed RTDL primitive calls. |
| Package-install support | Blocked. No packaging metadata exists; source-tree-only remains the current validated mode; Gemini accepted source-tree policy with boundary, but final 3-AI consensus is still required. | Goals1898, 1902, 1906, 1907, 1908 | Either create validated packaging metadata or get 3-AI consensus for source-tree-only v2.0. |

## Newly Added Since The Last Board

- Goal1889: road-hazard prepared partner reuse row and GTX 1070 local smoke.
- Goal1895: v2 partner performance matrix status.
- Goal1896: Gemini Flash interim review of Goal1889 labeled local smoke.
- Goal1897: one-command road-hazard RTX pod packet, local dry-run passed.
- Goal1898: package-install gate audit.
- Goal1900: user-facing partner acceleration boundary doc, linked from the
  front page, docs index, and tutorial ladder.
- Goal1903: v2 partner pod batch packet with fixed-radius, segment/polygon,
  and road-hazard heads; local GTX-only mechanics dry-run passed for the
  road-hazard head and remains non-release evidence.
- Goal1904: Gemini review accepted Goal1903's batch structure and constrained
  claim boundaries, without authorizing v2.0 release or broad speedup claims.
- Goal1905: post-pod acceptance validator for the Goal1903 artifact set.
- Goal1906: public v2 claim-boundary scanner for README, docs index,
  partner-boundary doc, and tutorials.
- Goal1907: Gemini review accepted the v2 boundary and source-tree policy with
  release still blocked.
- Goal1908: one-command local non-pod preflight for current v2 guardrails.
- Goal1909: v2 release packet skeleton listing populated and missing slots
  without authorizing release.
- Goal1910: Gemini review accepted the Goal1909 skeleton boundary.
- Goal1911: machine-readable v2 readiness aggregator; current status is
  blocked only by pod artifacts, post-pod review, final consensus, and release
  action.
- Goal1912: post-pod external review handoff template, waiting for actual pod
  artifacts.
- Goal1913: visible-progress pod session runbook for Goal1908, Goal1903,
  Goal1905, and Goal1911.
- Goal1914: pod artifact provenance hardening so accepted artifacts must carry
  RTX GPU provenance, git commit, and matching source labels.
- Goal1915: Gemini accepted the Goal1914 provenance hardening as a pre-pod
  guardrail while keeping actual pod artifacts and post-pod review required.
- Goal1916: post-pod artifact manifest generator for reviewer-ready commit,
  GPU, source-label, partner, and claim-boundary summaries.
- Goal1917: Gemini accepted Goal1916 as a post-pod review aid, not hardware
  evidence or release authorization.
- Goal1918: fixed-radius pod batch now caps optional dense partner-reference
  pair materialization to avoid GPU OOM on large rows.
- Goal1919: RTX pod artifacts are integrated locally; Goal1905 and Goal1916
  pass, and Goal1911 now marks pod evidence collected while keeping release
  blocked pending external review and final consensus.
- Goal1921: detailed post-pod performance report records fixed-radius positive
  rows, mixed 512-row segment/polygon and road-hazard behavior, positive 2048
  prepared-reuse rows, and exact claim boundaries.
- Goal1922: Numba/Triton/CuPy RawKernel strategy note keeps v2.0 focused on
  partner tensor composition, defers external custom-kernel interop to v2.5,
  and reserves engine-extension/JIT scope for v3.0.
- Goal1923: Claude decisive post-pod artifact review landed with
  `accept-with-boundary`, closing the fresh Claude/Pro-class review blocker
  while keeping v2.0 release blocked pending package/source-tree decision,
  final release consensus, and explicit release action.
- Goal1924: all-app v2 completion plan maps the 16 active public app rows to
  reusable implementation families and marks the current v2 evidence as a
  strong slice, not a finished all-app matrix.
- Goal1925: fixed-radius family harness covers six additional app rows
  (`facility_knn_assignment`, `hausdorff_distance`, `ann_candidate_search`,
  `outlier_detection`, `dbscan_clustering`, and `barnes_hut_force_app`) with a
  same-contract v1.8 prepared OptiX versus v2 prepared partner comparison;
  pod timing is still needed.
- Goal1927: robot collision v2 partner adapter writes generic any-hit ray
  flags through prepared OptiX, then reduces them to app pose-collision flags
  with Torch/CuPy partner operations; pod timing is still needed.
- Goal1928: robot collision v2 partner perf harness compares v1.8 prepared
  OptiX pose flags to the Goal1927 v2 partner adapter with scalar count parity;
  pod timing is still needed.
- Goal1930: all 16 active app rows now have a machine-readable v2 matrix
  decision: 4 already pod-timed, 7 harness-ready pending pod timing, 1
  implemented row needing a current rerun, and 4 explicit evidence-only
  control/fallback rows that must not be marketed as v2 partner speedups.
- Goal1931: current all-app v1.8-vs-v2 analysis report now consumes Goal1930
  plus accepted pod artifacts, showing 4 measured positive rows, 8 pending-pod
  rows, and 4 control rows with explanation rather than empty `n/a` cells.
- Goal1932: all-app pod batch runner now packages the pending fixed-radius,
  robot, segment-anyhit reruns, and the DB/graph/polygon evidence-only control
  rows with visible progress output for the next RTX pod session.
- Goal1933/1934: large-scale RTX A5000 pod evidence collected. Fixed-radius
  family rows now run at `524288 x 524288`, making v1.8 prepared rows
  seconds-scale while v2 prepared partner rows remain low-millisecond. DB,
  graph, and polygon controls are also seconds-scale evidence, but still not
  v2 partner speedup rows.
- Goal1935: Gemini accepted the Goal1933/1934 interpretation: fixed-radius is
  a strong narrow v2 result, robot and segment/polygon rows remain positive but
  sub-second, and DB/graph/polygon exact metrics remain control evidence rather
  than v2 partner speedup claims.
- Goal1936: Claude accepted the same packet with boundary notes: rerun the
  `524288 x 524288` fixed-radius row at `repeat >= 3` for variance-backed
  medians, label reused artifact provenance explicitly, investigate DB
  phase-total aggregation, and keep polygon controls out of RT-core speedup
  wording because their metadata says RT cores are inactive.
- Goal1937: the fixed-radius `524288 x 524288` rows were rerun on the RTX A5000
  pod with `repeat=3`; all 12 rows pass parity, v1.8 remains seconds-scale, and
  v2 prepared partner medians remain below `0.003` seconds with ratios under
  `0.001x`.
- Goal1938: Gemini accepted Goal1937 with boundary. Its fixed-radius provenance
  caveat was resolved by rerunning the repeat-3 packet with explicit source
  label `47490311d15acc668030b20324be05aeb709c4ac`; the run log is tracked.
- Goal1939: the DB control artifact's native phase-total aggregation anomaly
  is fixed. The refreshed OptiX compact-summary DB control remains seconds-scale
  and now reports six native operations with non-zero traversal, exact-filter,
  output-pack, raw-candidate, and emitted-count totals.
- Goal1940: robot and segment/polygon any-hit rows were scaled on the RTX A5000
  pod with source label `35666fb829a88f77ebdc6d18b9a66a45861d0e67`. Segment
  any-hit now has a seconds-scale same-contract positive row at 1,048,576 rows
  (`7.12s` v1.8 versus about `1.6s` v2 partner). Robot collision preserves exact
  pose-flag parity through 8,388,608 poses with about `0.02x` v2/v1.8 ratios,
  but its v1.8 baseline is still subsecond, so it remains a strong scaling
  signal rather than a seconds-scale whole-app claim.
- Goal1941: Gemini reviewed Goal1940 as `accept-with-boundary`, accepted the
  segment and robot interpretations, and kept the release/whole-app/broad
  RT-core/package-install/arbitrary-partner boundaries intact.

## Immediate Next Hardware Step

The fixed-radius family no longer needs the old Goal1925 small-scale command
for evidence. The next RTX pod work should be a visible-progress, background
run only if we are trying to push currently sub-second rows, especially robot
and segment/polygon any-hit, into seconds-scale scenarios:

```bash
OUT_DIR=docs/reports/goal1932_all_app_v2_pod_batch \
PARTNERS=cupy,torch \
PYTHONPATH=src:. \
timeout --preserve-status 45m \
bash scripts/goal1932_all_app_v2_pod_batch_runner.sh
```

Goal1903 remains the earlier accepted pod packet and can be rerun if a fresh
post-commit provenance packet is needed:

```bash
OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1903_v2_partner_pod_batch_runner.sh
```

Or run the visible-progress pod session wrapper:

```bash
OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1913_v2_pod_session_runbook.sh
```

Expected accepted artifacts:

- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1903_v2_partner_pod_batch_summary.json`

Then validate:

```bash
PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py
PYTHONPATH=src:. python3 scripts/goal1916_v2_post_pod_artifact_manifest.py
```

## Immediate Next Non-Hardware Step

Continue the all-app implementation plan from Goal1924 using the Goal1930
matrix. Family A has a runner, Family B has the robot runner and needs the
`segment_polygon_anyhit_rows` rerun, and Families D/E/F are explicit
evidence-only control rows until a reviewed partner continuation exists.

For the next all-app hardware session, run:

```bash
OUT_DIR=docs/reports/goal1932_all_app_v2_pod_batch \
PARTNERS=cupy,torch \
PYTHONPATH=src:. \
bash scripts/goal1932_all_app_v2_pod_batch_runner.sh
```

Keep the external review of the Goal1900 partner-acceleration boundary document
as part of the final release packet history; later all-app performance reports
must not broaden that accepted wording without new review.
If a new key performance conclusion is drawn from the all-app matrix, require a
fresh Claude or Pro-class review before release consensus.

Run Goal1906 after public doc edits:

```bash
PYTHONPATH=src:. python3 scripts/goal1906_public_v2_claim_boundary_scan.py
```

Run Goal1908 before pod work or release-review assembly:

```bash
PYTHONPATH=src:. python3 scripts/goal1908_v2_local_preflight.py
```

For a machine-readable readiness snapshot:

```bash
PYTHONPATH=src:. python3 scripts/goal1911_v2_readiness_aggregator.py
```

## Verdict

v2.0 is still not born. The fixed-radius and segment any-hit rows now have
seconds-scale positive pod evidence, while robot has large exact-parity scaling
evidence that remains subsecond on the v1.8 side. Goal1931 now rolls this up as
11 positive rows, 1 positive-subsecond robot row, and 4 control rows. The
strongest next progress is deciding whether more robot stress is technically
meaningful or whether the remaining release gate is consensus and
packaging/source-tree policy rather than more timing.
