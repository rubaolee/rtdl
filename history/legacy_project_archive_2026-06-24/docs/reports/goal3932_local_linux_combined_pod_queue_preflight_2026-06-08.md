# Goal3932 Local Linux Combined Pod Queue Preflight

Date: 2026-06-08

## Purpose

Goal3932 validates the Goal3927/Goal3931 chain on the local Linux development
host before spending A5000 pod time.

The preflight proves that:

- `scripts/goal3927_combined_pod_perf_queue.py --dry-run` writes a manifest;
- the manifest contains three planned commands;
- `scripts/goal3931_evaluate_combined_pod_perf_manifest.py` accepts the dry-run
  manifest with boundary status `accept_with_boundary`;
- all required planned commands are present.

## Local Preflight Result

Host: `192.168.1.20`

Command shape:

```bash
cd /home/lestat/work/rtdl_codex_local_check
export PYTHONPATH=src:.
python3 scripts/goal3927_combined_pod_perf_queue.py \
  --dry-run \
  --output-dir /tmp/goal3932_local_dry \
  --rtdl-optix-library /home/lestat/work/rtdl_codex_local_check/build/librtdl_optix.so
python3 scripts/goal3931_evaluate_combined_pod_perf_manifest.py \
  /tmp/goal3932_local_dry/summary_manifest.json
```

Observed summary:

```text
runner_status=dry_run
planned_commands=3
intake_status=accept_with_boundary
required_commands_present=True
```

## Pod Availability Note

The last known pod endpoint, `root@69.30.85.203:22057`, rejected the known key
with `Permission denied (publickey,password)`. No A5000 evidence was collected
from that endpoint in this goal.

## Boundary

Goal3932 is preflight evidence only. It does not run performance workloads,
authorize route promotion, authorize release wording, authorize public speedup
claims, authorize broad RT-core claims, authorize true-zero-copy claims, or
claim RayJoin/RTDBSCAN paper reproduction.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3932_local_linux_combined_pod_queue_preflight_test tests.goal3931_combined_pod_perf_manifest_intake_evaluator_test
```

Expected: all tests pass.
