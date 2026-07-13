# Goal4875 Closure: Section 5.7 Australia Representative Via Public RTDL Primitives

Date: 2026-07-02

## Verdict

`completed_bounded_representative_section57_public_primitives_byte_equal_to_author_rtdl_contract`

Goal4875 now has a bounded, byte-equal Section 5.7 representative result on
the current-OSM Australia Lakes x Parks pair.

This is not an exact eight-pair paper-input claim. It is a representative
current-source reproduction under the explicit `Author+RTDLContractPatch`
comparison contract.

## Route

The RTDL route is intentionally a user/application route:

- public `prepare_planar_map_lsi_2d_optix`;
- public `prepare_planar_map_point_location_2d_optix`;
- Python application-level output-chain assembly;
- no import of `rtdsl.rayjoin_overlay`;
- no Embree;
- no V3/V4 dependency.

Numba is not on the correctness-critical path in this specific result. It
remains a candidate for later acceleration of app-side compaction or output
assembly after correctness is closed.

## Final Evidence

Artifacts on POD:

- `Author+RTDLContractPatch` output:
  `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`
- public RTDL route output:
  `/workspace/goal4875_section57_au_representative/public_route_author_contract_rounding/rtdl_public_overlay.txt`
- summary:
  `/workspace/goal4875_section57_au_representative/public_route_author_contract_rounding/summary.json`

Result:

```text
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  author_contract_au_overlay.txt
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  rtdl_public_overlay.txt

276320  6189260  author_contract_au_overlay.txt
276320  6189260  rtdl_public_overlay.txt
```

Summary fields:

- `byte_equal_to_author: true`
- `bundled_rayjoin_overlay_imported: false`
- `public_lsi_used: true`
- `public_point_location_used: true`
- `full_eight_pair_paper_claim: false`
- `broad_performance_claim: false`
- `numba_on_correctness_critical_path: false`

## Workload Size

- left map: `357910` chains, `14788065` points, `14430155` edges;
- right map: `51130` chains, `992505` points, `941375` edges;
- LSI rows: `13452`;
- output chains: `19820`;
- output faces: `8229`;
- output lines: `276320`.

## Timings

Public RTDL route elapsed wall time was about `119.25s`.

Phase timing:

- load/pack left CDB: `71.32s`;
- load/pack right CDB: `4.56s`;
- public LSI rows: `5.95s`;
- intersection reprojection: `0.43s`;
- sort map0/map1: `0.20s` / `0.19s`;
- vertex PIP map0 in map1: `10.77s`;
- vertex PIP map1 in map0: `1.56s`;
- midpoint PIP map0/map1: `0.064s` / `0.057s`;
- output-chain write: `16.83s`.

Author+RTDLContractPatch log for the same pair:

- read map0: `134688ms`;
- read map1: `9573.8ms`;
- build index: `32.38ms`;
- intersection edges: `4.951ms`;
- map0 point-location: `21.07ms`;
- map1 point-location: `7.39ms`;
- compute output polygons: `8.66ms`;
- write file: `801.56ms`.

Interpretation: the RT-core primitives are functioning; the public Python
route is dominated by CDB load/pack and Python output assembly, not by the
OptiX LSI/PIP kernels.

## Debug Path

The route originally failed against an unpatched AuthorPatch output. The first
visible mismatch was a chain split around map0 source chain 21.

A focused small case was extracted:

- left: `left_chain21.cdb`;
- right: `right_relevant_chains.cdb`;
- size: about 15KB total;
- it reproduced the mismatch.

The decisive point-location evidence was:

- AuthorPatch selected small edge `178`, source global edge `925339`, face
  `49059`;
- RTDL selected source global edge `478508`, face `0`;
- candidate scan showed the two edges are exact reverse duplicate half-edges
  with identical `xsect_y` and slope.

Under the already defined RTDL duplicate-half-edge contract, the canonical
edge is the smallest source segment id. Therefore the fair comparator is not
the unstable unpatched AuthorPatch output. It is `Author+RTDLContractPatch`.

On the small case:

```text
db860a9240e8e644bdc61059653e94fcaa6ad295a8975dfbbe3b7ebac314c81f  author_contract_small.txt
db860a9240e8e644bdc61059653e94fcaa6ad295a8975dfbbe3b7ebac314c81f  rtdl_small.txt
ef98179788a31374d66c4c22f590424895b1cd25ef0f1b30786853b479377dc3  author_small.txt
```

The final full-run mismatch after switching to Author+RTDLContractPatch was
only display formatting at the last printed decimal. An obsolete positive
half-boundary nudge was removed from the public route and from the bundled
helper display function. After that, the full representative output matched
byte-for-byte.

## Files Touched

- `history/internal_docs/goal4875_public_primitives_au_overlay.py`
  - public user-route script;
  - removed obsolete positive half-boundary display-coordinate nudge.
- `src/rtdsl/rayjoin_overlay.py`
  - kept bundled helper display formatting aligned with the public route by
    removing the same obsolete nudge.
- `history/internal_docs/goal4875_small_edge_mapper.py`
  - diagnostic mapper from small-case edge ids to source global edge ids.
- `history/internal_docs/goal4875_run_author_pipdump_points.sh`
  - diagnostic author PIP dump runner for selected small-case point indices.

## Verification

Focused local tests:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4866_rayjoin_section57_output_contract_test

Ran 30 tests in 0.073s
OK
```

## Boundaries

Authorized:

- bounded Australia current-OSM representative Section 5.7 reproduction;
- public RTDL primitive route equivalent to the explicit
  `Author+RTDLContractPatch` contract;
- correctness evidence for this representative pair.

Not authorized:

- exact eight-pair Section 5.7 paper reproduction;
- any claim using the six missing exact paper input/answer pairs;
- broad RayJoin or RTDL performance claim;
- claiming that Numba is used in the correctness-critical route for this
  result;
- claiming equivalence to the unstable unpatched AuthorPatch output.

## Next

Recommended next actions:

1. Send this closure packet for external review.
2. Decide whether to stop Section 5.7 at this bounded representative success
   or pursue additional representative pairs.
3. If performance matters, optimize the public route's load/pack and Python
   output assembly; the current RT-core LSI/PIP kernels are not the dominant
   cost.
