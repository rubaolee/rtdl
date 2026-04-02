# Goal 34 Final Review - Claude

Date: 2026-04-02

## Numbers Verified Against Ground Truth

All six accepted parity-clean points match the provided measured Linux facts exactly:

| Slice | LSI CPU Median | LSI Embree Median | PIP CPU Median | PIP Embree Median |
| --- | ---: | ---: | ---: | ---: |
| `1x4` | `0.018810398` | `0.001951754` | `0.000607311` | `0.000478698` |
| `1x5` | `0.039446919` | `0.002359525` | `0.000662559` | `0.000476208` |
| `1x6` | `0.062070701` | `0.002815368` | `0.000748862` | `0.000483146` |
| `1x8` | `0.169970314` | `0.004655572` | `0.001392166` | `0.000732959` |
| `1x10` | `0.172933934` | `0.005615700` | `0.003049136` | `0.001310584` |
| `1x12` | `0.259253125` | `0.006209437` | `0.003330779` | `0.001340347` |

No rejected points, consistent with ground truth. Derived speedups in the report are arithmetically correct.

## Harness Quality

`scripts/goal34_linux_embree_performance.py`:

- selection policy reuses Goal 28D face-overlap logic correctly
- warmup + measured-iteration separation is sound; median is the reported statistic
- parity check sorts both CPU and Embree output before comparing
- accepted/rejected branching explicitly gates on both `lsi.pair_parity` and `pip.row_parity`
- outputs JSON and Markdown

`tests/goal34_performance_test.py` provides appropriate unit coverage for `summarize_times` and `render_markdown`.

## Acceptance Criteria

All criteria from `docs/goal_34_linux_embree_performance.md` are satisfied:

1. reproducible Linux-host performance harness in the repo
2. harness records parity and timing for `lsi` and `pip`
3. final report clearly separates accepted from rejected points
4. Gemini reviewed and approved

## Boundaries Honoured

The report correctly disclaims BVH backing for the local `lsi` path, full RayJoin paper reproduction, and generalization to OptiX/GPU backends.

## Conclusion

The implementation is complete, all numbers match measured hardware ground truth, the harness is sound, and all acceptance criteria are met.

APPROVED
