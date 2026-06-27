# Phoenix V3 Triangle M18 Focused Runner Harness Evidence

Status: `focused_pod_attempt_1_consumed_failed_wrong_interpreter_no_performance_evidence`

This evidence directory is from the single M18 focused Triangle POD run that
Bernoulli authorized. The authorization was consumed, but the attempt failed
before CuPy/OptiX variants produced payloads because the command used
`/usr/bin/python3`, which did not have CuPy.

Intake report:

```text
docs/reports/phoenix_v3_m18_triangle_focused_pod_failed_env_intake_2026-06-22.md
```

```json
{
  "all_app_pod_spend_authorized": false,
  "all_variant_oracle_checks_passed": false,
  "broad_v3_faster_than_v2_claim_authorized": false,
  "comparisons": {},
  "dry_run": false,
  "edge_file_checksum_matches_expected": true,
  "edge_file_generated_now": true,
  "edge_file_preflight_status": "pass",
  "edge_file_sha256": "8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005",
  "failed_check_count": 6,
  "focused_pod_spend_authorized_now": false,
  "pod_run_authorized_by_m18": false,
  "public_speedup_claim_authorized": false,
  "release_authorized": false,
  "requires_later_2ai_for_pod": true,
  "runner_harness_exists": true,
  "schema": "rtdl.phoenix_v3.triangle_runner_m18_pod_ab.v1",
  "status": "triangle_runner_m18_harness_ready_not_pod_authorized",
  "third_strict_set_a_material_probe_closed": false,
  "variant_count": 2
}
```

The K4 edge-file identity gate and RT hardware gate passed, and the Embree
same-contract control matched the oracle. The legacy OptiX and productized
runner variants failed with `ModuleNotFoundError: No module named 'cupy'`.

This artifact does not authorize release, public speedup wording, broad
V3-over-V2 wording, all-app POD, or Triangle third strict Set-A closure. A
replacement run using
`/root/rtdl_v3_rebuild_20260620/.venv/bin/python` requires fresh 2-AI
authorization.
