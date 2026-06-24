# Goal 734: Barnes-Hut Embree Compact Candidate Output

Date: 2026-04-21

## Scope

Goal 734 improves the public Barnes-Hut app surface:

- `examples/rtdl_barnes_hut_force_app.py` now accepts `--body-count` for a
  deterministic scalable body fixture.
- It adds `--output-mode full|candidate_summary|force_summary`.
- The default remains `full` with the original authored six-body fixture.

The goal is not to claim a fully native Barnes-Hut force engine. The goal is to
separate the RTDL/Embree candidate-generation slice from Python opening-rule
and force-reduction work.

## Output Modes

| Mode | What it returns | Boundary |
| --- | --- | --- |
| `full` | candidate rows, force rows, exact-force rows, and error rows | original app behavior; best for correctness explanation |
| `candidate_summary` | candidate-row count, body coverage count, and node coverage count | measures the RTDL candidate-generation slice without row payload |
| `force_summary` | candidate summary plus force-row, accepted-node, and exact-body totals | includes Python Barnes-Hut opening-rule and force reduction |

## Correctness

Focused tests verify:

- default full output remains oracle checked;
- `candidate_summary` omits heavy rows;
- Embree candidate summary matches the CPU Python reference at scale;
- `force_summary` omits exact oracle rows;
- invalid body counts and invalid modes are rejected.

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal734_barnes_hut_embree_compact_output_test \
  tests.goal505_v0_8_app_suite_test
```

Results:

- macOS: 9 focused/app tests passed.
- Linux: 9 focused/app tests passed.

## Performance Evidence

Measurement:

- `run_app(...)` plus `json.dumps(...)`
- CPU Python reference candidate summary versus Embree candidate summary
- Embree force summary reported separately because it includes Python force
  reduction
- 3 repeats

macOS:

| Bodies | CPU candidate summary | Embree candidate summary | Embree / CPU speedup | Embree force summary |
| ---: | ---: | ---: | ---: | ---: |
| 256 | 0.0009s | 0.0012s | 0.76x | 0.0139s |
| 1024 | 0.0037s | 0.0041s | 0.91x | 0.2102s |
| 4096 | 0.0165s | 0.0146s | 1.13x | 3.0432s |

Linux:

| Bodies | CPU candidate summary | Embree candidate summary | Embree / CPU speedup | Embree force summary |
| ---: | ---: | ---: | ---: | ---: |
| 256 | 0.0021s | 0.0028s | 0.75x | 0.0233s |
| 1024 | 0.0081s | 0.0086s | 0.94x | 0.3187s |
| 4096 | 0.0354s | 0.0320s | 1.11x | 5.1665s |

Raw evidence:

- `docs/reports/goal734_barnes_hut_compact_output_perf_local_2026-04-21.json`
- `docs/reports/goal734_barnes_hut_compact_output_perf_linux_2026-04-21.json`

## Conclusion

The Barnes-Hut app now has a reasonable Embree-facing performance mode for the
part RTDL actually owns today: body-to-quadtree-node candidate discovery.
At larger local/Linux scales, Embree candidate summary is slightly faster than
the CPU Python reference.

The full Barnes-Hut force path is still dominated by Python opening-rule and
force-reduction work. Do not claim a fully native Barnes-Hut speedup from this
goal.
