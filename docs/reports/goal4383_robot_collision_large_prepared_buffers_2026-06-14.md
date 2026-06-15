# Goal4383 Robot Collision Large Prepared-Buffer Refresh

Date: 2026-06-14

Status: v2.14 cleanup evidence for the same-contract prepared grouped-segment any-hit flags primitive. This strengthens the previous repeat-heavy millisecond row, but it is not a continuous-collision, planner, or exact solid-collision claim.

## Contract

Both backends run the same generic RTDL primitive:

`PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1`

The benchmark lowers each sampled robot link pose into vertical finite segments, tests those segments against a prepared static triangle scene, and returns compact `uint8` group any-hit flags. The large rows use `prepared_buffers` on both backends, meaning Python-owned host query/output buffers are reused for the same contract. The OptiX-only native device-buffer route is intentionally not mixed into the Embree-vs-OptiX table.

## Results

| Case | Backend | Groups | Query segments | Static triangles | Total run median sec | Traversal median sec | Output postprocess sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| medium | Embree | 65,536 | 589,824 | 2,048 | 0.068025 | 0.022172 | 0.007867 |
| medium | OptiX RT cores | 65,536 | 589,824 | 2,048 | 0.029494 | 0.001358 | 0.007890 |
| large | Embree | 524,288 | 4,718,592 | 8,192 | 0.558925 | 0.191628 | 0.063837 |
| large | OptiX RT cores | 524,288 | 4,718,592 | 8,192 | 0.307417 | 0.030935 | 0.063943 |
| xlarge | Embree | 1,048,576 | 9,437,184 | 16,384 | 1.143072 | 0.415152 | 0.125021 |
| xlarge | OptiX RT cores | 1,048,576 | 9,437,184 | 16,384 | 0.613828 | 0.062049 | 0.125740 |

## Same-Contract Speedups

| Case | Total speedup, Embree / OptiX | Traversal speedup, Embree / OptiX | Interpretation |
| --- | ---: | ---: | --- |
| 65,536 groups | 2.31x | 16.33x | Traversal is very RT-core friendly; fixed host postprocess already visible. |
| 524,288 groups | 1.82x | 6.19x | Total speedup compresses because output clear/postprocess grows with groups on both sides. |
| 1,048,576 groups | 1.86x | 6.69x | Single-run total is now human-scale: 1.14s Embree vs 0.61s OptiX. |

## Validation Boundary

The large rows use `--no-probe-reference` because exact CPU probe reference at 9.4M segments x 16K triangles is not a reasonable validation path. The smaller same-contract Goal4363 validation row confirmed Embree and OptiX match the probe-reference signature for the same prepared-buffer contract. These large rows are performance-scale refreshes, not new semantic-contract definitions.

## Conclusion

Robot collision should no longer be described as only a 1,024-pose, repeat-heavy row. v2.14 now has a large same-contract row with 1,048,576 groups and 9,437,184 query segments. OptiX RT cores are 6.69x faster in traversal and 1.86x faster in total prepared-buffer run time at that scale.

The public wording must stay narrow: this is a discrete sampled grouped-segment any-hit flag primitive, not continuous collision detection, not robot-planner acceleration, not exact solid collision, and not paper reproduction.
