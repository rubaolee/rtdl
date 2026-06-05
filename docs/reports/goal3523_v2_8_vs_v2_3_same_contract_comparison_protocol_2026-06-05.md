# Goal3523: v2.8 vs v2.3 Same-Contract Benchmark Comparison Protocol

Date: 2026-06-05

Status: protocol ready; fresh RTX pod evidence required before a final all-app
comparison table.

## Purpose

The user asked for a performance comparison between v2.8 and v2.3 for all
benchmark apps. This goal turns that request into a strict measurement contract.

The important decision is that we must not produce a fake all-app ratio by
placing the v2.3 release/evidence table beside the v2.8 prepared-execution
matrix. v2.8 changed several app contracts: some rows became prepared,
phase-split, primitive-first, grouped-stream, or exact-continuation paths. Those
changes are the point of v2.8, but they also mean that many existing artifacts
cannot be ratioed without a fresh same-contract run.

## Source Of Truth

New source:

- `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`
- `tests/goal3523_v2_8_vs_v2_3_same_contract_comparison_test.py`

Main evidence sources:

- v2.3 tag: `v2.3`
- v2.3 release package: `docs/release_reports/v2_3/README.md`
- v2.3-era performance evidence: `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- v2.8 benchmark matrix: `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`
- v2.8 final validation packet: `docs/reports/goal3521_v2_8_final_validation_packet_2026-06-05.md`

Important caveat: the `v2.3` tag itself does not contain
`scripts/goal2626_benchmark_embree_optix_baseline.py`. The all-app performance
runner and Goal2637/2654 evidence were produced after the v2.3 app-portfolio
release tag. The current `docs/release_reports/v2_3/README.md` also differs
from the tag copy for contact manifold: the tag text says nine promoted apps,
while the current release-report text and Goal2654 evidence include contact
manifold as a promoted benchmark. Therefore Goal3523 treats v2.3 as two
separate things:

1. the released app-portfolio boundary at tag `v2.3`;
2. the accepted v2.3-era benchmark evidence from Goal2654.

The final comparison packet must say which one each row uses.

## Current Comparison Map

| App | Existing comparison status | Existing v2.3 timing | Existing v2.8 timing | What blocks final all-app ratio |
| --- | --- | ---: | ---: | --- |
| `hausdorff_xhd` | fresh same-contract pod required | `0.0311073` threshold row | `0.007444375` exact witness row | threshold and exact-witness contracts differ |
| `spatial_rayjoin` | fresh same-contract pod required | `0.000529638` scoped summary | split rows: count/parity `0.000161098`, overlay `0.069889469` | v2.8 split count/parity and exact overlay-area; do not collapse |
| `rt_dbscan` | existing same-output bounded ratio allowed | `1.62144` cluster signature | `0.302337887` grouped-stream tail | final publication still needs one-pod rerun; raw RT-count nuance remains |
| `robot_collision` | fresh same-contract pod required | `0.00161413` prepared flags | Goal3521 uses a different `256x32x3` workload | same workload and phase split needed |
| `contact_manifold` | fresh same-contract pod required | `0.0184764` generic AABB broadphase collect-k | Goal3521 grid-4096 phase split | current v2.3 report/evidence includes contact, but tag/current-report drift must be disclosed |
| `raydb_style` | fresh same-contract pod required | count `0.0001704`, sum `0.0009476` | count `0.000459385`, sum `0.002161583` | scale/primitive-first rules differ |
| `barnes_hut` | fresh same-contract pod required | `0.00855045` node coverage | membership + vector sum row | node coverage and vector continuation differ |
| `librts_spatial_index` | fresh same-contract pod required | `0.691477` AABB count | `0.001551950` prepared query | apparent delta requires same workload/phase confirmation |
| `rtnn` | fresh same-contract pod required | `0.00153247` uniform ranked summary | `0.017263921` worst-of-distribution matrix row | distribution/scale selection differs |
| `triangle_counting` | existing same-contract bounded ratio allowed | `0.000364401` RT-Graph summary | `0.000413392` generic RT summary | final table should rerun, but existing row is same-contract enough for internal status |

## Existing-Artifact Ratios

Only rows explicitly marked by the machine-readable map may be ratioed from
existing artifacts:

| App | Ratio status | v2.8 / v2.3 interpretation |
| --- | --- | --- |
| `rt_dbscan` | bounded same-output internal ratio | v2.8 grouped stream is about `5.36x` faster than the v2.3-era OptiX cluster-signature row, but only for the grouped-stream path |
| `triangle_counting` | bounded same-contract internal ratio | v2.8 is about `0.881x` of v2.3 from existing artifacts, so it is slightly slower by this artifact-only view |

These are not final public claims. They are triage facts for the pod run.

## Required Pod Packet

The final all-app comparison should run on one RTX pod, one driver/toolchain
profile, with two clean workspaces:

```text
/root/rtdl_v23_release
/root/rtdl_v28_current
```

The pod packet must record:

- repository URL;
- tag/commit for v2.3;
- commit for v2.8;
- GPU name and driver;
- CUDA toolkit used to build OptiX;
- OptiX SDK path and tag;
- `RTDL_OPTIX_LIBRARY`;
- `PYTHONPATH`;
- dirty status for both workspaces;
- exact commands and JSON artifact paths.

The comparison rows should be grouped into three categories:

1. **strict same-contract rows**: run the same app output contract in both
   workspaces and ratio directly;
2. **split/evolved contract rows**: run both the old contract and the v2.8
   promoted contract, then report both without collapsing them;
3. **tag/report drift rows**: disclose whether the row is absent from the
   literal tag release text but present in the current v2.3 release report and
   accepted evidence baseline.

## Proposed Pod Run Order

Run small dry/smoke first, then the final standard scale.

1. Validate both workspaces and native builds.
2. Run v2.3 smoke commands from `docs/release_reports/v2_3/README.md`.
3. Run v2.8 smoke commands from `examples/v2_0/research_benchmarks/README.md`.
4. Run the Goal2626-style standard matrix on current v2.8.
5. For v2.3 rows that lack the current runner, run the historical app commands
   available at the tag and normalize through a Goal3523 adapter.
6. Run v2.8-specific prepared rows for RayJoin overlay, RT-DBSCAN grouped
   stream, robot/contact phase split, RTNN distributions, and RayDB count/sum.
7. Produce:
   - `docs/reports/goal3523_pod_artifacts/v2_3/`
   - `docs/reports/goal3523_pod_artifacts/v2_8/`
   - `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_results_2026-06-05.json`
   - `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_results_2026-06-05.md`

## Claim Boundary

Goal3523 does not authorize:

- public v2.8 release wording;
- public speedup wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- package-install or PyPI wording;
- true zero-copy wording;
- paper reproduction claims;
- hidden partner selection;
- app-specific native-engine behavior.

## Validation

Local validation for the protocol:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3523_v2_8_vs_v2_3_same_contract_comparison_test
```

The test enforces:

- all 10 v2.8 benchmark apps are represented;
- the v2.3 tag/current-report drift for `contact_manifold` is explicit;
- most rows remain blocked pending fresh same-contract pod evidence;
- only explicitly ratioable rows get artifact-only ratios;
- every public/release claim flag remains false.

## Verdict

`accept-with-boundary`

Goal3523 is ready for pod execution. It is not yet the final all-app comparison
report. The final report requires fresh same-hardware evidence and external
review after artifacts exist.
