# Goal 736: Robot Collision Scaled Embree Characterization

Date: 2026-04-21

## Scope

Goal 736 improves the public robot collision app for Embree-facing performance
characterization:

- `examples/rtdl_robot_collision_screening_app.py` now accepts
  `--pose-count` and `--obstacle-count` together to generate deterministic
  scalable fixtures.
- The default authored fixture remains unchanged.
- Existing output modes remain `full`, `pose_flags`, and `hit_count`.

This goal does not add a prepared Embree scalar-count ABI. Embree `hit_count`
still uses the native any-hit row path internally and then emits compact app
output.

## Correctness

Focused tests verify:

- scaled Embree `hit_count` matches the CPU Python reference;
- scaled `pose_flags` omits witness rows;
- `pose_count` and `obstacle_count` must be provided together;
- invalid generated fixture sizes are rejected;
- prior compact-output and profiler behavior remains compatible.

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal736_robot_collision_embree_scaled_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal702_robot_collision_profiler_output_modes_test \
  tests.goal503_robot_collision_screening_app_test
```

Results:

- macOS: 14 focused tests passed.
- Linux: 14 focused tests passed.

## Performance Evidence

Measurement:

- `run_app(...)` plus `json.dumps(...)`
- `--output-mode hit_count`
- 256 obstacles, represented as 512 triangles
- 3 repeats

macOS:

| Poses | Rays | CPU hit_count | Embree hit_count | Embree / CPU speedup | Embree full JSON expansion |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1024 | 4.2265s | 2.1284s | 1.99x | 383.10x |
| 1024 | 4096 | 16.4201s | 8.0360s | 2.04x | 1537.69x |

Linux:

| Poses | Rays | CPU hit_count | Embree hit_count | Embree / CPU speedup | Embree full JSON expansion |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1024 | 4.6699s | 2.3517s | 1.99x | 383.10x |
| 1024 | 4096 | 18.7060s | 9.3561s | 2.00x | 1537.69x |

Raw evidence:

- `docs/reports/goal736_robot_collision_scaled_perf_local_2026-04-21.json`
- `docs/reports/goal736_robot_collision_scaled_perf_linux_2026-04-21.json`

## Conclusion

The robot collision app now has deterministic scaled fixtures and demonstrates
reasonable Embree performance against the CPU Python reference on macOS and
Linux.

Important boundary: compact `hit_count` output drastically reduces JSON payload
relative to `full`, but it does not yet reduce native execution time because
Embree still materializes native any-hit rows internally. A future prepared
Embree scalar-count ABI would be needed to match the OptiX prepared-count
design.
