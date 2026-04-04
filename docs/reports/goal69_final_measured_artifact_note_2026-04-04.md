# Goal 69 Final Measured Artifact Note

Date: 2026-04-04
Status: internal only, do not publish yet

Exact artifact paths in the RTDL repo tree:
- `/home/lestat/work/rtdl_python_only/docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json`
- `/home/lestat/work/rtdl_python_only/docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.md`

Run scope:
- host: `lestat-lx1` (`192.168.1.20`)
- harness: `scripts/goal69_pip_positive_hit_performance.py`
- cases:
  - `county_zipcode`
  - `blockgroup_waterbodies`
- compared backends:
  - `optix`
  - `embree`
- PostGIS was used as the indexed positive-hit reference backend

Parity outcome:
- `county_zipcode`
  - OptiX parity vs PostGIS: `true`
  - Embree parity vs PostGIS: `true`
- `blockgroup_waterbodies`
  - OptiX parity vs PostGIS: `true`
  - Embree parity vs PostGIS: `true`

Practical reading:
- this broader measured package is parity-correct for both accelerated backends on both measured cases
- these copied files are the stable in-repo summary artifacts to hand to follow-on review work
- do not publish anything yet
