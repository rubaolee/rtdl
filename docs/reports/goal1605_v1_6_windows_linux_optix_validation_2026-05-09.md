# Goal 1605: v1.6 Windows, Linux, and NVIDIA OptiX Validation

## Verdict

The `v1.6` architecture-anchor validation slice is green on Windows and Linux,
and the scoped real NVIDIA OptiX slice is green on the Linux validation host.

This validation supports continuing toward the final `v1.6` release package. It
does not publish `v1.6`, does not authorize release/tag action, does not add
public speedup wording, and does not promote `COLLECT_K_BOUNDED`.

## Repository State

Validated Git commit:

```text
ae92aa8eabc969da856ea730c7b82e19345ca3a3
```

The Linux validation checkout was reset to `origin/main` at this commit before
the Linux runs.

## Windows Source-Tree Validation

Transcript:

```text
docs/reports/goal1605_windows_release_slice_cmd_2026-05-09.txt
```

Command shape:

```text
cmd.exe /c "set PYTHONPATH=src;.&& py -3 -m unittest ... > docs\reports\goal1605_windows_release_slice_cmd_2026-05-09.txt 2>&1"
```

Included tests:

- `tests.goal1604_v1_6_blocked_claim_regression_gate_test`
- `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test`
- `tests.goal1602_v1_6_public_docs_overclaim_audit_test`
- `tests.goal1601_v1_6_release_surface_proposal_test`
- `tests.goal1600_v1_6_python_rtdl_readiness_gate_test`
- `tests.report_smoke_test`
- `tests.evaluation_test`
- `tests.goal40_native_oracle_test`

Result:

```text
Exit code 0 was reported by the local cmd.exe wrapper.
ae92aa8eabc969da856ea730c7b82e19345ca3a3
Ran 38 tests in 75.395s
OK
```

The transcript includes known Windows native Embree compile warnings about
`dllexport` redeclaration and `getenv` deprecation. They did not fail the test
slice.

An earlier full unittest discovery attempt produced
`docs/reports/goal1605_windows_unittest_discovery_2026-05-09.txt` but hit the
local 10-minute timeout while compiling native Embree code. That timed-out
attempt is not used as green evidence.

## Linux Source-Tree Validation

Host:

```text
lestat@192.168.1.20
```

Transcript:

```text
docs/reports/goal1605_linux_release_slice_clean_2026-05-09.txt
```

Command shape:

```text
ssh lestat@192.168.1.20 "cd /home/lestat/work/rtdl_codex_local_check && PYTHONPATH=src:. python3 -m unittest ..."
```

Included tests matched the Windows source-tree validation slice.

Result:

```text
Exit code 0 was reported by the local cmd.exe wrapper.
ae92aa8eabc969da856ea730c7b82e19345ca3a3
Ran 38 tests in 36.713s
OK
```

## Real NVIDIA OptiX Validation

Host:

```text
lestat@192.168.1.20
```

GPU and driver:

```text
NVIDIA GeForce GTX 1070, 580.126.09
```

OptiX environment:

- `build/librtdl_optix.so` was present.
- `/home/lestat/vendor/optix-dev/include/optix.h` was present.

Transcript:

```text
docs/reports/goal1605_linux_nvidia_optix_slice_clean_2026-05-09.txt
```

Included tests:

- `tests.goal637_optix_native_any_hit_test`
- `tests.goal1288_v1_5_generic_anyhit_count_test`
- `tests.goal427_v0_7_rt_db_optix_backend_test`
- `tests.goal695_optix_fixed_radius_summary_test`
- `tests.goal757_prepared_optix_fixed_radius_count_test`
- `tests.goal850_optix_db_grouped_summary_fastpath_test`
- `tests.goal851_optix_db_sales_grouped_summary_fastpath_test`

Result:

```text
CMD_LASTEXITCODE=0
Ran 33 tests in 1.255s
OK
```

This is a real NVIDIA OptiX runtime validation for the scoped stable primitive
surface and adjacent supported reduction/summary paths. It is not a speedup
claim and not a broad claim that every OptiX path uses NVIDIA RT cores.

## Claim Boundary

This validation supports:

- Windows source-tree execution for the scoped `v1.6` gate slice;
- Linux source-tree execution for the scoped `v1.6` gate slice;
- real NVIDIA OptiX runtime availability and correctness for the selected
  scoped primitive/reduction paths.

This validation does not support:

- `v1.6` release/tag action by itself;
- package-install support;
- public speedup wording;
- whole-application speedup;
- broad RTX/GPU acceleration wording;
- true zero-copy wording;
- partner tensor handoff claims;
- stable `COLLECT_K_BOUNDED` promotion.

## Next Work

Proceed to the final `v1.6` release package: release statement, support matrix,
audit report, tag preparation note, and final 3-AI consensus.
