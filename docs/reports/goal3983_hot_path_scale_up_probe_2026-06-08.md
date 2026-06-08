# Goal3983: Hot-Path Scale-Up Probe

Date: 2026-06-08

## Purpose

Goal3982's Gemini review recommended scaling data size or batch counts for the
two short rows until the declared hot-path metrics become stable and
claim-grade. Goal3983 probes whether simple data-size scaling is enough for
RayDB and robot collision.

## Probes

RayDB:

- generated rows: 1,048,576
- generated rows: 4,194,304

Robot collision:

- 8,192 poses and 512 obstacles
- 16,384 poses and 1,024 obstacles

All probes ran on the RTX 4000 Ada pod under the same driver-550 partner setup.

## Results

| Probe | Primary Hot Metric | Value |
| --- | --- | ---: |
| `raydb_rows1m` | native call wall | 0.001932s |
| `raydb_rows4m` | native call wall | 0.002188s |
| `robot_pose8192_obs512` | traversal tail | 0.000115s |
| `robot_pose16384_obs1024` | traversal tail | 0.000205s |

The larger RayDB row does create a large cold-prepare cost
(`cold_prepare_total: 10.039s` at 4M rows), but the hot native call remains
around 2ms. The larger robot row creates a larger prepared-query construction
cost (`tail_prepared_query_build_sec: 3.015s`), but the hot traversal still
stays around 0.2ms.

## Conclusion

Simple data-size scaling is not enough for these two rows if the target is a
seconds-level hot-path metric. The next design step should be an explicit
resident/batched hot-query contract:

- keep prepared data resident;
- execute many independent hot queries inside one benchmark contract;
- report the median/total for the declared hot-path metric;
- keep wrapper/process/setup elapsed separate from the hot-path metric.

This is a benchmark-contract design task, not a direct CUDA loader or native
correctness bug.

## Boundary

This is a scale-up probe and planning report. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
