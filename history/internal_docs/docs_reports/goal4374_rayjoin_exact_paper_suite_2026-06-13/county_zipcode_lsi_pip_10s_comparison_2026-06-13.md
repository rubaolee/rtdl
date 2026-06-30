# RayJoin County x Zipcode 10s-Level LSI/PIP Comparison

Date: 2026-06-13

This is a same-source regenerated CDB result, not a recovered paper-preprocessed CDB result. The RayJoin Dryad preprocessed share was unavailable, so the current County x Zipcode input is the ArcGIS-derived topology-aware CDB tree under `/workspace/rayjoin_same_source_data/cdb_partial_topology`.

## Exactness Status

| Program | Exactness result | Public wording status |
| --- | --- | --- |
| LSI | RayJoin author RT and RTDL OptiX now match pair-for-pair: 180,506 pairs, 0 extra, 0 missing. RTDL Embree now matches the same count. | Ready for same-source County x Zipcode wording. Not paper-preprocessed wording. |
| PIP | RTDL OptiX and RTDL Embree match exactly: 3,823,790 positive points. RayJoin author PIP normal output reports timing but does not emit the positive count. | Ready for RTDL OptiX-vs-Embree wording. Author timing can be compared, but author count requires a diagnostic patch. |
| Polygon overlay | Not implemented as full materialization. | Not ready. Do not claim RayJoin Section 5.7 reproduction yet. |

## 10s-Level Hot Query Table

| Program | Engine | Repeat | Result count | Hot total | Median/query | Native traversal/query | Main comparison |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| LSI | RayJoin author RT | 2000 | 180,506 | ~8.77 s | 4.386 ms | n/a | Author baseline |
| LSI | RTDL OptiX RT cores | 6000 | 180,506 | 10.18 s | 1.694 ms | 1.662 ms | 183.4x faster than RTDL Embree hot; 2.59x faster than author hot |
| LSI | RTDL Embree CPU | 34 | 180,506 | 11.58 s | 310.546 ms | 310.461 ms | CPU baseline |
| PIP | RayJoin author RT | 1500 | not emitted | ~10.80 s | 7.200 ms | n/a | Author timing baseline |
| PIP | RTDL OptiX RT cores | 120 | 3,823,790 | 10.81 s | 89.860 ms | 9.381 ms | 2.19x faster than RTDL Embree hot; native traversal is 21.0x faster |
| PIP | RTDL Embree CPU | 112 | 3,823,790 | 20.89 s | 196.839 ms | 196.765 ms | CPU baseline |

## Interpretation

LSI is now the clean success case for RT hardware acceleration: same input, same RayJoin scaled-integer predicate, same count, and RTDL OptiX is about 183x faster than RTDL Embree at the hot-call level.

PIP has two truths. The native RT traversal is strong: RTDL OptiX native traversal is about 21x faster than Embree native traversal. The public RTDL hot call is only about 2.19x faster because it still pays Python/native call and point-stream upload overhead each repeat. Against RayJoin author PIP, RTDL native traversal is close but slower: 9.38 ms vs 7.20 ms.

## Fixes Made During This Pass

| Area | Fix |
| --- | --- |
| OptiX LSI exactness | Matched RayJoin GPU scaling by using fused multiply-add (`std::fma`) for scaled integer endpoints. This removed the six extra RTDL pairs. |
| OptiX LSI hot overhead | Added a cache fast path so repeated counts do not rescan all left/right segments to rediscover the RayJoin scale. |
| Embree LSI exactness | Added opt-in RayJoin LSI scaled-int predicate, FMA scaling, a RayJoin-coordinate Embree scene, and a wider RayJoin-specific bounds pad. |
| Auditability | Added RTDL OptiX pair dumping and `scripts/rayjoin_lsi_pair_diff.py` for author-vs-RTDL pair-set diffs. |

## Source Result Files

| Row | Result JSON |
| --- | --- |
| LSI author | `/workspace/rayjoin_same_source_data/results/lsi_county_zipcode_author_partial_topology_w5r2000.json` |
| LSI RTDL OptiX | `/workspace/rayjoin_same_source_data/results/lsi_county_zipcode_rtdl_optix_rayjoin_fma_cache_w5r6000.json` |
| LSI RTDL Embree | `/workspace/rayjoin_same_source_data/results/lsi_county_zipcode_rtdl_embree_rayjoin_scene_pad_w5r34.json` |
| PIP author | `/workspace/rayjoin_same_source_data/results/pip_county_zipcode_author_partial_topology_w5r1500.json` |
| PIP RTDL OptiX | `/workspace/rayjoin_same_source_data/results/pip_county_zipcode_rtdl_optix_rayjoin_cdb_w5r120.json` |
| PIP RTDL Embree | `/workspace/rayjoin_same_source_data/results/pip_county_zipcode_rtdl_all_rayjoin_cdb_w5r112.json` |

