# RTDL v0.3 Tag Preparation

Date: 2026-04-09
Prepared tag: `v0.3.0`

## Tag Meaning

`v0.3.0` marks the first released RTDL version that includes both:

- the stable `v0.2.0` workload/package surface
- the bounded `v0.3.0` RTDL-plus-Python application/demo layer

## Public Entry Points

- public video:
  - [RTDL Visual Demo Video](https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes)
- main visual-demo source:
  - [rtdl_hidden_star_stable_ball_demo.py](../../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- root front door:
  - [README.md](../../../README.md)

## Final Packaging Notes

- `VERSION` is set to `v0.3.0`
- release-facing docs now include a dedicated `docs/release_reports/v0_3/` package
- the public example chain no longer leaks internal `goal10` naming
- preserved generated artifacts now live under `examples/generated/`
