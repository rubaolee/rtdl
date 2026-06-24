ACCEPT

The changes introduced by Goal994 successfully address the stated objectives.

- `scripts/goal947_v1_rtx_app_status_page.py` has been updated to include `--output-mode density_count` for outlier detection and `--output-mode core_count` for DBSCAN clustering in the generated claim commands.
- `src/rtdsl/app_support_matrix.py` correctly reflects the Goal992 context and the scalar count boundaries for both outlier detection and DBSCAN clustering.
- `docs/v1_0_rtx_app_status.md` shows the updated RT-core subpath and native-continuation contract wording, clearly distinguishing scalar paths from per-point summary paths, thus avoiding stale wording.
- Both `tests/goal947_v1_rtx_app_status_page_test.py` and `tests/goal705_optix_app_benchmark_readiness_test.py` contain updated assertions that verify these changes, including the new output modes, scalar wording, and Goal992 evidence.

The implementation correctly preserves outlier `density_count` and DBSCAN `core_count` scalar claim commands/evidence and avoids stale core-threshold/per-point wording.