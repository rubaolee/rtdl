# First Run

Status: V3 rebuild tutorial.

Start from the repository root:

```powershell
py -3 scripts\run_test_matrix.py --group v3_rebuild
py -3 scripts\rtdl_source_tree_doctor.py --json --run-smoke
```

Expected result:

- the `v3_rebuild` group passes;
- the source tree doctor reports required checks as pass;
- Windows may warn that local optional CUDA/OptiX/CuPy/Numba dependencies are
  absent.

Those local warnings do not contradict the pod evidence. The serious GPU
benchmark evidence was collected on the RTX 4000 Ada pod and copied under:

```text
docs/rebuild/v3/evidence/
```

Read next:

- [Hello World](02_hello_world.md)
- [V3 Setup And Rerun Runbook](../../docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md)
- [V3 Benchmark Evidence](../../docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md)
