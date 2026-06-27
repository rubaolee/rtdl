# Goal 18 Final Consensus

Claude and Gemini both accepted the Goal 18 implementation.

Accepted result:

- `run_embree(..., result_mode="raw")` is now a first-class runtime path
- prepared/raw execution now covers the full current local Embree workload surface:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`
- raw-mode correctness is verified against the ordinary dict-return path across all six workloads
- native-comparison claims remain limited to `lsi` and `pip`

Validation executed:

- `PYTHONPATH=src:. python3 scripts/goal18_compare_result_modes.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal17_prepared_runtime_test tests.goal18_result_mode_test tests.report_smoke_test`
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`

Observed full-suite result:

- `79` tests passed

Consensus decision:

Goal 18 complete by consensus.
