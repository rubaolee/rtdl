# Goal4308: RTNN Embree Front Door For The v2.11 Packet

Date: 2026-06-11

## Verdict

`accept-with-boundary` for closing the Fable5 F7 RTNN Embree asymmetry.

Goal4298 honestly recorded RTNN as the only v2.11 Embree CPU packet row without
an Embree front door. Goal4308 removes that hard-coded exception by adding an
RTNN benchmark-app mode named `ann_embree_quality` and updating the current
Embree CPU reference registry to use it.

## What Changed

- Added `ann_embree_quality` to
  `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`.
- The mode wraps the existing generic ANN candidate app's Embree KNN route and
  reports it through the RTNN benchmark front door.
- After Claude Goal4309 and Goal4312 review, the wrapper exposes the inherited
  ANN RT-path note through `rt_path_note` and removes the inherited
  `optix_performance` key from the RTNN Embree output so the front door is not
  read as measuring OptiX performance.
- Updated `src/rtdsl/current_embree_cpu_partner_reference.py`:
  - version becomes `rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1`;
  - RTNN row becomes `rtnn_embree_cpu_ann_candidate_quality_reference`;
  - RTNN no longer uses the Numba-only packet exception;
  - validator now requires every benchmark row, including RTNN, to exercise
    Embree CPU.
- Updated the current Embree CPU packet test to expect ten Embree rows.
- Updated the historical Goal4298 report with a Goal4308 follow-up note.

## Boundary

The new RTNN Embree front door is for the 2-D ANN candidate-quality contract:

- Python chooses a candidate subset.
- Embree runs k=1 nearest-neighbor rows over that candidate subset.
- Python compares the candidate-subset result with the exact full-set oracle.

This is not the 3-D RTNN ranked-summary path, not full RTNN paper reproduction,
not a speedup claim, and not NVIDIA RT-core evidence. It is Embree CPU
compatibility coverage for the RTNN benchmark app's smaller ANN candidate
contract.

Goal4308 does not authorize:

- release action,
- package-install wording,
- public speedup wording,
- whole-app acceleration wording,
- broad RT-core wording,
- Intel GPU performance wording,
- true-zero-copy wording,
- automatic partner selection,
- paper reproduction claims,
- app-specific native-engine logic.

## Validation

Windows smoke:

```text
$env:PYTHONPATH='src;.'; py -3 scripts\rtdl_v2_11_embree_cpu_partner_reference_runner.py --dry-run --only rtnn --threads 2
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\rtnn\rtdl_rtnn_benchmark_app.py --mode ann_embree_quality --copies 1
```

Local Linux executable row:

```text
PYTHONPATH=src:. python3 scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py --only rtnn --threads 8 --output-json docs/reports/goal4308_rtnn_embree_front_door_local_linux.json

[v2.11-embree-cpu] 1/1 start rtnn_embree_cpu_ann_candidate_quality_reference timeout=180s threads=8
[v2.11-embree-cpu] 1/1 done rtnn_embree_cpu_ann_candidate_quality_reference status=pass elapsed=0.543s
```

Focused local Linux regression guard:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal4308_rtnn_embree_front_door_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test tests.goal4307_editable_source_tree_onboarding_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4305_fable5_evidence_and_process_docs_test tests.goal4303_current_security_redaction_guard_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test

Ran 31 tests in 1.730s
OK
```

Artifact:

`docs/reports/goal4308_rtnn_embree_front_door_local_linux.json`

Key artifact fields:

```json
{
  "all_pass": true,
  "version": "rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1",
  "validation": {"status": "accept", "errors": []},
  "rows": [
    {
      "row_id": "rtnn_embree_cpu_ann_candidate_quality_reference",
      "uses_embree": true,
      "uses_numba": false,
      "stdout_tail_contains_rt_path_note": true,
      "stdout_tail_contains_optix_performance": false,
      "status": "pass"
    }
  ]
}
```

## Remaining Work

The larger 3-D RTNN ranked-summary Embree path is still not implemented. It
should only be added if the benchmark campaign needs a CPU fallback for that
specific contract. Goal4308's purpose is narrower: remove the registry-level
RTNN exception without pretending Embree now covers the full RTNN paper-shaped
path.
