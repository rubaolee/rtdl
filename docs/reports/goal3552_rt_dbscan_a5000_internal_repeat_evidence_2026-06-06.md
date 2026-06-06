# Goal3552 RT-DBSCAN A5000 Internal-Repeat Evidence

Date: 2026-06-06

## Summary

Goal3551 added an app-level prepared-query repeat hook for the RT-DBSCAN grouped-stream benchmark. Goal3552 runs the targeted A5000 evidence packet for that row.

Final calibrated artifact:

- `docs/reports/goal3551_rt_dbscan_a5000_targeted_calibrated2/summary.json`
- `docs/reports/goal3551_rt_dbscan_a5000_targeted_calibrated2/summary.md`

Final dry plan:

- `docs/reports/goal3551_rt_dbscan_a5000_targeted_calibrated2_dry/summary.json`
- `docs/reports/goal3551_rt_dbscan_a5000_targeted_calibrated2_dry/summary.md`

Hardware:

- NVIDIA RTX A5000
- Driver 580.126.09
- 24564 MiB memory

## Result

| Row | Goal3548 speedup | Goal3552 speedup | v2.3 observed sec | v2.8 observed sec | Target observed met |
| --- | ---: | ---: | ---: | ---: | --- |
| `rt_dbscan_optix_grouped_stream` | `0.955x` | `0.992x` | `13.648385` | `13.473980` | yes/yes |

The row is now a valid 10-second-level targeted diagnostic: both sides meet the observed target after internal prepared-query repetition.

## Interpretation

The RT-DBSCAN weak row improved from a clear regression (`0.955x`) to near parity (`0.992x`). That is useful because it removes the old measurement weakness: the comparison is no longer dominated by subprocess wrapper repetition or stale seed calibration.

This is not a strong v2.8/v2.9 performance win. It says the v2.8 grouped-stream path is almost the same speed as the v2.3 overlay for this contract on A5000. The next v2.9 performance move must therefore be real kernel/runtime work, not more measurement cleanup, if we want RT-DBSCAN to become a positive row.

## Calibration Notes

The first targeted run used the Goal3548 seed and planned repeats `8`/`7`, but the new internal hook exposed a much smaller hot-query metric than the old seed. That attempt produced only about `0.10s` observed measured time and was discarded as calibration evidence.

The second run used the first run as a seed and planned repeats around `680`/`670`, producing about `8.5s` observed measured time, still below the 10-second rule.

The final run used the fresh calibrated seed with `--repeat-safety-factor 1.35`, planned repeats `1080`/`1058`, and cleared the target:

- v2.3 observed measured: `13.648385033011436`
- v2.8 observed measured: `13.473979668691754`
- v2.8 speedup vs v2.3: `0.9923098226130661`

## Boundary

This is internal performance evidence only. It does not authorize:

- public release wording;
- public speedup claims;
- whole-app speedup claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper-reproduction claims;
- package-install claims.

## Next Engineering Target

RT-DBSCAN is no longer a measurement-cleanup problem. It is a kernel/runtime performance problem. The most likely next target is the grouped-stream continuation itself:

- reduce per-query grouped union overhead;
- keep more component-label work device-resident;
- avoid any remaining scalar synchronization or host-visible summary work in the hot loop;
- compare against v2.3 after each kernel-level change with the same Goal3536 targeted protocol.
